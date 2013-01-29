from twisted.trial import unittest
from sage import triggers, aliases
from random import choice


class TestMatchables(unittest.TestCase):

    def test_create(self):

        group = triggers.create_group('test_create')
        self._make_triggers(group)

        self.assertEqual(100, len(group.matchables))

    def test_get_group(self):

        group = triggers.create_group('test_get')
        self._make_triggers(group)

        newgroup = triggers.get('test_get')

        self.assertEqual(newgroup.name, 'test_get')

    def test_get_trigger(self):

        group = triggers.create_group('test_get')
        self._make_triggers(group)

        trigger = triggers.get('test_get/test_30')

        self.assertEqual(trigger.name, 'test_30')

    def test_get_subgroup(self):

        group = triggers.create_group('test_get')

        subgroup = group.create_group('test_get_subgroup')

        new_subgroup = triggers.get('test_get/test_get_subgroup')

        self.assertEqual(new_subgroup.name, 'test_get_subgroup')

    def test_get_subtrigger(self):

        group = triggers.create_group('test_get')

        subgroup = group.create_group('test_get_subgroup')

        self._make_triggers(subgroup)

        trigger = triggers.get('test_get/test_get_subgroup/test_42')

        self.assertEqual(trigger.name, 'test_42')

    def test_fail_get_trigger(self):
        group = triggers.create_group('test_get')
        self._make_triggers(group)

        trigger = triggers.get('test_get/fail_30')

        self.assertEqual(trigger, None)

    def test_relative_get_trigger(self):
        group = triggers.create_group('test_get')

        subgroup = group.create_group('test_get_subgroup')

        self._make_triggers(subgroup)

        trigger = subgroup.get('test_42')

        self.assertEqual(trigger.name, 'test_42')

    def test_get_single_chaning(self):
        group = triggers.create_group('test_get')

        self._make_triggers(group)

        trigger = group.get('test_5')

        group.get('test_5').disable()

        self.assertEqual(trigger.enabled, False)

    def _make_triggers(self, group):

        for x in range(100):

            mtype = choice(['exact', 'substring', 'regex', 'startswith',
                'endswith'])

            kwargs = {
                'name': 'test_%s' % x,
                'mtype': mtype,
                'pattern': 'Test pattern'
            }

            group.create(**kwargs)
