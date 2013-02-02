# -*- coding: utf-8 -*-
import sys
from twisted.python.rebuild import rebuild
from sage.utils import imports
import gc
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class Apps(dict):
    """ Dict-like container of loaded apps """

    def __init__(self):
        super(Apps, self).__init__(self)

        self.groups = {
            'sage': set()
        }

        # names available before load is completed
        self._names = set(['sage'])

        self.observer = Observer()
        self.event_handler = FileSystemEventHandler()
        self.event_handler.on_any_event = self.file_event

    def file_event(self, event):
        if event.event_type != 'modified':
            return

        if '.py' not in event.src_path:
            return

        name = event.src_path.split('/')[-1][:-3]

        if name in self:
            self.reload(name)

    def add_group(self, app, matchable):
        self.groups[app].add(matchable)

    def remove_group(self, app, matchable):
        self.groups[app].discard(matchable)

    def load(self, names):
        """ Load a module or package into the namespace """

        if type(names) is list:
            for name in names:
                self._load(name)
        else:
            self._load(names)

    def _load(self, name):
        self._preload(name)

        with imports.cwd_in_path():
            app = imports.import_file(name)
            self[app.__name__] = app

            return True

        del(self.groups[name])
        self._names.discard(name)
        return False

    def _preload(self, name):
        if '/' in name:
            name = name.split('/')[-1]

        if '.py' in name:
            name = name[:-3]

        self._names.add(name)

        if name not in self.groups:
            self.groups[name] = set()

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

        while len(self.groups[name]) > 0:
            self.groups[name].pop().destroy()

        del(self[name])
        del(sys.modules[name])
        gc.collect()
        return True

    def valid(self, name):
        """ Is a string the name of a valid app """
        return name in self._names

    def __repr__(self):
        return str(self.__class__)
