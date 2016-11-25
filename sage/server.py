# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os

from twisted.internet import reactor
from twisted.conch.ssh.keys import Key

from sage import net, wamp, config, apps, path, triggers, player
from sage.signals import pre_start, player_connected
from sage.signals import pre_shutdown as pre_shutdown_signal


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

    if config.ws_proxy:
        wamp.wamp_registry.register_client(config.ws_host, config.ws_port, realm=config.ws_realm)
    # In case any apps want to register custom clients we will wait for reactor start
    reactor.addSystemEventTrigger('after', 'startup', wamp.wamp_registry.run_clients)

    # Add shutdown events
    reactor.addSystemEventTrigger('before', 'shutdown', pre_shutdown)
    reactor.addSystemEventTrigger('after', 'shutdown', post_shutdown)

    reactor.run()


def pre_shutdown():
    """ Before the reactor stops """
    pre_shutdown_signal.send()

    to_unload = [app for app in apps]

    for app in to_unload:
        apps.unload(app)


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
    # As of Twisted~v16.0.0 we now have to give host SSH keys to any subclass of SSHFactory
    key_path = os.path.expanduser(config.ssh_key_path)
    factory.publicKeys = {
        'ssh-rsa': Key.fromFile(key_path)
    }

    factory.privateKeys = {
        'ssh-rsa': Key.fromFile(key_path)
    }

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
