import time

import grpc
from alvinchow.lib.logging import get_logger


grpc_logger = get_logger('grpc_request')


class DefaultInterceptor(grpc.ServerInterceptor):
    """
    Interceptor to add basic timing, logging, and hooks for custom behavior
    """

    def before_request(self, request_info: dict):
        pass

    def after_request(self, request_info: dict):
        pass

    def intercept_service(self, continuation, handler_call_details):
        service_name_full, method_name = handler_call_details.method.split('/')[-2:]
        service_name = service_name_full.split('.')[-1]
        service_label = f'{service_name}/{method_name}'

        def wrapper(behavior, request_streaming, response_streaming):
            def new_behavior(request_or_iterator, servicer_context):
                start = time.time()

                request_info = dict(
                    service_label=service_label,
                    method_name=method_name
                )

                self.before_request(request_info=request_info)

                try:
                    result = behavior(request_or_iterator, servicer_context)
                    elapsed = time.time() - start
                    msg = f'gRPC -> {service_label} succeeded in {elapsed:.8f}s'
                    grpc_logger.info(msg)
                    return result
                except Exception:
                    # For exceptions, return error message
                    state = servicer_context._state
                    if state:
                        code_name = state.code._name_
                        error_details = state.details.decode('utf-8')   # details is in bytes
                        msg = f'gRPC -> {service_label} returned error {code_name}'
                        if state.details:
                            error_details = state.details.decode('utf-8')   # details is in bytes
                            msg += f' (details="{error_details}")'
                        grpc_logger.info(msg)
                    raise
                finally:
                    self.after_request(request_info=request_info)

            return new_behavior

        return _wrap_rpc_behavior(continuation(handler_call_details), wrapper)


# Taken from https://github.com/grpc/grpc/pull/14306/files, part of workaround for
# gRPC server interceptor to call code at end of request
def _wrap_rpc_behavior(handler, fn):
    if handler is None:   # pragma: no cover
        return None

    if handler.request_streaming and handler.response_streaming:
        behavior_fn = handler.stream_stream
        handler_factory = grpc.stream_stream_rpc_method_handler
    elif handler.request_streaming and not handler.response_streaming:
        behavior_fn = handler.stream_unary
        handler_factory = grpc.stream_unary_rpc_method_handler
    elif not handler.request_streaming and handler.response_streaming:
        behavior_fn = handler.unary_stream
        handler_factory = grpc.unary_stream_rpc_method_handler
    else:
        behavior_fn = handler.unary_unary
        handler_factory = grpc.unary_unary_rpc_method_handler

    return handler_factory(fn(behavior_fn,
                              handler.request_streaming,
                              handler.response_streaming),
                           request_deserializer=handler.request_deserializer,
                           response_serializer=handler.response_serializer)
