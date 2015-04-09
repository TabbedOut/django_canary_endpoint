from __future__ import unicode_literals

import re

from django.core.exceptions import ImproperlyConfigured
import requests

from ..constants import OK, WARNING, ERROR
from ..decorators import timed
from . import Resource


STATUS_MAPPING = {
    'green': OK,
    'yellow': WARNING,
    'red': ERROR,
}


class ElasticSearch(Resource):
    """
    Checks the status of an ElasticSearch cluster.

    ElasticSearch has its own health status we can wrap. See:
    http://www.elastic.co/guide/en/elasticsearch/reference/1.x/cluster-health.html

    :param name: The name of this canary.
    :param host: The ElasticSearch host to connect to.
    :param timeout: The maximum time (in seconds) to wait for a response.
    """
    def __init__(self, name, host, timeout=30.0, **kwargs):
        self.host = self._normalize_host(host)
        self.timeout = timeout
        kwargs.setdefault('description', self.host)
        super(ElasticSearch, self).__init__(name, **kwargs)

    @timed(threshold=0.1)
    def check(self):
        result = super(ElasticSearch, self).check()
        try:
            health_url = '{}/_cluster/health'.format(self.host)
            response = requests.get(health_url, timeout=self.timeout)
        except requests.exceptions.RequestException as e:
            return dict(result, status=ERROR, error=str(e))
        data = response.json()
        # WISHLIST there's more data that might be worth passing through
        # besides just the status, see the link in the docstring
        status = STATUS_MAPPING[data['status']]
        return dict(result, status=status)

    def _normalize_host(self, host):
        """
        Accept multiple ways to specify the ElasticSearch host.

        This way, projects can store the connection string in the format most
        convenient in the project.
        """
        # urlparse won't work here because it interprets the host as the path
        matches = re.match('(?P<scheme>https?:)?(//)?(?P<host>[^:]+)'
                           '(:(?P<port>\d+))?.*', host)
        if not matches:
            raise ImproperlyConfigured('{} does not look like an ElasticSearch'
                                       ' connection string'.format(host))
        data = matches.groupdict()
        return '{}//{}:{}'.format(
            data['scheme'] or 'http:',
            data['host'],
            data['port'] or '9200',
        )
