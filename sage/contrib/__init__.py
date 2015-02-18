from __future__ import division
from time import time
from sage.utils import MutableInt
from sage.dispatch.signal import Signal


class Balance(object):
    """ Tracks a balance """

    def __init__(self):
        self.balance = True
        self.last_on = 0
        self.last_off = 0
        self.waiting = False
        self.signal = Signal(providing_args=['state'])

    def is_on(self):
        """ Is this balance currently on balance? """

        if self.waiting:
            return False

        return self.balance

    def on(self):
        """ Set to on balance """

        self.waiting = False

        if self.balance == False:
            self.balance = True
            self.last_on = time()
            self.signal.send(state=True)

    def on_for(self):
        """ Return how long the balance has been available for or False if not"""

        if self.balance == False:
            return False

        return time() - self.last_on

    def off(self):
        """ Set to off balance """

        self.waiting = False

        if self.balance == True:
            self.balance = False
            self.last_off = time()
            self.signal.send(state=False)

    def off_for(self):
        """ Return how long the balance has been off for or False if on """

        if self.balance:
            return False

        return time() - self.last_off

    def wait(self):
        self.waiting = True

    def __repr__(self):
        if self.waiting:
            return str(False)
        return str(self.balance)

    def __eq__(self, other):
        if self.waiting:
            return False
        return self.balance == other

    def __nonzero__(self):
        if self.waiting:
            return False
        return self.balance


class Vital(MutableInt):
    """ Tracks a vital value (health, mana, etc) """

    def __init__(self):
        self.signal = Signal(providing_args=['vital', 'delta'])
        self.value = None
        self.max = None
        self.delta = None
        self.last = None
        self.percentage = None
        self.delta_percentage = None

        self.new = True

    def update(self, value, newmax=None):
        """ Update the vital's value """

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

        if self.delta is not 0:
            self.signal.send(vital=self,delta=self.delta)