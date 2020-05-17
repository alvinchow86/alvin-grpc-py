
def assert_grpc_context_succeeded(context):
    assert context.abort_with_status.called is False
    assert context.abort.called is False


def assert_grpc_context_aborted(context, status_code):
    assert context.abort_with_status.called
    assert context.abort_with_status.call_args[0][0].code == status_code
