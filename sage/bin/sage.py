from __future__ import absolute_import
import argparse
import sage
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
    elif args.command == 'console':
        console(args)
    elif args.command == 'version':
        version()

def console(args):

    host = args.host if args.host else sage.config.backdoor_host
    port = args.port if args.port else sage.config.backdoor_port
    user = args.user if args.user else sage.config.backdoor_user

    print("SSH to %s:%s as %s. Cntr-D to exit." % (host, port, user))
    os.system("ssh %s -p %s -l %s" % (host, port, user))


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

    if os.path.exists('%s/%s.py' % (path, args.app)):
        path = '/'.join(path.split('/')[:-1])

    os.chdir(path)

    sys.path.append(path)

    sage.path = path

    print(banner)

    observer = sage._log.startLogging(sys.stdout)

    observer.timeFormat = "%Y-%m-%d %H:%M:%S:%f"

    app = args.app

    from sage.server import run, setup_system

    setup_system()

    sage.apps.load(app)

    if args.no_backdoor:
        sage.config.backdoor = False

    if args.no_telnet_proxy:
        sage.config.telnet_proxy = False

    if args.no_websocket:
        sage.config.ws_server = False

    if args.profile:
        from cProfile import Profile
        profile = Profile()
        profile.runcall(run)
        profile.dump_stats(args.profile)
    else:
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
runparser.add_argument('-p', '--profile', help='Run cProfile and save the stats to file')
runparser.add_argument('-t', '--no-telnet-proxy', action='store_true', help='Disable the telnet proxy')
runparser.add_argument('-w', '--no-websocket', action='store_true', help='Disable the websocket server')
runparser.add_argument('-D', '--ws-debug', action='store_true', help='Enable Websocket WAMP debugging')
runparser.add_argument('app')

mkappparser = subparsers.add_parser('mkapp', parents=[parent])
mkappparser.add_argument('-m', '--minimal', action='store_true', help='Create a minimal application')
mkappparser.add_argument('app')

consoleparser = subparsers.add_parser('console', parents=[parent])
consoleparser.add_argument('-H', '--host', help='Hostname')
consoleparser.add_argument('-p', '--port', help='Port')
consoleparser.add_argument('-u', '--user', help='Username')

versionparser = subparsers.add_parser('version', parents=[parent])
