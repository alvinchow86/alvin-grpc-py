import functools

from grpc import StatusCode
from unittest.mock import MagicMock
from protobuf_serialization import protobuf_to_dict, serialize_to_protobuf

from alvinchow.grpc.test.asserts import assert_grpc_context_aborted, assert_grpc_context_succeeded


class GrpcTestClient:
    """
    Usage:

    grpc_client.call_method('GetCustomer', id=5)
    grpc_client.GetCustomer(id=5)
    """
    def __init__(self, servicer, service_descriptor, message_proto_map, response_formatter=protobuf_to_dict):
        self.servicer = servicer
        self.service_descriptor = service_descriptor
        self.message_proto_map = message_proto_map
        self.response_formatter = response_formatter

        self._cached_request_response_protos_for_method = {}

    def call_method(
        self, method_name, request=None, extra_proto_fields=None,
        assert_status=StatusCode.OK, not_found=False, bad_request=False, unauthorized=False,
        raw=False,
        **request_fields
    ):
        """
        - method_name: Name of a grpc method (GetCustomer)
        - extra_proto_fields: Additional protobuf, for cases when automatic serializer does not work
        - expected_status: Expect an error code
        - raw: If True, leave it as a protobuf response, don't run response_formatter
        - request_fields: Arguments for the request message
        """

        expected_status = assert_status    # assert_status is better as keyword arg, but more clear to rename in code

        if not_found:
            expected_status = StatusCode.NOT_FOUND
        elif bad_request:
            expected_status = StatusCode.INVALID_ARGUMENT
        elif unauthorized:
            expected_status = StatusCode.PERMISSION_DENIED

        context = MagicMock()
        request_proto, response_proto = self._get_request_response_protos_for_method(method_name)

        if not request:
            request = serialize_to_protobuf(
                request_fields, request_proto, extra_proto_fields=extra_proto_fields,
                message_proto_map=self.message_proto_map
            )

        response = getattr(self.servicer, method_name)(request, context)
        if expected_status != StatusCode.OK:
            assert_grpc_context_aborted(context, expected_status)
            return
        else:
            assert_grpc_context_succeeded(context)
            assert isinstance(response, response_proto)

        if raw:
            return response
        else:
            data = self.response_formatter(response)
            return data

    def __getattr__(self, name):
        """
        Shortcut for call_method
        """
        return functools.partial(self.call_method, name)

    def _get_request_response_protos_for_method(self, method_name):
        """
        Find the request and response protobuf classes for a gRPC method (i.e. input/output types)
        """
        try:
            # Get from cache
            request_proto, response_proto = self._cached_request_response_protos_for_method[method_name]
            return request_proto, response_proto
        except KeyError:
            pass

        method_descriptor = self.service_descriptor.methods_by_name[method_name]

        request_name = method_descriptor.input_type.full_name
        response_name = method_descriptor.output_type.full_name

        request_proto = self.message_proto_map[request_name]
        response_proto = self.message_proto_map[response_name]

        self._cached_request_response_protos_for_method[method_name] = (request_proto, response_proto)

        return (request_proto, response_proto)
