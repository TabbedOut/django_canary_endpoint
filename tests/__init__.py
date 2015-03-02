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
