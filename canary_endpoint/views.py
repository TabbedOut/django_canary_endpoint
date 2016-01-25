import json

from django.http import HttpResponse

from .constants import ERROR


def status(request, canary, indent=2, **kwargs):
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
