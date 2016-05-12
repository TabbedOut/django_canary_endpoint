from django.test import SimpleTestCase

from canary_endpoint.constants import OK, WARNING, ERROR
from canary_endpoint.mocks import MockTestCaseMixin, MockRequestsMixin
from canary_endpoint.resources.services import ServiceWithCanary


class ServiceWithCanaryTestCase(MockRequestsMixin,
                                MockTestCaseMixin,
                                SimpleTestCase):
    service = ServiceWithCanary('foo', 'http://service')

    def test_ok_status_reports_ok_on_success(self):
        service_result = {'status': OK}
        self.mock_ok_service(service_result)
        result = self.service.check()
        self.assertEqual(result['status'], OK)
        self.assertEqual(result['result'], service_result)

    def test_ok_status_reports_error_on_error(self):
        service_result = {'status': OK}
        self.mock_error_service(service_result)
        result = self.service.check()
        self.assertEqual(result['status'], ERROR)
        self.assertEqual(result['result'], service_result)

    def test_warning_status_reports_warning_on_success(self):
        service_result = {'status': WARNING}
        self.mock_ok_service(service_result)
        result = self.service.check()
        self.assertEqual(result['status'], WARNING)
        self.assertEqual(result['result'], service_result)

    def test_error_result_reports_error_on_success(self):
        service_result = {'status': ERROR}
        self.mock_ok_service(service_result)
        result = self.service.check()
        self.assertEqual(result['status'], ERROR)
        self.assertEqual(result['result'], service_result)

    def test_invalid_json_reports_error_on_success(self):
        self.mock_ok_service(data=None)
        json_decoding_error_messages = {
            'python2_error': 'No JSON object could be decoded',
            'python3_error': 'Expecting value: line 1 column 1 (char 0)',
        }

        result = self.service.check()
        self.assertEqual(result['status'], ERROR)
        self.assertEqual(result['result'], None)
        self.assertIn(result['error'], json_decoding_error_messages.values())
