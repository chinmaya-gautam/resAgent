# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: generalTA.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='generalTA.proto',
  package='generalTA',
  syntax='proto3',
  serialized_pb=_b('\n\x0fgeneralTA.proto\x12\tgeneralTA\"#\n\x0b\x65xitRequest\x12\x14\n\x0c\x65xitDelaySec\x18\x01 \x01(\x05\"\x1f\n\x0c\x65xitResponse\x12\x0f\n\x07retCode\x18\x01 \x01(\x05\x32H\n\tgeneralTA\x12;\n\x06\x65xitMe\x12\x16.generalTA.exitRequest\x1a\x17.generalTA.exitResponse\"\x00\x42&\n\x11io.grpc.generalTAB\tgeneralTAP\x01\xa2\x02\x03GTAb\x06proto3')
)




_EXITREQUEST = _descriptor.Descriptor(
  name='exitRequest',
  full_name='generalTA.exitRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='exitDelaySec', full_name='generalTA.exitRequest.exitDelaySec', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=30,
  serialized_end=65,
)


_EXITRESPONSE = _descriptor.Descriptor(
  name='exitResponse',
  full_name='generalTA.exitResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='retCode', full_name='generalTA.exitResponse.retCode', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=67,
  serialized_end=98,
)

DESCRIPTOR.message_types_by_name['exitRequest'] = _EXITREQUEST
DESCRIPTOR.message_types_by_name['exitResponse'] = _EXITRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

exitRequest = _reflection.GeneratedProtocolMessageType('exitRequest', (_message.Message,), dict(
  DESCRIPTOR = _EXITREQUEST,
  __module__ = 'generalTA_pb2'
  # @@protoc_insertion_point(class_scope:generalTA.exitRequest)
  ))
_sym_db.RegisterMessage(exitRequest)

exitResponse = _reflection.GeneratedProtocolMessageType('exitResponse', (_message.Message,), dict(
  DESCRIPTOR = _EXITRESPONSE,
  __module__ = 'generalTA_pb2'
  # @@protoc_insertion_point(class_scope:generalTA.exitResponse)
  ))
_sym_db.RegisterMessage(exitResponse)


DESCRIPTOR.has_options = True
DESCRIPTOR._options = _descriptor._ParseOptions(descriptor_pb2.FileOptions(), _b('\n\021io.grpc.generalTAB\tgeneralTAP\001\242\002\003GTA'))

_GENERALTA = _descriptor.ServiceDescriptor(
  name='generalTA',
  full_name='generalTA.generalTA',
  file=DESCRIPTOR,
  index=0,
  options=None,
  serialized_start=100,
  serialized_end=172,
  methods=[
  _descriptor.MethodDescriptor(
    name='exitMe',
    full_name='generalTA.generalTA.exitMe',
    index=0,
    containing_service=None,
    input_type=_EXITREQUEST,
    output_type=_EXITRESPONSE,
    options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_GENERALTA)

DESCRIPTOR.services_by_name['generalTA'] = _GENERALTA

try:
  # THESE ELEMENTS WILL BE DEPRECATED.
  # Please use the generated *_pb2_grpc.py files instead.
  import grpc
  from grpc.beta import implementations as beta_implementations
  from grpc.beta import interfaces as beta_interfaces
  from grpc.framework.common import cardinality
  from grpc.framework.interfaces.face import utilities as face_utilities


  class generalTAStub(object):
    # missing associated documentation comment in .proto file
    pass

    def __init__(self, channel):
      """Constructor.

      Args:
        channel: A grpc.Channel.
      """
      self.exitMe = channel.unary_unary(
          '/generalTA.generalTA/exitMe',
          request_serializer=exitRequest.SerializeToString,
          response_deserializer=exitResponse.FromString,
          )


  class generalTAServicer(object):
    # missing associated documentation comment in .proto file
    pass

    def exitMe(self, request, context):
      # missing associated documentation comment in .proto file
      pass
      context.set_code(grpc.StatusCode.UNIMPLEMENTED)
      context.set_details('Method not implemented!')
      raise NotImplementedError('Method not implemented!')


  def add_generalTAServicer_to_server(servicer, server):
    rpc_method_handlers = {
        'exitMe': grpc.unary_unary_rpc_method_handler(
            servicer.exitMe,
            request_deserializer=exitRequest.FromString,
            response_serializer=exitResponse.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        'generalTA.generalTA', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


  class BetageneralTAServicer(object):
    """The Beta API is deprecated for 0.15.0 and later.

    It is recommended to use the GA API (classes and functions in this
    file not marked beta) for all further purposes. This class was generated
    only to ease transition from grpcio<0.15.0 to grpcio>=0.15.0."""
    # missing associated documentation comment in .proto file
    pass
    def exitMe(self, request, context):
      # missing associated documentation comment in .proto file
      pass
      context.code(beta_interfaces.StatusCode.UNIMPLEMENTED)


  class BetageneralTAStub(object):
    """The Beta API is deprecated for 0.15.0 and later.

    It is recommended to use the GA API (classes and functions in this
    file not marked beta) for all further purposes. This class was generated
    only to ease transition from grpcio<0.15.0 to grpcio>=0.15.0."""
    # missing associated documentation comment in .proto file
    pass
    def exitMe(self, request, timeout, metadata=None, with_call=False, protocol_options=None):
      # missing associated documentation comment in .proto file
      pass
      raise NotImplementedError()
    exitMe.future = None


  def beta_create_generalTA_server(servicer, pool=None, pool_size=None, default_timeout=None, maximum_timeout=None):
    """The Beta API is deprecated for 0.15.0 and later.

    It is recommended to use the GA API (classes and functions in this
    file not marked beta) for all further purposes. This function was
    generated only to ease transition from grpcio<0.15.0 to grpcio>=0.15.0"""
    request_deserializers = {
      ('generalTA.generalTA', 'exitMe'): exitRequest.FromString,
    }
    response_serializers = {
      ('generalTA.generalTA', 'exitMe'): exitResponse.SerializeToString,
    }
    method_implementations = {
      ('generalTA.generalTA', 'exitMe'): face_utilities.unary_unary_inline(servicer.exitMe),
    }
    server_options = beta_implementations.server_options(request_deserializers=request_deserializers, response_serializers=response_serializers, thread_pool=pool, thread_pool_size=pool_size, default_timeout=default_timeout, maximum_timeout=maximum_timeout)
    return beta_implementations.server(method_implementations, options=server_options)


  def beta_create_generalTA_stub(channel, host=None, metadata_transformer=None, pool=None, pool_size=None):
    """The Beta API is deprecated for 0.15.0 and later.

    It is recommended to use the GA API (classes and functions in this
    file not marked beta) for all further purposes. This function was
    generated only to ease transition from grpcio<0.15.0 to grpcio>=0.15.0"""
    request_serializers = {
      ('generalTA.generalTA', 'exitMe'): exitRequest.SerializeToString,
    }
    response_deserializers = {
      ('generalTA.generalTA', 'exitMe'): exitResponse.FromString,
    }
    cardinalities = {
      'exitMe': cardinality.Cardinality.UNARY_UNARY,
    }
    stub_options = beta_implementations.stub_options(host=host, metadata_transformer=metadata_transformer, request_serializers=request_serializers, response_deserializers=response_deserializers, thread_pool=pool, thread_pool_size=pool_size)
    return beta_implementations.dynamic_stub(channel, 'generalTA.generalTA', cardinalities, options=stub_options)
except ImportError:
  pass
# @@protoc_insertion_point(module_scope)
