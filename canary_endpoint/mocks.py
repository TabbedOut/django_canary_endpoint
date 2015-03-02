from StringIO import StringIO
from subprocess import CalledProcessError
import json

from mock import patch, Mock
from requests import Response


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


class MockServiceMixin(MockMixin):
    def patch(self):
        super(MockServiceMixin, self).patch()
        self.get_patcher = patch('requests.get')
        self.mock_get = self.get_patcher.start()

    def unpatch(self):
        self.get_patcher.stop()
        super(MockServiceMixin, self).unpatch()

    def mock_ok_response(self, data=None):
        return self.mock_response(status_code=200, data=data)

    def mock_error_response(self, data=None):
        return self.mock_response(status_code=500, data=data)

    def mock_response(self, status_code, data=None):
        response = Response()
        content = json.dumps(data) if data else ''
        response.raw = StringIO(content)
        response.status_code = status_code
        self.mock_get.return_value = Mock(wraps=response)


class MockRQMixin(MockMixin):
    default_configuration = {'host': 'localhost', 'port': '6379', 'db': 0}

    def patch(self):
        super(MockRQMixin, self).patch()
        self.queues_patcher = patch('canary_endpoint.resources.rq.queues')
        self.worker_patcher = patch('canary_endpoint.resources.rq.Worker')
        self.mock_queues = self.queues_patcher.start()
        self.mock_worker = self.worker_patcher.start()
        self.mock_queues.get_queues.return_value = []

    def unpatch(self):
        self.mock_queues = self.queues_patcher.stop()
        self.mock_worker = self.worker_patcher.stop()
        super(MockRQMixin, self).unpatch()

    def mock_queue(self, name, configuration=None, count=0):
        mock_queue = Mock()
        mock_queue.name = name
        mock_queue.count = count
        configuration = configuration or self.default_configuration
        mock_queue.connection.connection_pool.connection_kwargs = configuration
        self.mock_queues.get_queues.return_value = [mock_queue]

    def mock_redis_error(self, message=None):
        from redis.exceptions import RedisError
        self.mock_queues.get_queues.side_effect = RedisError(message)


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
