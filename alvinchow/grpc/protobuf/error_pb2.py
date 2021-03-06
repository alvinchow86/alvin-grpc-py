# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: alvinchow/error.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='alvinchow/error.proto',
  package='alvinchow',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=b'\n\x15\x61lvinchow/error.proto\x12\talvinchow\"\x19\n\tErrorInfo\x12\x0c\n\x04\x63ode\x18\x01 \x01(\t\"\x80\x01\n\nBadRequest\x12\x36\n\x0c\x66ield_errors\x18\x01 \x03(\x0b\x32 .alvinchow.BadRequest.FieldError\x1a:\n\nFieldError\x12\r\n\x05\x66ield\x18\x01 \x01(\t\x12\x0f\n\x07message\x18\x02 \x01(\t\x12\x0c\n\x04\x63ode\x18\x03 \x01(\tb\x06proto3'
)




_ERRORINFO = _descriptor.Descriptor(
  name='ErrorInfo',
  full_name='alvinchow.ErrorInfo',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='code', full_name='alvinchow.ErrorInfo.code', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=36,
  serialized_end=61,
)


_BADREQUEST_FIELDERROR = _descriptor.Descriptor(
  name='FieldError',
  full_name='alvinchow.BadRequest.FieldError',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='field', full_name='alvinchow.BadRequest.FieldError.field', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='message', full_name='alvinchow.BadRequest.FieldError.message', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='code', full_name='alvinchow.BadRequest.FieldError.code', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=134,
  serialized_end=192,
)

_BADREQUEST = _descriptor.Descriptor(
  name='BadRequest',
  full_name='alvinchow.BadRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='field_errors', full_name='alvinchow.BadRequest.field_errors', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[_BADREQUEST_FIELDERROR, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=64,
  serialized_end=192,
)

_BADREQUEST_FIELDERROR.containing_type = _BADREQUEST
_BADREQUEST.fields_by_name['field_errors'].message_type = _BADREQUEST_FIELDERROR
DESCRIPTOR.message_types_by_name['ErrorInfo'] = _ERRORINFO
DESCRIPTOR.message_types_by_name['BadRequest'] = _BADREQUEST
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

ErrorInfo = _reflection.GeneratedProtocolMessageType('ErrorInfo', (_message.Message,), {
  'DESCRIPTOR' : _ERRORINFO,
  '__module__' : 'alvinchow.error_pb2'
  # @@protoc_insertion_point(class_scope:alvinchow.ErrorInfo)
  })
_sym_db.RegisterMessage(ErrorInfo)

BadRequest = _reflection.GeneratedProtocolMessageType('BadRequest', (_message.Message,), {

  'FieldError' : _reflection.GeneratedProtocolMessageType('FieldError', (_message.Message,), {
    'DESCRIPTOR' : _BADREQUEST_FIELDERROR,
    '__module__' : 'alvinchow.error_pb2'
    # @@protoc_insertion_point(class_scope:alvinchow.BadRequest.FieldError)
    })
  ,
  'DESCRIPTOR' : _BADREQUEST,
  '__module__' : 'alvinchow.error_pb2'
  # @@protoc_insertion_point(class_scope:alvinchow.BadRequest)
  })
_sym_db.RegisterMessage(BadRequest)
_sym_db.RegisterMessage(BadRequest.FieldError)


# @@protoc_insertion_point(module_scope)
