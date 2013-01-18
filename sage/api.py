# -*- coding: utf-8 -*-
from __future__ import absolute_import
from sage.server import run as run_server
import sage
from sage.utils import timestamp


def echo(msg):
    """ Echo a message back to the client """
    if sage._echo:
        sage._echo("%s\n" % msg)


def log(msg):
    pass
    #sage.console.urwid.app.writelog("%s %s" % (timestamp(), msg))


def write(msg):
    """ Send a message to the server """
    #write_out(msg)
    if sage._write:
        sage._write("%s\n" % msg)


def run():
    """ Start the SAGE server """

    #print("SAGE Framework %s" % sage.__version__)

    run_server()
