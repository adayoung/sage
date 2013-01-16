# -*- coding: utf-8 -*-
from datetime import datetime
import json

debug_mode = True


def debug(line):
    """ Debug output """

    if debug_mode:
        print("[%s]: %s\n" % (timestamp(), line))


def error(line):
    """ STDOUT for non-blocking errors"""

    print("ERROR [%s] %s\n" % (timestamp(), line))


def timestamp():
    """ Return a timestamp """

    return datetime.now().strftime("%H:%M:%S:%f")[:12]


def json_str_loads(data):
    """ Load JSON using regular strings instead of unicode """

    return json.loads(data, object_hook=_decode_dict)


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
