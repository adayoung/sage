# -*- coding: utf-8 -*-
from __future__ import absolute_import
from twisted.internet import reactor
#from sage.console import interact
from sage.console import urwid
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

    urwid.app.run()
    #reactor.callWhenRunning(urwid.app.run)
    #reactor.callWhenRunning(interact, stopReactor=True, local=imports)

    # Lets go!
    #reactor.run()


def shutdown():
    """Attempt to gracefully shutdown SAGE"""

    pass
