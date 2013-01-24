# -*- coding: utf-8 -*-
from __future__ import absolute_import
from twisted.internet import reactor
import sage.telnet as telnet


def run(host=None, port=None, local_port=None):
    """ Start Twisted """

    if host:
        telnet.options['host'] = host

    if port:
        telnet.options['port'] = port

    if local_port:
        telnet.options['local_port'] = local_port

    # Setup reactor to listen
    reactor.listenTCP(telnet.options['local_port'], telnet.build_factory())

    # Add shutdown events
    reactor.addSystemEventTrigger('before', 'shutdown', pre_shutdown)
    reactor.addSystemEventTrigger('after', 'shutdown', post_shutdown)

    '''
    import sage
    import sage.player as player
    import sage.gmcp as gmcp

    imports = {
        'sage': sage,
        'player': player,
        'gmcp': gmcp
    }
    '''

    reactor.run()


def pre_shutdown():
    """ Before the reactor stops """
    pass


def post_shutdown():
    """ After the reactor has stopped """
    pass
