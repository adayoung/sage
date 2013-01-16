# -*- coding: utf-8 -*-

"""
SAGE Framework
~~~~~~~~~~~~~~

SAGE makes it easy and fun to write client-independent systems for Iron Realms
games.

:copyright: (c) 2012 by Todd Wilson.
:license: GPLv3, see LICENSE for more details.
"""

version = (2, 0, 0)

__title__ = 'sage-framework'
__version__ = '.'.join(str(i) for i in version)
__author__ = 'Todd Wilson'
__license__ = 'GPLv3'
__copyright__ = 'Copyright 2012 Todd Wilson'

try:
    from setproctitle import setproctitle
    setproctitle('sage')
except ImportError:
    pass

from .api import run, echo, write, log
from .utils import error, debug
from .matching import TriggerMasterGroup, AliasMasterGroup
from .app import Apps

# States
connected = False

# Input buffer of lines
buffer = None

# telnet write and echo internal methods
_write = None
_echo = None

# Trigger and aliases interfaces
triggers = TriggerMasterGroup()
aliases = AliasMasterGroup()

# Loaded applications
apps = Apps()
