from __future__ import absolute_import
import argparse
import sage
from sage import config
from sage.utils import touch
import sys
import os
import re

banner = """** WARNING: This is a pre-release version of sage and it WILL EAT YOUR CAT! **
   _________ _____ ____
  / ___/ __ `/ __ `/ _ \\
 (__  ) /_/ / /_/ /  __/
/____/\__,_/\__, /\___/
           /____/ v%s (%s)
""" % (sage.__version__, sage.__series__)


def main():
    args = parser.parse_args()

    if args.command == 'mkapp':
        mkapp(args)
    elif args.command == 'run':
        run(args)
    elif args.command == 'version':
        version()


def mkapp(args):

    if bool(re.compile(r'[^a-zA-Z\-_0-9.]').search(args.app)) is True:
        raise Exception('Invalid name for app')

    if os.path.exists(args.app):
        raise Exception('%s already exists' % args.app)

    if args.app in sys.modules:
        raise Exception('%s already exists in PYTHONPATH' % args.app)

    name = args.app

    fullname = raw_input('Full app name [%s]: ' % name)
    if fullname == '':
        fullname = name

    description = raw_input('Description []: ')

    version = raw_input('Version: [1.0.0]: ')
    if version == '':
        version = '1.0.0'

    if version.count('.') == 2:
        version = '(' + ', '.join(version.split('.')) + ')'

    os.mkdir(name)

    touch("%s/__init__.py" % name)
    touch("%s/%s.py" % (name, name))

    meta = open("%s/meta.py" % name, 'w')

    meta.write(meta_template.format(
        name=fullname,
        description=description,
        version=version
    ))

    meta.close()

    print("Created '%s'" % name)


def run(args):

    path = sys.argv[1]

    if '/' in path:
        path = '/'.join(path.split('/')[:-1]) + '/'
        path = "%s/%s" % (os.getcwd(), path)
    else:
        path = os.getcwd()

    sys.path.append(path)

    sage.path = path

    print(banner)

    sage.log.startLogging(sys.stdout)

    app = args.app

    sage.apps.load(app)

    if args.no_backdoor:
        config.backdoor = False

    from sage.server import run

    run()


def version():
    print(sage.__version__)


meta_template = """name = '{name}'
description = '{description}'
version = {version}
installed_apps = ()
"""

parser = argparse.ArgumentParser(
    description='Framework and proxy for IRE\'s Achaea')
parent = argparse.ArgumentParser(add_help=False)

subparsers = parser.add_subparsers(dest='command')

runparser = subparsers.add_parser('run', parents=[parent])
runparser.add_argument('-b', '--no-backdoor', action='store_true', help='Disable the SSH backdoor')
runparser.add_argument('app')

mkappparser = subparsers.add_parser('mkapp', parents=[parent])
mkappparser.add_argument('-m', '--minimal', action='store_true', help='Create a minimal application')
mkappparser.add_argument('app')

versionparser = subparsers.add_parser('version', parents=[parent])
