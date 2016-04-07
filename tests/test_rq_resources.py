from django.test import SimpleTestCase

from canary_endpoint.mocks import MockTestCaseMixin, MockRQMixin
from nose.plugins.attrib import attr


@attr('rq')
class DjangoRQTestCase(MockTestCaseMixin, MockRQMixin, SimpleTestCase):

    # Helpers
    #########

    def get_resource(self, queues):
        from canary_endpoint.resources.rq import DjangoRQ
        return DjangoRQ(queues=queues)

    # Assertions
    ############

    def test_warns_when_number_of_jobs_exceeds_number_of_workers(self):
        self.mock_queue('default', count=1)

        resource = self.get_resource(queues=['default'])
        result = resource.check()

        self.assertEqual(result['status'], 'warning')
        self.assertEqual(result['queues']['default'], {
            'n_jobs': 1,
            'n_workers': 0,
            'url': 'redis://localhost:6379/0/'
        })

    def test_checks_specified_queues(self):
        self.mock_queue('low', count=10)
        self.mock_queue('high', count=1)

        resource = self.get_resource(queues=['low', 'high'])
        result = resource.check()

        self.assertEqual(result['queues'], {
            'high': {
                'n_jobs': 1,
                'n_workers': 0,
                'url': 'redis://localhost:6379/0/'
            },
            'low': {
                'n_jobs': 10,
                'n_workers': 0,
                'url': 'redis://localhost:6379/0/'
            }
        })
