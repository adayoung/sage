# -*- coding: utf-8 -*-
from __future__ import absolute_import
import re
from time import time
from sage.dispatch.signal import Hook
from twisted.internet import reactor
import weakref


class MatchableCreationError(Exception):
    pass


class MatchableGroupError(Exception):
    pass


class Matchable(object):

    def __init__(self, **kwargs):
        self.name = kwargs.pop('name', None)
        self.pattern = kwargs.pop('pattern', None)
        self.enabled = kwargs.pop('enabled', None)
        methods = kwargs.pop('methods', None)
        self.delay = kwargs.pop('delay', None)
        self.disable_on_match = kwargs.pop('disable_on_match', False)
        self.timer = None

        self.line = None
        self.time = None
        self.prefix = None
        self.suffix = None
        self.parent = kwargs.pop('parent', None)
        self.matchobj = None

        self.methods = Hook()

        if methods:
            for method in methods:
                self.bind(method)

    def enable(self):
        self.parent._enable(self)
        self.enabled = True

    def disable(self):
        self.parent._disable(self)
        self.enabled = False

    def destroy(self):
        self.parent._remove(self)

    def bind(self, method):
        self.methods.connect(method)

    def unbind(self, method):
        self.methods.disconnect(method)

    def successful_match(self, line):
        self.line = line
        self.time = time()

        if self.disable_on_match:
            self.disable()

        if self.delay:
            self.timer = reactor.callLater(self.delay, self.call_methods)
        else:
            self.call_methods()

        return True

    def call_methods(self):
        self.methods.send(self)


class CIMatchable(Matchable):

    def __init__(self, **kwargs):

        kwargs['pattern'] = kwargs['pattern'].lower()

        Matchable.__init__(self, **kwargs)


class Exact(Matchable):

    def match(self, line):

        if self.pattern == line:
            return self.successful_match(line)

        return False


class CIExact(CIMatchable):

    def match(self, line):

        if self.pattern == line.lower():
            return self.successful_match(line)

        return False


class Substring(Matchable):

    def match(self, line):

        if self.pattern in line:
            self.prefix, self.suffix = line.split(self.pattern)
            return self.successful_match(line)

        return False


class CISubstring(CIMatchable):

    def match(self, line):

        if self.pattern in line.lower():
            self.prefix, self.suffix = line.split(self.pattern)
            return self.successful_match(line)

        return False


class Regex(Matchable):

    def __init__(self, **kwargs):

        flags = 0

        if kwargs['ignorecase']:
            flags = re.IGNORECASE

        del(kwargs['ignorecase'])

        kwargs['pattern'] = re.compile(kwargs['pattern'], flags=flags)

        Matchable.__init__(self, **kwargs)

    def match(self, line):

        match = self.pattern.match(line)

        if match:
            self.matchobj = match
            self.groups = match.groups()
            return self.successful_match(line)

        return False


class Startswith(Matchable):

    def match(self, line):

        if line.startswith(self.pattern):
            self.suffix = line.split(self.pattern)[1]
            return self.successful_match(line)

        return False


class CIStartswith(CIMatchable):

    def match(self, line):

        if line.lower().startswith(self.pattern):
            self.suffix = line.split(self.pattern)[1]
            return self.successful_match(line)

        return False


class Endswith(Matchable):

    def match(self, line):

        if line.endswith(self.pattern):
            self.prefix = line.split(self.pattern)[0]
            return self.successful_match(line)

        return False


class CIEndswith(CIMatchable):

    def match(self, line):

        if self.line.lower().endswith(self.pattern):
            self.prefix = line.split(self.pattern)[0]
            return self.successful_match(line)

        return False


class Group(object):

    def __init__(self, name, parent, enabled=True):
        self.name = name
        self.parent = parent

        self.groups = weakref.WeakValueDictionary()
        self.matchables = weakref.WeakValueDictionary()
        self._states = {}

        self.enabled = enabled

    def create(self,
        name,
        mtype,
        pattern,
        methods=[],
        enabled=True,
        ignorecase=True,
        delay=None,
        disable_on_match=False):
        """ Create a trigger or alias """

        kwargs = {
            'name': name,
            'pattern': pattern,
            'methods': methods,
            'enabled': enabled,
            'delay': delay,
            'disable_on_match': disable_on_match,
            'parent': self
        }

        if mtype == 'exact':
            m = CIExact(**kwargs) if ignorecase == False \
                else Exact(**kwargs)
        elif mtype == 'substring':
            m = CISubstring(**kwargs) if ignorecase == False  \
                else Substring(**kwargs)
        elif mtype == 'regex':
            kwargs['ignorecase'] = ignorecase
            m = Regex(**kwargs)
        elif mtype == 'startswith':
            m = CIStartswith(**kwargs) if ignorecase == False \
                else Startswith(**kwargs)
        elif mtype == 'endswith':
            m = CIEndswith(**kwargs) if ignorecase == False \
                else Endswith(**kwargs)
        else:
            # you didn't specify a correct type!
            pass

        self.matchables[name] = m

        if enabled:
            self.parent._enable(m)

        return m

    def disable(self, name=None):

        if name is None:
            for instance in self.matchables.values():
                self.parent._disable(instance)
            self.enabled = False
            return True
        elif '/' in name:
            instance = self._parse_name(name)
            instance.disable()
            return True
        else:
            if name in self:
                self.matchables[name].disable()
                return True

        return False

    def enable(self, name=None):

        if name is None:
            for instance in self.matchables.values():
                if instance.enabled:
                    self.parent._enable(instance)
            self.enabled = True
            return True
        elif '/' in name:
            instance = self._parse_name(name)
            instance.enable()
            return True
        else:
            if name in self:
                self.matchables[name].enable()
                return True

        return False

    def create_group(self, name, enabled=True):

        self.groups[name] = Group(name, self, enabled)
        return self.groups[name]

    def remove_group(self, name):

        if name in self.groups:
            del(self.groups[name])
            return True

        return False

    def remove(self, name):

        if name in self.matchables:
            instance = self.matchables[name]
            self.parent._remove(instance)
            del(self.matchables[name])
            return True

        return False

    def get(self, name):
        if '/' in name:
            return self._parse_name(name)
        else:
            if name in self.matchables:
                return self.matchables[name]
            elif name in self.groups:
                return self.groups[name]
            else:
                return None

    def names(self):
        return self.matchables.keys()

    def _enable(self, instance):
        if self.enabled:
            self.parent._enable(instance)

    def _disable(self, instance):
        self.parent._disable(instance)

    def _remove(self, instance):
        self.parent._remove(instance)

    def _parse_name(self, name):
        parts = name.split('/')
        head = parts[:-1]
        tail = parts[-1]

        group = self

        for segment in head:
            group = group.groups[segment]

        if tail in group.groups:
            return group.groups[tail]
        elif tail in group:
            return group[tail]
        else:
            return None

    def _decorator(self, **kwargs):
        name = kwargs.pop('name', None)
        mtype = kwargs.pop('type', None)
        mtype = 'substring' if mtype is None else mtype
        pattern = kwargs.pop('pattern', None)
        enabled = kwargs.pop('enabled', True)
        ignorecase = kwargs.pop('ignorecase', True)
        delay = kwargs.pop('delay', None)

        def dec(func):

            if name is None:
                mname = func.__name__
            else:
                mname = name

            if pattern is None:
                # we are appending to an existing matchable?
                if name in self:
                    m = self[name]
                    m.methods.connect(func)
                    return func
                else:
                    raise MatchableCreationError('No pattern defined for %s' \
                        % mname)

            m = self.create(mname, mtype, pattern, \
                enabled=enabled, ignorecase=ignorecase, delay=delay)
            m.methods.connect(func)

            return func

        return dec

    def __repr__(self):
        return "%s '%s' (%s groups, %s objects)" % (self.__class__, \
            self.name, len(self.groups), len(self.matchables))


class TriggerGroup(Group):

    def trigger(self, **kwargs):
        return self._decorator(**kwargs)

    def create_group(self, name, enabled=True):

        g = TriggerGroup(name, self, enabled)  # I have to do this for weakrefs
        self.groups[name] = g
        return self.groups[name]


class AliasGroup(Group):

    def alias(self, **kwargs):
        return self._decorator(**kwargs)

    def create_group(self, name, enabled=True):

        g = AliasGroup(name, self, enabled)  # I have to do this for weakrefs
        self.groups[name] = g
        return self.groups[name]


class MasterGroup(Group):

    def __init__(self):

        self.enabled = set()
        self.parent = self
        self.groups = weakref.WeakValueDictionary()
        self.matchables = weakref.WeakValueDictionary()

    def _disable(self, instance):
        self.enabled.discard(instance)

    def _enable(self, instance):
        self.enabled.add(instance)

    def __repr__(self):
        return "%s (%s groups, %s objects)" % (self.__class__, \
            len(self.groups), len(self.matchables))


class TriggerMasterGroup(MasterGroup, TriggerGroup):
    pass


class AliasMasterGroup(MasterGroup, AliasGroup):
    pass
