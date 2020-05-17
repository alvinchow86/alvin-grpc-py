import pytest
from grpc import StatusCode, RpcError
from grpc_status.rpc_status import _GRPC_DETAILS_METADATA_KEY
from unittest.mock import MagicMock

from alvinchow.lib.exceptions import FieldError
from alvinchow.lib.remote.exceptions import BadRequestError, NotFoundError
from alvinchow.grpc.client.error_handling import handle_grpc_errors, handle_grpc_not_found
from alvinchow.grpc.server.error_handling import _grpc_error_to_status_proto
from alvinchow.grpc.server import exceptions as api_exceptions


def test_client_handle_grpc_errors():
    # Simulate a StatusProto sent by a python gRPC server
    error_msg = 'Something is wrong'
    error_code = 'foo_bar'
    field_errors = [
        FieldError(field='bar', message='Oops', code='invalid'),
        FieldError(field='baz', message='Oops', code='invalid'),
    ]
    grpc_error = api_exceptions.BadRequestError(
        error_msg, code=error_code, field_errors=field_errors
    )
    status_proto = _grpc_error_to_status_proto(grpc_error)

    @handle_grpc_errors()
    def foo():
        err = RpcError()
        err.code = MagicMock(return_value=StatusCode.INVALID_ARGUMENT)
        err.details = MagicMock(return_value=error_msg)

        # format is a list/tuple of 2-tuples (pairs)
        trailing_metadata = [
            (_GRPC_DETAILS_METADATA_KEY, status_proto.SerializeToString()),
        ]

        err.trailing_metadata = MagicMock(return_value=trailing_metadata)
        raise err

    assert foo.__name__ == 'foo'

    with pytest.raises(BadRequestError) as exc_info:
        foo()

    exc = exc_info.value
    assert exc.message == error_msg
    assert exc.code == error_code
    assert len(exc.field_errors) == 2
    fe = field_errors[0]
    assert fe.field == 'bar'
    assert fe.message == 'Oops'
    assert fe.code == 'invalid'


def test_client_handle_grpc_not_found():

    def raise_not_found():
        err = RpcError()
        err.code = MagicMock(return_value=StatusCode.NOT_FOUND)
        err.details = MagicMock(return_value='does not exist')
        err.trailing_metadata = MagicMock()

        raise err

    @handle_grpc_not_found()
    def foo():
        raise_not_found()

    assert foo.__name__ == 'foo'

    with pytest.raises(NotFoundError):
        foo()
    assert foo(raise_exception=False) is None

    # Try raise_default=False
    @handle_grpc_not_found(raise_default=False)
    def foo_noraise_default():
        raise_not_found()

    assert foo_noraise_default() is None
