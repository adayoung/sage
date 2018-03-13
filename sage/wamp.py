from __future__ import print_function

from autobahn.twisted import ApplicationSession
from autobahn.twisted.wamp import ApplicationRunner
from autobahn.wamp import SerializationError
from twisted.internet.defer import inlineCallbacks

import sage
from sage.net import ISageProxyReceiver, client
from sage.contrib import Vital, Balance
from sage.signals import gmcp


class WampComponent(ApplicationSession, ISageProxyReceiver):
    """
    Barebones WAMP component implementation for Sage. This is
    intended to be overridden elsewhere. In order to override it with
    Sage the ideal thing to do is set sage.config.ws_component to a subclass
    of this class.
    """

    def __init__(self,  config=None, channels=None):
        self.channels = {
            'io': u'com.sage.io',
            'vitals': u'com.sage.vitals',
            'comms': u'com.sage.communications',
            'rift': u'com.sage.rift',
            'room': u'com.sage.room',
            'ping': u'com.sage.ping',
            'inv': u'com.sage.inv',
            'players': u'com.sage.players',
            'skills': u'com.sage.skills'
        }

        # References to channels <-> signals mapping
        self.signals = {
            'vitals': None,
            'comms': None,
            'rift': None,
            'ping': None,
            'inv': None,
            'players': None,
            'skills': None
        }

        # Reference to the telnet_client from sage.net
        self.client = None

        ApplicationSession.__init__(self, config)
        ISageProxyReceiver.__init__(self)  # For self.connected..

    def write(self, data):
        if data:
            # Ugh, unicode in py27...
            try:
                data = unicode(data, errors='replace')
            except:
                data = data.encode('ascii', 'ignore')

            try:
                self.publish(self.channels['io'], data)
            except SerializationError as se:
                print("Error when publishing: %s" % se)

    def input(self, lines, prompt):
        """ Lines + Prompt emitted by Sage, should be sent to local client

        This is done by publishing to the 'io' channel.
        """
        outgoing = '{}\r\n{}'.format('\r\n'.join(lines), prompt)
        self.publish(self.channels['io'], outgoing)

    def publish_to_client(self, channel, data):
        try:
            self.publish(channel, unicode(data))
        except SerializationError as se:
            print("SerializationError: %s" % se)
        except Exception as e:
            print("Unexpected exception: %s" % e)

    def _from_client(self, data):
        # Browsers have a tendency to send unicode by default
        data = data.encode('ascii', 'ignore')
        self.client.send(data)

    def _connect_signals(self):
        """ Call when the signals need to be connected for GMCP """

        self.signals['vitals'] = gmcp.vitals.connect(self._recv_vitals)
        self.signals['comms'] = gmcp.comms.connect(self._recv_comms)
        self.signals['ping'] = gmcp.ping.connect(self._recv_ping)
        self.signals['room'] = gmcp.room.connect(self._recv_room)
        self.signals['rift'] = gmcp.rift.connect(self._recv_rift)
        self.signals['skills'] = gmcp.skills.connect(self._recv_skills)
        self.signals['players'] = gmcp.room_players.connect(self._recv_players)

    def _client_ready(self):
        """ Called by the the RPC endpoint come.sage.wsclientready,

        i.e.: NOT the telnet client from sage.net
        """
        self._connect_signals()
        self.client.connect()

    def _recv_vitals(self, *args, **kwargs):
        kwargs.pop('signal')
        values = {}

        for key, val in kwargs.iteritems():
            if isinstance(val, Vital):
                values[key] = val.value
            elif isinstance(val, Balance):
                values[key] = val.balance
            else:
                values[key] = val

        self.publish(self.channels['vitals'], values)

    def _recv_comms(self, signal, talker, channel, text):
        d = {
            'talker': talker,
            'channel': channel,
            'text': text
        }
        self.publish(self.channels['comms'], d)

    def _recv_ping(self, signal, latency):
        self.publish(self.channels['ping'], latency)

    def _recv_room(self, signal, room):
        self.publish(self.channels['room'], room.encode())

    def _recv_rift(self, signal, rift):
        self.publish(self.channels['rift'], rift)

    def _recv_skills(self, signal, skills):
        self.publish(self.channels['skills'], skills)

    def _recv_inv(self, signal, inv):
        self.publish(self.channels['inv'], inv.encode())

    def _recv_players(self, signal, players=None):
        self.publish(self.channels['players'], list(players))

    @inlineCallbacks
    def onJoin(self, details):
        # TODO Gotta do something about all these global references to obj instances
        self.client = client

        # TODO dedup, fix this nastiness
        # This is an ugly wart of a sage bootstrapping mechanism.
        # Because sage's telnet client's receivers are not setup immediately we can't bind
        # directly to their write() methods. This code also exists in
        # sage/net.py::TelnetServer::write
        sage._echo = self.write
        if self not in client.receivers:
            client.addReceiver(self)

        yield self.register(self._client_ready, u"com.sage.wsclientready")
        yield self.subscribe(self._from_client, self.channels['io'])

    def ready(self):
        self._connect_signals()


class WampClientContainer(object):

    def __init__(self, host, port, realm, component=WampComponent):
        self.host = unicode(host)
        self.port = unicode(port)
        self.realm = unicode(realm)
        self.connection_str = unicode("ws://{0}:{1}/ws".format(self.host, self.port))
        self.component = component
        self.runner = None

    def run(self, start_reactor=False):
        self.runner = ApplicationRunner(url=self.connection_str, realm=self.realm)
        self.runner.run(self.component, start_reactor=start_reactor)


class WampClientRegistry(object):

    def __init__(self):
        self.registered_clients = []
        self.active_clients = []

    def register_client(self, host, port, realm='realm1', component=WampComponent):
        """ Register a client to be created at startup

        :param host:  Hostname, DNS name, IP address
        :param port:  TCP port
        :param component: Default: WampComponent; could be a subclass of WampComponent
        :param realm: Default: realm1; name of realm to join on the router session
        :return:
        """

        self.registered_clients.append(WampClientContainer(host, port, realm, component))

    def run_clients(self):
        for wampclient in self.registered_clients:
            wampclient.run()
            print("WebSocket proxy running on %s, port %s" % (wampclient.host, wampclient.port))

wamp_registry = WampClientRegistry()
