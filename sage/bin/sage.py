from __future__ import absolute_import
from importlib import import_module
import argparse
import sage

parser = argparse.ArgumentParser(
    description='Framework and proxy for IRE\'s Achaea')
parser.add_argument('--version', action='version', version=sage.__version__)

def main():
    args = parser.parse_args()
    print args