# -*- coding: utf-8 -*-

"""
Sage Framework
~~~~~~~~~~~~~~

Sage makes it easy and fun to write client-independent systems for Iron Realms
games.

:copyright: (c) 2013 by Todd Wilson.
:license: GPLv3, see LICENSE for more details.
"""

version = (2, 0, 0, 'a1')

__title__ = 'sage'
__version__ = '.'.join(str(i) for i in version)
__series__ = 'Aegis'
__author__ = 'Todd Wilson'
__license__ = 'GPLv3'
__copyright__ = 'Copyright 2013 Todd Wilson'

try:
    from setproctitle import setproctitle
    setproctitle('sage')
except ImportError:
    pass

from twisted.python import log as _log

path = None

from .defaults import defaults

#: default configuration
config = defaults

from .app import Apps

#: Loaded applications
apps = Apps()

#: Is sage connected
connected = False

from .inbound import Buffer

#: Input buffer of lines (:class:`sage.inbound.Buffer`)
buffer = Buffer([])

from .matching import TriggerMasterGroup, AliasMasterGroup

#: Master alias group (:class:`sage.matching.AliasMasterGroup`)
aliases = AliasMasterGroup()

#: Master trigger group (:class:`sage.matching.TriggerMasterGroup`)
triggers = TriggerMasterGroup()

# telnet write and echo internal methods
_send = None
_echo = None

# methods defered to the prompt
_deferred = list()

from .api import echo, send, defer_to_prompt, delay, log
from .utils import error, debug
