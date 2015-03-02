import os

from unittest import TestCase

from canary_endpoint import version


class VersionTestCase(TestCase):
    root_path = os.path.join(os.path.dirname(__file__), '..')
    package_path = os.path.join(root_path, 'canary_endpoint')

    def test_version_can_be_read_from_version_file(self):
        namespace = {}
        version_path = os.path.join(self.package_path, 'version.py')
        exec(open(version_path).read(), namespace)
        self.assertEqual(version.__version__, namespace['__version__'])
