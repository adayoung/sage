# -*- coding: utf-8 -*-


class Item(object):

    def __init__(self, num, name, worn=False, wearable=False, wielded_left=False,
            wielded_right=False, groupable=False, riftable=False, takeable=False,
            denizen=False, dead=False, container=False):

        self.id = num
        self.name = name

        self.worn = worn
        self.wearable = wearable
        self.wielded_left = wielded_left
        self.wielded_right = wielded_right
        self.groupable = groupable
        self.riftable = riftable
        self.takeable = takeable
        self.denizen = denizen
        self.dead = dead
        self.container = container

        if wielded_left or wielded_right:
            self.wielded = True

            if wielded_left and wielded_right:
                self.wielded_both = True

        if wielded_right and wielded_left:
            self.wielded_both = True

        if self.container:
            self.items = Inventory()

    def __repr__(self):
        return "Item(%s)" % self.name


class Inventory(dict):
    """ Container for the inventory """

    def add(self, num, name, attrib=None):
        """ Add an item to the inventory """

        worn = False
        wearable = False
        groupable = False
        riftable = False
        takeable = False
        denizen = False
        dead = False
        wielded_right = False
        wielded_left = False
        container = False

        if attrib:
            if 'w' in attrib:
                worn = True
            if 'W' in attrib:
                wearable = True
            if 'l' in attrib:
                wielded_left = True
            if 'L' in attrib:
                wielded_right = True
            if 'g' in attrib:
                groupable = True
            if 'c' in attrib:
                container = True
            if 't' in attrib:
                takeable = True
            if 'r' in attrib:
                riftable = True
            if 'm' in attrib:
                denizen = True
            if 'd' in attrib:
                dead = True

        self[num] = Item(
            num,
            name,
            worn=worn,
            wearable=wearable,
            wielded_left=wielded_left,
            wielded_right=wielded_right,
            groupable=groupable,
            riftable=riftable,
            takeable=takeable,
            denizen=denizen,
            dead=dead,
            container=container
        )

        return self[num]

    def find(self, query):
        """ Search for an item by name """

        results = []

        query = query.lower()

        for item in self.values():
            if query in item.name.lower():
                results.append(item)

        return results

    def worn(self):
        """ Return list of worn items """

        return [item for item in self.values() if item.worn]

    def wearable(self):
        """ Return list of wearable (but not currently worn) items """

        return [item for item in self.values() if item.wearable]

    def wielded(self):
        """ Return list of wielded items """

        return [item for item in self.values() if item.wielded]

    def groupable(self):
        """ Return list of groupable items """

        return [item for item in self.values() if item.groupable]

    def riftable(self):
        """ Return list of riftable items """

        return [item for item in self.values() if item.riftable]

    def takeable(self):
        """ Return list of riftable items """

        return [item for item in self.values() if item.takeable]

    def denizens(self):
        """ Return list of denizens """

        return [item for item in self.values() if item.denizen]

    def dead(self):
        """ Return list of dead things """

        return [item for item in self.values() if item.dead]

    def containers(self):
        """ Return list of containers """

        return [item for item in self.values() if item.container]
