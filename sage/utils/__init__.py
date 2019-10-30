# -*- coding: utf-8 -*-

from datetime import datetime
import json
import os
import inspect


def error(line):
    """ STDOUT for non-blocking errors"""

    print(("ERROR [%s] %s\n" % (timestamp(), line)))


def timestamp():
    """ Return a timestamp """

    return datetime.now().strftime("%H:%M:%S:%f")[:12]


def json_str_loads(data):
    """ Load JSON using regular strings instead of unicode """

    return json.loads(data, object_hook=str_to_utf8)


def json_str_load(path):
    """ Load JSON file using regular strings instead of unicode """
    return json.load(path, object_hook=str_to_utf8)

def str_to_utf8(data):
    """ JSON object hook utility to convert unicode strings to regular ones """

    if isinstance(data, str):
        data = data.encode('utf-8')
    elif isinstance(data, list):
        data = _str_to_utf8_list(data)
    elif isinstance(data, dict):
        data = _str_to_utf8_dict(data)
    return data

def _str_to_utf8_list(data):
    """ JSON object hook utility to convert unicode strings to regular ones """

    rv = []
    for item in data:
        if isinstance(item, str):
            item = item.encode('utf-8')
        elif isinstance(item, list):
            item = _str_to_utf8_list(item)
        elif isinstance(item, dict):
            item = _str_to_utf8_dict(item)
        rv.append(item)
    return rv


def _str_to_utf8_dict(data):
    """ JSON object hook utility to convert unicode strings to regular ones """

    rv = {}
    for key, value in data.items():
        if isinstance(key, str):
            key = key.encode('utf-8')
        if isinstance(value, str):
            value = value.encode('utf-8')
        elif isinstance(value, list):
            value = _str_to_utf8_list(value)
        elif isinstance(value, dict):
            value = _str_to_utf8_dict(value)
        rv[key] = value
    return rv

def json_str_dumps(data):
    """ Dump utf8 strings to json """
    return json.dumps(utf8_to_str(data)).encode("utf-8")

def utf8_to_str(data):
    if isinstance(data, bytes):
        data = data.decode("utf-8")
    elif isinstance(data, list):
        data = _utf8_to_str_list(data)
    elif isinstance(data, dict):
        data = _utf8_to_str_dict(data)
    return data

def _utf8_to_str_list(data):
    """ Convert list with byte strings to unicode strings """

    rv = []
    for item in data:
        if isinstance(item, bytes):
            item = item.decode("utf-8")
        elif isinstance(item, list):
            item = _utf8_to_str_list(item)
        elif isinstance(item, dict):
            item = _utf8_to_str_dict(item)
        rv.append(item)
    return rv


def _utf8_to_str_dict(data):
    """ Convert dict with byte strings to unicode strings """

    rv = {}
    for key, value in data.items():
        if isinstance(key, bytes):
            key = key.decode("utf-8")
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        elif isinstance(value, list):
            value = _utf8_to_str_list(value)
        elif isinstance(value, dict):
            value = _utf8_to_str_dict(value)
        rv[key] = value
    return rv


def touch(fname, times=None):
    """ Implementation of unix touch """

    with open(fname, 'a'):
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
