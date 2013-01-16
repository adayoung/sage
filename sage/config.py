# -*- coding: utf-8 -*-
import json
import os
from . import app_path, debug, error


class Config(dict):
    """Config supports both dict-style and object-style config. It uses JSON as the
    persistent store."""

    def __init__(self, path, defaults=None):
        """Builds class attributes based on defaults dict"""

        self.config_path = app_path + path
        self.config_defaults = defaults

        if self.config_defaults is not None:
            for element in self.config_defaults.keys():
                self.__setattr__(element, self.config_defaults[element])

    def __setattr__(self, name, value):
        dict.__setitem__(self, name, value)
        dict.__setattr__(self, name, value)

    def __setitem__(self, name, value):
        dict.__setitem__(self, name, value)
        dict.__setattr__(self, name, value)

    def load(self):
        """Loads configuration defaults file"""

        if os.path.isfile(self.config_path):
            f = open(self.config_path, 'r')
            data = json.load(f, object_hook=self._decode_dict)
            f.close()

            for element in data.keys():
                self.__setattr__(element, data[element])
        else:
            debug("sage.config.load_defaults: Couldn't load defaults configuration file. Building new one.")
            self.save_defaults()

    def save(self):
        """Saves configuration"""

        data = {}
        for key in self.keys():
            # Don't allow other instances of Config to be written
            if isinstance(self[key], Config) is False \
            and key not in ('config_path', 'config_defaults'):
                data[key] = self[key]

        f = open(self.config_path, 'w+')
        json.dump(data, f, sort_keys=True, indent=4)
        f.close()

    def save_defaults(self):
        """Save default configuration"""

        if self.config_defaults is None:
            return

        data = {}
        for key in self.config_defaults.keys():
            data[key] = self[key]

        try:
            f = open(self.config_path + self.config_name, 'w+')
            json.dump(data, f, sort_keys=True, indent=4)
            f.close()
        except IOError:
            error("Config: Unable to write file %s \
                (called from save_defaults())" % self.config_path)

    def _decode_list(self, lst):
        '''Convert JSON unicode to str'''

        newlist = []
        for i in lst:
            if isinstance(i, unicode):
                i = i.encode('us-ascii')
            elif isinstance(i, list):
                i = self._decode_list(i)
            newlist.append(i)
        return newlist

    def _decode_dict(self, dct):
        '''Convert JSON unicode to str'''

        newdict = {}
        for k, v in dct.iteritems():
            if isinstance(k, unicode):
                k = k.encode('us-ascii')
            if isinstance(v, unicode):
                v = v.encode('us-ascii')
            elif isinstance(v, list):
                v = self._decode_list(v)
            newdict[k] = v
        return newdict