import unittest

from django.test import RequestFactory
try:
    from prometheus_client import CONTENT_TYPE_LATEST
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
import mock

from . import MockTestCase
from .projects.example import canary
from canary_endpoint.views import prometheus_response


class PrometheusResponseTestCase(MockTestCase):
    def setUp(self):
        self.canary = canary
        self.checker_patch = mock.patch.object(canary, 'check')
        mock_check = self.checker_patch.start()
        mock_check.return_value = self.get_fixture('ok.json')
        self.factory = RequestFactory()
        super(PrometheusResponseTestCase, self).setUp()

    def tearDown(self):
        self.checker_patch.stop()

    @unittest.skipIf(not PROMETHEUS_AVAILABLE, 'requires prometheus client')
    def test_prometheus_response_output_looks_right(self):
        response = prometheus_response(self.canary)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], CONTENT_TYPE_LATEST)
        text = response.content
        self.assertIn('# HELP example latency_seconds', text)
        self.assertIn('# HELP example redis_queue_jobs', text)
        self.assertIn('# HELP example redis_queue_workers', text)
        self.assertIn('example{resource="database"} 0.0', text)
        self.assertIn('example{queue="default",resource="rq"} 0.0', text)
