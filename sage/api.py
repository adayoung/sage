# -*- coding: utf-8 -*-
from __future__ import absolute_import
from sage.server import run as run_server
import sage
import weakref


def echo(msg):
    """ Echo a message back to the client """
    if sage._echo:
        sage._echo("%s\n" % msg)


def send(msg):
    """ Send a message to the server """
    if sage._send:
        sage._send("%s\n" % msg)


def run():
    """ Start the sage server """

    run_server()


def defer_to_prompt(method, *args):
    """ Defer execution of a method until the prompt is received """

    sage._deferred.append((weakref.ref(method), args))
