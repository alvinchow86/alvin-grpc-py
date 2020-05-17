import functools

from grpc import StatusCode, RpcError
from grpc_status import rpc_status

from alvinchow.grpc.protobuf.error_pb2 import ErrorInfo, BadRequest
from alvinchow.lib.exceptions import FieldError
from alvinchow.lib.remote.exceptions import APIRequestError, NotFoundError
from alvinchow.lib.remote import exceptions
from alvinchow.lib.logging import get_logger


logger = get_logger(__name__)


STATUS_CODE_TO_EXCEPTION = {
    StatusCode.INVALID_ARGUMENT: exceptions.BadRequestError,
    StatusCode.NOT_FOUND: exceptions.NotFoundError,
    StatusCode.PERMISSION_DENIED: exceptions.UnauthorizedError,
    StatusCode.UNKNOWN: exceptions.ServerError,
}


def handle_grpc_errors():
    """
    Catch gRPC exceptions and translate to our own custom error classes
    """
    def wrap(func):
        @functools.wraps(func)
        def wrapped_func(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except RpcError as error:
                message = error.details()
                status_code = error.code()
                exception_cls = STATUS_CODE_TO_EXCEPTION.get(status_code, APIRequestError)

                error_code = None
                field_errors = None
                extra_error_data = _get_extra_data_from_error(error)
                if extra_error_data:
                    error_code = extra_error_data['error_code']
                    field_errors = extra_error_data['field_errors']

                if exception_cls == exceptions.BadRequestError:
                    raise exceptions.BadRequestError(message, code=error_code, field_errors=field_errors)
                else:
                    raise exception_cls(message, code=error_code)

        return wrapped_func

    return wrap


def handle_grpc_not_found(raise_default=True):
    """
    Catch gRPC NOT_FOUND exception. Later on will make this more generic to handle other errors
    """
    def wrap(func):
        # Apply handle_grpc_errors decorator
        func = handle_grpc_errors()(func)

        @functools.wraps(func)
        def wrapped_func(*args, raise_exception=raise_default, **kwargs):
            try:
                return func(*args, **kwargs)
            except NotFoundError as e:
                if raise_exception:
                    raise e
                else:
                    return None

        return wrapped_func

    return wrap


def _get_extra_data_from_error(error: RpcError):
    """
    Extra error info is stored in trailing_metadata as custom protos
    """
    status = rpc_status.from_call(error)

    if not status:
        return

    error_code = None
    field_errors = None
    for detail in status.details:
        # detail is an Any proto. Right now these are usually ErrorInfo protos.
        if detail.Is(ErrorInfo.DESCRIPTOR):
            error_info = ErrorInfo()
            detail.Unpack(error_info)
            error_code = error_info.code
        if detail.Is(BadRequest.DESCRIPTOR):
            bad_request = BadRequest()
            detail.Unpack(bad_request)
            field_errors = [
                FieldError(
                    field=field_error.field,
                    message=field_error.message,
                    code=field_error.code,
                ) for field_error in bad_request.field_errors
            ]

    return dict(
        error_code=error_code,
        field_errors=field_errors,
    )
