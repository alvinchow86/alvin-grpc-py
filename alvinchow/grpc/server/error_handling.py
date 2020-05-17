import functools
from typing import List

from grpc import StatusCode
from grpc_status import rpc_status
from google.protobuf.any_pb2 import Any
from google.rpc.status_pb2 import Status

from alvinchow.lib.exceptions import FieldError
from alvinchow.lib.logging import get_logger

from alvinchow.grpc.protobuf.error_pb2 import ErrorInfo, BadRequest
from alvinchow.grpc.server.exceptions import GrpcError, BadRequestError


logger = get_logger(__name__)


def create_grpc_error_handler(on_uncaught_exception=None):
    """
    Create an exception handler decorator, which can catch custom GrpcError exceptions and
    abort the request appropriately.

    - on_uncaught_exception: callback function to handle exception

    Usage:
    handle_grpc_errors = create_grpc_error_handler(on_uncaught_exception=my_handler)

    @handle_grpc_errors
    def GetFoo():
        ...
    """

    def handle_grpc_errors():
        def wrap(func):
            @functools.wraps(func)
            def wrapped_func(self, request, context, *args, **kwargs):
                try:
                    return func(self, request, context, *args, **kwargs)
                except GrpcError as e:
                    status_proto = _grpc_error_to_status_proto(e)
                    grpc_status = rpc_status.to_status(status_proto)
                    context.abort_with_status(grpc_status)
                except Exception as e:
                    if on_uncaught_exception:
                        on_uncaught_exception(e)
                    context.abort(StatusCode.UNKNOWN, 'Server error')

            return wrapped_func

        return wrap

    return handle_grpc_errors


def _grpc_error_to_status_proto(error: GrpcError) -> Status:
    """
    Given a GrpcError, construct a google.rpc.status_pb2.Status proto
    """
    message = error.message or ''
    details = []
    if error.code:
        error_info = ErrorInfo(code=error.code)
        error_info_packed = Any()
        error_info_packed.Pack(error_info)
        details.append(error_info_packed)
    if isinstance(error, BadRequestError) and error.field_errors:
        bad_request = _construct_bad_request_proto(error.field_errors)
        bad_request_packed = Any()
        bad_request_packed.Pack(bad_request)
        details.append(bad_request_packed)

    status_code_int = error.status_code.value[0]

    status_proto = Status(code=status_code_int, message=message, details=details)
    return status_proto


def _construct_bad_request_proto(field_errors: List[FieldError]) -> BadRequest:
    """
    Build BadRequest proto, to embed in a Status proto
    """
    field_error_protos = [
        BadRequest.FieldError(
            field=error.field,
            message=error.message,
            code=error.code
        ) for error in field_errors
    ]
    bad_request = BadRequest(field_errors=field_error_protos)
    return bad_request
