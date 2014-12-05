from twisted.trial import unittest
from twisted.test import proto_helpers

import sys
sys.path.append('../')
from sage.net import TelnetClient, IAC, GA
from sage import player
import json

IAC = chr(255)
SB = chr(250)
SE = chr(240)
GMCP = chr(201)


class Achaea(object):
    """ Represents stuff coming from Achaea """

    def gmcp(self, command, data):
        return self._gmcp("%s %s" % (command, json.dumps(data)))

    def _gmcp(self, data):
        return IAC + SB + GMCP + data + IAC + SE


class TestingClient(TelnetClient):

    def __init__(self):
        self.results = []
        TelnetClient.__init__(self)

    def to_client(self, data):
        print "I GOT CALLED"
        """ Override to_client to work for tests """

        print data
        self.results.append(data)

    def write(self, data):
        data = data + "\nprompt"
        self.dataReceived(data + IAC + GA)


class TelnetTests(unittest.TestCase):

    def setUp(self):
        self.client = TestingClient()
        self.a = Achaea()

        self.client.write('Hello')

    def test_anything(self):
        pass

    """
    def test_gmcp_name(self):
        data = self.a.gmcp('Char.Name', {'name': 'Test', \
            'fullname': 'Full Name Test'})
        self.protocol.dataReceived(data)
        self.assertEqual(player.name, 'Test')
    """

if __name__ == '__main__':
    unittest.main()
