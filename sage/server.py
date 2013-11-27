# -*- coding: utf-8 -*-
from __future__ import absolute_import
from twisted.internet import reactor
from sage import net, config, apps, path, triggers, player
from sage.signals import pre_start, player_connected
from sage.signals import pre_shutdown as pre_shutdown_signal, post_shutdown as post_shutdown_signal


def run():
    """ Start Sage Server """

    pre_start.send()

    if config.auto_reload:
        apps.observer.schedule(apps.event_handler, path, recursive=True)
        apps.observer.start()

    # setup the backdoor
    if config.backdoor:
        import sage
        import sage.gmcp as gmcp

        imports = {
            'sage': sage,
            'player': player,
            'gmcp': gmcp,
            'apps': apps
        }

        reactor.listenTCP(config.backdoor_port, get_manhole_factory(imports),
            interface=config.backdoor_host)
        print("Backdoor port: %s" % config.backdoor_port)

    if config.telnet_proxy:
        factory = net.build_telnet_factory()
        import sage
        sage.factory = factory
        print("Telnet proxy port: %s" % config.telnet_port)

    if config.ws_server:
        net.build_ws_factory()
        print("Sage WS protocol: ws://%s:%s" % (config.ws_host, config.ws_port))

    # Add shutdown events
    reactor.addSystemEventTrigger('before', 'shutdown', pre_shutdown)
    reactor.addSystemEventTrigger('after', 'shutdown', post_shutdown)

    reactor.run()


def pre_shutdown():
    """ Before the reactor stops """
    pre_shutdown_signal.send()


def post_shutdown():
    """ After the reactor has stopped """
    post_shutdown_signal.send()


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


def setup_system():
    """ Creates system triggers """

    sage_group = triggers.get_group('sage')

    sage_group.create(
        'connect',
        'exact',
        'Password correct. Welcome to Achaea.',
        [connect])


def connect(trigger):
    """ Successful login """
    player.connected = True
    player_connected.send()
    trigger.destroy()
