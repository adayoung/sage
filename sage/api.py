# -*- coding: utf-8 -*-

import sage
from sage import config
from twisted.internet import reactor, task
import inspect
from .utils import caller_name, str_to_utf8


def echo(msg):
    """Echo a message back to the client

    :param msg: message to be echoed back to the client.
    :type msg: string or list
    """

    msg = str_to_utf8(msg)

    if sage._echo:
        if type(msg) is list:
            for line in msg:
                sage._echo(b"%b\n" % line)
        else:
            sage._echo(b"%b\n" % msg)


def send(msg, separated=False):
    """ Send a message to the server

    :param msg: message to be sent to the server.
    :type msg: string or list
    """

    msg = str_to_utf8(msg)

    if sage._send:
        if type(msg) is list:
            if separated:
                for line in msg:
                    sage._send(b"%s\n" % line)
            else:
                chunks = [msg[i:i + 10] for i in range(0, len(msg), 10)]
                for chunk in chunks:
                    sep = config['serverside_command_separator'].encode("utf-8")
                    m = sep.join(chunk) + b"\n"
                    sage._send(m)
        else:
            sage._send(b"%s\n" % msg)


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
