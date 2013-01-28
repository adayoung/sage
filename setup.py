#!/usr/bin/env python

import sys
import os

if sys.version_info < (2, 7, 0):
    sys.stderr.write("sage requires Python 2.7 or newer.")
    sys.stderr.write(os.linesep)
    sys.exit(-1)

import sage

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

requires = [
    'twisted',
    'setproctitle',
    'pyasn1',
    'pycrypto'
]

entrypoints = {
    'console_scripts': 'sage = sage.__main__:main'
}

setup(
    name='sage',
    version=sage.__version__,
    description="Proxy and development framework for IRE's Achaea.",
    author='Todd Wilson',
    url='http://github.com/astralinae/sage',
    install_requires=requires,
    license='GPLv3',
    packages=['sage'],
    package_dir={'sage': 'sage'},
    entry_points=entrypoints
)
