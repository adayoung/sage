"""
    http://astralinae.github.io/sage/html/quickstart.html
"""

from sage import triggers, aliases, ansi, send
from sage.signals.gmcp import room as room_signal

room_triggers = triggers.create_group('room', app='quickstart')

room_aliases = aliases.create_group('room', app='quickstart')


# interception to False means the original command passes through
@room_aliases.exact(pattern="ql", intercept=False)
def ql(alias):

    # enable the exits trigger
    room_triggers('exits').enable()

    # send to Achaea
    #send('ql')


@room_triggers.regex("^You see (a single exit leading|exits leading) ([a-z, \(\)]+)\.$", enabled=False)
def exits(trigger):
    exit_str = trigger.groups[1]
    exit_str = exit_str.replace('and', '')
    exits = [ansi.bold_white(e.strip()) for e in exit_str.split(',')]
    new_str = ', '.join(exits)
    trigger.line.output = "Exits: " + new_str

    # now disable this trigger
    trigger.disable()


def on_room_update(**kwargs):
    room_triggers('exits').enable()


room_signal.connect(on_room_update)  # Enable the room exits trigger on room change