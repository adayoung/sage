# -*- coding: utf-8 -*-
from __future__ import absolute_import
from sage import ansi
import sage


class Line(object):
    """ An individual line in sage's buffer """

    def __init__(self, line, position):

        self.raw = line
        self.line = ansi.filter(line)
        self.position = position
        self.output = line

    def gag(self):
        self.output = None

    def __eq__(self, other):
        return self.line == other

    def __repr__(self):
        return "'%s'" % self.line


class Buffer(list):
    """ All lines received since the last prompt """

    def __init__(self, lines):

        self.raw_lines = []

        for line in lines:
                self.append(line)

        self.raw_lines = [line.line for line in self]

    def append(self, line):
        super(Buffer, self).append(Line(line, len(self)))


def receiver(lines):
    """ Receives lines since the last prompt """

    sage.buffer = Buffer(lines)

    # create a local for faster access
    match_lines = sage.buffer.raw_lines

    # run trigger matching over lines
    for trigger in sage.triggers.enabled:
        map(trigger.match, match_lines)

    # since the prompt has already run, we execute deferred methods here
    for ref, args in sage._deferred:
        method = ref()

        if method is not None:
            method(*args)

    sage._deferred = list()

    output = [line.output for line in sage.buffer if line.output != None]

    return output
