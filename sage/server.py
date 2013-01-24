# -*- coding: utf-8 -*-
from __future__ import absolute_import
from twisted.internet import reactor
from sage import telnet, config


def run():
    """ Start Twisted """

    # Setup reactor to listen
    reactor.listenTCP(config.proxy_port, telnet.build_factory())
    print("Proxy: %s" % config.proxy_port)

    # setup the backdoor
    if config.backdoor:
        import sage
        import sage.player as player
        import sage.gmcp as gmcp

        imports = {
            'sage': sage,
            'player': player,
            'gmcp': gmcp
        }

        reactor.listenTCP(config.backdoor_port, get_manhole_factory(imports))
        print("Backdoor: %s" % config.backdoor_port)

    # Add shutdown events
    reactor.addSystemEventTrigger('before', 'shutdown', pre_shutdown)
    reactor.addSystemEventTrigger('after', 'shutdown', post_shutdown)

    reactor.run()


def pre_shutdown():
    """ Before the reactor stops """
    pass


def post_shutdown():
    """ After the reactor has stopped """
    pass


def get_manhole_factory(namespace):
    """ Build a twisted manhole factory """

    from twisted.conch import manhole, manhole_ssh
    from twisted.cred import portal, checkers

    # I really hate Twisted's default colors
    colors = {
        'identifier': '\x1b[1;36m',
        'keyword': '\x1b[33m',
        'parameter': '\x1b[33m',
        'variable': '\x1b[36m',
        'string': '\x1b[35m',
        'number': '\x1b[1;32m',
        'op': '\x1b[33m'
    }

    manhole.VT102Writer.typeToColor.update(colors)

    realm = manhole_ssh.TerminalRealm()

    def get_manhole(_):
        return manhole.ColoredManhole(namespace)

    realm.chainedProtocolFactory.protocolFactory = get_manhole
    p = portal.Portal(realm)
    checker = checkers.InMemoryUsernamePasswordDatabaseDontUse()
    checker.addUser(config.backdoor_user, config.backdoor_password)
    p.registerChecker(checker)

    factory = manhole_ssh.ConchFactory(p)
    return factory
