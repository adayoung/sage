from __future__ import absolute_import
from sage.dispatch.signal import Signal

#: Blackout on/off
blackout = Signal(providing_args=['blackout'])