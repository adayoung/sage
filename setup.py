#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

if sys.version_info < (2, 7, 0):
    sys.stderr.write("sage requires Python 2.7 or newer.")
    sys.stderr.write(os.linesep)
    sys.exit(-1)


from setuptools import setup, find_packages

requires = [
    'twisted',
    'pycrypto',
    'pyasn1',
    'watchdog',
    'autobahn',
    'six'
]

entrypoints = {
    'console_scripts': 'sage = sage.__main__:main'
}

setup(
    name='sage',
    version='2.0.0.a2',
    description="Proxy and development framework for IRE's Achaea.",
    author='Todd Wilson',
    url='http://github.com/spicerack/sage',
    install_requires=requires,
    license='GPLv3',
    packages=find_packages(exclude=['ez_setup', 'tests', 'tests.*']),
    entry_points=entrypoints
)
