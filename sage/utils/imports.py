# -*- coding: utf-8 -*-

from __future__ import absolute_import

import imp as _imp
from contextlib import contextmanager
import sys
import os as _os


class NotAPackage(Exception):
    pass


@contextmanager
def cwd_in_path():
    cwd = _os.getcwd()
    if cwd in sys.path:
        yield
    else:
        sys.path.insert(0, cwd)
        try:
            yield cwd
        finally:
            try:
                sys.path.remove(cwd)
            except ValueError:
                pass


def _import_in_path(name):
    # attempt to load from sys.path first

    if '.py' in name:
        name = name[:-3]

    module = None
    fhandle = None
    try:
        tup = _imp.find_module(name)
        module = _imp.load_module(name, *tup)
        fhandle = tup[0]
    finally:
        if fhandle is not None:
            fhandle.close()

    return module


def import_file(fpath):
    '''
    fpath - the relative or absolute path to the .py file which is imported.

    Returns the imported module.

    NOTE: if import_file is called twice with the same module, the module
    is reloaded.
    '''

    try:
        module = _import_in_path(fpath)
        return module
    except:
        pass

    if hasattr(_os, 'getcwdu'):
        # python 2 returns question marks in os.path.realpath for
        # ascii input (eg '.').
        original_path = _os.path.realpath(_os.getcwdu())
    else:
        original_path = _os.path.realpath(_os.path.curdir)
    dst_path = _os.path.dirname(fpath)

    if dst_path == '':
        dst_path = '.'

    # remove the .py suffix
    script_name = _os.path.basename(fpath)
    if script_name.endswith('.py'):
        mod_name = script_name[:-3]
    else:
        # packages for example.
        mod_name = script_name

    _os.chdir(dst_path)
    fhandle = None

    if _os.path.isdir(mod_name):
        _os.chdir(mod_name)

    tup = _imp.find_module(mod_name, ['.'])
    fhandle = tup[0]
    module = None
    try:
        module = _imp.load_module(mod_name, *tup)
        _os.chdir(original_path)
        return module
    finally:
        if fhandle:
            fhandle.close()
