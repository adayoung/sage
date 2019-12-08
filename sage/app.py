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

class App(object):
    def __init__(self, name, spec, manager):
        self.name = name
        self.fullname = None

        self.module = None
        self.matchables = []
        self.subapps = None

        self.spec = spec
        self.path = spec.submodule_search_locations[0]
        self.manager = manager
        self.manager.paths[self.path] = name

    def load(self):
        try:
            self.namespace = importlib.util.module_from_spec(self.spec)
        except ImportError:
            try:
                self.namespace = imports.import_file(name)
            except ImportError:
                sage._log.err("Error: Unable to import app '%s'" % name)
                return

        meta = importlib.import_module(f'{self.name}.meta')
        if hasattr(meta, 'installed_apps'):
            if os.path.exists(self.path + '/apps') or os.path.isdir(self.path + '/apps'):
                sys.path.append(self.path + '/apps')

            self.subapps = meta.installed_apps

        if hasattr(meta, 'name'):
            self.fullname = meta.name

        if hasattr(meta, 'version'):
            if type(meta.version) is tuple:
                self.fullname = "%s %s" % (self.fullname, '.'.join(str(x) for x in meta.version))
            else:
                self.fullname = '%s %s' % (self.fullname, meta.version)

        self.load_subapps()
        self.module = importlib.import_module(f'{self.name}.{self.name}')
        if hasattr(self.module, 'init'):
            try:
                self.module.init()
            except:
                sage._log.msg("Error in '%s' init" % self.name)
                sage._log.err()
                return False

        return True

    def post_init(self):
        if hasattr(self.module, 'post_init'):
            try:
                self.module.post_init()
            except:
                sage._log.msg("Error in '%s' post-init" % self.name)
                sage._log.err()

    def load_subapps(self):
        if self.subapps is not None:
            if os.path.exists(self.path + '/apps') or os.path.isdir(self.path + '/apps'):
                sys.path.append(self.path + '/apps')

            for subapp in self.subapps:
                self.manager.load(subapp)

    def reload(self):
        if hasattr(self.module, 'pre_reload'):
            try:
                self.module.pre_reload()
            except:
                sage._log.msg("Error in '%s' pre-reload" % self.name)
                sage._log.err()

        for group in self.matchables:
            group.destroy()
        self.matchables = []

        targets = []

        for mname, module in list(sys.modules.items()):
            if module:
                if hasattr(module, '__file__'):
                    if self.path in module.__file__ and \
                        self.path + '/apps' not in module.__file__:
                        targets.append(module)
        try:
            for target in targets:
                rebuild(target, False)

            self.module = rebuild(self.module, False)
        except:
            sage._log.msg("Error reloading '%s'" % self.name)
            sage._log.err()
            return False

    def post_reload(self):
        if hasattr(self.module, 'post_reload'):
            try:
                self.module.post_reload()
            except:
                sage._log.msg("Error in '%s' post-reload" % self.name)
                sage._log.err()

    def unload(self):
        if hasattr(self.module, 'unload'):
            try:
                self.module.unload()
            except:
                sage._log.msg("Error in '%s' unload" % self.name)
                sage._log.err()

    def add_matchables(self, group):
        self.matchables.append(group)

    def remove_matchables(self, group):
        self.matchables.append(group)

class AppManager(dict):
    """ Dict-like container of loaded apps """

    __bases__ = [dict]  # or unittests don't work

    def __init__(self):
        super(AppManager, self).__init__(self)

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

        if not event.src_path.endswith('.py'):
            return

        path, filename = os.path.split(event.src_path)

        for app_path in self.paths:
            if app_path in path:
                self.reload(self.paths[app_path], path, filename)

    def add_matchables(self, app, group):
        if app == 'sage':
            return

        self[app].add_matchables(group)

    def remove_matchables(self, app, group):
        if app == 'sage':
            return

        self[app].remove_matchables(group)

    def load_apps(self, root_app):
        self.load(root_app)
        for app in self:
            self[app].post_init()

    def load(self, name):
        """ Load a sage app """
        spec = importlib.util.find_spec(name)
        if not spec:
            sage._log.err("Error: Unable to locate app '%s'" % name)
        self[name] = App(name, spec, self)

        if self[name].load():
            sage._log.msg("Loaded app '%s'" % self[name].fullname)
            return

        sage._log.msg("Failed to load app '%s'" % name)
        return

    def load_manifest(self):
        for app in sage.manifest.apps:
            if 'path' in app:
                self.load(app['path'])
            else:
                self.load(app['name'])

    def reload(self, name, path, filename):
        """ Try to fully rebuild an app """

        for f in os.listdir(path):
            if os.path.isfile(f) and f.endswith('.pyc'):
                os.remove(f)

        if name in self:
            self[name].reload()

        gc.collect()

        self[name].post_reload()

        sage._log.msg("Reloaded app '%s'" % name)

    def unload(self, name):
        """ Attempt to remove a module from the namespace """

        if name not in self:
            return False

        self[name].unload()
        to_del = [mod for mod in sys.modules if mod.startswith(name)]

        for mod in to_del:
            del(sys.modules[mod])

        gc.collect()
        return True

    def valid(self, name):
        """ Is a string the name of a valid app """
        if name == 'sage':
            return True

        return name in self

    def __repr__(self):
        return str(self.__class__)

    def __getattr__(self, item):
        if item in self:
            return self.__getitem__(item).module
        else:
            raise AppNotLoaded("App '%s' not currently loaded" % item)


class ManifestFile(object):

    def __init__(self, path):
        pass
