from __future__ import absolute_import
import argparse
import os
import sys
import sage


def main():
    parser = argparse.ArgumentParser(
    description='Framework and proxy for IRE\'s Achaea')
    parser.add_argument('--version', action='version', version=sage.__version__)
    subparsers = parser.add_subparsers()

    parser_run = subparsers.add_parser('run',
        help='start sage with your module')
    parser_run.set_defaults(func=run)
    parser_run.add_argument('-i', '--interactive', action='store_true',
        help='run sage with an interactive interpreter')
    parser_run.add_argument('file')

    parser_app = subparsers.add_parser('app', help='create a new sage app')
    parser_app.set_defaults(func=app)

    args = parser.parse_args()
    args.func(args)


def run(args):
    path = "%s/%s" % (os.getcwd(), args.file)
    if not os.path.isfile(path):
        sys.exit("Error: %s is not a file" % args.file)


def app(args):
    print 'app'
