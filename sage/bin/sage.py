from __future__ import absolute_import
import argparse
import os
import sys
import sage

banner = """   _________ _____ ____
  / ___/ __ `/ __ `/ _ \\
 (__  ) /_/ / /_/ /  __/
/____/\__,_/\__, /\___/
           /____/ v%s (%s)
""" % (sage.__version__, sage.__series__)


def main():
    args = parser.parse_args()
    print(banner)
    args.func(args)


def run(args):
    path = "%s/%s" % (os.getcwd(), args.file)
    if not os.path.isfile(path):
        sys.exit("Error: %s is not a file" % args.file)


def app(args):
    print 'app'


parser = argparse.ArgumentParser(
description='Framework and proxy for IRE\'s Achaea')
parser.add_argument('--version', action='version', version=sage.__version__)
parser.add_argument('file')
