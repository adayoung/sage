from autobahn.websocket import listenWS
from autobahn.wamp import WampServerFactory, WampServerProtocol
from twisted.web.static import File
from twisted.web.server import Site
from twisted.internet import reactor
import sage


class SAGEProtoServerProtocol(WampServerProtocol):

    def onSessionOpen(self):

        ## register a single, fixed URI as PubSub topic
        self.registerForPubSub("http://example.com/simple")

        ## register a URI and all URIs having the string as prefix as PubSub topic
        self.registerForPubSub("http://example.com/event#", True)

        ## register any URI (string) as topic
        #self.registerForPubSub("", True)


def init():
    path = sage.apps.get_path('sageprotocol')
    factory = WampServerFactory("ws://localhost:9000", debugWamp=True)
    factory.protocol = SAGEProtoServerProtocol
    factory.setProtocolOptions(allowHixie76=True)
    listenWS(factory)

    webdir = File(path + '/web')
    web = Site(webdir)
    reactor.listenTCP(8080, web)
