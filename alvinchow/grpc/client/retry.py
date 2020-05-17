import time

from grpc import StatusCode, RpcError
from grpc._channel import _UnaryUnaryMultiCallable

from alvinchow.lib.logging import get_logger

logger = get_logger(__name__)


RETRY_MIN_SLEEP = 0.015625
RETRY_MAX_SLEEP = 1.0

RETRYABLE_GRPC_STATUS_CODES = {
    StatusCode.CANCELLED,
    StatusCode.DEADLINE_EXCEEDED,
    StatusCode.FAILED_PRECONDITION,
    StatusCode.UNAVAILABLE,
}

DEFAULT_MAX_RETRIES = 3


def retry_grpc(func, max_retries=DEFAULT_MAX_RETRIES):
    def wrapped_func(*args, **kwargs):
        retry_attempts = 0
        while True:
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                if isinstance(e, RpcError) and (e.code() not in RETRYABLE_GRPC_STATUS_CODES):
                    raise e

                retry_attempts += 1

                if retry_attempts > max_retries:
                    # raise original exception
                    raise e

                backoff = min(RETRY_MIN_SLEEP * 2 ** retry_attempts, RETRY_MAX_SLEEP)

                logger.info(
                    'GRPC retrying call, attempt %s, sleeping for %s (exception=%s)', retry_attempts, backoff, e
                )

                time.sleep(backoff)

    return wrapped_func


def make_stub_methods_retryable(obj):
    for key, attr in obj.__dict__.items():
        if isinstance(attr, _UnaryUnaryMultiCallable):
            setattr(obj, key, retry_grpc(attr))
