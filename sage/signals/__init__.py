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

pre_start = Signal()

pre_prompt = Signal(providing_args=['raw_data'])

post_prompt = Signal()
