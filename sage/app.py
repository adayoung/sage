# -*- coding: utf-8 -*-
import sys
from twisted.python.rebuild import rebuild
from sage.utils import imports


class Apps(dict):
    """ Container of loaded apps """

    def load(self, names):
        """ Load a module or package into the namespace """

        if type(names) is list:
            for name in names:
                self._load(name)
        else:
            self._load(name)

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
        """ A really sad attempt to remove a module from the namespace """

        if name not in self:
            return False

        del(self[name])
        del(sys.modules[name])
        return True
