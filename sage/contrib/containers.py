# -*- coding: utf-8 -*-


class Item(object):

    def __init__(self, num, name, worn=False, wearable=False, wielded_left=False,
            wielded_right=False, groupable=False, rifted=False, takeable=False,
            denizen=False, dead=False, container=False):

        self.id = num
        self.name = name

        self.worn = worn
        self.wearable = wearable
        self.wielded_left = wielded_left
        self.wielded_right = wielded_right
        self.groupable = groupable
        self.rifted = rifted
        self.takeable = takeable
        self.denizen = denizen
        self.dead = dead
        self.container = container

        if self.container:
            self.items = Inventory()

    def update_item(self, attrib):
        self.worn = False
        self.wearable = False
        self.wielded_left = False
        self.wielded_right = False
        self.groupable = False
        self.container = False
        self.takeable = False
        self.rifted = False
        self.denizen = False
        self.dead = False

        if attrib is None:
            return

        if 'w' in attrib:
            self.worn = True
        if 'W' in attrib:
            self.wearable = True
        if 'l' in attrib:
            self.wielded_left = True
        if 'L' in attrib:
            self.wielded_right = True
        if 'g' in attrib:
            self.groupable = True
        if 'c' in attrib:
            self.container = True
        if 't' in attrib:
            self.takeable = True
        if 'r' in attrib:
            self.rifted = True
        if 'm' in attrib:
            self.denizen = True
        if 'd' in attrib:
            self.dead = True
        if 't' in attrib:
            self.takeable = True

    def wielded(self):
        """ Is the item wielded? """
        return self.wielded_left or self.wielded_right

    def wielded_both(self):
        """ Is the item wielded in both hands? """
        return self.wielded_left and self.wielded_right

    def add_item(self, num, name, attrib=None):
        """ Add an item to this item's inventory. """
        self.container = True
        if not hasattr(self, 'items'):
                self.items = Inventory()
        return self.items.add(num, name, attrib)


    def __repr__(self):
        return "Item(%s)" % self.name

    def encode(self):
        representation = {
            'id': self.id,
            'name': self.name,
            'worn': self.worn,
            'wearable': self.wearable,
            'wielded_left': self.wielded_left,
            'wielded_right': self.wielded_right,
            'groupable': self.groupable,
            'rifted': self.rifted,
            'takeable': self.takeable,
            'denizen': self.denizen,
            'dead': self.dead,
            'container': self.container,
            'items': None
        }

        if self.container:
            representation['items'] = self.items.encode()

        return representation


class Inventory(dict):
    """ Container for the inventory """

    def add(self, num, name, attrib=None):
        """ Add an item to the inventory """

        worn = False
        wearable = False
        groupable = False
        rifted = False
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
                rifted = True
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
            rifted=rifted,
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

        return [item for item in self.values() if item.wielded()]

    def groupable(self):
        """ Return list of groupable items """

        return [item for item in self.values() if item.groupable]

    def rifted(self):
        """ Return list of rifted items """

        return [item for item in self.values() if item.rifted]

    def takeable(self):
        """ Return list of rifted items """

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

    def encode(self):
        representation = {}

        for num,item in self.iteritems():
            representation[num] = item.encode()

        return representation



class Rift(dict):
    """ Container for the Rift """
    pass


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
        self.items = Inventory()
        self.players = set()
        self.last_id = None

    def encode(self):
        representation = {
            'id': self.id,
            'name': self.name,
            'exits': self.exits,
            'area': self.area,
            'environment': self.environment,
            'coords': self.coords,
            'details': self.details,
            'map': self.map,
            'items': self.items.encode(),
            'players': list(self.players),
            'last_id': self.last_id
        }

        return representation
