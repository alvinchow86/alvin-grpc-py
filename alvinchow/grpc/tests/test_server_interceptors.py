from concurrent import futures

from grpc import RpcError
import pytest
import grpc

from alvinchow.grpc.tests.compiled import example_pb2_grpc
from alvinchow.grpc.tests.compiled.example_pb2 import FooRequest, Foo
from alvinchow.grpc.server.interceptors import DefaultInterceptor as _DefaultInterceptor


class FooApiServicer(example_pb2_grpc.FooApiServicer):
    def GetFoo(self, request, context):
        if request.value == 'error':
            context.abort(grpc.StatusCode.UNKNOWN, 'Server error')

        return Foo(id=1, name=request.value)

    def GetFooResponseStream(self, request, context):
        for i in range(2):
            yield Foo(id=i)

    def GetFooRequestStream(self, request_iterator, context):
        for req in request_iterator:
            print('Got request')
        return Foo(id=123)

    def GetFooBidirectional(self, request_iterator, context):
        for req in request_iterator:
            yield Foo()


def create_server(servicer, interceptor_cls):
    pool = futures.ThreadPoolExecutor(max_workers=1)
    server = grpc.server(pool, interceptors=(interceptor_cls(),))

    example_pb2_grpc.add_FooApiServicer_to_server(
        servicer, server
    )
    server.add_insecure_port('[::]:50051')
    # server.start()
    return server


@pytest.fixture
def stub():
    channel = grpc.insecure_channel('localhost:50051')
    stub = example_pb2_grpc.FooApiStub(channel)
    return stub


def test_default_interceptor_basic(stub):
    before_request_counter = dict(count=0)
    after_request_counter = dict(count=0)

    class DefaultInterceptor(_DefaultInterceptor):
        def before_request(self, request_info):
            before_request_counter['count'] += 1
            super().before_request(request_info)

        def after_request(self, request_info):
            after_request_counter['count'] += 1
            super().after_request(request_info)

    server = create_server(FooApiServicer(), DefaultInterceptor)
    server.start()

    # Synchronous
    request = FooRequest()
    response = stub.GetFoo(request)
    assert response.id == 1

    assert before_request_counter['count'] == 1
    assert after_request_counter['count'] == 1

    # Test exception
    request = FooRequest(value='error')
    with pytest.raises(RpcError):
        response = stub.GetFoo(request)

    assert before_request_counter['count'] == 2
    assert after_request_counter['count'] == 2

    # Request stream
    def foo_reqs():
        for i in range(2):
            yield FooRequest()

    response = stub.GetFooRequestStream(foo_reqs())

    assert before_request_counter['count'] == 3
    assert after_request_counter['count'] == 3

    # Response stream
    request = FooRequest()
    results = [foo for foo in stub.GetFooResponseStream(request)]
    assert len(results) == 2
    assert before_request_counter['count'] == 4
    assert after_request_counter['count'] == 4

    # Bidrectional stream
    results = [foo for foo in stub.GetFooBidirectional(foo_reqs())]
    assert len(results) == 2

    assert before_request_counter['count'] == 5
    assert after_request_counter['count'] == 5

    server.stop(0)
