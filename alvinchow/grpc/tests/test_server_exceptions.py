from grpc import StatusCode

from alvinchow.grpc.server.exceptions import GrpcError


def test_grpc_error_custom_status():
    error = GrpcError(status_code=StatusCode.INTERNAL)
    assert error.status_code == StatusCode.INTERNAL
