# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

import toolManager_pb2 as toolManager__pb2


class toolManagerStub(object):
  """The resourceManager service definition.
  """

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.runManagedProcess = channel.unary_unary(
        '/toolManager.toolManager/runManagedProcess',
        request_serializer=toolManager__pb2.managedProcessRequest.SerializeToString,
        response_deserializer=toolManager__pb2.managedProcessResponse.FromString,
        )
    self.runUnmanagedProcess = channel.unary_unary(
        '/toolManager.toolManager/runUnmanagedProcess',
        request_serializer=toolManager__pb2.unmanagedProcessRequest.SerializeToString,
        response_deserializer=toolManager__pb2.unmanagedProcessResponse.FromString,
        )
    self.runManagedTool = channel.unary_unary(
        '/toolManager.toolManager/runManagedTool',
        request_serializer=toolManager__pb2.managedToolRequest.SerializeToString,
        response_deserializer=toolManager__pb2.managedToolResponse.FromString,
        )
    self.runUnmanagedTool = channel.unary_unary(
        '/toolManager.toolManager/runUnmanagedTool',
        request_serializer=toolManager__pb2.unmanagedToolRequest.SerializeToString,
        response_deserializer=toolManager__pb2.unmanagedToolResponse.FromString,
        )


class toolManagerServicer(object):
  """The resourceManager service definition.
  """

  def runManagedProcess(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def runUnmanagedProcess(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def runManagedTool(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def runUnmanagedTool(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_toolManagerServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'runManagedProcess': grpc.unary_unary_rpc_method_handler(
          servicer.runManagedProcess,
          request_deserializer=toolManager__pb2.managedProcessRequest.FromString,
          response_serializer=toolManager__pb2.managedProcessResponse.SerializeToString,
      ),
      'runUnmanagedProcess': grpc.unary_unary_rpc_method_handler(
          servicer.runUnmanagedProcess,
          request_deserializer=toolManager__pb2.unmanagedProcessRequest.FromString,
          response_serializer=toolManager__pb2.unmanagedProcessResponse.SerializeToString,
      ),
      'runManagedTool': grpc.unary_unary_rpc_method_handler(
          servicer.runManagedTool,
          request_deserializer=toolManager__pb2.managedToolRequest.FromString,
          response_serializer=toolManager__pb2.managedToolResponse.SerializeToString,
      ),
      'runUnmanagedTool': grpc.unary_unary_rpc_method_handler(
          servicer.runUnmanagedTool,
          request_deserializer=toolManager__pb2.unmanagedToolRequest.FromString,
          response_serializer=toolManager__pb2.unmanagedToolResponse.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'toolManager.toolManager', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))