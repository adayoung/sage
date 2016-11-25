from __future__ import print_function

from autobahn.twisted import ApplicationSession
from autobahn.twisted.wamp import ApplicationRunner
from autobahn.wamp import SerializationError
from twisted.internet.defer import inlineCallbacks

from sage.net import ISageProxyReceiver, client


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

    def _from_client(self, data):
        # Browsers have a tendency to send unicode by default
        data = data.encode('ascii', 'ignore')
        self.client.send(data)

    def _client_ready(self):
        """ This is where we should do all signal connections """
        self.client.connect()

    @inlineCallbacks
    def onJoin(self, details):
        # TODO Gotta do something about all these global references to obj instances
        self.client = client
        if self not in client.receivers:
            client.addReceiver(self)

        yield self.register(self._client_ready, u"com.sage.wsclientready")
        yield self.subscribe(self._from_client, u"com.sage.io")

    def ready(self):
        pass


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