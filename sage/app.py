# -*- coding: utf-8 -*-
import sage
import sys
from twisted.python.rebuild import rebuild
from sage.utils import imports
import gc
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import importlib
from collections import OrderedDict
import inspect


class Apps(dict):
    """ Dict-like container of loaded apps """

    __bases__ = [dict]  # or unittests don't work

    def __init__(self):
        super(Apps, self).__init__(self)

        self.groups = {
            'sage': set()
        }

        self.meta = OrderedDict()

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

    def load(self, name):
        """ Load a module or package into the namespace """

        self._preload(name)

        with imports.cwd_in_path():
            try:
                ns = imports.import_file(name)
            except ImportError:
                sage.log.err("Error: Unable to import app '%s'" % name)

            path = os.path.dirname(inspect.getabsfile(ns))

            meta = importlib.import_module('%s.meta' % name)

            meta.path = path
            meta.name = ns.__name__

            if hasattr(meta, 'INSTALLED_APPS'):
                if os.path.exists(path + '/apps') or os.path.isdir(path + '/apps'):
                    sys.path.append(path + '/apps')

                for subapp in meta.INSTALLED_APPS:
                    self.load(subapp)

            self.meta[meta.name] = meta

            app = importlib.import_module('%s.%s' % (ns.__name__, name))
            self[app.__name__] = app

            if hasattr(app, 'init'):
                app.init()

            sage.log.msg("Loaded app '%s'" % ns.__name__)
            return True

        del(self.groups[name])
        self._names.discard(name)
        sage.log.msg("Failed to load app '%s'" % name)

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

        for obj in list(self.groups[name]):
            obj.destroy()

        try:
            self[name] = rebuild(self[name], False)
            sage.log.msg("Reloaded app '%s'" % name)
        except:
            sage.log.msg("Error reloading '%s'" % name)
            sage.log.err()
            return False

        gc.collect()
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

    def __getattr__(self, item):
        return self.__getitem__(item)
