# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from . import shopee_pb2 as shopee__pb2


class ProductServiceControllerStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.List = channel.unary_stream(
                '/shopee.ProductServiceController/List',
                request_serializer=shopee__pb2.ProductListRequest.SerializeToString,
                response_deserializer=shopee__pb2.Product.FromString,
                )
        self.Create = channel.unary_unary(
                '/shopee.ProductServiceController/Create',
                request_serializer=shopee__pb2.Product.SerializeToString,
                response_deserializer=shopee__pb2.Product.FromString,
                )
        self.Retrieve = channel.unary_unary(
                '/shopee.ProductServiceController/Retrieve',
                request_serializer=shopee__pb2.ProductRetrieveRequest.SerializeToString,
                response_deserializer=shopee__pb2.Product.FromString,
                )
        self.Update = channel.unary_unary(
                '/shopee.ProductServiceController/Update',
                request_serializer=shopee__pb2.Product.SerializeToString,
                response_deserializer=shopee__pb2.Product.FromString,
                )
        self.Destory = channel.unary_unary(
                '/shopee.ProductServiceController/Destory',
                request_serializer=shopee__pb2.Product.SerializeToString,
                response_deserializer=shopee__pb2.Product.FromString,
                )
        self.Query = channel.unary_stream(
                '/shopee.ProductServiceController/Query',
                request_serializer=shopee__pb2.QueryRequest.SerializeToString,
                response_deserializer=shopee__pb2.Product.FromString,
                )


class ProductServiceControllerServicer(object):
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

    def Destory(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Query(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ProductServiceControllerServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'List': grpc.unary_stream_rpc_method_handler(
                    servicer.List,
                    request_deserializer=shopee__pb2.ProductListRequest.FromString,
                    response_serializer=shopee__pb2.Product.SerializeToString,
            ),
            'Create': grpc.unary_unary_rpc_method_handler(
                    servicer.Create,
                    request_deserializer=shopee__pb2.Product.FromString,
                    response_serializer=shopee__pb2.Product.SerializeToString,
            ),
            'Retrieve': grpc.unary_unary_rpc_method_handler(
                    servicer.Retrieve,
                    request_deserializer=shopee__pb2.ProductRetrieveRequest.FromString,
                    response_serializer=shopee__pb2.Product.SerializeToString,
            ),
            'Update': grpc.unary_unary_rpc_method_handler(
                    servicer.Update,
                    request_deserializer=shopee__pb2.Product.FromString,
                    response_serializer=shopee__pb2.Product.SerializeToString,
            ),
            'Destory': grpc.unary_unary_rpc_method_handler(
                    servicer.Destory,
                    request_deserializer=shopee__pb2.Product.FromString,
                    response_serializer=shopee__pb2.Product.SerializeToString,
            ),
            'Query': grpc.unary_stream_rpc_method_handler(
                    servicer.Query,
                    request_deserializer=shopee__pb2.QueryRequest.FromString,
                    response_serializer=shopee__pb2.Product.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'shopee.ProductServiceController', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class ProductServiceController(object):
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
        return grpc.experimental.unary_stream(request, target, '/shopee.ProductServiceController/List',
            shopee__pb2.ProductListRequest.SerializeToString,
            shopee__pb2.Product.FromString,
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
        return grpc.experimental.unary_unary(request, target, '/shopee.ProductServiceController/Create',
            shopee__pb2.Product.SerializeToString,
            shopee__pb2.Product.FromString,
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
        return grpc.experimental.unary_unary(request, target, '/shopee.ProductServiceController/Retrieve',
            shopee__pb2.ProductRetrieveRequest.SerializeToString,
            shopee__pb2.Product.FromString,
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
        return grpc.experimental.unary_unary(request, target, '/shopee.ProductServiceController/Update',
            shopee__pb2.Product.SerializeToString,
            shopee__pb2.Product.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Destory(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/shopee.ProductServiceController/Destory',
            shopee__pb2.Product.SerializeToString,
            shopee__pb2.Product.FromString,
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
        return grpc.experimental.unary_stream(request, target, '/shopee.ProductServiceController/Query',
            shopee__pb2.QueryRequest.SerializeToString,
            shopee__pb2.Product.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)