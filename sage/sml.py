# -*- coding: utf-8 -*-

import yaml
from sage import triggers, aliases


class NoMatchableType(Exception):
    pass


class NoMatchablePattern(Exception):
    pass


def load_file(f, parent):
    f = file(f, 'r')
    data = yaml.load(f)

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

    methods = {}

    for key, value in data.iteritems():
        if ':' in key:
            continue

        if key in ('exact', 'substring', 'startswith', 'endswith', 'regex'):
            params['type'] = key
            params['pattern'] = value

        elif key in params.keys():
            params[key] = value

        else:
            methods[key] = value

    if params['type'] is None:
        raise NoMatchableType("%s doesn't have a correct type defined" % name)

    if params['pattern'] is None:
        raise NoMatchablePattern("%s doesn't have a pattern defined" % name)

    parent.create(name, params.pop('type'), params.pop('pattern'), **params)
