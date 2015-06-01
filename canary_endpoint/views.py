import json

from django.http import HttpResponse

from .constants import ERROR
from .prometheus import (
    PROMETHEUS_AVAILABLE,
    PROMETHEUS_SCHEMA,
    prometheus_response,
)


def should_output_prometheus(request):
    """
    Decide if Canary should output for Prometheus based on the request.

    The Python Prometheus client only supports the plain text format and not
    the protocol buffer format.

    Prometheus formats:
    http://prometheus.io/docs/instrumenting/exposition_formats/
    """
    if not PROMETHEUS_AVAILABLE:
        return False

    if request.GET.get('format') == 'prometheus':
        return True

    return PROMETHEUS_SCHEMA in request.META.get('HTTP_ACCEPT', '')


def json_response(canary, indent=2):
    """
    Return a 200 if the database is available, or a 503 otherwise.
    """
    result = canary.check()
    content = json.dumps(result, indent=indent)
    status = 503 if result['status'] == ERROR else 200
    return HttpResponse(
        content,
        status=status,
        content_type='application/json'
    )


def status(request, canary, **kwargs):
    if should_output_prometheus(request):
        return prometheus_response(canary, **kwargs)
    else:
        return json_response(canary, **kwargs)
