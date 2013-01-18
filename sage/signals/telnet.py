from __future__ import absolute_import
from sage.dispatch.signal import Signal

# Connected to Achaea
connected = Signal()

# Disconnected from Achaea
disconnected = Signal()

# Lines from the server
inbound = Signal(providing_args=['lines', 'prompt'])
