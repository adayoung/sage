# -*- coding: utf-8 -*-
from __future__ import absolute_import
from sage.ansi import filter_ansi
import sage


class Line(str):
    """ An individual line in sage's buffer """

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
        super(Buffer, self).append(Line(line))

    def __repr__(self):
        return str(self.__class__)


def receiver(lines):
    """ Receives lines since the last prompt """

    sage.buffer = Buffer(lines)

    # run trigger matching over lines
    for trigger in sage.triggers.enabled:
        map(trigger.match, sage.buffer)

    # since the prompt has already run, we execute deferred methods here
    for ref, args in sage._deferred:
        method = ref()

        if method is not None:
            method(*args)

    sage._deferred = list()

    output = [line.output for line in sage.buffer if line.output != None]

    return output
