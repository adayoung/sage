# -*- coding: utf-8 -*-
from __future__ import absolute_import
import re
from time import time
from sage.dispatch.signal import Signal, Hook


class MatchableCreationError(Exception):
    pass


class MatchableGroupError(Exception):
    pass


class Matchable(object):

    def __init__(self, **kwargs):
        self.name = kwargs.pop('name', None)
        self.pattern = kwargs.pop('pattern', None)
        self.enabled = kwargs.pop('enabled', None)

        self.line = None
        self.time = None
        self.prefix = None
        self.suffix = None
        self.parent = kwargs.pop('parent', None)
        self.matchobj = None

        self.methods = Hook()

    def enable(self):
        self.parent._enable(self)
        self.enabled = True

    def disable(self):
        self.parent._disable(self)
        self.enabled = False

    def destroy(self):
        self.parent._remove(self)

    def connect(self, *args, **kwargs):
        self.signals.connect(*args, **kwargs)

    def disconnect(self, **kwargs):
        self.signals.disconnect(**kwargs)

    def successful_match(self, line):

        self.line = line
        self.time = time()
        self.methods.send(self)
        return True


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

        if self.pattern in line.line:
            self.prefix, self.suffix = line.line.split(self.pattern)
            return self.successful_match(line)

        return False


class CISubstring(CIMatchable):

    def match(self, line):

        if self.pattern in line.lower():
            self.prefix, self.suffix = line.line.split(self.pattern)
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

        match = self.pattern.match(line.line)

        if match:
            self.matchobj = match
            self.groups = match.groups()
            return self.successful_match(line)

        return False


class Startswith(Matchable):

    def match(self, line):

        if line.line.startswith(self.pattern):
            self.suffix = line.line.split(self.pattern)[1]
            return self.successful_match(line)

        return False


class CIStartswith(CIMatchable):

    def match(self, line):

        if line.line.lower().startswith(self.pattern):
            self.suffix = line.line.split(self.pattern)[1]
            return self.successful_match(line)

        return False


class Endswith(Matchable):

    def match(self, line):

        if line.line.endswith(self.pattern):
            self.prefix = line.line.split(self.pattern)[0]
            return self.successful_match(line)

        return False


class CIEndswith(CIMatchable):

    def match(self, line):

        if self.line.line.lower().endswith(self.pattern):
            self.prefix = line.line.split(self.pattern)[0]
            return self.successful_match(line)

        return False


class Group(dict):

    def __init__(self, name, parent, enabled=True):
        self.name = name
        self.parent = parent

        self.groups = {}
        self._states = {}

        self.enabled = enabled

    def create(self,
        name,
        mtype,
        pattern,
        enabled=True,
        ignorecase=True):
        """ Create a trigger or alias """

        kwargs = {
            'name': name,
            'pattern': pattern,
            'enabled': enabled,
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

        self[name] = m

        if enabled:
            self.parent._enable(m)

        return m

    def disable(self, name=None):

        if name is None:
            for instance in self.values():
                self.parent._disable(instance)
            self.enabled = False
            return True
        elif ':' in name:
            instance = self._parse_name(name)
            instance.disable()
            return True
        else:
            if name in self:
                self[name].disable()
                return True

        return False

    def enable(self, name=None):

        if name is None:
            for instance in self.values():
                if instance.enabled:
                    self.parent._enable(instance)
            self.enabled = True
            return True
        elif ':' in name:
            instance = self._parse_name(name)
            instance.enable()
            return True
        else:
            if name in self:
                self[name].enable()
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

        if name in self:
            instance = self[name]
            self.parent._remove(instance)
            del(self[name])
            return True

        return False

    def get(self, name):
        if ':' in name:
            return self._parse_name(name)
        else:
            super(Group, self).get(self, name)

    def get_group(self, name):
        if ':' in name:
            return self._parse_group(name)
        elif name in self.groups:
            return self.groups[name]

    def names(self):
        return self.keys()

    def _enable(self, instance):
        if self.enabled:
            self.parent._enable(instance)

    def _disable(self, instance):
        self.parent._disable(instance)

    def _remove(self, instance):
        self.parent._remove(instance)

    def _parse_group(self, name):
        parts = name.split(':')

        group = self

        for segment in parts:
            group = group.groups[segment]

        return group

    def _parse_name(self, name):
        parts = name.split(':')
        head = parts[:-1]
        tail = parts[-1]

        group = self

        for segment in head:
            group = group.groups[segment]

        return group[tail]

    def _decorator(self, **kwargs):
        name = kwargs.pop('name', None)
        mtype = kwargs.pop('type', None)
        mtype = 'substring' if mtype is None else mtype
        pattern = kwargs.pop('pattern', None)
        enabled = kwargs.pop('enabled', True)
        ignorecase = kwargs.pop('ignorecase', True)

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
                enabled=enabled, ignorecase=ignorecase)
            m.methods.connect(func)

            return func

        return dec

    def __repr__(self):
        return "%s '%s' (%s groups, %s objects)" % (self.__class__, \
            self.name, len(self.groups), len(self))


class TriggerGroup(Group):

    def trigger(self, **kwargs):
        return self._decorator(**kwargs)

    def create_group(self, name, enabled=True):

        self.groups[name] = TriggerGroup(name, self, enabled)
        return self.groups[name]


class AliasGroup(Group):

    def alias(self, **kwargs):
        return self._decorator(**kwargs)

    def create_group(self, name, enabled=True):

        self.groups[name] = AliasGroup(name, self, enabled)
        return self.groups[name]


class MasterGroup(Group):

    def __init__(self):

        self.enabled = set()
        self.parent = self
        self.groups = {}

    def _disable(self, instance):
        self.enabled.discard(instance)

    def _enable(self, instance):
        self.enabled.add(instance)

    def __repr__(self):
        return "%s (%s groups, %s objects)" % (self.__class__, \
            len(self.groups), len(self))


class TriggerMasterGroup(MasterGroup, TriggerGroup):
    pass


class AliasMasterGroup(MasterGroup, AliasGroup):
    pass
