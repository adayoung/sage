# -*- coding: utf-8 -*-
import sage
import sys
import gc
import os
import time
import importlib
from collections import OrderedDict
import inspect

from twisted.python.rebuild import rebuild

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from sage.utils import imports

class AppNotLoaded(Exception):
    pass


class Apps(dict):
    """ Dict-like container of loaded apps """

    __bases__ = [dict]  # or unittests don't work

    def __init__(self):
        super(Apps, self).__init__(self)

        self.groups = {
            'sage': set()
        }

        self.meta = OrderedDict()
        self.paths = dict()

        self._last_reload = dict()
        self._reload_backoff = 5  # secs to wait before reloading again

        # names available before load is completed
        self._names = set(['sage'])

        self.observer = Observer()
        self.event_handler = FileSystemEventHandler()
        self.event_handler.on_any_event = self.file_event

    def file_event(self, event):
        if event.is_directory:
            return

        if '.py' not in event.src_path:
            return

        for app, path in self.paths.items():
            if path in event.src_path:
                self.reload(app, event.src_path)

    def add_group(self, app, group):
        self.groups[app].add(group)

    def remove_group(self, app, group):
        self.groups[app].discard(group)

    def load(self, name):
        self._load(name)

        for app in self._names:
            if app is not 'sage':
                if hasattr(self[app], 'init'):
                    self[app].init()

        for app in self._names:
            if app is not 'sage':
                if hasattr(self[app], 'post_init'):
                    self[app].post_init()

    def _load(self, name):
        """ Load a module or package into the namespace """

        name = self._preload(name)

        with imports.cwd_in_path():
            try:
                ns = importlib.import_module(name)
            except ImportError:
                try:
                    ns = imports.import_file(name)
                except ImportError:
                    sage._log.err("Error: Unable to import app '%s'" % name)
                    return

            path = os.path.dirname(inspect.getabsfile(ns))

            meta = importlib.import_module('%s.meta' % name)

            modname = ns.__name__

            if '.' in ns.__name__:
                modname = name.split('.')[-1]

            self._names.add(modname)

            meta.path = path
            meta.__name__ = modname

            if hasattr(meta, 'installed_apps'):
                if os.path.exists(path + '/apps') or os.path.isdir(path + '/apps'):
                    sys.path.append(path + '/apps')

                for subapp in meta.installed_apps:
                    self._load(subapp)

            self.meta[meta.__name__] = meta

            app = importlib.import_module('%s.%s' % (ns.__name__, modname))

            self[meta.__name__] = app

            fullname = ns.__name__
            if hasattr(meta, 'name'):
                fullname = meta.name

            if hasattr(meta, 'version'):
                if type(meta.version) is tuple:
                    fullname = "%s %s" % (fullname, '.'.join(str(x) for x in meta.version))
                else:
                    fullname = '%s %s' % (fullname, meta.version)

            if meta.__name__ not in self.paths:
                self._generate_paths()

            sage._log.msg("Loaded app '%s'" % fullname)
            return True

        del(self.groups[name])
        sage._log.msg("Failed to load app '%s'" % name)
        return False

    def load_manifest(self):
        for app in sage.manifest.apps:
            if 'path' in app:
                self.load(app['path'])
            else:
                self.load(app['name'])

    def _generate_paths(self):
        self.paths = dict()

        for name, meta in self.meta.items():
            self.paths[name] = meta.path

    def _preload(self, name):

        if name[-1] == '/':
            name = name[0:-1]

        if '/' in name:
            shortname = name = name.split('/')[-1]
        else:
            shortname = name

        if '.' in shortname:
            shortname = shortname.split('.')[-1]

        if name not in self.groups:
            self.groups[shortname] = set()

        return name

    def get_path(self, name):
        return self.meta[name].path

    def reload(self, name, event_src_path=None):
        """ Try to fully rebuild an app """

        # Don't reload the same app if we did it within last the 5 sec
        if time.time() - self._last_reload.get(name, 0) < 5:
            return

        self._last_reload[name] = time.time()

        if name not in self:
            return False

        if hasattr(self[name], 'pre_reload'):
            self[name].pre_reload()

        try:
            if event_src_path:

                if event_src_path.endswith('.py'):
                    path, f = os.path.split(event_src_path)
                    pyc = path + '/' + f[:-3] + '.pyc'
                    if os.path.isfile(pyc):
                        os.remove(pyc)

                targets = []

                for mname, module in sys.modules.items():
                    if module:
                        if hasattr(module, '__file__'):
                            if event_src_path in module.__file__:
                                targets.append(module)

                for target in targets:
                    rebuild(target, False)

            else:
                # generally try to reload the app
                self[name] = rebuild(self[name], False)
        except:
            sage._log.msg("Error reloading '%s'" % name)
            sage._log.err()
            return False

        gc.collect()

        if hasattr(self[name], 'post_reload'):
            self[name].post_reload()

        sage._log.msg("Reloaded app '%s'" % self.meta[name].name)

        return True

    def unload(self, name):
        """ Attempt to remove a module from the namespace """

        if name not in self:
            return False

        if hasattr(self[name], 'unload'):
            self[name].unload()

        if name in self.groups:
            while len(self.groups[name]) > 0:
                self.groups[name].pop().destroy()

        del(self.groups[name])
        del(self.paths[name])
        del(self[name])
        del(self.meta[name])
        self._names.discard(name)

        to_del = [mod for mod in sys.modules if mod.startswith(name)]

        for mod in to_del:
            del(sys.modules[mod])

        gc.collect()
        return True

    def valid(self, name):
        """ Is a string the name of a valid app """
        return name in self._names

    def __repr__(self):
        return str(self.__class__)

    def __getattr__(self, item):
        if item in self:
            return self.__getitem__(item)
        else:
            raise AppNotLoaded("App '%s' not currently loaded" % item)


class ManifestFile(object):

    def __init__(self, path):
        pass