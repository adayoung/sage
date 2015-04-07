# -*- coding: utf-8 -*-
from __future__ import division
from datetime import datetime
import json
import os
import inspect


def error(line):
    """ STDOUT for non-blocking errors"""

    print("ERROR [%s] %s\n" % (timestamp(), line))


def timestamp():
    """ Return a timestamp """

    return datetime.now().strftime("%H:%M:%S:%f")[:12]


def json_str_loads(data):
    """ Load JSON using regular strings instead of unicode """

    return json.loads(data, object_hook=_decode_dict)


def json_str_load(path):
    """ Load JSON file using regular strings instead of unicode """
    return json.load(path, object_hook=_decode_dict)


def _decode_list(data):
    """ JSON object hook utility to convert unicode strings to regular ones """

    rv = []
    for item in data:
        if isinstance(item, unicode):
            item = item.encode('utf-8')
        elif isinstance(item, list):
            item = _decode_list(item)
        elif isinstance(item, dict):
            item = _decode_dict(item)
        rv.append(item)
    return rv


def _decode_dict(data):
    """ JSON object hook utility to convert unicode strings to regular ones """

    rv = {}
    for key, value in data.iteritems():
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        elif isinstance(value, list):
            value = _decode_list(value)
        elif isinstance(value, dict):
            value = _decode_dict(value)
        rv[key] = value
    return rv


def touch(fname, times=None):
    """ Implementation of unix touch """

    with file(fname, 'a'):
        os.utime(fname, times)


class MutableInt(object):

    def __init__(self, value=None):
        self.value = value

    def update(self, value):
        self.value = value

    def __repr__(self):
        return str(self.value)

    def __eq__(self, other):
        return self.value == other

    def __ne__(self, other):
        return self.value != other

    def __lt__(self, other):
        return self.value < other

    def __gt__(self, other):
        return self.value > other

    def __le__(self, other):
        return self.value >= other

    def __ge__(self, other):
        return self.value >= other


def caller_name(skip=2):
    """Get a name of a caller in the format module.class.method

       `skip` specifies how many levels of stack to skip while getting caller
       name. skip=1 means "who calls me", skip=2 "who calls my caller" etc.

       An empty string is returned if skipped levels exceed stack height
    """

    stack = inspect.stack()
    start = 0 + skip
    if len(stack) < start + 1:
        return ''
    parentframe = stack[start][0]

    name = []
    module = inspect.getmodule(parentframe)
    # `modname` can be None when frame is executed directly in console
    # TODO(techtonik): consider using __main__
    if module:
        name.append(module.__name__)
    # detect classname
    if 'self' in parentframe.f_locals:
        # I don't know any way to detect call from the object method
        # XXX: there seems to be no way to detect static method call - it will
        #      be just a function call
        name.append(parentframe.f_locals['self'].__class__.__name__)
    codename = parentframe.f_code.co_name
    if codename != '<module>':  # top level usually
        name.append(codename)  # function or a method
    del parentframe
    return ".".join(name)
