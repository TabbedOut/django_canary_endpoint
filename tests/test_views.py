from functools import wraps
import unittest

from django.test import SimpleTestCase, RequestFactory

from canary_endpoint import views
from canary_endpoint.prometheus import PROMETHEUS_AVAILABLE
from canary_endpoint.views import should_output_prometheus


# To find this header, tell Prometheus to collect data from a requestb.in
ACCEPTS = """
application/vnd.google.protobuf;proto=io.prometheus.client.MetricFamily;encoding=delimited;q=0.7,text/plain;version=0.0.4;q=0.3,application/json;schema="prometheus/telemetry";version=0.0.2;q=0.2,*/*;q=0.1
""".strip()


def pretend_prometheus_is_not_installed(func):
    @wraps(func)
    def inner(*args, **kwargs):
        _original = views.PROMETHEUS_AVAILABLE
        views.PROMETHEUS_AVAILABLE = False
        output = func(*args, **kwargs)
        views.PROMETHEUS_AVAILABLE = _original
        return output
    return inner


class ShouldOutputPrometheusTestCase(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_normal_request_defaults_to_false(self):
        request = self.factory.get('/foo/')
        self.assertFalse(should_output_prometheus(request))

    @unittest.skipIf(not PROMETHEUS_AVAILABLE, 'requires prometheus client')
    def test_can_be_forced_with_get_param(self):
        request = self.factory.get('/foo/?format=prometheus')
        self.assertTrue(should_output_prometheus(request))

    @unittest.skipIf(not PROMETHEUS_AVAILABLE, 'requires prometheus client')
    def test_accept_header_triggers_prometheus_format(self):
        request = self.factory.get('/foo/', HTTP_ACCEPT=ACCEPTS)
        self.assertTrue(should_output_prometheus(request))

    @pretend_prometheus_is_not_installed
    def test_cannot_be_forced_with_get_param(self):
        request = self.factory.get('/foo/?format=prometheus')
        self.assertFalse(should_output_prometheus(request))

    @pretend_prometheus_is_not_installed
    def test_accept_header_doesnt_trigger_prometheus_format(self):
        request = self.factory.get('/foo/', HTTP_ACCEPT=ACCEPTS)
        self.assertFalse(should_output_prometheus(request))
