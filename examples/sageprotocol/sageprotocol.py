from autobahn.websocket import listenWS
from autobahn.wamp import WampServerFactory, WampServerProtocol

class MyServerProtocol(WampServerProtocol):

    def onSessionOpen(self):

        ## register a single, fixed URI as PubSub topic
        self.registerForPubSub("http://example.com/simple")

        ## register a URI and all URIs having the string as prefix as PubSub topic
        self.registerForPubSub("http://example.com/event#", True)

        ## register any URI (string) as topic
        #self.registerForPubSub("", True)


def init():
    print "SHIT RAN WOOHOO"
