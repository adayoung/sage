from twisted.internet import reactor
from sage import config
from sage.net import WampComponent
from twisted.internet.defer import inlineCallbacks
from twisted.internet.endpoints import TCP4ClientEndpoint
from sage.net import client, WAMPProxyFactory     # This fucky stuff will be erased with the net refactor
from sage.contrib import Vital, Balance
from sage.signals.gmcp import vitals
import json

class CustomComponent(WampComponent):
    """
    A customized WAMP component that overrides Sage's default 
    onJoin method. This component exposes more Mint-based services
    and is a lot more flexible than the default one.
    """

    @inlineCallbacks
    def onJoin(self, details):

        if client.wamp_client is None:
            client.wamp_client = self

        def onIOEvent(msg):
            # We must decode to ascii because browsers may send unicode
            tmp_msg = msg.encode('ascii', 'ignore')
            client.send(tmp_msg)


        def vitalsReceived(*args, **kwargs):
            kwargs.pop('signal')
            values = {}

            for key,val in kwargs.iteritems():
                if isinstance(val, Vital):
                    values[key] = val.value
                elif isinstance(val, Balance):
                    values[key] = val.balance
                else:
                    values[key] = val

            self.publish(u"com.sage.vitals", values)


        def ready():
            if not self.deferred:
                point = TCP4ClientEndpoint(reactor, "localhost", 5493)
                self.deferred = point.connect(WAMPProxyFactory())
                self.vitals = vitals.connect(vitalsReceived)


        yield self.register(ready, u"com.sage.wsclientready")
        yield self.subscribe(onIOEvent, u"com.sage.io")

config.ws_component = CustomComponent
