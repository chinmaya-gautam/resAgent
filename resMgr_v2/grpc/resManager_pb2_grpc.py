# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

import resManager_pb2 as resManager__pb2


class resManagerStub(object):
  """The resourceManager service definition.
  """

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.reserveWindows = channel.unary_unary(
        '/resAdmin.resManager/reserveWindows',
        request_serializer=resManager__pb2.reserveRequest.SerializeToString,
        response_deserializer=resManager__pb2.reserveResponse.FromString,
        )
    self.releaseWindows = channel.unary_unary(
        '/resAdmin.resManager/releaseWindows',
        request_serializer=resManager__pb2.releaseRequest.SerializeToString,
        response_deserializer=resManager__pb2.releaseResponse.FromString,
        )
    self.updateResPool = channel.unary_unary(
        '/resAdmin.resManager/updateResPool',
        request_serializer=resManager__pb2.resStatusInfo.SerializeToString,
        response_deserializer=resManager__pb2.resStatusInfo.FromString,
        )
    self.getResPoolInfo = channel.unary_unary(
        '/resAdmin.resManager/getResPoolInfo',
        request_serializer=resManager__pb2.Empty.SerializeToString,
        response_deserializer=resManager__pb2.resGetResPoolInfo.FromString,
        )
    self.checkHeartBeat = channel.unary_unary(
        '/resAdmin.resManager/checkHeartBeat',
        request_serializer=resManager__pb2.resAgentInfo.SerializeToString,
        response_deserializer=resManager__pb2.heartBeat.FromString,
        )


class resManagerServicer(object):
  """The resourceManager service definition.
  """

  def reserveWindows(self, request, context):
    """Sends a resource request
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def releaseWindows(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def updateResPool(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def getResPoolInfo(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def checkHeartBeat(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_resManagerServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'reserveWindows': grpc.unary_unary_rpc_method_handler(
          servicer.reserveWindows,
          request_deserializer=resManager__pb2.reserveRequest.FromString,
          response_serializer=resManager__pb2.reserveResponse.SerializeToString,
      ),
      'releaseWindows': grpc.unary_unary_rpc_method_handler(
          servicer.releaseWindows,
          request_deserializer=resManager__pb2.releaseRequest.FromString,
          response_serializer=resManager__pb2.releaseResponse.SerializeToString,
      ),
      'updateResPool': grpc.unary_unary_rpc_method_handler(
          servicer.updateResPool,
          request_deserializer=resManager__pb2.resStatusInfo.FromString,
          response_serializer=resManager__pb2.resStatusInfo.SerializeToString,
      ),
      'getResPoolInfo': grpc.unary_unary_rpc_method_handler(
          servicer.getResPoolInfo,
          request_deserializer=resManager__pb2.Empty.FromString,
          response_serializer=resManager__pb2.resGetResPoolInfo.SerializeToString,
      ),
      'checkHeartBeat': grpc.unary_unary_rpc_method_handler(
          servicer.checkHeartBeat,
          request_deserializer=resManager__pb2.resAgentInfo.FromString,
          response_serializer=resManager__pb2.heartBeat.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'resAdmin.resManager', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
