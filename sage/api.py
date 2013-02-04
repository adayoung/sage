# -*- coding: utf-8 -*-
from __future__ import absolute_import
import sage
import weakref
from twisted.internet import reactor


def echo(msg):
    """Echo a message back to the client

    :param msg: message to be echoed back to the client.
    :type msg: string or list
    """
    if sage._echo:
        if type(msg) is list:
            for line in msg:
                sage._echo("%s\n" % line)
        else:
            sage._echo("%s\n" % msg)


def send(msg):
    """ Send a message to the server

    :param msg: message to be sent to the server.
    :type msg: string or list
    """
    if sage._send:
        if type(msg) is list:
            for line in msg:
                sage._send("%s\n" % line)
        else:
            sage._send("%s\n" % msg)


def defer_to_prompt(method, *args):
    """ Defer execution of a method until the prompt is received

    :param method: the method to be deferred.
    :param \*args: optional arguments to be passed to the provided method.
    """

    sage._deferred.append((weakref.ref(method), args))


def delay(seconds, method, *args, **kwargs):
    return reactor.callLater(seconds, method, *args, **kwargs)
