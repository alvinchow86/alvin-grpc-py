import pytest
import grpc
from grpc import StatusCode, RpcError
from grpc._channel import _UnaryUnaryMultiCallable

from unittest.mock import MagicMock

from alvinchow.grpc.client.retry import make_stub_methods_retryable, DEFAULT_MAX_RETRIES
from alvinchow.grpc.tests.compiled.example_pb2_grpc import FooApiStub


def make_stub_with_func(func):
    channel = grpc.insecure_channel('localhost')  # just a stub
    stub = FooApiStub(channel)

    stub.GetFoo = MagicMock(
        spec=_UnaryUnaryMultiCallable,
        side_effect=func
    )
    return stub


def test_client_grpc_retry_success(mocker):
    num_calls = 0

    def get_foo():
        nonlocal num_calls

        if num_calls < 2:
            err = RpcError()
            err.code = MagicMock(return_value=StatusCode.CANCELLED)
            err.details = MagicMock(return_value='Server broke')

            num_calls += 1
            raise err

        return 'success'

    stub = make_stub_with_func(get_foo)
    make_stub_methods_retryable(stub)
    result = stub.GetFoo()
    assert result == 'success'
    assert num_calls > 0


def test_client_grpc_retry_fail(mocker):
    num_calls = 0

    err = RpcError()
    err.code = MagicMock(return_value=StatusCode.CANCELLED)
    err.details = MagicMock(return_value='Server broke')

    def get_foo():
        nonlocal num_calls
        num_calls += 1
        raise err

    stub = make_stub_with_func(get_foo)
    make_stub_methods_retryable(stub)

    with pytest.raises(RpcError) as exc_info:
        stub.GetFoo()

    # Should raise original error
    assert exc_info.value.code() == StatusCode.CANCELLED
    assert exc_info.value == err

    # num calls should be 1(orig call) + MAX_RETRIES
    assert num_calls == DEFAULT_MAX_RETRIES + 1


def test_client_grpc_retry_non_retryable(mocker):
    err = RpcError()
    err.code = MagicMock(return_value=StatusCode.INVALID_ARGUMENT)
    err.details = MagicMock(return_value='bad value')

    def get_foo():
        raise err

    stub = make_stub_with_func(get_foo)
    make_stub_methods_retryable(stub)

    with pytest.raises(RpcError) as exc_info:
        stub.GetFoo()

    # Should raise original error
    assert exc_info.value.code() == StatusCode.INVALID_ARGUMENT
    assert exc_info.value == err
