# -*- coding: utf-8 -*-
from __future__ import absolute_import
from sage import ansi
import sage


class Line(object):
    """ An individual line in sage's buffer """

    def __init__(self, line, position):

        #: the 'raw' line without ANSI filtering
        self.raw = line

        #: the filtered line
        self.line = ansi.filter(line)

        #: position in the buffer
        self.position = position

        #: output that will be sent to the client
        self.output = line

    def gag(self):
        """ Gag the line """
        self.output = None

    def __eq__(self, other):
        return self.line == other

    def __repr__(self):
        return str(self.line)

    def __str__(self):
        return self.line


class Buffer(list):
    """ List of all lines received since the last prompt """

    def __init__(self, lines):

        for line in lines:
                self.append(line)

    def append(self, line):
        """ Append a line to the buffer as a :class:`sage.inbound.Line` """
        super(Buffer, self).append(Line(line, len(self)))

    def __repr__(self):
        return str(self.__class__)

    def __setitem__(self, key, value):
        super(Buffer, self).__setitem__(key, Line(value))


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
