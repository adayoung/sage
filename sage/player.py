# -*- coding: utf-8 -*-
"""
sage.player
~~~~~~~~~~~

This module contains all player "state" data much like a session.
"""
from __future__ import division
from sage.utils import MutableInt
from sage.inventory import Inventory
from time import time


class Balance(object):

    def __init__(self):
        self.balance = True
        self.last_on = 0
        self.last_off = 0

    def on(self):
        """ Set to on balance """

        if self.balance == False:
            self.balance = True
            self.last_on = time()

    def on_for(self):
        """ Return how long the balance has been available for or False if not"""

        if self.balance == False:
            return False

        return time() - self.last_on

    def off(self):
        """ Set to off balance """

        if self.balance == True:
            self.balance = False
            self.last_off = time()

    def off_for(self):
        """ Return how long the balance has been off for or False if on """

        if self.balance:
            return False

        return time() - self.last_off

    def __repr__(self):
        return str(self.balance)

    def __eq__(self, other):
        return self.balance == other


class Room(object):
    """ Container for room information """

    def __init__(self):
        self.id = None
        self.name = None
        self.exits = None
        self.area = None
        self.environment = None
        self.coords = None
        self.details = None
        self.map = None
        self.items = {}


class Rift(dict):
    """ Container for the Rift """
    pass


class Vital(MutableInt):

    def __init__(self):
        self.value = None
        self.max = None
        self.delta = None
        self.last = None
        self.percentage = None
        self.delta_percentage = None

        self.new = True

    def update(self, value, newmax=None):
        if newmax:
            self.max = int(newmax)

        self.last = self.value
        self.value = int(value)

        if self.new:
            self.delta = 0
            self.new = False
        else:
            self.delta = self.value - self.last
            self.delta_percentage = int(round(self.delta / self.max * 100))

        self.percentage = int(round(self.value / self.max * 100))


# name of the player
name = None

# name with titles and suffixes
fullname = None

# age of character
age = None

# race of character
race = None

# class of character
combatclass = None

# character specialization
specialization = None

# level of your character
level = None

# experience until next level in percentage
xp = None

# rank by experience
xprank = None

# city character inhabits
city = None

# house character is a member of
house = None

# order character belongs to
order = None

# number of bound credits
boundcredits = None

# number of unbound credits
credits = None

# number of mayan crowns
mayancrowns = None

# number of bound mayan crowns
boundmayancrowns = None

# number of lessons
lessons = None

# rank in exploreres
explorerrank = None

# skill => rank out of the 12 levels of compentency
skill_groups = {}

# dictionary of skills and contained abilities
skills = {}

# player vitals
health = Vital()
mana = Vital()
willpower = Vital()
endurance = Vital()

# Comm Channels like clans, newbie, HT, etc
comm_channels = None

# Room data
room = Room()

# Player inventory dict
inv = Inventory()

# Rift dict
rift = Rift()

# Balances
balance = Balance()
equilibrium = Balance()

# stunned
stunned = False


# balance + eq + no stun
def ready():
    if balance == False or equilibrium == False:
        return False

    if stunned:
        return False

    return True
