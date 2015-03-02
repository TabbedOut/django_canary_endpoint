from django.test import SimpleTestCase

from canary_endpoint.constants import OK, WARNING, ERROR
from canary_endpoint.mocks import MockTestCaseMixin, MockServiceMixin
from canary_endpoint.resources.services import ServiceWithCanary


class ServiceWithCanaryTestCase(MockServiceMixin,
                                MockTestCaseMixin,
                                SimpleTestCase):
    service = ServiceWithCanary('foo', '//foo')

    def test_ok_status_reports_ok_on_success(self):
        service_result = {'status': OK}
        self.mock_ok_response(service_result)
        result = self.service.check()
        self.assertEqual(result['status'], OK)
        self.assertEqual(result['result'], service_result)

    def test_ok_status_reports_error_on_error(self):
        service_result = {'status': OK}
        self.mock_error_response(service_result)
        result = self.service.check()
        self.assertEqual(result['status'], ERROR)
        self.assertEqual(result['result'], service_result)

    def test_warning_status_reports_warning_on_success(self):
        service_result = {'status': WARNING}
        self.mock_ok_response(service_result)
        result = self.service.check()
        self.assertEqual(result['status'], WARNING)
        self.assertEqual(result['result'], service_result)

    def test_error_result_reports_error_on_success(self):
        service_result = {'status': ERROR}
        self.mock_ok_response(service_result)
        result = self.service.check()
        self.assertEqual(result['status'], ERROR)
        self.assertEqual(result['result'], service_result)

    def test_invalid_json_reports_error_on_success(self):
        self.mock_ok_response(data=None)
        result = self.service.check()
        self.assertEqual(result['status'], ERROR)
        self.assertEqual(result['result'], None)
        self.assertEqual(result['error'], 'No JSON object could be decoded')
