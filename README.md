Django Canary Endpoint
======================

Provides [canary endpoints](http://byterot.blogspot.com/2014/11/health-endpoint-in-api-design-slippery-rest-api-design-canary-endpoint-hysterix-asp-net-web-api.html)
for common Django dependencies.


### Installation

    pip install django-canary-endpoint

If you use RQ you also need to install the `rq` extra:

    pip install django-canary-endpoint[rq]


### Quickstart

```
# Canary
########

from canary_endpoint import GitCanary
from canary_endpoint.resources.databases import DjangoDatabase
from canary_endpoint.resources.rq import DjangoRQ
from canary_endpoint.resources.services import Service, ServiceWithCanary

canary = GitCanary('example', root=ROOT, version=VERSION, resources=[
    DjangoDatabase(statements=['SELECT 1 FROM foo LIMIT 1']),
    DjangoRQ(),
    Service('foo', url=HTTP_ENDPOINT),
    ServiceWithCanary('bar', url=HTTP_ENDPOINT_WITH_CANARY),
])


# URLs
######

from canary_endpoint.views import status
from django.conf.urls import patterns, url

urlpatterns = patterns('', url(r'^_status/$', status, {'canary': canary}))
```

See the [example project](./tests/projects/example.py) for full configuration.

Also see the [example response data](./tests/fixtures/ok.json).


### Testing

    make test
    open coverage/index.html

For more thorough multi-Django version testing use:

    tox


### License

The MIT License (MIT)

Copyright 2016 ATX Innovations
