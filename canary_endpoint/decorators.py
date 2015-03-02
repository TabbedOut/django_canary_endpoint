import functools
import time

from .constants import OK, WARNING


def timed(check=None, threshold=1.0):
    """
    Wrap a status check with a latency in seconds.

    :param threshold:
        The number of seconds before the status is elevated to WARNING.
    """
    def wrap_check(check):
        @functools.wraps(check)
        def wrapped_check(*args, **kwargs):
            start = time.time()
            result = check(*args, **kwargs)
            latency = time.time() - start

            status = result['status']
            if status == OK and latency >= threshold:
                status = WARNING

            return dict(result, status=status, latency=latency)

        return wrapped_check

    return wrap_check(check) if check else wrap_check
