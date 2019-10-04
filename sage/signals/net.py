
from sage.dispatch.signal import Signal

#: Connected to Achaea
connected = Signal()

#: Disconnected from Achaea
disconnected = Signal()

#: Processed lines about to go out to the client
pre_outbound = Signal(providing_args=['raw_lines', 'lines', 'prompt', 'ansi_prompt'])

#: Sage is lagging
lagging = Signal()

#: Sage is no longer lagging
lag_recovered = Signal()

#: Input from client
wamp_input = Signal(providing_args=['data'])
