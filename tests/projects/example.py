import os
import sys


# Project
#########

DEBUG = True

ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.append(ROOT)

VERSION = '1.2.3'

ROOT_URLCONF = 'tests.projects.example'

SECRET_KEY = 'foo'

ALLOWED_HOSTS = ['testserver']


# Databases
###########

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'USER': 'bar',
        'PASSWORD': 'baz',
    }
}


# RQ
####

RQ_QUEUES = {
    'default': {
        'URL': 'redis://foo',
        'DEFAULT_TIMEOUT': 360,
        'DB': 0,
    },
    'low': {
        'URL': 'redis://foo',
        'DEFAULT_TIMEOUT': 360,
        'DB': 0,
    },
    'high': {
        'URL': 'redis://foo',
        'DEFAULT_TIMEOUT': 360,
        'DB': 0,
    },
}


# Services
##########

HTTP_ENDPOINT = 'http://service/'

HTTP_ENDPOINT_WITH_CANARY = 'http://service/_status/'


# Canary
########

from canary_endpoint import Canary
from canary_endpoint.resources.databases import DjangoDatabase
from canary_endpoint.resources.search import ElasticSearch
from canary_endpoint.resources.services import Service, ServiceWithCanary

canary = Canary('example', root=ROOT, version=VERSION, resources=[
    DjangoDatabase(statements=['SELECT 1 FROM foo;']),
    ElasticSearch('es_resource', host='http://elasticsearch.example:9200'),
    Service('foo', url=HTTP_ENDPOINT),
    ServiceWithCanary('bar', url=HTTP_ENDPOINT_WITH_CANARY),
])


# URLs
######

from canary_endpoint.views import status
from django.conf.urls import patterns, url

urlpatterns = patterns('', url(r'^_status/$', status, {'canary': canary}))
