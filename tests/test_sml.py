from twisted.trial import unittest
from sage import sml, triggers
import os

path = os.getcwd()
path = "%s/sml/" % path


class LoadSML(unittest.TestCase):

    def test_creation(self):

        sml.methods.register(self.sml_method_2)

        sml.load_file(path + 'test1.yaml', triggers)

        self.assertIn('test_1', triggers.groups)
        self.assertIn('test_2', triggers.groups)

        self.assertIn('trigger_1', triggers.groups['test_1'].matchables)
        self.assertIn('trigger_2', triggers.groups['test_2'].matchables)

    def test_load(self):
        sml.load_file(path + 'test1.yaml', triggers)

    def test_register(self):
        sml.methods.register(self.sml_method_1)

        self.assertIn('sml_method_1', sml.methods)

    def sml_method_1(self):
        pass

    def sml_method_2(self, *args):
        pass
