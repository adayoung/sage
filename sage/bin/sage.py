from __future__ import absolute_import
import argparse
import sage
from sage.utils import imports
import sys

banner = """** WARNING: This is a pre-release version of sage and it WILL EAT YOUR CAT! **
   _________ _____ ____
  / ___/ __ `/ __ `/ _ \\
 (__  ) /_/ / /_/ /  __/
/____/\__,_/\__, /\___/
           /____/ v%s (%s)
""" % (sage.__version__, sage.__series__)


def main():
    args = parser.parse_args()

    print(banner)

    app = args.app

    with imports.cwd_in_path():
        app = imports.import_file(app)
        sage.apps[app.__name__] = app

        print sage.aliases
        del(app)

    del(sage.apps['jaiko'])
    del(sys.modules['jaiko'])

    print sage.aliases

    from sage.server import run
    run()


parser = argparse.ArgumentParser(
    description='Framework and proxy for IRE\'s Achaea')
parser.add_argument('--version', action='version', version=sage.__version__)
parser.add_argument('app')
