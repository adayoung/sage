# -*- coding: utf-8 -*-
from __future__ import absolute_import
from twisted.internet import reactor
from sage.console.term import interact
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

    # Add shutdown event
    reactor.addSystemEventTrigger("before", "shutdown", shutdown)

    import sage
    import sage.player as player
    import sage.gmcp as gmcp
    imports = {
        'sage': sage,
        'player': player,
        'gmcp': gmcp
    }

    reactor.callWhenRunning(interact, stopReactor=True, local=imports)

    # Lets go!
    reactor.run()


def shutdown():
    """Attempt to gracefully shutdown SAGE"""

    pass
