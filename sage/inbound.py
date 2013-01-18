# -*- coding: utf-8 -*-
from __future__ import absolute_import
from sage import ansi
import sage


class Line(object):

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

    def __init__(self, lines):

        i = 0
        for line in lines:
            self.append(Line(line, i))
            i += 1


def receiver(lines):
    sage.buffer = Buffer(lines)

    # run trigger matching over lines
    for trigger in sage.triggers.enabled:
        map(trigger.match, sage.buffer)

    output = [line.output for line in sage.buffer if line.output != None]

    return output
