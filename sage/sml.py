# -*- coding: utf-8 -*-

import yaml
from sage import triggers, aliases


class NoMatchableType(Exception):
    pass


class NoMatchablePattern(Exception):
    pass


class InvalidSMLMethod(Exception):
    pass


class SMLMethods(dict):

    reserved_names = ('exact', 'substring', 'regex', 'startswith', 'endswith',
        'delay', 'enabled', 'ignorecase', 'disable_on_match')

    def register(self, method, name=None):
        if name is None:
            name = method.__name__

        if name in self.reserved_names:
            raise InvalidSMLMethod('%s is considered a reserved name and '
                'cannot be registered' % name)

        if name in self:
            raise InvalidSMLMethod('%s is already a registered name')

        self[name] = method


def load_file(f, parent):
    f = file(f, 'r')
    data = yaml.load(f)

    load(data, parent)


def load(data, parent):
    if '::parent' in data:
        parent = parent.get_group(data['::parent'])
        if parent is None:
            raise InvalidParent("Can't find a valid parent named %s"
                % data['::parent'])

    walk(data, triggers)


def walk(d, parent=None):

    attrs = {}
    matchables = {}
    groups = {}

    for k in d.iterkeys():
        if ':' not in k:
            continue

        target, name = k.split(':')

        if target in ('g', 'group'):
            groups[name] = d[k]
        elif target == '':
            matchables[name] = d[k]

    for name, data in groups.iteritems():
        new_group = create_group(name, data, parent)
        walk(data, new_group)

    for name, data in matchables.iteritems():
        create_matchable(name, data, parent)


def create_group(name, data, parent):
    attrs = {k: v for k, v in data.iteritems() if ':' not in k}

    app = attrs.pop('app', None)
    enabled = attrs.pop('enabled', True)

    group = parent.get_group(name)

    if group is None:
        group = parent.create_group(name, app=app, enabled=enabled)

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
            raise InvalidSMLMethod('No registered method called %s available '
                'for matchable %s' % (method, name))


methods = SMLMethods()
