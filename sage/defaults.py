# -*- coding: utf-8 -*-
import json


class Configuration(dict):
    """ Container for sage configuration """

    def __init__(self, contents=None):

        if contents:
            self.update(contents)

    def __call__(self, conf):
        self.update(conf)

    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        self[name] = value


defaults = Configuration({
    'DEBUG': False,
    'gmcp_debug': False,
    'gmcp_ignore_channels': ['Core.Ping'],
    'port': 2003,
    'host': 'achaea.com',
    'telnet_proxy': True,
    'telnet_port': 5493,
    # Set only if you want the default server. Otherwise construct your own!
    'ws_proxy': False,
    'ws_port': 5495,
    'ws_host': '127.0.0.1',
    'ws_realm': 'realm1',
    'ws_debug': False,
    'wamp_realm': 'realm1',
    'backdoor': True,
    'backdoor_user': 'sage',
    'backdoor_password': 'sage',
    'backdoor_port': 5494,
    'backdoor_host': 'localhost',
    'auto_reload': True,
    'exit_on_disconnect': False,
    # Path to private key (pub is derived from that), does not support passphrases
    'ssh_key_path': '~/.ssh/ssh_host_key'
})


class Manifest(object):

    apps = []

    def load(self, path):
        self.fp = open(path, 'rw')
        data = json.load(self.fp)
        self.apps = data['apps']

    def create_template(self, path):
        template = {
            'apps': []
        }

        with open(path, 'w') as f:
            json.dump(template, f)

    def save(self):
        data = {
            'apps': self.apps
        }

        json.dump(self.fp, data)
