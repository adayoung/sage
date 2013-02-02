from __future__ import absolute_import
import argparse
import sage
import sys
import os


banner = """** WARNING: This is a pre-release version of sage and it WILL EAT YOUR CAT! **
   _________ _____ ____
  / ___/ __ `/ __ `/ _ \\
 (__  ) /_/ / /_/ /  __/
/____/\__,_/\__, /\___/
           /____/ v%s (%s)
""" % (sage.__version__, sage.__series__)


def main():
    args = parser.parse_args()

    path = sys.argv[1]

    if '/' in path:
        path = '/'.join(path.split('/')[:-1]) + '/'
        sys.path.append("%s/%s" % (os.getcwd(), path))
    else:
        path = '.'
        sys.path.append(os.getcwd())

    sage.path = path

    print(banner)

    app = args.app

    sage.apps.load(app)

    from sage.server import run
    run()


parser = argparse.ArgumentParser(
    description='Framework and proxy for IRE\'s Achaea')
parser.add_argument('--version', action='version', version=sage.__version__)
parser.add_argument('app')

