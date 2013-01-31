# -*- coding: utf-8 -*-
import sys
from twisted.python.rebuild import rebuild
from sage.utils import imports
import gc


class Apps(dict):
    """ Dict-like container of loaded apps """

    def __init__(self):
        super(Apps, self).__init__(self)

        self.matchables = {
            'sage': set()
        }

        # names available before load is completed
        self._names = set(['sage,'])

    def add_matchable(self, app, matchable):
        self.matchables[app].add(matchable)

    def load(self, names):
        """ Load a module or package into the namespace """

        if type(names) is list:
            for name in names:
                self._load(name)
        else:
            self._load(names)

    def _load(self, name):
        self.preload(name)

        with imports.cwd_in_path():
            app = imports.import_file(name)
            self[app.__name__] = app

            return True

        del(self.matchables[name])
        self._names.discard(name)
        return False

    def preload(self, name):
        if '.py' in name:
            name = name[:-3]

        self._names.add(name)

        if name not in self.matchables:
            self.matchables[name] = set()

    def reload(self, name):
        """ Try to fully rebuild an app """

        if name not in self:
            return False

        self[name] = rebuild(self[name])
        return True

    def unload(self, name):
        """ Attempt to remove a module from the namespace """

        if name not in self:
            return False

        for matchable in self.matchables[name]:
            matchable.destroy()

        del(self[name])
        del(sys.modules[name])
        gc.collect()
        return True

    def valid(self, name):
        return name in self._names

    def __repr__(self):
        return str(self.__class__)
