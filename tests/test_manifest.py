from twisted.trial import unittest
from sage import manifest, apps

class ManifestTests(unittest.TestCase):

    def test_load_json(self):
        manifest.load('../tests/apps_manifest.json')
        self.assertEqual(len(manifest.apps), 2)

    def test_load_apps(self):
        manifest.load('../tests/apps_manifest.json')
        apps.load_manifest()
        self.assertIn('dummyapp', list(apps.keys()))