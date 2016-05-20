import requests
try:
    from json.decoder import JSONDecodeError
except ImportError:
    class JSONDecodeError(ValueError):
        pass

from ..constants import OK, WARNING, ERROR
from ..decorators import timed
from . import Resource


class Service(Resource):
    """
    Checks the status of a service with an HTTP GET request.

    :param url: The URL of the service's status endpoint.
    :param headers: A dictionary of headers to include with the check.
    :param timeout: The number of seconds before an error is returned.
    """
    def __init__(self, name, url, headers=None, timeout=1.0, **kwargs):
        self.url = url
        self.timeout = timeout
        self.headers = headers
        super(Service, self).__init__(name=name, description=url, **kwargs)

    @timed
    def check(self):
        result = super(Service, self).check()
        try:
            self.last_response = None
            self.last_response = self.get_http_response()
            self.last_response.raise_for_status()
            return dict(result, status=OK)
        except requests.RequestException as e:
            return dict(result, status=ERROR, error=str(e))

    def get_http_response(self):
        return requests.get(
            self.url,
            headers=self.headers,
            timeout=self.timeout
        )


class ServiceWithCanary(Service):
    """
    Checks the status of a service with a canary endpoint.

    Reports an error if no JSON can be decoded from the remote canary.

    :param url: The URL of the service's canary endpoint.
    """
    def check(self):
        result = super(ServiceWithCanary, self).check()
        status = result.get('status')
        try:
            service_result = self.last_response.json()
            service_status = service_result.get('status')
            if status == OK and service_status == WARNING:
                status = WARNING
            elif service_status == ERROR:
                status = ERROR
            return dict(result, status=status, result=service_result)
        except JSONDecodeError:
            error_message = 'No JSON object could be decoded'
            return dict(result, status=ERROR, result=None, error=error_message)
        except (AttributeError, ValueError) as e:
            return dict(result, status=ERROR, result=None, error=str(e))
