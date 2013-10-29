# -*- coding: utf-8 -*-
"""
sage.signals
~~~~~~~~~~~~

This module defines the signals (Observer pattern) used throught SAGE.

Functions can be connected to these signals, and connected functions are called
whenever a signal is called.

"""

from __future__ import absolute_import
from sage.dispatch.signal import Signal

#: Before the sage server starts
pre_start = Signal()

#: Before prompt processing
pre_prompt = Signal(providing_args=['raw_data'])

#: After prompt is received
post_prompt = Signal()

#: Player has successfully logged in
player_connected = Signal()
