from autobahn.websocket import listenWS
from autobahn.wamp import WampServerFactory, WampServerProtocol
from sage.signals.telnet import pre_outbound as outbound_signal


factory = WampServerFactory("ws://localhost:9000", debugWamp=True)


class SAGEProtoServerProtocol(WampServerProtocol):

    def onSessionOpen(self):
        self.registerForPubSub("http://sage/event#", True)


def instream(**kwargs):
    lines = [line.output for line in kwargs['lines'] if line.output is not None]
    factory.dispatch('http://sage/event#instream', {'lines': lines, 'prompt': kwargs['prompt']})


def init():
    outbound_signal.connect(instream)
    factory.protocol = SAGEProtoServerProtocol
    factory.setProtocolOptions(allowHixie76=True)
    listenWS(factory)