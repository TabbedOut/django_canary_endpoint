[![Build Status](https://travis-ci.org/TabbedOut/django_canary_endpoint.svg?branch=master)](https://travis-ci.org/TabbedOut/django_canary_endpoint)

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

There are several ways to run the projects tests.  The recommended approach
is to run `tox`, becuase your testing environment will be properly set-up.

For a thorough multi-Django version testing use:

    $ tox

To list the configured environments:

    $ tox -l
    py27-django15
    py27-django16
    py27-django17
    py27-django18
    py27-djangorq
    py35-django18

You can execute a single test environment:

    $ tox -e py35-django18

If you manage your own environment, you can run the `make test` command
yourself.  It is recommened that you do this in a _virtualenv_.

    $ pip install -r requirements.txt     # Normally tox would install these
    $ pip install "django<1.9" django-rq  # Normally tox would install these
    $ make test
    $ open coverage/index.html

You can run a subset of tests by setting the `PACKAGES` variable:

    $ make PACKAGES="tests.test_endpoint tests.test_service_resources"

To run a single test:

    $ make PACKAGES=tests.test_endpoint:EndpointTestCase.test_status_endpoint_returns_200_on_success


### License

The MIT License (MIT)

Copyright 2016 ATX Innovations
