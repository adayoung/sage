# -*- coding: utf-8 -*-
from __future__ import absolute_import
import sage
from twisted.internet import reactor, task
import inspect
from .utils import caller_name


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

    sage._deferred.append((method, args))


def delay(seconds, method, *args, **kwargs):
    """ Delay a method call in the reactor

    :param seconds: seconds to delay by.
    :type seconds: int
    :param method: method to be called.
    :param \*args: optional arguments to be passed to the provided method.
    :param \*\*kwargs: optional keyword arguments.
    """

    return reactor.callLater(seconds, method, *args, **kwargs)


def loopdelay(seconds, func, immediate=True, *args, **kwargs):
    """ Delay a method call in the reactor...

    ...and do it again, and again..

    :param seconds: seconds between each function call
    :type seconds: float
    :param method: function to call
    :type method: callable
    :param immediate:
    :type immediate: bool
    :param args:
    :param kwargs:
    """
    interval = task.LoopingCall(func, *args, **kwargs)
    interval.start(seconds, now=immediate)
    return interval


def log(msg, inspection=True):
    """ Write to the system log

    :param msg: Message to log.
    :type msg: string
    :param inspection: Show caller module and method.
    :type inspection: boolean
    """

    if inspection:
        sage._log.msg(msg, system=caller_name())
    else:
        sage._log.msg(msg)
