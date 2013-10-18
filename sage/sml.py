# -*- coding: utf-8 -*-

import yaml
from sage import triggers, aliases


class NoMatchableType(Exception):
    pass


class NoMatchablePattern(Exception):
    pass


class InvalidMethod(Exception):
    pass


class InvalidParent(Exception):
    pass


class SMLMethods(dict):

    reserved_names = ('exact', 'substring', 'regex', 'startswith', 'endswith',
        'delay', 'enabled', 'ignorecase', 'disable_on_match')

    def register(self, method, name=None):
        if name is None:
            name = method.__name__

        if name in self.reserved_names:
            raise InvalidMethod('%s is considered a reserved name and '
                'cannot be registered' % name)

        if name in self:
            raise InvalidMethod('%s is already a registered name')

        self[name] = method


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
        if k.startswith(':') is False:
            groups[k] = d[k]
        else:
            matchables[k[1:]] = d[k]

        """
        target, name = k.split(':')

        if target in ('g', 'group'):
            groups[name] = d[k]
        elif target == '':
            matchables[name] = d[k]
        """

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


methods = SMLMethods()
