from __future__ import absolute_import
from sage.dispatch.signal import Signal

# Connected to Achaea
connected = Signal()

# Disconnected from Achaea
disconnected = Signal()

# Processed lines about to go out to the client
pre_outbound = Signal(providing_args=['lines', 'prompt'])