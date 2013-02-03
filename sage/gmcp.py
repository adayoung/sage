# -*- coding: utf-8 -*-
from __future__ import absolute_import
from twisted.internet.task import LoopingCall
import json
from sage.utils import json_str_loads
from sage import __version__ as version
from sage.signals import gmcp as gmcp_signals
from time import time
import sage.player as player

# small copy of some telnet bytes
IAC = chr(255)
SB = chr(250)
SE = chr(240)
GMCPOPT = chr(201)

skill_ranks = {
    'Inept': 0,
    'Novice': 1,
    'Apprentice': 2,
    'Capable': 3,
    'Adept': 4,
    'Skilled': 5,
    'Gifted': 6,
    'Expert': 7,
    'Virtuoso': 8,
    'Fabled': 9,
    'Mythical': 10,
    'Transcendent': 11
}


class GMCPReceiver(object):

    def __init__(self):

        # for sending out commands
        self.out = None

        self.command_map = {
            'Core.Ping': self.ping,
            'Char.Name': self.name,
            'Char.Status': self.status,
            'Core.Goodbye': self.goodbye,
            'Char.Skills.Groups': self.skill_groups,
            'Char.Skills.List': self.skill_list,
            'Char.Vitals': self.vitals,
            'Char.StatusVars': self.statusvars,
            'Comm.Channel.List': self.comm_channels,
            'Comm.Channel.Start': self.comm_channel_start,
            'Comm.Channel.End': self.comm_channel_end,
            'Room.Info': self.room,
            'Char.Items.List': self.items,
            'Char.Items.Add': self.add_item,
            'Char.Items.Remove': self.remove_item,
            #'Char.Items.Update': self.update_item,
            'Room.WrongDir': self.wrong_dir
        }

        # time when ping started
        self.ping_start = None
        # if we are waiting for a ping
        self.pinging = False

    def map(self, cmd, args=None):
        """ Map GMCP commands to assigned methods """

        if cmd not in self.command_map:
            self.unhandled_command(cmd, args)
            return

        if args:
            self.command_map[cmd](args)
        else:
            self.command_map[cmd]()

    def unhandled_command(self, cmd, args):
        #pass
        print "GMCP - Unhandled Command: %s %s" % (cmd, args)

    # Char.Name
    def name(self, d):
        """ Char.Name is redundant information that we also get from
        Char.Status but it does make a handy signal for being logged in """

        player.name = d['name']
        player.fullname = d['fullname']

    # Char.Vitals
    def vitals(self, d):
        player.health.update(d['hp'], d['maxhp'])
        player.mana.update(d['mp'], d['maxmp'])
        player.endurance.update(d['ep'], d['maxep'])
        player.willpower.update(d['wp'], d['maxwp'])
        player.xp = float(d['nl'])

    # Char.Status
    def status(self, d):

        for k, v in d.items():
            if v == '(None)':
                v = None

            if k == 'lessons':
                player.lessons = int(v)
            elif k == 'city':
                player.city = v.lower() if v is not None else None
            elif k == 'xprank':
                player.xprank = int(v)
            elif k == 'name':
                player.name = v
            elif k == 'level':
                player.level = int(v)
            elif k == 'house':
                player.house = v
            elif k == 'age':
                player.age = int(v)
            elif k == 'specialisation':
                player.specialisation = v.lower() if v is not None else None
            elif k == 'class':
                player.combatclass = v.lower() if v is not None else None
            elif k == 'order':
                player.order = v
            elif k == 'race':
                player.race = v.lower()
            elif k == 'mayancrowns':
                player.mayancrowns = int(v)
            elif k == 'boundmayancrowns':
                player.boundmayancrowns = int(v)
            elif k == 'unboundcredits':
                player.credits = int(v)
            elif k == 'boundcredits':
                player.boundcredits = int(v)
            elif k == 'xp':
                player.xp = float(v[:-1])
            elif k == 'explorerrank':
                player.explorerrank = v

    # Char.StatusVars
    def statusvars(self, d):
        """ Not really sure what the point of StatusVars is... """
        pass

    # Char.Skills.Groups
    def skill_groups(self, d):
        """ Parses all skills into a dictionary of skill => skill_rank on a
        0 - 11 scale (11 being Transcendence) """

        result = {}

        for item in d:
            skill, rank = item.values()

            result[skill.lower()] = skill_ranks[rank]

        player.skill_groups = result

        # Get full listing of our skills
        for skill in player.skill_groups.keys():
            self.out.get_skills(group=skill)

    # Char.Skills.List
    def skill_list(self, d):
        """ Receives a list of skills for a skill group """

        group = d['group']
        skills = d['list']

        player.skills[group] = [skill.lower() for skill in skills]

    # Room.Info
    def room(self, d):
        player.room.id = int(d['num'])
        player.room.name = d['name']
        player.room.area = d['area']
        player.room.exits = d['exits']
        player.room.environment = d['environment']
        if d['coords'] == '':
            player.room.coords = None
        else:
            player.room.coords = [int(c) for c in d['coords'].split(',')]
        player.room.details = d['details']
        player.room.map = d['map']

    # Char.Items.List
    def items(self, d):

        items = {}

        if d['location'] == 'room':
            for item in d['items']:
                items[int(item['id'])] = item['name']

            player.room.items = items
            gmcp_signals.room_items.send_robust(self, items=player.room.items)

        elif d['location'] == 'inv':
            player.inv.clear()
            for item in d['items']:
                attrib = item['attrib'] if 'attrib' in item else None
                player.inv.add(int(item['id']), item['name'], attrib)

        else:
            print "Char.Items.List %s" % d

    # Char.Items.Add
    def add_item(self, d):

        num = int(d['item']['id'])
        name = d['item']['name']
        attrib = None

        if 'attrib' in d['item']:
            attrib = d['item']['attrib']

        if d['location'] == 'room':
            player.room.items[num] = name

        elif d['location'] == 'inv':
            player.inv.add(num, name, attrib)

        else:
            print "Char.Items.Add %s" % d

    # Char.Items.Remove
    def remove_item(self, d):

        item = int(d['item'])  # just be sure...

        if d['location'] == 'room':
            if item in player.room.items:
                del(player.room.items[item])
        elif d['location'] == 'inv':
            if item in player.room.items:
                del(player.inv[item])
        else:
            print "Char.Items.Remove %s" % d

    # Core.Goodbye
    def goodbye(self, d):
        gmcp_signals.goodbye.send_robust(self)

    # Core.Ping
    def ping(self):
        """ Recieves a Core.Ping and times it """

        latency = time() - self.ping_start
        self.pinging = False

        gmcp_signals.ping.send_robust(self, latency=latency)

    # Comm.Channel.List
    def comm_channels(self, d):
        player.comm_channels = d

    # Comm.Channel.Start
    def comm_channel_start(self, d):
        pass

    # Comm.Channel.End
    def comm_channel_end(self, d):
        pass

    # Room.WrongDir
    def wrong_dir(self, d):
        pass


class GMCP(object):

    def __init__(self, client):
        self.client = client
        self.receiver = GMCPReceiver()

        # I know, wtf right?
        self.receiver.out = self

        # Options for IRE's GMCP
        self.options = {
            'modules': ["Char 1", "Char.Vitals 1", "Char.Skills 1", \
            "Char.Items 1", "Room 1", "IRE.Rift 1", "Comm.Channel 1"],
            'ping': True,
            'ping_frequency': 5
        }

        # looping ping call
        self.ping_task = LoopingCall(self.ping)

    def call(self, data):
        """ Process incoming GMCP data """

        if ' ' in data:
            cmd, data = data.split(' ', 1)
            data = json_str_loads(data)
        else:
            cmd = data
            data = None

        self.receiver.map(cmd, data)

    def cmd(self, command, data=None):
        """ Send a GMCP command """

        self.write('%s %s' % (command, json.dumps(data)))

    def write(self, data):
        """ Write to server over GMCP """

        self.client.transport.write(IAC + SB + GMCPOPT + data + IAC + SE)

    # Char.Items.Contents
    def contents(self, container):
        """ Get the list of items located inside another item """

        self.cmd('Char.Items.Contents', container)

    # Char.Skills.Get
    def get_skills(self, group=None, name=None):
        """ Request skill information

          * if both group and name is provided, the server will send
            Char.Skills.Info for the specified skill
          * if group is provided but name is not, the server will send
            Char.Skills.List for that group
          * otherwise the server will send Char.Skills.Groups """

        params = {}

        if name:
            params['name'] = name

        if group:
            params['group'] = group

        if params:
            self.cmd('Char.Skills.Get', params)
        else:
            self.write('Char.Skills.Get')

    # Core.Hello
    def hello(self):
        """ GMCP Hello """

        self.cmd('Core.Hello', {'client': 'SAGE', 'version': version})
        self._start_pinging()

    # Core.Ping
    def ping(self):
        """ Request a ping from the server """

        if self.receiver.pinging:
            return

        self.receiver.pinging = True
        self.receiver.ping_start = time()
        self.cmd('Core.Ping')

    def _start_pinging(self):
        """ Start regular pinging """
        if self.options['ping'] == False:
            return

        self.ping_task.start(self.options['ping_frequency'])

    # Core.KeepAlive
    def keepalive(self):
        """ Causes the server to reset the timeout for the character """

        self.write('Core.KeepAlive')

    # Char.Login
    def login(self, name, password):

        self.cmd('Char.Login', {'name': name, 'password': password})

    # Char.Items.Inv
    def inv(self):
        """ Send the list of items in player's inventory """

        self.write('Char.Items.Inv')

    # IRE.Rift.Request
    def rift(self):
        """ Send the Rift contents using the IRE.Rift.List message """

        self.write('IRE.Rift.Request')

    # Core.Supports.Add
    def add_support(self, options):
        """ Add enabled modules in the same format of Core.Supports.Set """

        self.cmd('Core.Supports.Add', options)

    # Core.Supports.Remove
    def remove_support(self, options):
        """ Remove a list of modules """

        self.cmd('Core.Supports.Remove', options)

    # Core.Supports.Set
    def set_support(self, options=None):
        """ Set enabled modules """

        if options is None:
            options = self.options['modules']

        self.cmd('Core.Supports.Set', options)