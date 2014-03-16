# -*- coding: utf-8 -*-

import yaml
from sage import triggers, aliases
import os
from functools import wraps


class NoMatchableType(Exception):
    pass


class NoMatchablePattern(Exception):
    pass


class InvalidMethod(Exception):
    pass


class InvalidParent(Exception):
    pass

class SMLMethodException(Exception):
    pass


class SMLMethods(dict):

    reserved_names = ('exact', 'substring', 'regex', 'startswith', 'endswith',
        'delay', 'enabled', 'ignorecase', 'disable_on_match', 'enable', 'disable',
        'enable_group', 'disable_group', 'echo', 'gag')

    def register(self, method, name=None, system=False):
        if name is None:
            name = method.__name__

        if name in self.reserved_names and system is False:

            raise InvalidMethod('%s is considered a reserved name and '
                'cannot be registered' % name)

        self[name] = method


def load_directory(path, parent, extension=None):
    """ Load all SML files in a directory

        :param path: path to directory
        :type path: string
        :param parent: Matchable group to be the parent of those created by the SML file
        :type parent: string
        :param extension: (optional) limit files to a file extension
        :type extension: string
    """
    if path.endswith('/') is False:
        path += '/'

    if extension is not None:
        if extension.startswith('.') is False:
            extension = '.' + extension

    for f in os.listdir(path):
        if extension is None:
            load_file(path + f, parent)
            continue
        elif f.endswith(extension):
            load_file(path + f, parent)


def load_file(f, parent):
    """ Load and parse a SML file

        :param file: path to file to be loaded
        :type file: string
        :param parent: Matchable group to be the parent of those created by the SML file
        :type parent: `sage.matchable.Group`
    """
    f = file(f, 'r')
    data = yaml.load(f)

    load(data, parent)


def load(data, parent):
    """ Load a dictionary and process as SML

        :param data: parsed SML dictionary
        :type data: dict
        :param parent: Matchable group to be the parent of those created by the SML file
        :type parent: `sage.matchable.Group`
    """
    if parent is None:
        raise InvalidParent("Parent cannot be None for SML")

    if parent.app is None:
        raise InvalidParent("SML parent must be registered to an app")

    walk(data, parent)


def walk(d, parent):

    attrs = {}
    matchables = {}
    groups = {}

    for k in d.iterkeys():
        if k == 'enabled':
            continue
        elif k.startswith(':') is False:
            groups[k] = d[k]
        else:
            matchables[k[1:]] = d[k]

    for name, data in groups.iteritems():
        new_group = create_group(name, data, parent)
        walk(data, new_group)

    for name, data in matchables.iteritems():
        create_matchable(name, data, parent)


def create_group(name, data, parent):
    attrs = {k: v for k, v in data.iteritems() if ':' not in k}

    enabled = attrs.pop('enabled', True)

    group = parent.get_group(name)

    if group is None:
        group = parent.create_group(name, app=parent.app, enabled=enabled)

    return group


def create_matchable(name, data, parent):

    params = {
        'type': None,
        'pattern': None,
        'enabled': True,
        'ignorecase': True,
        'delay': None,
        'disable_on_match': False
    }

    matchable_methods = {}

    for key, value in data.iteritems():
        if ':' in key:
            continue

        if key in ('exact', 'substring', 'startswith', 'endswith', 'regex'):
            params['type'] = key
            params['pattern'] = value

        elif key in params.keys():
            params[key] = value

        else:
            matchable_methods[key] = value

    if params['type'] is None:
        raise NoMatchableType("%s doesn't have a correct type defined" % name)

    if params['pattern'] is None:
        raise NoMatchablePattern("%s doesn't have a pattern defined" % name)

    m = parent.create(name, params.pop('type'), params.pop('pattern'), **params)

    for method, args in matchable_methods.iteritems():
        if method in methods:
            m.bind(methods[method], args)
        else:
            raise InvalidMethod('No registered method called %s available '
                'for matchable %s' % (method, name))


def register(method, name=None):
    """ Register a method as an SML method

        :param method: method to register
        :type method: method
        :param name: (optional) name to use to call the method in SML
        :type name: string
    """

    methods.register(method, name)


def sml(method, **kwargs):
    """ Decorator for registering SML methods """

    name = kwargs.pop('name', None)
    register(method, name=name)
    return wraps(method)


methods = SMLMethods()


""" Default methods """

def disable(sender, param):
    if param == 'self':
        sender.disable()
        return

    if sender.type == 'trigger':
        m = triggers.get(param)
    else:
        m = aliases.get(param)

    if m:
        m.disable()
    else:
        raise SMLMethodException('Cannot find matchable `%s` for disable()' % param)

methods.register(disable, system=True)


def enable(sender, param):
    if param == 'self':
        sender.enable()
        return

    if sender.type == 'trigger':
        m = triggers.get(param)
    else:
        m = aliases.get(param)

    if m:
        m.enable()
    else:
        raise SMLMethodException('Cannot find matchable `%s` for enable()' % param)

methods.register(enable, system=True)


def disable_group(sender, param):
    if param == 'self':
        sender.parent().disable()
        return

    if sender.type == 'trigger':
        g = triggers.get_group(param)
    else:
        g = aliases.get_group(param)

    if g:
        g.disable()
    else:
        raise SMLMethodException('Cannot find group `%s` for disable_group()' % param)

methods.register(disable_group, system=True)


def enable_group(sender, param):
    if param == 'self':
        sender.parent().enable()
        return

    if sender.type == 'trigger':
        g = triggers.get_group(param)
    else:
        g = aliases.get_group(param)

    if g:
        g.enable()
    else:
        raise SMLMethodException('Cannot find group `%s` for enable_group()' % param)

methods.register(enable_group, system=True)


def enable_trigger_group(sender, param):
    g = triggers.get_group(param)

    if g:
        g.enable()
    else:
        raise SMLMethodException('Cannot find trigger group `%s` for enable_group()' % param)

methods.register(enable_trigger_group, system=True)


def enable_alias_group(sender, param):
    g = aliases.get_group(param)

    if g:
        g.enable()
    else:
        raise SMLMethodException('Cannot find alias group `%s` for enable_group()' % param)

methods.register(enable_alias_group, system=True)


def disable_trigger_group(sender, param):
    g = triggers.get_group(param)

    if g:
        g.disable()
    else:
        raise SMLMethodException('Cannot find trigger group `%s` for disable_group()' % param)

methods.register(disable_trigger_group, system=True)


def disable_alias_group(sender, param):
    g = aliases.get_group(param)

    if g:
        g.disable()
    else:
        raise SMLMethodException('Cannot find alias group `%s` for disable_group()' % param)

methods.register(disable_alias_group, system=True)