# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from . import goods_pb2 as goods__pb2


class GoodsControllerStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.List = channel.unary_stream(
                '/goods.GoodsController/List',
                request_serializer=goods__pb2.GoodsListRequest.SerializeToString,
                response_deserializer=goods__pb2.Goods.FromString,
                )
        self.Create = channel.unary_unary(
                '/goods.GoodsController/Create',
                request_serializer=goods__pb2.Goods.SerializeToString,
                response_deserializer=goods__pb2.Response.FromString,
                )
        self.Retrieve = channel.unary_unary(
                '/goods.GoodsController/Retrieve',
                request_serializer=goods__pb2.GoodsRetrieveRequest.SerializeToString,
                response_deserializer=goods__pb2.Response.FromString,
                )
        self.Update = channel.unary_unary(
                '/goods.GoodsController/Update',
                request_serializer=goods__pb2.Goods.SerializeToString,
                response_deserializer=goods__pb2.Response.FromString,
                )
        self.Destroy = channel.unary_unary(
                '/goods.GoodsController/Destroy',
                request_serializer=goods__pb2.Goods.SerializeToString,
                response_deserializer=goods__pb2.Response.FromString,
                )
        self.Query = channel.unary_stream(
                '/goods.GoodsController/Query',
                request_serializer=goods__pb2.GoodsQueryRequest.SerializeToString,
                response_deserializer=goods__pb2.Goods.FromString,
                )


class GoodsControllerServicer(object):
    """Missing associated documentation comment in .proto file."""

    def List(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Create(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Retrieve(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Update(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Destroy(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Query(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_GoodsControllerServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'List': grpc.unary_stream_rpc_method_handler(
                    servicer.List,
                    request_deserializer=goods__pb2.GoodsListRequest.FromString,
                    response_serializer=goods__pb2.Goods.SerializeToString,
            ),
            'Create': grpc.unary_unary_rpc_method_handler(
                    servicer.Create,
                    request_deserializer=goods__pb2.Goods.FromString,
                    response_serializer=goods__pb2.Response.SerializeToString,
            ),
            'Retrieve': grpc.unary_unary_rpc_method_handler(
                    servicer.Retrieve,
                    request_deserializer=goods__pb2.GoodsRetrieveRequest.FromString,
                    response_serializer=goods__pb2.Response.SerializeToString,
            ),
            'Update': grpc.unary_unary_rpc_method_handler(
                    servicer.Update,
                    request_deserializer=goods__pb2.Goods.FromString,
                    response_serializer=goods__pb2.Response.SerializeToString,
            ),
            'Destroy': grpc.unary_unary_rpc_method_handler(
                    servicer.Destroy,
                    request_deserializer=goods__pb2.Goods.FromString,
                    response_serializer=goods__pb2.Response.SerializeToString,
            ),
            'Query': grpc.unary_stream_rpc_method_handler(
                    servicer.Query,
                    request_deserializer=goods__pb2.GoodsQueryRequest.FromString,
                    response_serializer=goods__pb2.Goods.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'goods.GoodsController', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class GoodsController(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def List(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/goods.GoodsController/List',
            goods__pb2.GoodsListRequest.SerializeToString,
            goods__pb2.Goods.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Create(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/goods.GoodsController/Create',
            goods__pb2.Goods.SerializeToString,
            goods__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Retrieve(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/goods.GoodsController/Retrieve',
            goods__pb2.GoodsRetrieveRequest.SerializeToString,
            goods__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Update(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/goods.GoodsController/Update',
            goods__pb2.Goods.SerializeToString,
            goods__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Destroy(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/goods.GoodsController/Destroy',
            goods__pb2.Goods.SerializeToString,
            goods__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Query(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/goods.GoodsController/Query',
            goods__pb2.GoodsQueryRequest.SerializeToString,
            goods__pb2.Goods.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
