from __future__ import absolute_import

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django_rq import queues
from redis import RedisError
from rq import Worker

from ..constants import OK, WARNING, ERROR
from ..decorators import timed
from . import Resource


class DjangoRQ(Resource):
    """
    Checks the status of any RQ queues configured by Django.

    All queues must share the same Redis connection.
    """

    def __init__(
            self,
            name='rq',
            description='Django RQ',
            queues=None,
            **kwargs):
        self.queue_names = queues or settings.RQ_QUEUES.keys()
        super(DjangoRQ, self).__init__(
            name=name,
            description=description,
            **kwargs
        )

    @timed
    def check(self):
        result = super(DjangoRQ, self).check()
        status = result.get('status', OK)
        try:
            result['queues'] = {}
            for queue in self.get_queues():
                queue_result = self.check_queue(queue)
                status = self.get_status_for_queue_result(status, queue_result)
                result['queues'][queue.name] = queue_result

            return dict(result, status=status)
        except (ImproperlyConfigured, RedisError) as e:
            return dict(result, status=ERROR, error=str(e))

    def get_queues(self):
        return queues.get_queues(*self.queue_names)

    def check_queue(self, queue):
        n_jobs = queue.count
        n_workers = self.count_queue_workers(queue)
        url = self.get_queue_url(queue)
        return {'n_jobs': n_jobs, 'n_workers': n_workers, 'url': url}

    def get_queue_url(self, queue):
        configuration = queue.connection.connection_pool.connection_kwargs
        return 'redis://{host}:{port}/{db}/'.format(**configuration)

    def count_queue_workers(self, queue):
        connection = queues.get_connection(queue.name)
        workers = Worker.all(connection=connection)
        return len([_ for _ in workers if queue in _.queues])

    def get_status_for_queue_result(self, status, result):
        if status == OK and result['n_jobs'] > result['n_workers']:
            return WARNING
        else:
            return status
