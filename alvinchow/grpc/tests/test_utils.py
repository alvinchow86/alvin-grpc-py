from alvinchow.grpc.utils import create_message_proto_map
from alvinchow.grpc.tests.compiled import example_pb2


def test_message_proto_map():
    message_proto_map = create_message_proto_map(package_paths=['alvinchow.grpc.tests.compiled'])
    assert message_proto_map['example.Foo'] == example_pb2.Foo
    assert message_proto_map['example.Collection'] == example_pb2.Collection
