# -*- coding: utf-8 -*-


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
    'ws_host': '127.0.0.1',
    'ws_debug': False,
    'wamp_realm': 'realm1',
    'backdoor': True,
    'backdoor_user': 'sage',
    'backdoor_password': 'sage',
    'backdoor_port': 5494,
    'backdoor_host': 'localhost',
    'auto_reload': True
})
