# -*- coding: utf-8 -*-
import sys
from twisted.python.rebuild import rebuild
from sage.utils import imports
import gc


class Apps(dict):
    """ Dict-like container of loaded apps """

    def load(self, names):
        """ Load a module or package into the namespace """

        if type(names) is list:
            for name in names:
                self._load(name)
        else:
            self._load(names)

    def _load(self, name):
        with imports.cwd_in_path():
            app = imports.import_file(name)
            self[app.__name__] = app

            return True

        return False

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

        if hasattr(self[name], '__matchables__'):
            for matchable in self[name].__matchables__:
                matchable.destroy()

        del(self[name])
        del(sys.modules[name])
        gc.collect()
        return True

    def __repr__(self):
        return str(self.__class__)
