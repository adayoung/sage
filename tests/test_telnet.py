from twisted.trial import unittest
import sys
sys.path.append('../')
from sage.net import TelnetClient, IAC, GA, ISageProxyReceiver
from sage import player
import json

IAC = chr(255)
SB = chr(250)
SE = chr(240)
GMCP = chr(201)


class Achaea(object):
    """ Represents stuff coming from Achaea """

    def __init__(self, client):
        self.client = client

    def gmcp(self, command, data):
        self._gmcp("%s %s" % (command, json.dumps(data)))

    def _gmcp(self, data):
        self._write(IAC + SB + GMCP + data + IAC + SE)

    def _write(self, data):
        self.client.write_raw(data)


class TestReceiver(ISageProxyReceiver):

    def __init__(self):
        super(TestReceiver, self).__init__()
        self.lines = []
        self.prompt = ''

    def input(self, lines, prompt):
        self.lines = lines
        self.prompt = prompt

    def reset(self):
        self.lines = []
        self.prompt = ''


class TestClient(TelnetClient):

    def __init__(self):
        self.results = []
        TelnetClient.__init__(self)

    def write_simple(self, data):
        data = data + "\nprompt"
        self.dataReceived(data + IAC + GA)

    def write_raw(self, data):
        self.dataReceived(data)


class TelnetTests(unittest.TestCase):

    def setUp(self):
        self.client = TestClient()
        self.receiver = TestReceiver()
        self.client.addReceiver(self.receiver)
        self.a = Achaea(self.client)

    def test_write_simple(self):
        self.client.write_simple('test')
        self.assertIn('test', self.receiver.lines)

    def test_write_raw(self):
        self.client.write_raw('test\nprompt' + IAC + GA)
        self.assertIn('test', self.receiver.lines)
        self.assertEqual('prompt', self.receiver.prompt)

    """
    def test_gmcp_name(self):
        self.a.gmcp('Char.Name', {'name': 'Test', 'fullname': 'Full Name Test'})
        self.assertEqual(player.name, 'Test')
    """

if __name__ == '__main__':
    unittest.main()
