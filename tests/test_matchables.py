from twisted.trial import unittest
from sage import triggers, aliases, apps
from random import choice


def make_triggers(group, num=100, prefix='test_'):

    for x in range(num):

        mtype = choice(['exact', 'substring', 'regex', 'startswith',
            'endswith'])

        kwargs = {
            'name': '%s%s' % (prefix, x),
            'mtype': mtype,
            'pattern': 'Test pattern'
        }

        group.create(**kwargs)


class TestGet(unittest.TestCase):

    def setUp(self):
        self.group = triggers.create_group('test_get', app='sage')
        make_triggers(self.group)

        self.subgroup = self.group.create_group('subgroup')
        make_triggers(self.subgroup)

    def tearDown(self):
        triggers('test_get').destroy()

    def test_get_group(self):
        newgroup = triggers.get('test_get')
        self.assertEqual(newgroup.name, 'test_get')

    def test_get_trigger(self):
        trigger = triggers.get('test_get/test_30')
        self.assertEqual(trigger.name, 'test_30')

    def test_get_subgroup(self):
        new_subgroup = triggers.get('test_get/subgroup')
        self.assertEqual(new_subgroup.name, 'subgroup')

    def test_get_subtrigger(self):
        trigger = triggers.get('test_get/subgroup/test_42')
        self.assertEqual(trigger.name, 'test_42')

    def test_fail_get_trigger(self):
        trigger = triggers.get('test_get/fail_30')
        self.assertEqual(trigger, None)

    def test_fail_get_group(self):
        testgroup = self.group.get('subgroup2')
        self.assertEqual(testgroup, None)

    def test_relative_get_trigger(self):
        trigger = self.subgroup.get('test_42')
        self.assertEqual(trigger.name, 'test_42')

    def test_get_chaning(self):
        trigger = self.group.get('test_5')
        self.group.get('test_5').disable()
        self.assertEqual(trigger.enabled, False)

    def test_call_group_as_get(self):
        self.assertEqual('test_get', triggers('test_get').name)


class TestMatchables(unittest.TestCase):

    def test_create_group(self):

        group = triggers.create_group('test_create', app='sage')

        self.assertIn('test_create', triggers.groups)

        group.create_group('test_subgroup')

        self.assertIn('test_subgroup', group.groups)

    def test_create(self):

        group = triggers.create_group('test_create', app='sage')
        make_triggers(group)

        self.assertEqual(100, len(group.matchables))

    def test_group_disable(self):
        group = triggers.create_group('test', app='sage')

        make_triggers(group, 10, 'dis_')

        group.disable()

        self.assertEqual(self._trigger_in_enabled('dis_1'), False)

    def test_trigger_disable(self):
        group = triggers.create_group('test', app='sage')

        make_triggers(group, 10, 'dis_')

        group.disable('dis_2')

        self.assertEqual(self._trigger_in_enabled('dis_2'), False)

    def test_destroy(self):
        group = triggers.create_group('test', app='sage')

        make_triggers(group, 1)

        trigger = group['test_0']

        trigger.destroy()

        self.assertNotIn(trigger, triggers.enabled)

    def test_remove(self):

        group = triggers.create_group('test', app='sage')

        make_triggers(group, 1)

        trigger = group['test_0']

        group.remove('test_0')

        self.assertNotIn('test_0', group.matchables)
        self.assertNotIn(trigger, triggers.enabled)

    def _trigger_in_enabled(self, trigger_name):
        for enabled in triggers.enabled:
            if enabled.name == trigger_name:
                return True

        return False


class TestHooks(unittest.TestCase):

    def setUp(self):
        group = triggers.create_group('test_hooks', app='sage')
        make_triggers(group, 1)

    def tearDown(self):
        triggers('test_hooks').destroy()

    def test_hookbind_noparam(self):
        trigger = triggers.get('test_hooks/test_0')

        def test_callback(matchable):
            pass

        trigger.bind(test_callback)
        trigger.call_methods()

    def test_hookbind_param(self):
        trigger = triggers.get('test_hooks/test_0')

        def test_callback(matchable, param):
            self.assertEqual(True, param['test'])

        trigger.bind(test_callback, {'test': True})
        trigger.call_methods()

    def test_hook_multi(self):
        trigger = triggers.get('test_hooks/test_0')

        def test_callback_1(matchable, param):
            self.assertEqual(True, param['test'])

        def test_callback_2(matchable, param):
            self.assertEqual(False, param['an_arg'])

        trigger.bind(test_callback_1, {'test': True})
        trigger.bind(test_callback_2, {'an_arg': False})

        trigger.call_methods()



class TestApps(unittest.TestCase):

    def setUp(self):
        apps.load('dummyapp')

    def tearDown(self):
        apps.unload('dummyapp')

    def test_created_group(self):
        self.assertIn('dummyapp', apps)
        self.assertIn('dummy', triggers.groups)
        self.assertEqual('dummyapp', triggers.groups['dummy'].app)
        self.assertIn('dummyapp', apps.groups)
        group = triggers.groups['dummy']
        self.assertIn(group, apps.groups['dummyapp'])

    def test_subgroup_ownership(self):
        group = triggers.get('dummy/subdummy')
        self.assertEqual('dummyapp', group.app)

    def test_parent_removal(self):
        triggers.get('dummy').destroy()
        self.assertNotIn('dummy', triggers.groups)
        self.assertEqual(len(triggers.enabled), 0)
        self.assertEqual(len(apps.groups['dummyapp']), 0)

    def test_child_removal(self):
        triggers.get('dummy/subdummy').destroy()
        self.assertIn('dummy', triggers.groups)
        self.assertEqual(len(apps.groups['dummyapp']), 1)


class TestGroups(unittest.TestCase):

    def setUp(self):
        self.l1 = triggers.create_group('level_1', app='sage')
        self.l2 = self.l1.create_group('level_2', enabled=False)
        self.l3 = self.l2.create_group('level_3')

    def test_subgroup_disable_chain(self):
        self.assertFalse(self.l2.enabled)
        self.l1.disable()
        self.assertFalse(self.l1.enabled)
        self.assertTrue(self.l3.enabled)

if __name__ == '__main__':
    unittest.main()
