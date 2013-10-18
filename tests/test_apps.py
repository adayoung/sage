from twisted.trial import unittest
from sage import apps, triggers
import sys


class AppTests(unittest.TestCase):

    def test_loading_in_syspath(self):

        apps.load('dummyapp')

        self.assertEquals(apps['dummyapp'].__name__, 'dummyapp.dummyapp')


    '''
    def test_loading_outside_syspath(self):
        pass'''

    def test_deleting(self):

        apps.load('dummyapp')

        apps.unload('dummyapp')

        self.assertFalse('dummyapp' in sys.modules)
        self.assertFalse('dummyapp' in apps)

if __name__ == '__main__':
    unittest.main()
