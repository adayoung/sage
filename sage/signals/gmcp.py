from __future__ import absolute_import
from sage.dispatch.signal import Signal

#: Goodbye
goodbye = Signal()

#: Recieved a GMCP Ping from Achaea
ping = Signal(providing_args=['latency'])

#: Received a Char.Vitals
vitals = Signal(providing_args=[
    'health',
    'max_health',
    'mana',
    'max_mana',
    'endurance',
    'max_endurance',
    'willpower',
    'max_willpower',
    'xp'
])

#: Updated room
room = Signal(providing_args=['room'])

#: Updated room items
room_items = Signal(providing_args=['items'])

#: Item added to room
room_add_item = Signal(providing_args=['item'])

#: Item in room updated
room_update_item = Signal(providing_args=['item'])

#: Item removed from room
room_remove_item = Signal(providing_args=['item'])

#: Add a player to the room
room_add_player = Signal(providing_args=['player'])

#: Remove a player to the room
room_remove_player = Signal(providing_args=['player'])

#: Updated players in the room
room_players = Signal(providing_args=['players'])

#: You attempted to go in the wrong direction
room_wrongdir = Signal()

#: Item added to inventory
inv_add_item = Signal(providing_args=['item', 'container'])

#: Item updated
inv_update_item = Signal(providing_args=['item'])

#: Item removed from inventory
inv_remove_item = Signal(providing_args=['item', 'container'])

#: Updated inventory items
inv_items = Signal(providing_args=['items'])

#: Updated rift change
rift = Signal(providing_args=['rift'])

#: Changed rift item
rift_change = Signal(providing_args=['name', 'amount'])

#: IRE Time update
iretime = Signal(providing_args=['time'])

#: Updated dictionary of all skills
skills = Signal(providing_args=['skills'])

#: Someone speaking on a communications channel
comms = Signal(providing_args=['talker', 'channel', 'text'])
