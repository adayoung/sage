"""
    http://astralinae.github.io/sage/html/quickstart.html
"""

from sage import triggers, aliases, ansi, send

room_triggers = triggers.create_group('room', app='quickstart')

room_aliases = aliases.create_group('room', app='quickstart')


@room_aliases.exact("ql")
def ql(alias):

    # enable the exits trigger
    room_triggers('exits').enable()

    # send to Achaea
    send('ql')


@room_triggers.regex("^You see (a single exit leading|exits leading) ([a-z, \(\)]+)\.$", enabled=False)
def exits(trigger):
    exit_str = trigger.groups[1]
    exit_str = exit_str.replace('and', '')
    exits = [ansi.bold_white(e.strip()) for e in exit_str.split(',')]
    new_str = ', '.join(exits)
    trigger.line.output = "Exits: " + new_str

    # now disable this trigger
    trigger.disable()
