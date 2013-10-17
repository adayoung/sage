from autobahn.websocket import listenWS
from autobahn.wamp import WampServerFactory, WampServerProtocol
from sage.signals.net import pre_outbound as outbound_signal, connected as connected_signal
import sage


factory = WampServerFactory("ws://localhost:9000", debugWamp=True)


class SAGEProtoServerProtocol(WampServerProtocol):

    def onSessionOpen(self):
        self.registerForPubSub("http://sage/event#", True)
        self.registerMethodForRpc('http://sage/input', self, SAGEProtoServerProtocol.input)
        self.registerMethodForRpc('http://sage/is_connected', self, SAGEProtoServerProtocol.is_connected)

    def input(self, msg):
        sage.send(msg.encode('us-ascii'))

    def is_connected(self):
        self.dispatch('http://sage/event#connected', sage.connected)


def instream(**kwargs):
    lines = [line.output for line in kwargs['lines'] if line.output is not None]
    factory.dispatch('http://sage/event#instream', {'lines': lines, 'prompt': kwargs['prompt']})


def connected(**kwargs):
    factory.dispatch('http://sage/event#connected', True)


def init():
    outbound_signal.connect(instream)
    connected_signal.connect(connected)
    factory.protocol = SAGEProtoServerProtocol
    factory.setProtocolOptions(allowHixie76=True)
    listenWS(factory)
