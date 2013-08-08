from sage import echo
from twisted.words.protocols.irc import IRCClient
from twisted.internet import protocol, defer


class SAGEIRCClient(IRCClient):

    versionName = 'SAGE2 IRC Module'

    def __init__(self, *args, **kwargs):
        self._namescallback = {}

    def connectionMade(self):
        IRCClient.connectionMade(self)
        echo('IRC: Connected')

    def connectionLost(self, reason):
        IRCClient.connectionLost(self, reason)

    def say(self, channel, message, length=None):
        ''' Say to channel and echo back '''

        IRCClient.msg(self, channel, message, length)
        echo('[%s] <%s> %s' % (channel, self.nickname, message))

    def msg(self, user, message, length=None):
        ''' Send message to user '''

        IRCClient.msg(self, user, message, length)
        echo('[IRC] You->%s: %s' % (user, message))

    #: callbacks for events

    def signedOn(self):
        """ Called when client has succesfully signed on to server. """

        if self.channel:
            self.join(self.channel)

    def joined(self, channel):
        """ This will get called when the client joins the channel. """

        echo('IRC: Joined %s' % channel)

    def privmsg(self, user, channel, msg):
        """ This will get called when the client receives a message. """

        user = user.split('!', 1)[0]

        # Check to see if they're sending a private message
        if channel == self.nickname:
            echo('[IRC] %s->You: %s' % (user, msg))
            return

        echo('[%s] <%s> %s' % (channel, user, msg))

    def action(self, user, channel, msg):
        """ This will get called when the client sees someone do an action. """

        user = user.split('!', 1)[0]
        echo("[%s] * %s %s" % (channel, user, msg))

    def userJoined(self, user, channel):
        ''' User joining the channel '''

        user = user.split('!', 1)[0]
        echo('[%s] %s has joined %s' % (channel, user, channel))

    def userLeft(self, user, channel):
        ''' User leaving channel '''

        user = user.split('!', 1)[0]
        echo('[%s] %s has left %s' % (channel, user, channel))

    def userQuit(self, user, quitMessage):
        ''' User quitting the network '''

        user = user.split('!', 1)[0]
        echo('[IRC] %s has disconnected. Reason: %s' % (user, quitMessage))

    def userKicked(self, kickee, channel, kicker, message):
        """ A user has been kicked from the channel """

        echo('[%s] %s has been kicked by %s in %s: %s' % (channel, kickee, kicker, channel, message))

    def kickedFrom(self, channel, kicker, message):
        """ You have been kicked from the channel """

        echo('[%s] You have been kicked from %s by %s: %s' % (channel, channel, kicker, message))

    #: irc callbacks

    def irc_NICK(self, prefix, params):
        """ Called when an IRC user changes their nickname """

        old_nick = prefix.split('!')[0]
        new_nick = params[0]
        echo("[IRC] %s is now known as %s" % (old_nick, new_nick))

    def names(self, channel):
        """ Who for IRC """

        channel = channel.lower()
        d = defer.Deferred()
        if channel not in self._namescallback:
            self._namescallback[channel] = ([], [])

        self._namescallback[channel][0].append(d)
        self.sendLine("NAMES %s" % channel)
        return d

    def irc_RPL_NAMREPLY(self, prefix, params):
        channel = params[2].lower()
        nicklist = params[3].split(' ')

        if channel not in self._namescallback:
            return

        n = self._namescallback[channel][1]
        n += nicklist

    def irc_RPL_ENDOFNAMES(self, prefix, params):
        channel = params[1].lower()
        if channel not in self._namescallback:
            return

        callbacks, namelist = self._namescallback[channel]

        for cb in callbacks:
            cb.callback(namelist)

        del self._namescallback[channel]


class IRCClientFactory(protocol.ClientFactory):
    """ Twisted IRC Protocol """

    def __init__(self, client):
        self.disconnecting = False
        self.client = client

    def buildProtocol(self, addr):
        #self.client = client
        return self.client

    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server"""

        if self.disconnecting is False:
            connector.connect()

    def clientConnectionFailed(self, connector, reason):
        echo("IRC: connection failed: %s" % reason)


def mkfactory():
    client = SAGEIRCClient()
    factory = IRCClientFactory(client)

    return factory
