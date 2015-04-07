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
    'DEBUG': True,
    'gmcp_debug': False,
    'gmcp_ignore_channels': ['Core.Ping'],
    'port': 2003,
    'host': 'achaea.com',
    'telnet_proxy': True,
    'telnet_port': 5493,
    'ws_server': True,
    'ws_port': 9000,
    'ws_host': 'localhost',
    'ws_debug': False,
    'backdoor': True,
    'backdoor_user': 'sage',
    'backdoor_password': 'sage',
    'backdoor_port': 5494,
    'backdoor_host': 'localhost',
    'auto_reload': True,
    'exit_on_disconnect': False
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