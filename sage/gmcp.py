# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from twisted.internet.task import LoopingCall
from twisted.internet import reactor
import json
import sage
from sage.utils import json_str_loads
from sage.signals import gmcp as gmcp_signals
from sage.signals import net as net_signals
from time import time
import sage.player as player
from collections import deque

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
            'Comm.Channel.Text': self.comm_channel_text,
            'Comm.Channel.End': self.comm_channel_end,
            'Room.Info': self.room,
            'Room.Players': self.room_players,
            'Room.AddPlayer': self.room_addplayer,
            'Room.RemovePlayer': self.room_removeplayer,
            'Char.Items.List': self.items,
            'Char.Items.Add': self.add_item,
            'Char.Items.Remove': self.remove_item,
            'Char.Items.Update': self.update_item,
            'Room.WrongDir': self.wrong_dir,
            'IRE.Rift.List': self.rift_list,
            'IRE.Rift.Change': self.rift_change,
            'IRE.Time.Update': self.time_update,
            'IRE.Time.List': self.time_update
        }

        # time when ping started
        self.ping_start = None
        # if we are waiting for a ping
        self.pinging = False
        # container for skill groups left to query
        self._skill_groups = set()
        # skills that don't have subskills
        self._skill_exclude = set((
            'frost',
            'thermology',
            'constitution',
            'galvanism',
            'philosophy',
            'fitness',
            'avoidance',
            'antidotes'
        ))

        self.pings = deque(maxlen=20)
        self.lag_defer = None

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

        print("GMCP - Unhandled Command: %s %s" % (cmd, args))

    # Char.Name
    def name(self, d):
        """ Char.Name is redundant information that we also get from
        Char.Status but it does make a handy signal for being logged in """

        player.name = d['name']
        player.fullname = d['fullname']

        self.out.send_inits()  # treating this like a login

    # Char.Vitals
    def vitals(self, d):
        player.health.update(d['hp'], d['maxhp'])
        player.mana.update(d['mp'], d['maxmp'])
        player.endurance.update(d['ep'], d['maxep'])
        player.willpower.update(d['wp'], d['maxwp'])
        player.xp = float(d['nl'])

        if d['eq'] == '1':
            player.equilibrium.on()
        else:
            player.equilibrium.off()

        if d['bal'] == '1':
            player.balance.on()
        else:
            player.balance.off()

        gmcp_signals.vitals.send(
            health=player.health,
            max_health=player.health.max,
            mana=player.mana,
            max_mana=player.mana.max,
            endurance=player.endurance,
            max_endurance=player.endurance.max,
            willpower=player.willpower,
            max_willpower=player.willpower.max,
            xp=player.xp,
            bal=player.balance,
            eq=player.equilibrium
        )

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
                player.level = int(v.split(' ')[0])
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

        self._skill_groups = set(result.keys())
        self._skill_groups.difference_update(self._skill_exclude)

        # Get full listing of our skills
        for skill in player.skill_groups.keys():
            self.out.get_skills(group=skill)

    # Char.Skills.List
    def skill_list(self, d):
        """ Receives a list of skills for a skill group """

        group = d['group']
        skills = d['list']

        player.skills[group] = [skill.lower() for skill in skills]

        self._skill_groups.discard(group)

        if len(self._skill_groups) == 0:
            gmcp_signals.skills.send(skills=player.skills)

    # Room.Info
    def room(self, d):
        if int(d['num']) != player.room.id:
            player.room.last_id = player.room.id
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

        gmcp_signals.room.send(room=player.room)

    # Room.Players
    def room_players(self, d=None):
        player.room.players.clear()

        if d is not None:
            for p in d:
                if p['name'] != player.name:
                    player.room.players.add(p['name'])

        gmcp_signals.room_players.send(players=player.room.players)

    # Room.AddPlayer
    def room_addplayer(self, d):

        player.room.players.add(d['name'])
        gmcp_signals.room_add_player.send(player=d['name'])

    # Room.RemovePlayer
    def room_removeplayer(self, d):

        if d in player.room.players:
            player.room.players.remove(d)
        gmcp_signals.room_remove_player.send(player=d)

    # Char.Items.List
    def items(self, d):

        if d['location'] == 'room':
            player.room.items.clear()

            for item in d['items']:
                attrib = item['attrib'] if 'attrib' in item else None
                player.room.items.add(int(item['id']), item['name'], attrib)

            gmcp_signals.room_items.send(items=player.room.items)

        elif d['location'] == 'inv':
            player.inv.clear()
            for item in d['items']:
                attrib = item['attrib'] if 'attrib' in item else None
                player.inv.add(int(item['id']), item['name'], attrib)

            gmcp_signals.inv_items.send(items=player.inv.items)

        else:
            print("Char.Items.List %s" % d)

    # 'Char.Items.Update'
    def update_item(self, d):

        item = d['item']
        iid = int(item['id'])

        if d['location'] == 'inv':
            if iid in player.inv:
                if 'attrib' in item:
                    player.inv[iid].update_item(item['attrib'])
                else:
                    player.inv[iid].update_item(None)

                gmcp_signals.inv_update_item.send(item=player.inv[iid])

        elif d['location'] == 'room':
            if iid in player.room.items:
                player.room.items[iid].update_items(item['attrib'])
                gmcp_signals.room_update_item.send(item=player.room.items[iid])

    # Char.Items.Add
    def add_item(self, d):

        num = int(d['item']['id'])
        name = d['item']['name']
        attrib = None

        if 'attrib' in d['item']:
            attrib = d['item']['attrib']

        if d['location'] == 'room':
            item = player.room.items.add(num, name, attrib)
            gmcp_signals.room_add_item.send(item=item, container=player.room.items)

        elif d['location'] == 'inv':
            item = player.inv.add(num, name, attrib)
            gmcp_signals.inv_add_item.send(item=item, container=player.inv)

        elif d['location'].startswith('rep'):
            num = int(d['location'][3:])

            if num in player.inv:
                item = player.inv[num].items.add(num, name, attrib)
                gmcp_signals.inv_add_item.send(item=item, container=player.inv[num])

        else:
            print("Char.Items.Add %s" % d)

    # Char.Items.Remove
    def remove_item(self, d):

        item = int(d['item']['id'])

        if d['location'] == 'room':
            if item in player.room.items:
                del(player.room.items[item])
            gmcp_signals.room_remove_item.send(item=item, container=player.room.items)
        elif d['location'] == 'inv':
            if item in player.room.items:
                del(player.inv[item])
            gmcp_signals.inv_remove_item.send(item=item, container=player.inv)

        elif d['location'].startswith('rep'):
            num = int(d['location'][3:])

            if num in player.inv:
                gmcp_signals.room_remove_item.send(item=item, container=player.inv[num])
                del(player.inv[num])
        else:
           print("Char.Items.Remove %s" % d)

    # IRE.Rift.List
    def rift_list(self, d=None):

        player.rift.clear()

        if d is None:
            return

        for i in d:
            player.rift[i['name']] = int(i['amount'])

        gmcp_signals.rift.send(rift=player.rift)

    # IRE.Rift.Change
    def rift_change(self, d):
        player.rift[d['name']] = int(d['amount'])

        gmcp_signals.rift_change.send(name=d['name'], amount=int(d['amount']))

    # Core.Goodbye
    def goodbye(self, d):
        gmcp_signals.goodbye.send()

    # Core.Ping
    def ping(self):
        """ Recieves a Core.Ping and times it """

        if self.lag_defer is not None:
            self.lag_defer.cancel()

        self.lag_defer = None

        latency = time() - self.ping_start
        self.pinging = False

        self.pings.append(latency)

        sage.average_ping = sum(self.pings) / len(self.pings)

        gmcp_signals.ping.send(latency=latency)

    # Comm.Channel.List
    def comm_channels(self, d):
        player.comm_channels = d

    # Comm.Channel.Start
    def comm_channel_start(self, d):
        pass

    # Comm.Channel.End
    def comm_channel_end(self, d):
        pass

    # Comm.Channel.Text
    def comm_channel_text(self, d):
        gmcp_signals.comms.send(
            talker=d['talker'],
            channel=d['channel'],
            text=d['text']
        )

    # Room.WrongDir
    def wrong_dir(self, d):
        gmcp_signals.room_wrongdir.send()

    # IRE.Time.Update & IRE.Time.List
    def time_update(self, d):
        player.iretime = d
        gmcp_signals.iretime.send(time=d)


class GMCP(object):

    def __init__(self, client):
        self.client = client
        self.receiver = GMCPReceiver()

        # I know, wtf right?
        self.receiver.out = self

        # Options for IRE's GMCP
        self.options = {
            'modules': ["Char 1", "Char.Vitals 1", "Char.Skills 1", \
            "Char.Items 1", "Room 1", "IRE.Rift 1", "Comm.Channel 1", \
            "IRE.Time 1"],
            'ping': True,
            'ping_frequency': 1,
            'lag_factor': 5  # multiple by how much time over average ping is lagging
        }

        self.lagging = False

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

    # Comm.Channel.Players
    def comm_channel_players(self):
        """ Request a list of players in channels """

        self.cmd('Comm.Channel.Players')

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

        self.cmd('Core.Hello', {'client': 'SAGE', 'version': sage.__version__})
        self._start_pinging()

    # Core.Ping
    def ping(self):
        """ Request a ping from the server """

        if self.receiver.pinging:
            return

        self.receiver.pinging = True
        self.receiver.ping_start = time()
        self.cmd('Core.Ping')

        if player.connected:
            self.receiver.lag_defer = reactor.callLater(
                sage.average_ping * self.options['lag_factor'],
                self._lag_event
            )

    def _lag_event(self):
        self.receiver.lag_defer = None
        sage.lagging = True
        net_signals.lagging.send()

    def _start_pinging(self):
        """ Start regular pinging """
        if self.options['ping'] is False:
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

    # IRE.Time.Request
    def iretime(self):
        """ Ask for an update on current game time """

        self.write('IRE.Time.Request')

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

    def send_inits(self):
        """ Send messages when GMCP initiates """

        self.inv()
        self.rift()
        self.iretime()
