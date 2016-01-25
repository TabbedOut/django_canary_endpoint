import json

from requests.exceptions import HTTPError

from . import MockTestCase


class EndpointTestCase(MockTestCase):
    # maxDiff = None  # DEBUG uncomment for untruncated assertion output

    def setUp(self):
        super(EndpointTestCase, self).setUp()
        self.mock_ok_service({'status': 'ok'})
        self.mock_ok_elasticsearch()
        self.mock_queue('default')
        self.expected_data = self.get_fixture('ok.json')

    def assert_content(self, content, status='ok', **overrides):
        data = json.loads(content)
        expected_data = self.expected_data.copy()
        expected_data['status'] = status
        expected_data['resources'].update(**overrides)
        # print data; print '*' * 80; print expected_data  # DEBUG
        self.assertEqual(data, expected_data)

    # Assertions
    ############

    def test_status_endpoint_returns_200_on_success(self):
        response = self.client.get('/_status/')
        self.assertEqual(response.status_code, 200)
        # print response.content  # DEBUG uncomment when updating ok.json
        self.assert_content(response.content)

    def test_status_endpoint_returns_200_with_warning_on_timeout(self):
        self.mock_duration(step=1.0)

        response = self.client.get('/_status/')
        self.assertEqual(response.status_code, 200)

        n_resources = len(self.expected_data['resources'])
        self.expected_data['latency'] = 1.0 * n_resources
        for resource in self.expected_data['resources'].values():
            resource.update(status='warning', latency=1.0)

        self.assert_content(response.content, status='warning')

    def test_status_endpoint_returns_503_on_http_error(self):
        # redo requests mocks
        self.reset_responses()
        self.mock_ok_elasticsearch()
        self.mock_error_service({'status': 'warning'})

        response = self.client.get('/_status/')
        self.assertEqual(response.status_code, 503)

        resources = self.expected_data['resources']
        foo_error = u'500 Server Error: None for url: http://service/'
        foo_data = dict(resources['foo'], status=u'error', error=foo_error)
        bar_error = u'500 Server Error: None for url: http://service/_status/'
        bar_data = dict(resources['bar'], status=u'error', error=bar_error)
        bar_data['result']['status'] = u'warning'
        overrides = {'foo': foo_data, 'bar': bar_data}
        self.assert_content(response.content, status=u'error', **overrides)

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

    def test_status_endpoint_returns_503_on_elasticsearch_error(self):
        # redo requests mocks
        self.reset_responses()
        self.mock_ok_service({'status': 'ok'})
        self.mock_error_elasticsearch(body=HTTPError('Some ES error'))

        response = self.client.get('/_status/')
        self.assertEqual(response.status_code, 503)

        es_data = self.expected_data['resources']['es_resource'].copy()
        expected_data = dict(es_data, status='error', error='Some ES error')
        overrides = {'es_resource': expected_data}
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
