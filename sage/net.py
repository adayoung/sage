# -*- coding: utf-8 -*-
"""
This file creates a telnet proxy and works like this:

Local Client <--> TelnetServer() <--> TelnetClient() <--> Remote Server
"""
from __future__ import absolute_import
from twisted.conch.telnet import Telnet, StatefulTelnetProtocol
from twisted.internet.protocol import ClientFactory, ServerFactory
from twisted.internet import reactor
from autobahn.websocket import listenWS
from autobahn.wamp import WampServerFactory, WampServerProtocol
import sage
from sage.utils import error
from sage import inbound, outbound, gmcp, prompt, config, _log
from sage.signals import net as signal
from sage.signals import post_prompt, pre_prompt
import re
import zlib


""" TELNET VALUES """
NULL = chr(0)       # NULL
ECHO = chr(1)       # Telnet Echo
SGA = chr(3)        # Suppress Go-Ahead
BEL = chr(7)        # Produces an audible or visible signal (which does NOT move the print head).
BS = chr(8)         # Moves the print head one character position towards the left margin.
HT = chr(9)         # Moves the printer to the next horizontal tab stop.
LF = chr(10)        # Moves the printer to the next print line, keeping the same horizontal position.
NL = chr(10)        # Newline
VT = chr(11)        # Moves the printer to the next vertical tab stop.
FF = chr(12)        # Moves the printer to the top of the next page, keeping the same horizontal position.
CR = chr(13)        # Carriage Return
EOR = chr(25)       # End of record
ESC = chr(27)       # Escape byte
NAWS = chr(31)      # Negotiate About Window Size
LINEMODE = chr(34)
COMPRESS = chr(85)   # MCCP Version 1
COMPRESS2 = chr(86)  # MCCP Version 2
ATCP = chr(200)     # ATCP
GMCP = chr(201)     # GMCP
EORD = chr(239)     # End of Record indicator
SE = chr(240)       # End of subnegotiation parameters
NOP = chr(241)      # No operation
DM = chr(242)       # "Data Mark": The data stream portion of a Synch.  This should always be accompanied by a TCP Urgent notification.
BRK = chr(243)      # NVT character Break.
IP = chr(244)       # The function Interrupt Process.
AO = chr(245)       # The function Abort Output
AYT = chr(246)      # The function Are You There.
EC = chr(247)       # The function Erase Character.
EL = chr(248)       # The function Erase Line
GA = chr(249)       # Go ahead
SB = chr(250)       # Subnegotiation of the indicated option follows.
WILL = chr(251)     # Indicates the desire to begin performing, or confirmation that you are now performing, the indicated option.
WONT = chr(252)     # Indicates the refusal to perform, or continue performing, the indicated option.
DO = chr(253)       # Indicates the request that the other party perform, or confirmation that you are expecting the other party to perform, the indicated option.
DONT = chr(254)     # Indicates the demand that the other party stop performing, or confirmation that you are no longer expecting the other party to perform, the indicated option.
IAC = chr(255)      # Interpret as a command


class TelnetClient(Telnet):
    """ Connects to the remote server. """

    def __init__(self):
        Telnet.__init__(self)

        self.compress = False
        self.decompressobj = zlib.decompressobj()
        self.compressobj = zlib.compressobj()

        self.gmcp = gmcp.GMCP(self)
        sage.gmcp = self.gmcp  # make easily accessible
        self.gmcp_passthrough = False  # send GMCP to client

        # Hold over incomplete app data until the next packet
        self.data_buffer = ''

        # Setup recieving GMCP negotation
        self.negotiationMap[GMCP] = self.gmcpRecieved
        self.negotiationMap[COMPRESS2] = self.enableCompress

        # telnet options to enable
        self.options_enabled = (
            GMCP,
            EOR,
            #COMPRESS2  # MCCP2 seems to break GMCP's Core.Ping in Achaea
        )

        self.options_disabled = ()

        self.buffer = ''  # Buffer of recieved data

        # Used to identify a line that is only a color code
        self.color_prefix = chr(27) + '[1;'

        # Achaea will sometimes give us a line that is just a color code...
        self.color_newline = re.compile('^' + ESC + '\[[0-9;]*[m]' + NL)

        #self.write_server = self.server.transport.write

    def applicationDataReceived(self, data):
        """ Gather data until we get EOR or GA (prompt) """

        self.data_buffer += data

    def segmentReceived(self):
        data = self.data_buffer
        self.data_buffer = ''

        # don't lead with a newline
        if data[0] == NL:
            data = data[1:]

        # Fix color-only leading line
        color_newline = self.color_newline.match(data)
        if color_newline:
            color = data[0:color_newline.end() - 1]
            data = color + data[color_newline.end():]

        data = data.split('\n')

        pre_prompt.send_robust(sender=None, raw_data=data)

        # lines recieved
        lines = data[:-1]

        # last line is always the prompt
        prompt_data = data[-1]

        # Send the prompt to the prompt receiver
        prompt_output = prompt.receiver(prompt_data)

        # send lines to inbound receiver
        lines = inbound.receiver(lines)

        post_prompt.send_robust(sender=None)

        output = ''

        if len(lines):
            output = '\r\n'.join(lines) + '\r\n'

        output += prompt_output + '\r\n'

        signal.pre_outbound.send_robust(sender=self, lines=sage.buffer,
            prompt=prompt_output)

        self.to_client(output)

    def connectionMade(self):
        for option in self.options_enabled:
            self.do(option)

        sage.connected = True
        self.server.ready()
        signal.connected.send_robust(sender=self)
        sage._send = self.transport.write

    def connectionLost(self, reason):
        sage.connected = False
        signal.disconnected.send_robust(sender=self)
        if self.server is not None:
            self.server.transport.loseConnection()
            self.server = None

    def dataReceived(self, data):
        """ Recieves and processes raw data from the server """

        if self.compress:
            data = self.decompressobj.decompress(data)

        appDataBuffer = []

        for b in data:
            if self.state == 'data':
                if b == IAC:
                    self.state = 'escaped'
                elif b == '\r':
                    self.state = 'newline'
                else:
                    appDataBuffer.append(b)
            elif self.state == 'escaped':
                if b == IAC:
                    appDataBuffer.append(b)
                    self.state = 'data'
                elif b == SB:
                    self.state = 'subnegotiation'
                    self.commands = []
                elif b in (GA, EORD, NOP, DM, BRK, IP, AO, AYT, EC, EL):
                    self.state = 'data'
                    if appDataBuffer:
                        self.applicationDataReceived(''.join(appDataBuffer))
                        del appDataBuffer[:]
                    self.commandReceived(b, None)
                    if b == EORD or b == GA:
                        self.segmentReceived()
                elif b in (WILL, WONT, DO, DONT):
                    self.state = 'command'
                    self.command = b
                else:
                    self.state = 'data'
                    appDataBuffer.append(b)
                    error("Unexpected signal: %s" % ord(b))
            elif self.state == 'command':
                self.state = 'data'
                command = self.command
                del self.command
                if appDataBuffer:
                    self.applicationDataReceived(''.join(appDataBuffer))
                    del appDataBuffer[:]
                self.commandReceived(command, b)
            elif self.state == 'newline':
                self.state = 'data'
                if b == '\n':
                    appDataBuffer.append('\n')
                elif b == '\0':
                    appDataBuffer.append('\r')
                elif b == IAC:
                    # IAC isn't really allowed after \r, according to the
                    # RFC, but handling it this way is less surprising than
                    # delivering the IAC to the app as application data.
                    # The purpose of the restriction is to allow terminals
                    # to unambiguously interpret the behavior of the CR
                    # after reading only one more byte.  CR LF is supposed
                    # to mean one thing (cursor to next line, first column),
                    # CR NUL another (cursor to first column).  Absent the
                    # NUL, it still makes sense to interpret this as CR and
                    # then apply all the usual interpretation to the IAC.
                    appDataBuffer.append('\r')
                    self.state = 'escaped'
                else:
                    appDataBuffer.append('\r' + b)
            elif self.state == 'subnegotiation':
                if b == IAC:
                    self.state = 'subnegotiation-escaped'
                else:
                    self.commands.append(b)
            elif self.state == 'subnegotiation-escaped':
                if b == SE:
                    self.state = 'data'
                    commands = self.commands
                    del self.commands
                    if appDataBuffer:
                        self.applicationDataReceived(''.join(appDataBuffer))
                        del appDataBuffer[:]
                    self.negotiate(commands)
                else:
                    self.state = 'subnegotiation'
                    self.commands.append(b)
            else:
                error("Invalid telnet state")

        if appDataBuffer:
            self.applicationDataReceived(''.join(appDataBuffer))

    def enableRemote(self, option):

        if option in self.options_enabled:

            if option == GMCP:
                self.gmcp.hello()
                self.gmcp.set_support()

            return True

        return False

    def enableCompress(self, data):
        """ Called for IAC SB COMPRESS2. Enable compression. """

        self.compress = True

    def gmcpRecieved(self, data):
        """ Send GMCP data to the GMCP reciever """

        data = ''.join(data)
        self.gmcp.call(data)

        if self.gmcp_passthrough:
            self.server.write(IAC + SB + GMCP + data + IAC + SE)

    def to_client(self, data):
        """ Send to connected client """

        if self.server.connected is False:
            self.buffer += data
            return

        self.server.write(data)

# client instance
client = TelnetClient()


class TelnetClientFactory(ClientFactory):

    def __init__(self):
        self.client = client

    def buildProtocol(self, addr):
        return self.client


class TelnetServerFactory(ServerFactory):
    pass


class TelnetServer(Telnet, StatefulTelnetProtocol):
    """
    Local client connects to TelnetServer().
    TelnetServer() connects to TelnetClient()
    """

    def __init__(self):
        Telnet.__init__(self)
        self.client_factory = TelnetClientFactory()

        self.data_buffer = ''

        if self.client_factory.client.connected:
            self.ready()

    def ready(self):
        """ Gets called when the client successfully connects """
        self.applicationDataReceived = self._applicationDataReceived
        self.applicationDataReceived(self.data_buffer)
        self.data_buffer = ''

    def connectionMade(self):
        """ Local client connected. Start client connection to server. """
        self.factory.transports.append(self.transport)
        self.transport.write("Connected to Sage\n")
        self.client = self.client_factory.client
        self.client.server = self
        sage._echo = self.write

        if len(self.client.buffer) > 0:
            self.write(">>> Data in buffer >>>\n")
            self.write(self.client.buffer)
            self.write("<<< End of buffer <<<\n")
            self.client.buffer = ''

        if bool(self.client.connected) is False:
            reactor.connectTCP(config.host, config.port, self.client_factory)

        self.will(GMCP)

    def connectionLost(self, reason):
        self.connected = False
        self.factory.transports.remove(self.transport)
        if sage.connected:
            _log.msg('Client disconnected. Sage is still connected to Achaea.')

    def applicationDataReceived(self, data):
        if self.client.transport is None:
            self.data_buffer += data

    def _applicationDataReceived(self, data):
        if data == NL:
            self.client.transport.write(data)

        if NL in data:
            data = data.replace(CR, '').split(NL)[:-1]

            for line in data:
                if line == '':
                    continue

                line = outbound.receiver(line)

                if line:
                    self.client.transport.write(line + CR + NL)

    def write(self, data):
        for transport in self.factory.transports:
            transport.write(data)

    def enableLocal(self, option):
        if option == GMCP:
            self.client.gmcp_passthrough = True
            return True

        return False


class SAGEProtoServerProtocol(WampServerProtocol):

    def onSessionOpen(self):
        self.registerForPubSub("http://sage/event#", True)
        self.registerMethodForRpc('http://sage/input', self, SAGEProtoServerProtocol.input)
        self.registerMethodForRpc('http://sage/is_connected', self, SAGEProtoServerProtocol.is_connected)

    def input(self, msg):
        sage.send(msg.encode('us-ascii'))

    def is_connected(self):
        self.dispatch('http://sage/event#connected', sage.connected)


def build_telnet_factory():
    """ Setup Twisted factory """

    factory = TelnetServerFactory()
    factory.protocol = TelnetServer
    factory.transports = []
    reactor.listenTCP(config.telnet_port, factory)
    return factory


def build_ws_factory():
    """ Setup Websocket factory """

    factory = WampServerFactory("ws://%s:%s" % (config.ws_host, config.ws_port), debugWamp=config.ws_debug)
    factory.protocol = SAGEProtoServerProtocol
    factory.setProtocolOptions(allowHixie76=True)
    listenWS(factory)
    return factory
