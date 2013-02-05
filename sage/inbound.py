# -*- coding: utf-8 -*-
from __future__ import absolute_import
from itertools import imap
from sage.ansi import filter_ansi
import sage


class Line(str):
    """ An individual line in sage's buffer

        :attribute raw: the original 'raw' value of the line
        :attribute output: output that will be sent to the client
    """

    def __new__(cls, string):
        line = str.__new__(cls, filter_ansi(string))
        line.raw = string
        line.output = string
        return line

    def gag(self):
        """ Gag the line """
        self.output = None


class Buffer(list):
    """ List of all lines received since the last prompt

        .. warning:: It's very import all values of Buffer are instances of
            :class:`sage.inbound.Line`
    """

    def __init__(self, lines):

        for line in lines:
                self.append(line)

    def append(self, line):
        """ Append a line to the buffer as a :class:`sage.inbound.Line` """
        if isinstance(line, Line) == False:
            super(Buffer, self).append(Line(line))
        else:
            super(Buffer, self).append(line)

    def insert(self, index, line):
        """ Insert line before index as a :class:`sage.inbound.Line` """
        if isinstance(line, Line) == False:
            super(Buffer, self).insert(index, Line(line))
        else:
            super(Buffer, self).insert(index, line)

    def __repr__(self):
        return str(self.__class__)


def receiver(lines):
    """ Receives lines since the last prompt """

    sage.buffer = buf = Buffer(lines)
    trigs = sage.triggers.enabled

    sage.triggers.in_loop = True
    # run trigger matching over lines
    for line in buf:
        for trigger in trigs:
            if trigger.enabled:
                trigger.match(line)

        sage.triggers.flush_set()

    sage.triggers.in_loop = False

    # since the prompt has already run, we execute deferred methods here
    for ref, args in sage._deferred:
        method = ref()

        if method is not None:
            method(*args)

    sage._deferred = list()

    output = [line.output for line in sage.buffer if line.output != None]

    return output
