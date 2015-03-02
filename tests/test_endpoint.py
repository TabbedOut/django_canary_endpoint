import json

from django import db
from django.http import HttpResponseServerError
from mock import patch

from . import MockTestCase


class EndpointTestCase(MockTestCase):
    def setUp(self):
        super(EndpointTestCase, self).setUp()
        self.mock_ok_response({'status': 'ok'})
        self.mock_queue('default')
        self.expected_data = self.get_fixture('ok.json')

    def assert_content(self, content, status='ok', **overrides):
        data = json.loads(content)
        expected_data = self.expected_data.copy()
        expected_data['status'] = status
        expected_data['resources'].update(**overrides)
        self.assertEqual(data, expected_data)

    # Assertions
    ############

    def test_status_endpoint_returns_200_on_success(self):
        response = self.client.get('/_status/')
        self.assertEqual(response.status_code, 200)
        self.assert_content(response.content)

    def test_status_endpoint_returns_200_with_warning_on_timeout(self):
        self.mock_duration(step=1.0)

        response = self.client.get('/_status/')
        self.assertEqual(response.status_code, 200)

        self.expected_data['latency'] = 4.0
        for resource in self.expected_data['resources'].values():
            resource.update(status='warning', latency=1.0)

        self.assert_content(response.content, status='warning')

    def test_status_endpoint_returns_503_on_http_error(self):
        self.mock_error_response({'status': 'warning'})

        response = self.client.get('/_status/')
        self.assertEqual(response.status_code, 503)

        resources = self.expected_data['resources']
        error = '500 Server Error: None'
        foo_data = dict(resources['foo'], status='error', error=error)
        bar_data = dict(resources['bar'], status='error', error=error)
        bar_data['result']['status'] = 'warning'
        overrides = {'foo': foo_data, 'bar': bar_data}
        self.assert_content(response.content, status='error', **overrides)

    def test_status_endpoint_returns_503_on_database_error(self):
        message = 'mock error'
        self.mock_database_error(message=message)

        response = self.client.get('/_status/')
        self.assertEqual(response.status_code, 503)

        database_data = self.expected_data['resources']['database'].copy()
        expected_data = dict(database_data, status='error', error=message)
        overrides = {'database': expected_data}
        self.assert_content(response.content, status='error', **overrides)

    def test_status_endpoint_returns_503_on_redis_error(self):
        message = 'mock error'
        self.mock_redis_error(message)

        response = self.client.get('/_status/')
        self.assertEqual(response.status_code, 503)

        rq_data = self.expected_data['resources']['rq'].copy()
        expected_data = dict(rq_data, status='error', error=message, queues={})
        overrides = {'rq': expected_data}
        self.assert_content(response.content, status='error', **overrides)

    def test_status_endpoint_returns_200_with_warning_on_rq_contention(self):
        self.mock_queue('default', count=10)

        response = self.client.get('/_status/')
        self.assertEqual(response.status_code, 200)

        rq_data = self.expected_data['resources']['rq'].copy()
        rq_data['queues']['default']['n_jobs'] = 10
        expected_data = dict(rq_data, status='warning')
        overrides = {'rq': expected_data}
        self.assert_content(response.content, status='warning', **overrides)

    @patch('canary_endpoint.views.HttpResponse')
    def test_status_endpoint_returns_500_on_error(self, mock_response):
        def on_500(*args, **kwargs):
            db._rollback_on_exception()
            return HttpResponseServerError()

        mock_response.side_effect = on_500
        response = self.client.get('/_status/')
        self.assertEqual(response.status_code, 500)
