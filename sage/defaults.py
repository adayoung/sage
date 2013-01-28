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
    'port': 2003,
    'host': 'achaea.com',
    'proxy_port': 8007,
    'backdoor': True,
    'backdoor_user': 'sage',
    'backdoor_password': 'sage',
    'backdoor_port': 8006
})