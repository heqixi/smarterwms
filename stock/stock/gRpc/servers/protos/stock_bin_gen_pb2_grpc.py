# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from . import stock_bin_gen_pb2 as stock__bin__gen__pb2


class StockBinModelControllerStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.List = channel.unary_stream(
                '/stock_bin_gen.StockBinModelController/List',
                request_serializer=stock__bin__gen__pb2.StockBinModelListRequest.SerializeToString,
                response_deserializer=stock__bin__gen__pb2.StockBinModel.FromString,
                )
        self.Create = channel.unary_unary(
                '/stock_bin_gen.StockBinModelController/Create',
                request_serializer=stock__bin__gen__pb2.StockBinModel.SerializeToString,
                response_deserializer=stock__bin__gen__pb2.StockBinModel.FromString,
                )
        self.Retrieve = channel.unary_unary(
                '/stock_bin_gen.StockBinModelController/Retrieve',
                request_serializer=stock__bin__gen__pb2.StockBinModelRetrieveRequest.SerializeToString,
                response_deserializer=stock__bin__gen__pb2.StockBinModel.FromString,
                )
        self.Update = channel.unary_unary(
                '/stock_bin_gen.StockBinModelController/Update',
                request_serializer=stock__bin__gen__pb2.StockBinModel.SerializeToString,
                response_deserializer=stock__bin__gen__pb2.StockBinModel.FromString,
                )
        self.Destroy = channel.unary_unary(
                '/stock_bin_gen.StockBinModelController/Destroy',
                request_serializer=stock__bin__gen__pb2.StockBinModel.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                )


class StockBinModelControllerServicer(object):
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


def add_StockBinModelControllerServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'List': grpc.unary_stream_rpc_method_handler(
                    servicer.List,
                    request_deserializer=stock__bin__gen__pb2.StockBinModelListRequest.FromString,
                    response_serializer=stock__bin__gen__pb2.StockBinModel.SerializeToString,
            ),
            'Create': grpc.unary_unary_rpc_method_handler(
                    servicer.Create,
                    request_deserializer=stock__bin__gen__pb2.StockBinModel.FromString,
                    response_serializer=stock__bin__gen__pb2.StockBinModel.SerializeToString,
            ),
            'Retrieve': grpc.unary_unary_rpc_method_handler(
                    servicer.Retrieve,
                    request_deserializer=stock__bin__gen__pb2.StockBinModelRetrieveRequest.FromString,
                    response_serializer=stock__bin__gen__pb2.StockBinModel.SerializeToString,
            ),
            'Update': grpc.unary_unary_rpc_method_handler(
                    servicer.Update,
                    request_deserializer=stock__bin__gen__pb2.StockBinModel.FromString,
                    response_serializer=stock__bin__gen__pb2.StockBinModel.SerializeToString,
            ),
            'Destroy': grpc.unary_unary_rpc_method_handler(
                    servicer.Destroy,
                    request_deserializer=stock__bin__gen__pb2.StockBinModel.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'stock_bin_gen.StockBinModelController', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class StockBinModelController(object):
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
        return grpc.experimental.unary_stream(request, target, '/stock_bin_gen.StockBinModelController/List',
            stock__bin__gen__pb2.StockBinModelListRequest.SerializeToString,
            stock__bin__gen__pb2.StockBinModel.FromString,
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
        return grpc.experimental.unary_unary(request, target, '/stock_bin_gen.StockBinModelController/Create',
            stock__bin__gen__pb2.StockBinModel.SerializeToString,
            stock__bin__gen__pb2.StockBinModel.FromString,
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
        return grpc.experimental.unary_unary(request, target, '/stock_bin_gen.StockBinModelController/Retrieve',
            stock__bin__gen__pb2.StockBinModelRetrieveRequest.SerializeToString,
            stock__bin__gen__pb2.StockBinModel.FromString,
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
        return grpc.experimental.unary_unary(request, target, '/stock_bin_gen.StockBinModelController/Update',
            stock__bin__gen__pb2.StockBinModel.SerializeToString,
            stock__bin__gen__pb2.StockBinModel.FromString,
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
        return grpc.experimental.unary_unary(request, target, '/stock_bin_gen.StockBinModelController/Destroy',
            stock__bin__gen__pb2.StockBinModel.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
