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

            for key,val in kwargs.items():
                if isinstance(val, Vital):
                    values[key] = val.value
                elif isinstance(val, Balance):
                    values[key] = val.balance
                else:
                    values[key] = val

            self.publish("com.sage.vitals", values)

        def pingReceived(signal, latency):
            self.publish("com.sage.ping", latency)

        def roomUpdated(signal, room):
            self.publish("com.sage.room", room.encode())

        def riftUpdated(signal, rift):
            self.publish("com.sage.rift", rift)

        def skillsUpdated(signal, skills):
            self.publish("com.sage.skills", skills)

        def commsReceived(signal, talker, channel, text):
            self.publish("com.sage.communications", {
                "talker": talker,
                "channel": channel,
                "text": text
            })

        def invItemsUpdated(signal, items):
            self.publish("com.sage.inv", items.encode())

        def ready():
            if not self.deferred:
                point = TCP4ClientEndpoint(reactor, "localhost", 5493)
                self.deferred = point.connect(WAMPProxyFactory())

                # Connect signals to publish events, signals 
                # on right are imported from sage.signals.gmcp
                self.vitals = vitals.connect(vitalsReceived)
                self.ping = ping.connect(pingReceived)
                self.room = room.connect(roomUpdated)
                self.rift = rift.connect(riftUpdated)
                self.skills = skills.connect(skillsUpdated)
                self.comms = comms.connect(commsReceived)
                self.inv = inv_items.connect(invItemsUpdated)

        yield self.register(ready, "com.sage.wsclientready")
        yield self.subscribe(onIOEvent, "com.sage.io")

config.ws_component = CustomComponent
