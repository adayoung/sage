# -*- coding: utf-8 -*-
"""
This module contains all player "state" data much like a session.
"""
from sage.contrib.containers import Inventory, Rift, Room
from sage.contrib import Vital, Balance

#: player is logged in and GMCP data received
connected = False

#: name of the player
name = None

#: name with titles and suffixes
fullname = None

#: age of character
age = None

#: race of character
race = None

#: class of character
combatclass = None

#: character specialization
specialization = None

#: level of your character
level = None

#: experience until next level in percentage
xp = None

#: rank by experience
xprank = None

#: city character inhabits
city = None

#: house character is a member of
house = None

#: order character belongs to
order = None

#: number of bound credits
boundcredits = None

#: number of unbound credits
credits = None

#: number of mayan crowns
mayancrowns = None

#: number of bound mayan crowns
boundmayancrowns = None

#: number of lessons
lessons = None

#: rank in exploreres
explorerrank = None

#: skill => rank out of the 12 levels of compentency
skill_groups = {}

#: dictionary of skills and contained abilities
skills = {}

# dictionary of battlerage, class-related vitals, etc
charstats = {}

#: player health vital
health = Vital()

#: player mana vital
mana = Vital()

#: player willpower vital
willpower = Vital()

#: player endurance vital
endurance = Vital()

#: Comm Channels like clans, newbie, HT, etc
comm_channels = None

#: Room data
room = Room()

#: Player inventory dict
inv = Inventory()

#: Rift data
rift = Rift()

#: Achaea time data
iretime = dict()

#: 'balance' balance
balance = Balance()

#: 'equilibrium' balance
equilibrium = Balance()

#: Player in blackout
blackout = False

#: Prompt stats
prompt_stats = ''

#: List of active afflictions
afflictions = set()

#: List of active defences
defences = set()