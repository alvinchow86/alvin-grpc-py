from grpc import StatusCode

from alvinchow.lib.exceptions import BaseException, FieldErrorsMixin


class GrpcError(BaseException):
    status_code = StatusCode.FAILED_PRECONDITION

    def __init__(self, *args, status_code=None, **kwargs):
        super().__init__(*args, **kwargs)
        if status_code is not None:
            self.status_code = status_code


class BadRequestError(FieldErrorsMixin, GrpcError):
    status_code = StatusCode.INVALID_ARGUMENT


class UnauthorizedError(GrpcError):
    status_code = StatusCode.PERMISSION_DENIED


class NotFoundError(GrpcError):
    status_code = StatusCode.NOT_FOUND


class ServerError(GrpcError):
    status_code = StatusCode.UNKNOWN
