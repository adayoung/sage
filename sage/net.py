# -*- coding: utf-8 -*-
"""
This file creates a telnet proxy and works like this:

Local Client <--> TelnetServer() <--> TelnetClient() <--> Remote Server
"""
from __future__ import absolute_import
from twisted.conch.telnet import Telnet, StatefulTelnetProtocol
from twisted.internet.defer import inlineCallbacks
from twisted.internet.protocol import ClientFactory, ServerFactory
from twisted.internet.endpoints import serverFromString
from twisted.internet import reactor
#from autobahn.websocket import listenWS
#from autobahn.wamp import WampServerFactory, WampServerProtocol
from autobahn.twisted.wamp import ApplicationSession, ApplicationSessionFactory    # New shit
from autobahn.twisted.websocket import WampWebSocketClientFactory, WampWebSocketServerFactory, WampWebSocketServerProtocol   # Wamp-over-Websocket transport
from autobahn.wamp import router, broker, dealer
from autobahn.websocket.protocol import parseWsUrl
from autobahn.twisted.wamp import RouterFactory
from autobahn.twisted.wamp import RouterSessionFactory
# from autobahn.twisted.wamp import ApplicationRunner
from autobahn.wamp.types import ComponentConfig

import sage
from sage.utils import error
from sage import inbound, outbound, gmcp, prompt, config, _log, ansi
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


class ISageProxy(object):

    def __init__(self):
        self.connected = False

    def ready(self):
        pass

    def write(self, data):
        pass

    def send(self, data):
        pass


class ISageWSProxy(ISageProxy):

    def instream(self, lines, prompt):
        pass

class TelnetClient(Telnet):
    """ Connects to the remote server. """

    def __init__(self):
        Telnet.__init__(self)

        self.ws_server = ISageWSProxy()
        self.wamp_client = None  # Ref to ApplicationSession object -- main component for WAMP
        self.telnet_server = ISageProxy()

        self.compress = False
        self.decompressobj = zlib.decompressobj()
        self.compressobj = zlib.compressobj()

        self.gmcp = gmcp.GMCP(self)
        sage.gmcp = self.gmcp  # make easily accessible
        self.gmcp_passthrough = False  # send GMCP to client

        # Hold over incomplete app data until the next packet
        self.data_buffer = ''
        self.outbound_buffer = ''

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

        # Used to identify a line that is only a color code
        self.color_prefix = chr(27) + '[1;'

        # Achaea will sometimes give us a line that is just a color code...
        self.color_newline = re.compile('^' + ESC + '\[[0-9;]*[m]' + NL)

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

        pre_prompt.send(raw_data=data)

        # lines recieved
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
        lines = inbound.receiver(lines)

        post_prompt.send()

        output = ''

        if len(lines):
            output = '\r\n'.join(lines) + '\r\n'

        output += prompt_output + '\r\n'

        signal.pre_outbound.send(
            lines=sage.buffer,
            ansi_prompt=prompt_output,
            prompt=ansi.filter_ansi(prompt_output)
        )

        self.ws_server.instream(lines, prompt_output)
        self.telnet_server.write(output)

    def connectionMade(self):
        for option in self.options_enabled:
            self.do(option)

        sage.connected = True
        self.telnet_server.ready()
        self.ws_server.ready()
        signal.connected.send()
        sage._send = self.transport.write

    def connectionLost(self, reason):
        self.telnet_server.write(self.data_buffer)
        sage.connected = False
        signal.disconnected.send()
        self.telnet_server.write("Disconnected from Achaea.")
        reactor.stop()

    def dataReceived(self, data):
        """ Recieves and processes raw data from the server """

        if sage.lagging:
            sage.lagging = False
            signal.lag_recovered.send()

        #if self.compress:  # disabled until it works with GMCP
            #data = self.decompressobj.decompress(data)

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
            self.telnet_server.write(IAC + SB + GMCP + data + IAC + SE)

    def send(self, data):
        if data == '':
            return

        if data == NL:
            self.transport.write(CR + NL)
            return

        if NL not in data:
            line = outbound.receiver(data)
            self.transport.write(line + CR + NL)
        else:
            data = data.replace(CR, '').split(NL)[:-1]

            for line in data:
                if line == '':
                    continue

                line = outbound.receiver(line)

                if line:
                    self.transport.write(line + CR + NL)


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
        self.reset()
        self.client_factory = TelnetClientFactory()
        self.client = self.client_factory.client
        self.client.telnet_server = self

        self.outbound_buffer = ''
        self.inbound_buffer = ''

        if self.client_factory.client.connected:
            self.ready()

    def ready(self):
        """ Gets called when the client successfully connects """
        self.applicationDataReceived = self._applicationDataReceived
        self.applicationDataReceived(self.outbound_buffer)
        self.outbound_buffer = ''

    def reset(self):
        self.applicationDataReceived = self._buffer_applicationDataReceived

    def connectionMade(self):
        """ Local client connected. Start client connection to server. """
        self.factory.transports.append(self.transport)
        self.transport.write("Connected to Sage\n")
        sage._echo = self.write

        if bool(self.client.connected) is False:
            self.transport.write("Connected to Sage\n")
            reactor.connectTCP(config.host, config.port, self.client_factory)
        else:
            self.transport.write("Reconnected to Sage\n")

        self.will(GMCP)

        if len(self.client.outbound_buffer) > 0:
            self.transport.write(">>> Start Buffer >>>\n")
            self.write(self.client.outbound_buffer)
            self.transport.write(">>> End Buffer >>>\n")

        self.client.outbound_buffer = ''

    def connectionLost(self, reason):
        self.connected = False
        self.factory.transports.remove(self.transport)
        self.reset()
        if sage.connected:
            _log.msg('Client disconnected. Sage is still connected to Achaea.')

    def applicationDataReceived(self, data):
        pass

    def _buffer_applicationDataReceived(self, data):
        if self.client.transport is None:
            self.outbound_buffer += data

    def _applicationDataReceived(self, data):
        self.client.send(data)

    def write(self, data):
        for transport in self.factory.transports:
            transport.write(data)
            self.client.wamp_client.write(data)

        if len(self.factory.transports) == 0:
            self.client.outbound_buffer += data

    def enableLocal(self, option):
        if option == GMCP:
            self.client.gmcp_passthrough = True
            return True

        return False


def build_telnet_factory():
    """ Setup Twisted factory """

    factory = TelnetServerFactory()
    factory.protocol = TelnetServer
    factory.transports = []
    reactor.listenTCP(config.telnet_port, factory)
    return factory

from twisted.internet.protocol import Factory, Protocol
from twisted.internet.endpoints import TCP4ClientEndpoint

# Pls don't kill me todd, I know it's ugly. We'll fix this prototype soon
class Greeter(Protocol):
    def sendMessage(self, msg):
        # self.transport.write("blelaksdjflsf\r\n")
        pass

    def dataReceived(self, data):
        pass

class GreeterFactory(Factory):
    def buildProtocol(self, addr):
        return Greeter()

def gotProtocol(p):
    p.sendMessage("Hello")

class WampComponent(ApplicationSession, ISageWSProxy):

    @inlineCallbacks
    def onJoin(self, details):

        # We have to set this reference somewhere
        # this may not be the way to do it, but this is
        # how it's getting done for now
        if client.wamp_client is None:
            client.wamp_client = self

        import sage
        print "on join"

        def ready():
            point = TCP4ClientEndpoint(reactor, "localhost", 5493)
            d = point.connect(GreeterFactory())
            d.addCallback(gotProtocol)


        def onIOEvent(msg):
            # We must decode to ascii because browsers may send unicode
            tmp_msg = msg.encode('ascii', 'ignore')
            client.send(tmp_msg)
            
        yield self.register(ready, u"com.sage.wsclientready")
        yield self.subscribe(onIOEvent, u"com.sage.io") 
        # allplayers = yield self.call(u'com.pyrator.getplayercities', ["mhaldor", "ashtan", "hashan", "targossas", "cyrene", "eleusis"])

        # print allplayers

    @inlineCallbacks
    def instream(self, lines, prompt):
        yield self.publish(u'com.sage.io', [lines, prompt])

    def write(self, data):
        self.publish(u'com.sage.io', data)

class ApplicationRunner:
    """
    This class is a convenience tool mainly for development and quick hosting
    of WAMP application components.
    It can host a WAMP application component in a WAMP-over-WebSocket client
    connecting to a WAMP router.
    """

    def __init__(self, url, realm, extra = None, serializers = None, standalone = False,
        debug = False, debug_wamp = False, debug_app = False):
        """
        :param url: The WebSocket URL of the WAMP router to connect to (e.g. `ws://somehost.com:8090/somepath`)
        :type url: unicode
        :param realm: The WAMP realm to join the application session to.
        :type realm: unicode
        :param extra: Optional extra configuration to forward to the application component.
        :type extra: dict
        :param serializers: A list of WAMP serializers to use (or None for default serializers).
        Serializers must implement :class:`autobahn.wamp.interfaces.ISerializer`.
        :type serializers: list
        :param debug: Turn on low-level debugging.
        :type debug: bool
        :param debug_wamp: Turn on WAMP-level debugging.
        :type debug_wamp: bool
        :param debug_app: Turn on app-level debugging.
        :type debug_app: bool
        """
        self.url = url
        self.realm = realm
        self.extra = extra or dict()
        self.standalone = standalone
        self.debug = debug
        self.debug_wamp = debug_wamp
        self.debug_app = debug_app
        self.make = None
        self.serializers = serializers


    def run(self, make, start_reactor = True):
        """
        Run the application component.
        :param make: A factory that produces instances of :class:`autobahn.asyncio.wamp.ApplicationSession`
        when called with an instance of :class:`autobahn.wamp.types.ComponentConfig`.
        :type make: callable
        """
        from twisted.internet import reactor

        isSecure, host, port, resource, path, params = parseWsUrl(self.url)

        ## start logging to console
        if self.debug or self.debug_wamp or self.debug_app:
            log.startLogging(sys.stdout)

        ## factory for use ApplicationSession
        def create():
            cfg = ComponentConfig(self.realm, self.extra)
            try:
                session = make(cfg)
            except Exception:
                ## the app component could not be created .. fatal
                log.err()
                reactor.stop()
            else:
                session.debug_app = self.debug_app
                return session

        ## create a WAMP-over-WebSocket transport client factory
        transport_factory = WampWebSocketClientFactory(create, url = self.url, serializers = self.serializers,
        debug = self.debug, debug_wamp = self.debug_wamp)

        ## start the client from a Twisted endpoint
        from twisted.internet.endpoints import clientFromString

        if isSecure:
            endpoint_descriptor = "ssl:{0}:{1}".format(host, port)
        else:
            endpoint_descriptor = "tcp:{0}:{1}".format(host, port)

        client = clientFromString(reactor, endpoint_descriptor)
        client.connect(transport_factory)

        ## now enter the Twisted reactor loop
        if start_reactor:
            reactor.run()
            

def build_wamp_client():
    # wamp_app_config = ComponentConfig(realm=config.realm)
    runner = ApplicationRunner("ws://%s:%s/ws" % (config.ws_host, config.ws_port), config.wamp_realm)
    runner.run(WampComponent, start_reactor=False)

def build_wamp_router():
    """ 
    This is a basica WAMP Router implementation 

    Got it from: 
    https://github.com/tavendo/AutobahnPython/blob/master/examples/twisted/wamp/basic/basicrouter.py
    """ 

    from autobahn.twisted.wamp import RouterFactory
    from autobahn.twisted.wamp import RouterSessionFactory
    from autobahn.twisted.websocket import WampWebSocketServerFactory

    router_factory = RouterFactory()
    session_factory = RouterSessionFactory(router_factory)

    transport_factory = WampWebSocketServerFactory(session_factory, debug = False)
    transport_factory.setProtocolOptions(failByDrop = False)

    server = serverFromString(reactor, b"tcp:%s" % config.ws_port)
    server.listen(transport_factory)
