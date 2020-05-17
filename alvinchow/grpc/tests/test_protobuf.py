from alvinchow.grpc.protobuf.error_pb2 import ErrorInfo, BadRequest


def test_error_proto():
    error_info = ErrorInfo(code='invalid_login')
    assert error_info.code == 'invalid_login'


def test_bad_request_proto():
    field_error1 = BadRequest.FieldError(
        field='email',
        message='Not a valid email',
        code='invalid_email',
    )
    field_error2 = BadRequest.FieldError(
        field='password',
        message='Password strength is too weak',
        code='password_strength_insufficient',
    )

    bad_request = BadRequest(field_errors=[field_error1, field_error2])
    assert len(bad_request.field_errors) == 2
    assert bad_request.field_errors[0].field == 'email'
    assert bad_request.field_errors[0].code == 'invalid_email'

    # Construct it another way
    br2 = BadRequest()
    fv1 = br2.field_errors.add()
    fv1.field = 'foo'
    fv1.message = 'foo bar'
    assert br2.field_errors[0].field == 'foo'
