from __future__ import unicode_literals

import re

from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
import requests.exceptions
import responses

from canary_endpoint.resources.search import ElasticSearch


class ElasticSearchTestCase(TestCase):
    resource = ElasticSearch('dummy_name', 'dummy_host')

    def test_normalize_host_works(self):
        real_connection = 'http://example.com:9200'
        wannabe_connections = (
            'example.com',
            'http://example.com',
            'http://example.com:9200',
            'http://example.com:9200/',
            'http://example.com:9200/donut',
        )
        for attempt in wannabe_connections:
            self.assertEqual(self.resource._normalize_host(attempt),
                             real_connection)

    def test_normalize_host_finds_custom_port(self):
        self.assertEqual(self.resource._normalize_host('elastic:999'),
                         'http://elastic:999')

    def test_normalize_host_finds_scheme(self):
        self.assertEqual(self.resource._normalize_host('https://elastic'),
                         'https://elastic:9200')

    def test_normalize_host_raises_on_bad_input(self):
        with self.assertRaises(ImproperlyConfigured):
            self.resource._normalize_host('')

    @responses.activate
    def test_check_catches_connection_problems(self):
        # Try to actually hit http://dummy_host. It's bad practice to do live
        # requests in tests, but this is fast and doesn't actually go outside
        # the host (aka this test will work on an airplane).
        response = self.resource.check()
        self.assertEqual(response['status'], 'error')
        self.assertIn('Connection refused', response['error'])

        # Now mock
        es_urls = re.compile(r'https?://dummy_host.*')
        responses.add(
            responses.GET, es_urls,
            body=requests.exceptions.ConnectionError('Connection refused'))

        response = self.resource.check()
        self.assertEqual(response['status'], 'error')
        self.assertIn('Connection refused', response['error'])

        responses.reset()
        responses.add(
            responses.GET, es_urls,
            body=requests.exceptions.HTTPError('derp'))
        response = self.resource.check()
        self.assertEqual(response['status'], 'error')
        self.assertIn('derp', response['error'])
