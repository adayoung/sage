#!/usr/bin/env python

import sage

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

requires = [
    'twisted'
]

setup(
    name='sage-framework',
    version=sage.__version__,
    description='Developing for IRE games in easy-mode.',
    install_requires=requires,
    license='GPLv3',
    packages=['sage'],
    package_dir={'sage': 'sage'}
)
