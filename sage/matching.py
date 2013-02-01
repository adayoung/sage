# -*- coding: utf-8 -*-
"""
    Defines sage's triggers and aliases.

    In sage, a 'matchable' is either a trigger or an alias. The behavior of
    both are identical. The only difference is where they occur in execution.
"""
from __future__ import absolute_import
import re
from time import time
from sage.dispatch.signal import Hook
from sage import apps
from twisted.internet import reactor
import weakref


class MatchableCreationError(Exception):
    pass


class MatchableGroupError(Exception):
    pass


class InvalidMatchableType(Exception):
    pass


class AppNotFound(Exception):
    pass


class OrphanedMatchableGroupError(Exception):
    pass


class Matchable(object):
    """ Base class for a trigger or alias """

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
        self.parent = weakref.ref(kwargs.pop('parent'))
        self.matchobj = None

        self.methods = Hook()

        if methods:
            for method in methods:
                self.bind(method)

    def enable(self):
        """ Enable the matchable """
        self.parent()._enable(self)
        self.enabled = True

    def disable(self):
        """ Disable the matchable """
        self.parent()._disable(self)
        self.enabled = False

    def destroy(self):
        """ Destroys (deletes) the matchable """
        self.parent()._remove_child(self)

    def bind(self, method):
        """ Add a method to a matchable """
        self.methods.connect(method)

    def unbind(self, method):
        """ Remove a method from a matchable """
        self.methods.disconnect(method)

    def successful_match(self, line):
        """ Called when the matchable successfully matches """
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
        """ Send to all bound methods """
        self.methods.send(self)


class CIMatchable(Matchable):
    """ Case-insensitive matchable """

    def __init__(self, **kwargs):

        kwargs['pattern'] = kwargs['pattern'].lower()

        Matchable.__init__(self, **kwargs)


class Exact(Matchable):
    """ Exact-match matchable """

    def match(self, line):

        if self.pattern == line:
            return self.successful_match(line)

        return False


class CIExact(CIMatchable):
    """ Case-insensitive exact-match matchable """

    def match(self, line):

        if self.pattern == line.lower():
            return self.successful_match(line)

        return False


class Substring(Matchable):
    """ Substring matchable """

    def match(self, line):

        if self.pattern in line:
            self.prefix, self.suffix = line.split(self.pattern)
            return self.successful_match(line)

        return False


class CISubstring(CIMatchable):
    """ Case-insensitive substring matchable """

    def match(self, line):

        if self.pattern in line.lower():
            self.prefix, self.suffix = line.split(self.pattern)
            return self.successful_match(line)

        return False


class Regex(Matchable):
    """ Regular expression matchable """

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
    """ Starts-with string matchable """

    def match(self, line):

        if line.startswith(self.pattern):
            self.suffix = line.split(self.pattern)[1]
            return self.successful_match(line)

        return False


class CIStartswith(CIMatchable):
    """ Case-insensitive starts-with string matchable """

    def match(self, line):

        if line.lower().startswith(self.pattern):
            self.suffix = line.split(self.pattern)[1]
            return self.successful_match(line)

        return False


class Endswith(Matchable):
    """ Ends-with string matchable """

    def match(self, line):

        if line.endswith(self.pattern):
            self.prefix = line.split(self.pattern)[0]
            return self.successful_match(line)

        return False


class CIEndswith(CIMatchable):
    """ Case-insensitive ends-with string matchable """

    def match(self, line):

        if self.line.lower().endswith(self.pattern):
            self.prefix = line.split(self.pattern)[0]
            return self.successful_match(line)

        return False


class Group(object):
    """ Base matchable group """

    def __init__(self, name, parent, app, enabled=True):
        self.name = name
        self.parent = weakref.ref(parent)
        self.app = app
        self.enabled = enabled

        self.groups = {}
        self.matchables = {}

        if apps.valid(app) == False:
            raise AppNotFound("Unable to find app named '%s'" % app)

        apps.add_group(app, self)

    def create(self,
        name,
        mtype,
        pattern,
        methods=[],
        enabled=True,
        ignorecase=True,
        delay=None,
        disable_on_match=False):
        """ Create a trigger or alias (depending on the master group)

            :param name: name of the matchable.
            :type name: string
            :param type: 'type' of matchable. Must be 'exact', 'substring',
                'regex', 'startswith', or 'endswith'.
            :type type: string
            :param pattern: pattern to match against.
            :type pattern: string
            :param methods: (optional) methods to bind to the matchable.
            :type methods: list
            :param enabled: (optional) is the matchable enabled.
            :type enabled: bool
            :param ignorecase: (optional) is the matchable case-insensitive.
            :type ignorecase: bool
            :param delay: (optional) how many seconds to delay execution of
                bound methods after a successful match.
            :type delay: int or None
            :param disable_on_match: (optional) disable matchable after a
                successful match.
            :type disable_on_match: bool
        """

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
            raise InvalidMatchableType('Unsupported matchable type: %s' % mtype)

        self.matchables[name] = m

        if enabled:
            self.parent()._enable(m)

        return m

    def disable(self, name=None):
        """ Disable a group or matchable

            If called without a parameter, will disable the group being called.
            If name is provided, it will do a :meth:`get`
            lookup and call :meth:`disable` on that object.

            :param name: (optional) matchable query string
        """

        if name is None:
            for instance in self.matchables.values():
                self.parent()._disable(instance)
            self.enabled = False
            return True
        else:
            target = self.get(name)

            if target:
                target.disable()
                return True

        return False

    def destroy(self):
        """ Destroys (deletes) the group """
        for matchable in self.matchables.values():
            matchable.destroy()

        for child_group in self.groups.values():
            child_group.destroy()

        self.parent()._remove_group(self.name)

    def enable(self, name=None):
        """ Enable a group or matchable

            If called without a parameter, will enable the group being called.
            If name is provided, it will do a :meth:`get`
            lookup and call :meth:`enable` on that object.

            :param name: (optional) matchable query string
        """

        if name is None:
            for instance in self.matchables.values():
                if instance.enabled:
                    self.parent()._enable(instance)
            self.enabled = True
            return True
        else:
            target = self.get(name)

            if target:
                target.enable()
                return True

        return False

    def create_group(self, name, app=None, enabled=True):
        """ Creates a child group

            :param name: name of group
            :param app: name of app the group belongs to. If not set will be
                the group's parent's app.
            :param enabled: (optional) if group is enabled
            :type enabled: bool
        """

        if app is None:
            if self.app is None:
                raise OrphanedMatchableGroupError(
                "Top-level group '%s' must have an app declared in "
                "create_group()" % name)
            app = self.app
        elif apps.valid(app) == False:
            raise AppNotFound("Unable to find app named '%s'" % app)

        if self.__class__ in (TriggerMasterGroup, TriggerGroup):
            klass = TriggerGroup
        else:
            klass = AliasGroup

        self.groups[name] = klass(name, self, app, enabled)
        return self.groups[name]

    def remove_group(self, name):
        """ Removes a child group by name

            :param name: name of group
        """

        if name in self.groups:
            self.groups[name].destroy()
            return True

        return False

    def _remove_group(self, name):
        apps.remove_group(self.groups[name].app, self.groups[name])
        del(self.groups[name])

    def remove(self, name):
        """ Remove a matchable by name

            :param name: name of matchable
        """

        if name in self.matchables:
            instance = self.matchables[name]
            self._remove_child(instance)
            return True

        return False

    def get(self, name):
        """ Returns a group or matchable from a matchable query string

        :param name: matchable query string
        """
        if '/' in name:
            return self._parse_name(name)
        else:
            if name in self.matchables:
                return self.matchables[name]
            elif name in self.groups:
                return self.groups[name]
            return None

    def get_group(self, name):
        """ Returns a group from a matchable query string

        :param name: matchable query string
        """
        if '/' in name:
            parts = name.split('/')
            group = self
            for segment in parts:
                if segment in group.groups:
                    group = group.groups[segment]
                    if group is None:
                        return None
                else:
                    return None

            return group
        else:
            if name in self.groups:
                return self.groups[name]
            return None

    def names(self):
        """ Returns names of all matchables """
        return self.matchables.keys()

    def _enable(self, instance):
        if self.enabled:
            self.parent()._enable(instance)

    def _disable(self, instance):
        self.parent()._disable(instance)

    def _remove_child(self, instance):
        if instance.name in self.matchables:
            del(self.matchables[instance.name])

        self._remove(instance)

    def _remove(self, instance):
        self.parent()._remove(instance)

    def _parse_name(self, name):
        parts = name.split('/')
        head = parts[:-1]
        tail = parts[-1]

        group = self

        for segment in head:
            if segment in group.groups:
                group = group.groups[segment]

        if tail in group.groups:
            return group.groups[tail]
        elif tail in group.matchables:
            return group.matchables[tail]
        else:
            return None

    def _decorator(self, **kwargs):
        name = kwargs.pop('name', None)
        mtype = kwargs.pop('type', None)
        mtype = 'exact' if mtype is None else mtype
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

    def __getitem__(self, *args, **kwargs):
        return self.matchables.__getitem__(*args, **kwargs)

    def __call__(self, name):
        return self.get(name)


class TriggerGroup(Group):

    def trigger(self, **kwargs):
        return self._decorator(**kwargs)


class AliasGroup(Group):

    def alias(self, **kwargs):
        return self._decorator(**kwargs)


class MasterGroup(Group):

    def __init__(self):

        self.enabled = weakref.WeakSet()
        self.parent = self
        self.app = None
        self.groups = {}
        self.matchables = {}

    def _disable(self, instance):
        self.enabled.discard(instance)

    def _enable(self, instance):
        self.enabled.add(instance)

    def _remove(self, instance):
        self.enabled.discard(instance)

    def __repr__(self):
        return "%s (%s groups, %s objects)" % (self.__class__, \
            len(self.groups), len(self.matchables))


class TriggerMasterGroup(MasterGroup, TriggerGroup):
    pass


class AliasMasterGroup(MasterGroup, AliasGroup):
    pass
