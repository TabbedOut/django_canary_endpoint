import json
import os

from django.test import TestCase

from canary_endpoint.mocks import (
    MockTestCaseMixin,
    MockTimeMixin,
    MockDatabaseMixin,
    MockServiceMixin,
    MockRQMixin
)

try:
    # If the app cache is not explicitly loaded before running the tests,
    # errors will be squashed by template errors in Django 1.7 and later.
    import django
    django.setup()
except AttributeError:
    pass


class MockTestCase(MockTimeMixin,
                   MockDatabaseMixin,
                   MockServiceMixin,
                   MockRQMixin,
                   MockTestCaseMixin,
                   TestCase):
    """
    Test case that mocks all supported resources.
    """
    fixtures_path = os.path.join(os.path.dirname(__file__), 'fixtures')

    def get_fixture(self, name):
        path = os.path.join(self.fixtures_path, name)
        with open(path) as stream:
            return json.load(stream)
