# -*- coding: utf-8 -*-
from __future__ import absolute_import
import sage
import weakref


def echo(msg):
    """ Echo a message back to the client """
    if sage._echo:
        if type(msg) is list:
            for line in msg:
                sage._echo("%s\n" % line)
        else:
            sage._echo("%s\n" % msg)


def send(msg):
    """ Send a message to the server """
    if sage._send:
        if type(msg) is list:
            for line in msg:
                sage._send("%s\n" % line)
        else:
            sage._send("%s\n" % msg)


def defer_to_prompt(method, *args):
    """ Defer execution of a method until the prompt is received """

    sage._deferred.append((weakref.ref(method), args))
