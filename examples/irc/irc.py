import sage
from sage import player, signals, aliases, echo
from . import client
from twisted.internet import reactor

channel = '#trifecta'
server = 'irc.freenode.net'
port = 6667

factory = client.mkfactory()
ic = factory.client


def init():
    from sage import config

    print "SAGE CONFIG"
    print config
    
    if sage.connected:
        connect()
    else:
        signals.player_connected.connect(connect)


def unload():
    ic.disconnect()


def connect(**kwargs):
    ic.channel = channel
    ic.nickname = player.name
    reactor.connectTCP(server, port, factory)


def got_names(nicklist):
        nicklist.sort()
        echo('%s members:' % channel)
        echo('-' * 10)
        for nick in nicklist:
            echo(nick)


alias = aliases.create_group('irc', app='irc')


@alias.startswith('it ')
def it(alias):
    ic.say(channel, alias.suffix)


@alias.startswith('itme ')
def itme(alias):
    ic.describe(channel, alias.suffix)


@alias.regex('^pm (\w+) (.*)')
def privmsg(alias):
    target = alias.groups[0]
    msg = alias.groups[1]
    ic.msg(target, msg)


@alias.exact('iwho')
def iwho(alias):
    ic.names(channel).addCallback(got_names)
