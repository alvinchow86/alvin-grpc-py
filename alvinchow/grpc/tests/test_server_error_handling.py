import pytest
from grpc import StatusCode
from unittest.mock import MagicMock
from google.rpc.status_pb2 import Status
from grpc_status.rpc_status import _GRPC_DETAILS_METADATA_KEY

from alvinchow.grpc.protobuf.error_pb2 import ErrorInfo, BadRequest

from alvinchow.lib.exceptions import FieldError
from alvinchow.grpc.server.exceptions import BadRequestError
from alvinchow.grpc.server.error_handling import create_grpc_error_handler
from alvinchow.grpc.tests.compiled import example_pb2_grpc, example_pb2
from alvinchow.grpc.test.asserts import assert_grpc_context_aborted


@pytest.fixture
def context():
    return MagicMock()


def test_handle_grpc_errors_bad_request(context):
    handle_grpc_errors = create_grpc_error_handler()

    error_msg = 'something is wrong'
    error_code = 'invalid'

    class FooApiServicer(example_pb2_grpc.FooApiServicer):
        @handle_grpc_errors()
        def GetFoo(self, request, context):
            raise BadRequestError(error_msg, code=error_code, field_errors=[
                FieldError('foo', 'No good', 'bad_format'),
                FieldError('bar', 'Oh no', 'invalid_value'),
            ])

    servicer = FooApiServicer()

    response = servicer.GetFoo(example_pb2.FooRequest(), context)
    assert response is None
    assert_grpc_context_aborted(context, StatusCode.INVALID_ARGUMENT)

    status = context.abort_with_status.call_args[0][0]
    assert status.code == StatusCode.INVALID_ARGUMENT
    assert status.details == 'something is wrong'

    # Check trailing metadata
    assert status.trailing_metadata[0][0] == _GRPC_DETAILS_METADATA_KEY
    serialized_status = status.trailing_metadata[0][1]
    status_proto = Status.FromString(serialized_status)
    assert status_proto.code == StatusCode.INVALID_ARGUMENT.value[0]
    assert status_proto.message == error_msg

    error_info = ErrorInfo()
    bad_request = BadRequest()

    for detail in status_proto.details:
        if detail.Is(ErrorInfo.DESCRIPTOR):
            detail.Unpack(error_info)
        if detail.Is(BadRequest.DESCRIPTOR):
            detail.Unpack(bad_request)

    assert error_info.code == error_code
    assert len(bad_request.field_errors) == 2
    assert bad_request.field_errors[0].field == 'foo'
    assert bad_request.field_errors[0].message == 'No good'
    assert bad_request.field_errors[0].code == 'bad_format'


def test_handle_grpc_errors_uncaught_exception(context):
    count = 0

    def uncaught_handler(exc):
        nonlocal count
        count += 1

    handle_grpc_errors = create_grpc_error_handler(on_uncaught_exception=uncaught_handler)

    class FooApiServicer(example_pb2_grpc.FooApiServicer):
        @handle_grpc_errors()
        def GetFoo(self, request, context):
            raise Exception('uh oh')

    servicer = FooApiServicer()

    response = servicer.GetFoo(example_pb2.FooRequest(), context)
    assert response is None
    assert context.abort.call_args[0][0] == StatusCode.UNKNOWN

    # Check that the handler was called
    assert count == 1
