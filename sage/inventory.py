# -*- coding: utf-8 -*-


class Item(object):

    def __init__(self, num, name, worn=False, wearable=False, wielded=False, \
            groupable=False, container=False):

        self.id = num
        self.name = name

        self.worn = worn
        self.wearable = wearable
        self.wielded = wielded
        self.groupable = groupable
        self.container = container

        if self.container:
            self.items = Inventory()

    def __repr__(self):
        return "Item(%s)" % self.name


class Inventory(dict):
    """ Container for the inventory """

    def add(self, num, name, attrib=None):

        worn = False
        wearable = False
        wielded = False
        groupable = False
        container = False

        if attrib:
            if 'w' in attrib:
                worn = True
            if 'W' in attrib:
                wearable = True
            if 'l' in attrib:
                wielded = True
            if 'g' in attrib:
                groupable = True
            if 'c' in attrib:
                container = True

        self[num] = Item(
            num,
            name,
            worn=worn,
            wearable=wearable,
            wielded=wielded,
            groupable=groupable,
            container=container
        )

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

    def containers(self):
        """ Return list of containers """

        return [item for item in self.values() if item.container]
