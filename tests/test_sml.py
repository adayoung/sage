from twisted.trial import unittest
from sage import sml, triggers
import os

path = os.getcwd()
if 'tests' not in path:
    path = "%s/tests/sml/" % path
else:
    path = "%s/sml/" % path


class LoadSML(unittest.TestCase):

    def setUp(self):
        self.group = triggers.create_group('sml_parent', app='sage')
        sml.register(self.sml_method_2)
        sml.register(self.sml_method_1)

    def tearDown(self):
        self.group.destroy()
        sml.methods.clear()

    def test_creation(self):
        sml.load_file(path + 'test1.yaml', self.group)

        self.assertIn('test_1', self.group.groups)
        self.assertIn('test_2', self.group.groups)

        self.assertIn('trigger_1', self.group.groups['test_1'].matchables)
        self.assertIn('trigger_2', self.group.groups['test_2'].matchables)

    def test_load(self):
        sml.load_file(path + 'test1.yaml', self.group)

    def test_register(self):
        self.assertIn('sml_method_1', sml.methods)

    def sml_method_1(self, *args):
        pass

    def sml_method_2(self, *args):
        pass
