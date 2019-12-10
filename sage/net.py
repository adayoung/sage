# -*- coding: utf-8 -*-
"""
This file creates a telnet proxy and works like this:

Local Client <--> TelnetServer() <--> TelnetClient() <--> Remote Server
"""


import re
import zlib

from twisted.conch.telnet import Telnet, StatefulTelnetProtocol
from twisted.internet import reactor
from twisted.internet.protocol import ClientFactory, ServerFactory
from twisted.python.compat import _bytesChr as chr, iterbytes

import sage
from sage import inbound, outbound, gmcp, prompt, config, _log, ansi, aliases
from sage.signals import net as signal
from sage.signals import post_prompt, pre_prompt
from sage.utils import error, utf8_to_str

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


class ISageProxyReceiver(object):

    def __init__(self):
        self.connected = False

    def ready(self):
        raise NotImplementedError("Ready is not implemented in %s" % self.__class__)

    def write(self, data):
        raise NotImplementedError("Write is not implemented in %s" % self.__class__)

    def send(self, data):
        raise NotImplementedError("Send is not implemented in %s" % self.__class__)

    def input(self, lines, prompt):
        raise NotImplementedError("Input is not implemented in %s" % self.__class__)


class Receivers(list):

    def ready(self):
        for r in self:
            r.ready()

    def write(self, data):
        for r in self:
            r.write(data)

    def input(self, lines, prompt):
        for r in self:
            r.input(lines, prompt)


class TelnetClient(Telnet):
    """ Connects to the remote server. """

    def __init__(self):
        Telnet.__init__(self)

        # ISageProxyReceiver receivers (like a Telnet Server or a WS Server)
        self.receivers = Receivers()

        self.compress = False
        self.decompressobj = zlib.decompressobj()
        self.compressobj = zlib.compressobj()

        self.gmcp = gmcp.GMCP(self)
        sage.gmcp = self.gmcp  # make easily accessible

        # Hold over incomplete app data until the next packet
        self.data_buffer = b''
        self.outbound_buffer = b''

        # Setup recieving GMCP negotation
        self.negotiationMap[GMCP] = self.gmcpReceived
        self.negotiationMap[COMPRESS2] = self.enableCompress

        # telnet options to enable
        self.options_enabled = (
            GMCP,
            EOR,
            #COMPRESS2  # MCCP2 seems to break GMCP's Core.Ping in Achaea
        )

        self.options_disabled = ()

        # Used to identify a line that is only a color code
        self.color_prefix = chr(27) + b'[1;'

        # Achaea will sometimes give us a line that is just a color code...
        self.color_newline = re.compile(b'^' + ESC + b'\[[0-9;]*[m]' + NL)

    def addReceiver(self, receiver):
        """ Helper method for adding an ISageProxyReceiver """
        self.receivers.append(receiver)

    def applicationDataReceived(self, data):
        """ Gather data until we get EOR or GA (prompt) """

        self.data_buffer += data

    def segmentReceived(self):
        data = self.data_buffer
        self.data_buffer = b''

        # don't lead with a newline
        if data[0] == NL:
            data = data[1:]

        # Fix color-only leading line
        color_newline = self.color_newline.match(data)
        if color_newline:
            color = data[0:color_newline.end() - 1]
            data = color + data[color_newline.end():]

        data = data.split(b'\n')

        pre_prompt.send(raw_data=data)

        # lines received
        lines = data[:-1]

        # last line is always the prompt
        prompt_data = data[-1]

        # Send the prompt to the prompt receiver
        try:
            prompt_output = prompt.receiver(prompt_data)
        except Exception as err:
            _log.err()
            prompt_output = "%s - %s" % (ansi.bold_red('ERROR:'), ansi.red(str(err)))

        # send lines to inbound receiver
        sage.gmcp_buffer = self.gmcp.receiver.buffer
        lines = inbound.receiver(lines)
        self.gmcp.receiver.clear()

        post_prompt.send()

        signal.pre_outbound.send(
            raw_lines=sage.buffer,
            lines=lines,
            ansi_prompt=prompt_output,
            prompt=ansi.filter_ansi(prompt_output)
        )

        lines = [ line.encode("utf-8") for line in lines ]
        prompt_output = prompt_output.encode("utf-8")
        self.receivers.input(lines, prompt_output)

    def connect(self):
        """ Initiate connection to Achaea """
        if not sage.connected:
            reactor.connectTCP(config.host, config.port, TelnetClientFactory())

    def disconnect(self):
        """ Disconnect client from Achaea """
        self.transport.loseConnection()

    def reset(self):
        """ Reset the client for a new connection """
        self.options = {}  # reset negotiation options
        self.gmcp = gmcp.GMCP(self)
        sage.gmcp = self.gmcp

    def connectionMade(self):
        for option in self.options_enabled:
            self.do(option)

        sage.connected = True
        self.receivers.ready()
        signal.connected.send()
        sage._send = self.transport.write

    def connectionLost(self, reason):
        self.receivers.write(self.data_buffer)
        sage.connected = False
        signal.disconnected.send()

        self.reset()

        self.receivers.write(b"Sage has disconnected from Achaea." + IAC + GA)

        if config.exit_on_disconnect is True:
            if reactor.running:
                self.receivers.write(b"sage.config.exit_on_disconnect is enabled. Shutting down Sage." + IAC + GA)
                reactor.callLater(1, reactor.stop)
        else:
            self.receivers.write(b"Sage is still running. Type '.connect' to reconnect." + IAC + GA)


    def dataReceived(self, data):
        """ Recieves and processes raw data from the server """

        if sage.lagging:
            sage.lagging = False
            signal.lag_recovered.send()

        #if self.compress:  # disabled until it works with GMCP
            #data = self.decompressobj.decompress(data)

        appDataBuffer = []

        for b in iterbytes(data):
            if self.state == 'data':
                if b == IAC:
                    self.state = 'escaped'
                elif b == b'\r':
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
                elif b in (NOP, DM, BRK, IP, AO, AYT, EC, EL, GA, EORD):
                    self.state = 'data'
                    if appDataBuffer:
                        self.applicationDataReceived(b''.join(appDataBuffer))
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
                    self.applicationDataReceived(b''.join(appDataBuffer))
                    del appDataBuffer[:]
                self.commandReceived(command, b)
            elif self.state == 'newline':
                self.state = 'data'
                if b == b'\n':
                    appDataBuffer.append(b'\n')
                elif b == b'\0':
                    appDataBuffer.append(b'\r')
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
                    appDataBuffer.append(b'\r')
                    self.state = 'escaped'
                else:
                    appDataBuffer.append(b'\r' + b)
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
                        self.applicationDataReceived(b''.join(appDataBuffer))
                        del appDataBuffer[:]
                    self.negotiate(commands)
                else:
                    self.state = 'subnegotiation'
                    self.commands.append(b)
            else:
                error("Invalid telnet state")

        if appDataBuffer:
            self.applicationDataReceived(b''.join(appDataBuffer))

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

    def gmcpReceived(self, data):
        """ Send GMCP data to the GMCP reciever """
        data = b''.join(data)
        self.gmcp.read(data, source='server')

    def send(self, data):

        if data == '':
            self.transport.write(CR + NL + GA)
            return

        if data == NL:
            self.transport.write(CR + NL + GA)
            return

        if NL not in data:
            line = outbound.receiver(data) or ""
            data = line.encode("utf-8")
            self.transport.write(data + CR + NL + GA)
        else:
            data = data.replace(b'\r', b'').split(b'\n')[:-1]

            for line in data:
                if line == b'':
                    self.transport.write(CR + NL + GA)
                    continue

                line = outbound.receiver(line)

                if line:
                    data = line.encode("utf-8")
                    self.transport.write(data + CR + NL + GA)


# client instance
client = TelnetClient()


class TelnetClientFactory(ClientFactory):

    def __init__(self):
        self.client = client

    def buildProtocol(self, addr):
        return self.client


class TelnetServerFactory(ServerFactory):

    def buildProtocol(self, addr):
        instance = TelnetServer(client)
        instance.factory = self
        return instance


class TelnetServer(Telnet, StatefulTelnetProtocol, ISageProxyReceiver):
    """
    Local client connects to TelnetServer().
    TelnetServer() connects to TelnetClient()
    """

    def __init__(self, telnet_client):
        Telnet.__init__(self)
        self.reset()
        self.client = telnet_client

        self.negotiationMap[GMCP] = self.gmcpReceived

        # telnet options to enable
        self.options_enabled = (
            GMCP,
            EOR,
        )

        self.options_disabled = ()

        if self not in self.client.receivers:
            self.client.addReceiver(self)

        self.outbound_buffer = b''
        self.inbound_buffer = b''

        if self.client.connected:
            self.ready()

    def ready(self):
        """ Gets called when the client successfully connects """
        self.applicationDataReceived = self._applicationDataReceived
        self.applicationDataReceived(self.outbound_buffer)
        self.outbound_buffer = b''

    def reset(self):
        self.applicationDataReceived = self._buffer_applicationDataReceived

    def connectionMade(self):
        """ Local client connected. Start client connection to server. """
        self.factory.transports.append(self.transport)

        # self.transport.write("Connected to Sage\n")
        sage._echo = self.write

        if bool(self.client.connected) is False:
            self.write(b"Connected to Sage\n")
            self.client.connect()
        else:
            self.write(b"Reconnected to Sage\n")

        self.will(GMCP)

        if len(self.client.outbound_buffer) > 0:
            self.write(b">>> Start Buffer >>>\n")
            self.write(self.client.outbound_buffer)
            self.write(b">>> End Buffer >>>\n")

        self.client.outbound_buffer = b''

    def connectionLost(self, reason):
        self.connected = False
        self.factory.transports.remove(self.transport)
        self.reset()
        if sage.connected:
            _log.msg('Client disconnected. Sage is still connected to Achaea.')

    def gmcpReceived(self, data):
        """ Forward GMCP data from user client to game server """
        data = b''.join(data)
        self.client.gmcp.read(data, source='client')

    def applicationDataReceived(self, data):
        pass

    def _buffer_applicationDataReceived(self, data):
        if self.client.transport is None:
            self.outbound_buffer += data

    def _applicationDataReceived(self, data):
        """
        Input from local clients received, passes it on to TelnetClient
        Remote Server <- TelnetClient <- TelnetServer._applicationDataReceived() <- Local Clients
        """
        self.client.send(data)

    def write(self, data):
        """
        Writes assembled data (lines + prompt) coming from Achaea to clients
        TelnetServer.write() -> Local clients
        """
        if len(self.factory.transports) == 0:
            self.client.outbound_buffer += data

        self.transport.write(data)

    def enableLocal(self, option):
        if option == GMCP:
            self.client.gmcp.client_passthrough = True
            return True

        return False

    def input(self, lines, prompt):
        """ Assembles data from Achaea, passes it to self.write to be emitted to clients """
        if len(lines) > 0:
            output = b'\r\n'.join(lines) + b'\r\n'
        else:
            output = b''

        output += prompt + IAC + EORD

        self.write(output)


def build_telnet_factory():
    """ Setup Twisted factory """

    factory = TelnetServerFactory()
    factory.protocol = TelnetServer
    factory.transports = []
    reactor.listenTCP(config.telnet_port, factory)
    return factory


net_aliases = aliases.get_group('sage')


@net_aliases.exact('.connect')
def connect(alias):
    if sage.connected is False:
        client.connect()


@net_aliases.exact('.disconnect')
def disconnect(alias):
    client.disconnect()


@net_aliases.exact('.disconnect')
def disconnect(alias):
    client.disconnect()

