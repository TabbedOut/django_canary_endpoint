from django.http import HttpResponse
try:
    from prometheus_client import CONTENT_TYPE_LATEST, Gauge, generate_latest
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False


PROMETHEUS_SCHEMA = 'schema="prometheus/telemetry"'


class PrometheusCanaryMixin(object):
    """
    Enable a Canary to give reports that can be consumed by Prometheus.

    The keys of the prometheus dict aren't that meaningful, so they're named
    after how to access the data from the canary dict.
    """
    def __init__(self, name, *args, **kwargs):
        if not PROMETHEUS_AVAILABLE:
            return
        self.prometheus = {
            'latency': Gauge(
                name, 'latency_seconds', ['resource']),
            'queues.n_jobs': Gauge(
                name, 'redis_queue_jobs_count', ['resource', 'queue']),
            'queues.n_workers': Gauge(
                name, 'redis_queue_workers_count', ['resource', 'queue']),
        }


def prometheus_response(canary):
    """
    Return a HTTP Canary response that Prometheus can understand.
    """
    result = canary.check()
    prom = canary.prometheus
    for name, resource in result['resources'].items():
        if 'latency' in resource:
            prom['latency'].labels(name).set(resource['latency'])
        if 'queues' in resource:
            for queue_name, queue_stats in resource['queues'].items():
                (prom['queues.n_jobs']
                    .labels(name, queue_name)
                    .set(queue_stats['n_jobs']))
                (prom['queues.n_workers']
                    .labels(name, queue_name)
                    .set(queue_stats['n_workers']))

    return HttpResponse(
        generate_latest(),
        content_type=CONTENT_TYPE_LATEST,
    )
