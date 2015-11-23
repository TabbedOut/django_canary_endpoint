from subprocess import CalledProcessError
import json
import re

from mock import patch, Mock
import responses


class MockMixin(object):
    def patch(self):
        pass

    def unpatch(self):
        pass


class MockTestCaseMixin(MockMixin):
    def setUp(self):
        super(MockTestCaseMixin, self).setUp()
        self.patch()

    def tearDown(self):
        self.unpatch()
        super(MockTestCaseMixin, self).tearDown()


class MockTimeMixin(MockMixin):
    def patch(self):
        super(MockTimeMixin, self).patch()
        self.time_patcher = patch('canary_endpoint.decorators.time')
        self.mock_time_module = self.time_patcher.start()
        self.mock_duration()

    def unpatch(self):
        self.time_patcher.stop()
        super(MockTimeMixin, self).unpatch()

    def mock_duration(self, initial=0.0, step=0.0):
        timings = self.get_timings(initial=initial, step=step)
        self.mock_time_module.time.side_effect = timings

    def get_timings(self, initial=0.0, step=0.0):
        # Yield an initial time for the canary
        yield initial
        while True:
            # Yield times for each resource
            yield initial
            yield initial + step
            initial = initial + step


class MockDatabaseMixin(MockMixin):
    database = 'default'

    def patch(self):
        super(MockDatabaseMixin, self).patch()
        execute = 'django.db.backends.util.CursorDebugWrapper.execute'
        self.cursor_patcher = patch(execute, autospec=True)
        self.mock_execute = self.cursor_patcher.start()

    def unpatch(self):
        self.cursor_patcher.stop()
        super(MockDatabaseMixin, self).unpatch()

    def mock_database_error(self, message=None):
        from django.db import DatabaseError
        self.mock_execute.side_effect = DatabaseError(message)


class MockRequestsMixin(object):
    """If you need to mock `requests` GET requests in your Canary tests."""
    elasticsearch_urls = re.compile(r'https?://elasticsearch.*')
    service_urls = re.compile(r'http://service.*')

    def setUp(self):
        super(MockRequestsMixin, self).setUp()
        responses.start()

    def tearDown(self):
        responses.stop()
        responses.reset()
        super(MockRequestsMixin, self).tearDown()

    def reset_responses(self):
        responses.reset()

    def mock_ok_service(self, data=None):
        self.mock_service_response(status_code=200, data=data)

    def mock_error_service(self, data=None):
        self.mock_service_response(status_code=500, data=data)

    def mock_service_response(self, status_code, data=None):
        responses.add(
            responses.GET, self.service_urls,
            body=json.dumps(data) if data else '',
            status=status_code,
            content_type='application/json')

    def mock_ok_elasticsearch(self):
        responses.add(
            responses.GET, self.elasticsearch_urls,
            body='{"status": "green"}',
            content_type='application/json')

    def mock_error_elasticsearch(self, body='{"status": "red"}'):
        responses.add(
            responses.GET, self.elasticsearch_urls,
            body=body,
            content_type='application/json')


class MockRQMixin(MockMixin):

    rq_default_configuration = {'host': 'localhost', 'port': '6379', 'db': 0}

    def patch(self):
        super(MockRQMixin, self).patch()
        self.get_queue_patcher = patch(
            'canary_endpoint.resources.rq.queues.get_queue',
            autospec=True
        )
        self.worker_patcher = patch('canary_endpoint.resources.rq.Worker')
        self.mock_get_queue = self.get_queue_patcher.start()
        self.mock_get_queue.side_effect = self.get_mock_queue
        self.mock_worker = self.worker_patcher.start()
        self.rq_queues = {}

    def unpatch(self):
        self.mock_get_queue = self.get_queue_patcher.stop()
        self.mock_worker = self.worker_patcher.stop()
        super(MockRQMixin, self).unpatch()

    def mock_queue(self, name, configuration=None, count=0):
        mock_queue = Mock()
        mock_queue.name = name
        mock_queue.count = count
        configuration = configuration or self.rq_default_configuration
        mock_queue.connection.connection_pool.connection_kwargs = configuration
        self.rq_queues[name] = mock_queue

    def get_mock_queue(self, name, **kwargs):
        return self.rq_queues[name]

    def mock_redis_error(self, message=None):
        from redis.exceptions import RedisError
        self.mock_get_queue.side_effect = RedisError(message)


class MockGitMixin(MockMixin):
    def patch(self):
        super(MockGitMixin, self).patch()
        self.git_output_patcher = patch(
            'canary_endpoint.resources.projects'
            '.subprocess.check_output'
        )
        self.mock_git_output = self.git_output_patcher.start()

    def unpatch(self):
        self.mock_git_output = self.git_output_patcher.stop()

    def mock_git_revision(self, revision):
        self.mock_git_output.return_value = revision

    def mock_git_error(self, command='foo', code=1, output=None):
        output = output or "'{}' is not a git command.".format(command)
        exception = CalledProcessError(code, command, output)
        self.mock_git_output.side_effect = exception

    def mock_git_not_found(self, message='command not found: git'):
        self.mock_git_output.side_effect = OSError(message)
