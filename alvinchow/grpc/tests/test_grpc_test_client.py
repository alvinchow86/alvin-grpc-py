import pytest
from grpc import StatusCode
from unittest.mock import MagicMock

from alvinchow.grpc.server.exceptions import BadRequestError, NotFoundError, UnauthorizedError
from alvinchow.grpc.server.error_handling import create_grpc_error_handler
from alvinchow.grpc.tests.compiled import example_pb2_grpc, example_pb2
from alvinchow.grpc.test.client import GrpcTestClient
from alvinchow.grpc.utils import create_message_proto_map


message_proto_map = create_message_proto_map(package_paths=['alvinchow.grpc.tests.compiled'])


@pytest.fixture
def context():
    return MagicMock()


def test_grpc_test_client():
    handle_grpc_errors = create_grpc_error_handler()

    class FooApiServicer(example_pb2_grpc.FooApiServicer):
        @handle_grpc_errors()
        def GetFoo(self, request, context):
            # data = protobuf_to_dict(request)
            if request.value == 'bad':
                raise BadRequestError()
            elif request.value == 'unauthorized':
                raise UnauthorizedError()
            elif request.value == 'not_found':
                raise NotFoundError()

            print('request value==>', request.value)
            return example_pb2.Foo(id=1, name=request.value)

    servicer = FooApiServicer()
    service_descriptor = example_pb2.DESCRIPTOR.services_by_name['FooApi']
    message_proto_map = create_message_proto_map(package_paths=['alvinchow.grpc.tests.compiled'])

    grpc_client = GrpcTestClient(
        servicer=servicer,
        service_descriptor=service_descriptor,
        message_proto_map=message_proto_map
    )

    data = grpc_client.GetFoo(value='foobar')
    assert data['id'] == 1
    assert data['name'] == 'foobar'

    # Test raw response
    assert grpc_client.GetFoo(value='foobar', raw=True).id == 1

    # Test errors
    grpc_client.GetFoo(value='not_found', not_found=True)
    grpc_client.GetFoo(value='bad', bad_request=True)
    grpc_client.GetFoo(value='unauthorized', unauthorized=True)
    grpc_client.GetFoo(value='bad', assert_status=StatusCode.INVALID_ARGUMENT)
