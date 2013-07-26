from __future__ import absolute_import
from sage.dispatch.signal import Signal

# Goodbye
goodbye = Signal()

# Recieved a GMCP Ping from Achaea
ping = Signal(providing_args=['latency'])

# Updated room items
room_items = Signal(providing_args=['items'])