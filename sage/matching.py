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
from sage.api import defer_to_prompt
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
        #: name of the matchable.
        self.name = kwargs.pop('name', None)

        #: pattern matched against.
        self.pattern = kwargs.pop('pattern', None)

        #: enabled.
        self.enabled = kwargs.pop('enabled', None)

        #: methods bound to the matchable.
        methods = kwargs.pop('methods', None)

        #: seconds execution is delayed by after match. None to disable.
        self.delay = kwargs.pop('delay', None)

        #: disable the matchable on a successful match
        self.disable_on_match = kwargs.pop('disable_on_match', False)

        #: disable on the prompt after a successful match
        self.disable_on_prompt = kwargs.pop('disable_on_prompt', False)

        #: gag the line on match
        self.gag = kwargs.pop('gag', False)

        #: (aliases only) intercept the output of the command
        self.intercept = kwargs.pop('intercept', True)

        self.type = kwargs.pop('group_type', None)

        self.timer = None

        #: matched line
        self.line = None

        #: time match occurred
        self.time = None

        #: text before matching pattern (substring and endswith only)
        self.prefix = None

        #: text after matching mattern (substring and startswith only)
        self.suffix = None

        #: parent group
        self.parent = weakref.ref(kwargs.pop('parent'))

        #: re.MatchObject (regex only)
        self.matchobj = None

        #: re.MatchObject.groups() - regex groups as a list (regex only)
        self.groups = None

        self.methods = []

        if methods:
            for method in methods:
                if type(method) is tuple or type(method) is list:
                    if len(method) != 2:
                        raise MatchableCreationError("Methods with parameters must be a " + \
                            "tuple or list with 2 elements")
                    self.bind(method[0], method[1])
                else:
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

    def bind(self, method, param=None):
        """ Add a method to a matchable """

        if param is not None:
            signal = Hook(providing_args=['param'])
        else:
            signal = Hook()

        signal.connect(method)

        self.methods.append((
            signal,
            param
        ))

    def unbind(self, method):
        """ Remove a method from a matchable """
        self.methods.disconnect(method)

    def successful_match(self, line):
        """ Called when the matchable successfully matches """
        self.line = line
        self.time = time()

        if self.disable_on_match:
            self.disable()

        if self.disable_on_prompt:
            defer_to_prompt(self.disable)

        if self.gag:
            self.line.gag()

        if self.delay:
            self.timer = reactor.callLater(self.delay, self.call_methods)
        else:
            self.call_methods()

        return True

    def call_methods(self):
        """ Send to all bound methods """
        for signal, param in self.methods:
            if param:
                signal.send(self, param)
            else:
                signal.send(self)


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

        if apps.valid(app) is False:
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
        disable_on_match=False,
        disable_on_prompt=False,
        gag=False,
        intercept=True):
        """ Create a trigger or alias (depending on the master group)

            :param name: name of the matchable.
            :type name: string
            :param mtype: 'type' of matchable. Must be 'exact', 'substring',
                'regex', 'startswith', or 'endswith'.
            :type mtype: string
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
            :param disable_on_prompt: (optional) disable matchable after a
                successful match on the following prompt.
            :type disable_on_prompt: bool
            :param gag: (optional) gag the line on a match.
            :type gag: bool
            :param intercept: (optional) -aliases only- Intercept the output of
                the command being sent.
            :type intercept: bool
        """

        kwargs = {
            'name': name,
            'pattern': pattern,
            'methods': methods,
            'enabled': enabled,
            'delay': delay,
            'disable_on_match': disable_on_match,
            'disable_on_prompt': disable_on_prompt,
            'gag': gag,
            'intercept': intercept,
            'parent': self,
            'group_type': self.group_type
        }

        if mtype == 'exact':
            m = CIExact(**kwargs) if ignorecase is False \
                else Exact(**kwargs)
        elif mtype == 'substring':
            m = CISubstring(**kwargs) if ignorecase is False  \
                else Substring(**kwargs)
        elif mtype == 'regex':
            kwargs['ignorecase'] = ignorecase
            m = Regex(**kwargs)
        elif mtype == 'startswith':
            m = CIStartswith(**kwargs) if ignorecase is False \
                else Startswith(**kwargs)
        elif mtype == 'endswith':
            m = CIEndswith(**kwargs) if ignorecase is False \
                else Endswith(**kwargs)
        else:
            raise InvalidMatchableType('Unsupported matchable type: %s' % mtype)

        self.matchables[name] = m

        if enabled:
            self.parent()._enable(m)

        return m

    def disable(self, name=None, child=False):
        """ Disable a group or matchable

            If called without a parameter, will disable the group being called.
            If name is provided, it will do a :meth:`get`
            lookup and call :meth:`disable` on that object.

            :param name: (optional) matchable query string
        """

        if name is None:
            if child is False:
                self.enabled = False

            for instance in self.matchables.values():
                self.parent()._disable(instance)

            for group in self.groups.values():
                group.disable(child=True)

            return True
        else:
            target = self.get(name)

            if target:
                target.disable()
                return True

    def destroy(self):
        """ Destroys (deletes) the group """
        for matchable in self.matchables.values():
            matchable.destroy()

        for child_group in self.groups.values():
            child_group.destroy()

        self.parent()._remove_group(self.name)

    def debug(self, indent=0):
        """ Print out a visual representation of all child matchables and groups

            :param indent: (optional) number of tabs to ident by
            :type indent: integer
        """

        for name, g in self.groups.iteritems():
            print("%s<%s [%s]>" % ('\t' * indent, name, '+' if g.enabled else ' '))
            g.debug(indent+1)

        for name, m in self.matchables.iteritems():
            print("%s-%s [%s]" % ('\t' * indent, name, '+' if m.enabled else ' '))


    def enable(self, name=None, child=False):
        """ Enable a group or matchable

            If called without a parameter, will enable the group being called.
            If name is provided, it will do a :meth:`get`
            lookup and call :meth:`enable` on that object.

            :param name: (optional) matchable query string
        """

        if name is None:
            if child is False:
                self.enabled = True

            for instance in self.matchables.values():
                if instance.enabled:
                    self.parent()._enable(instance)
            for group in self.groups.values():
                if group.enabled:
                    group.enable(child=True)
            return True
        else:
            target = self.get(name)

            if target:
                target.enable()
                return True


    def create_group(self, name, app=None, enabled=True):
        """ Creates a child group

            :param name: name of group
            :param app: name of app the group belongs to. If not set will be
                the group's parent's app.
            :param enabled: (optional) if group is enabled
            :type enabled: bool
        """
        if name in self.groups:
            return self.groups[name]

        if app is None:
            if self.app is None:
                raise OrphanedMatchableGroupError(
                "Top-level group '%s' must have an app declared in "
                "create_group()" % name)
            app = self.app
        elif apps.valid(app) is False:
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
        if name in self.groups:
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
        param = kwargs.pop('param', None)
        disable_on_prompt = kwargs.pop('disable_on_prompt', False)
        disable_on_match = kwargs.pop('disable_on_match', False)
        gag = kwargs.pop('gag', False)
        intercept = kwargs.pop('intercept', True)

        def dec(func):

            if name is None:
                mname = func.__name__

                # matchable by this name already exists, increment a new one
                if mname in self.matchables:
                    if hasattr(func, '_matchable_counter'):
                        func._matchable_counter += 1
                    else:
                        func._matchable_counter = 2

                    mname = mname + str(func._matchable_counter)
            else:
                mname = name

            if pattern is None:
                # we are appending to an existing matchable?
                if name in self:
                    m = self[name]
                    m.bind(func, param)
                    return func
                else:
                    raise MatchableCreationError('No pattern defined for %s' % mname)

            m = self.create(mname, mtype, pattern,
                enabled=enabled, ignorecase=ignorecase, delay=delay,
                disable_on_match=disable_on_match, disable_on_prompt=disable_on_prompt, gag=gag,
                intercept=intercept)
            m.bind(func, param)

            return func

        return dec

    def exact(self, *args, **kwargs):
        if len(args) == 1:
            kwargs['pattern'] = args[0]
        kwargs['type'] = 'exact'
        return self._decorator(**kwargs)

    def startswith(self, *args, **kwargs):
        if len(args) == 1:
            kwargs['pattern'] = args[0]
        kwargs['type'] = 'startswith'
        return self._decorator(**kwargs)

    def endswith(self, *args, **kwargs):
        if len(args) == 1:
            kwargs['pattern'] = args[0]
        kwargs['type'] = 'endswith'
        return self._decorator(**kwargs)

    def substring(self, *args, **kwargs):
        if len(args) == 1:
            kwargs['pattern'] = args[0]
        kwargs['type'] = 'substring'
        return self._decorator(**kwargs)

    def regex(self, *args, **kwargs):
        if len(args) == 1:
            kwargs['pattern'] = args[0]
        kwargs['type'] = 'regex'
        return self._decorator(**kwargs)

    def __repr__(self):
        estring = 'enabled' if self.enabled else 'disabled'
        return "%s '%s' (%s groups, %s objects) [%s]" % (self.__class__,
            self.name, len(self.groups), len(self.matchables), estring)

    def __getitem__(self, *args, **kwargs):
        return self.matchables.__getitem__(*args, **kwargs)

    def __call__(self, name):
        return self.get(name)


class TriggerGroup(Group):

    group_type = 'trigger'

    #: deprecated
    def trigger(self, **kwargs):
        return self._decorator(**kwargs)


class AliasGroup(Group):

    group_type = 'alias'

    #: deprecated
    def alias(self, **kwargs):
        return self._decorator(**kwargs)


class MasterGroup(Group):

    def __init__(self):

        self.name = 'master'
        self.enabled = set()
        self.parent = self
        self.app = None
        self.groups = {}
        self.matchables = {}

        self._to_add = set()
        self._to_remove = set()

        self.in_loop = False

    def _disable(self, instance):
        if self.in_loop:
            self._to_remove.add(instance)
        else:
            self.enabled.discard(instance)

    def _enable(self, instance):
        if self.in_loop:
            self._to_add.add(instance)
        else:
            self.enabled.add(instance)

    def _remove(self, instance):
        if self.in_loop:
            self._to_remove.add(instance)
        else:
            self.enabled.discard(instance)

    def flush_set(self):
        self.enabled.difference_update(self._to_remove)
        self.enabled.update(self._to_add)
        self._to_add.clear()
        self._to_remove.clear()

    def __repr__(self):
        return "%s (%s groups, %s objects)" % (self.__class__,
            len(self.groups), len(self.matchables))


class TriggerMasterGroup(MasterGroup, TriggerGroup):
    pass


class AliasMasterGroup(MasterGroup, AliasGroup):
    pass
