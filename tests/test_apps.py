from twisted.trial import unittest
from sage.app import Apps
import sys


class AppTests(unittest.TestCase):

    def test_loading_in_syspath(self):
        apps = Apps()

        apps.load('import_this')

        self.assertEquals(apps['import_this'].__name__, 'import_this')

    '''
    def test_loading_outside_syspath(self):
        pass'''

    def test_deleting(self):
        apps = Apps()
        apps.load('import_this')

        apps.unload('import_this')

        self.assertFalse('import_this' in sys.modules)
        self.assertFalse('import_this' in apps)
