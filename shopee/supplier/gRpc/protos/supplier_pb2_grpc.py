# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from . import supplier_pb2 as supplier__pb2


class SupplierControllerStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.List = channel.unary_stream(
                '/supplier.SupplierController/List',
                request_serializer=supplier__pb2.SupplierListRequest.SerializeToString,
                response_deserializer=supplier__pb2.Supplier.FromString,
                )
        self.Create = channel.unary_unary(
                '/supplier.SupplierController/Create',
                request_serializer=supplier__pb2.Supplier.SerializeToString,
                response_deserializer=supplier__pb2.Response.FromString,
                )
        self.Retrieve = channel.unary_unary(
                '/supplier.SupplierController/Retrieve',
                request_serializer=supplier__pb2.SupplierListRequest.SerializeToString,
                response_deserializer=supplier__pb2.Response.FromString,
                )
        self.Update = channel.unary_unary(
                '/supplier.SupplierController/Update',
                request_serializer=supplier__pb2.Supplier.SerializeToString,
                response_deserializer=supplier__pb2.Response.FromString,
                )
        self.Destroy = channel.unary_unary(
                '/supplier.SupplierController/Destroy',
                request_serializer=supplier__pb2.Supplier.SerializeToString,
                response_deserializer=supplier__pb2.Response.FromString,
                )
        self.CreatePurchasePlan = channel.unary_unary(
                '/supplier.SupplierController/CreatePurchasePlan',
                request_serializer=supplier__pb2.PurchasePlan.SerializeToString,
                response_deserializer=supplier__pb2.PurchasePlan.FromString,
                )


class SupplierControllerServicer(object):
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

    def CreatePurchasePlan(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_SupplierControllerServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'List': grpc.unary_stream_rpc_method_handler(
                    servicer.List,
                    request_deserializer=supplier__pb2.SupplierListRequest.FromString,
                    response_serializer=supplier__pb2.Supplier.SerializeToString,
            ),
            'Create': grpc.unary_unary_rpc_method_handler(
                    servicer.Create,
                    request_deserializer=supplier__pb2.Supplier.FromString,
                    response_serializer=supplier__pb2.Response.SerializeToString,
            ),
            'Retrieve': grpc.unary_unary_rpc_method_handler(
                    servicer.Retrieve,
                    request_deserializer=supplier__pb2.SupplierListRequest.FromString,
                    response_serializer=supplier__pb2.Response.SerializeToString,
            ),
            'Update': grpc.unary_unary_rpc_method_handler(
                    servicer.Update,
                    request_deserializer=supplier__pb2.Supplier.FromString,
                    response_serializer=supplier__pb2.Response.SerializeToString,
            ),
            'Destroy': grpc.unary_unary_rpc_method_handler(
                    servicer.Destroy,
                    request_deserializer=supplier__pb2.Supplier.FromString,
                    response_serializer=supplier__pb2.Response.SerializeToString,
            ),
            'CreatePurchasePlan': grpc.unary_unary_rpc_method_handler(
                    servicer.CreatePurchasePlan,
                    request_deserializer=supplier__pb2.PurchasePlan.FromString,
                    response_serializer=supplier__pb2.PurchasePlan.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'supplier.SupplierController', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class SupplierController(object):
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
        return grpc.experimental.unary_stream(request, target, '/supplier.SupplierController/List',
            supplier__pb2.SupplierListRequest.SerializeToString,
            supplier__pb2.Supplier.FromString,
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
        return grpc.experimental.unary_unary(request, target, '/supplier.SupplierController/Create',
            supplier__pb2.Supplier.SerializeToString,
            supplier__pb2.Response.FromString,
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
        return grpc.experimental.unary_unary(request, target, '/supplier.SupplierController/Retrieve',
            supplier__pb2.SupplierListRequest.SerializeToString,
            supplier__pb2.Response.FromString,
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
        return grpc.experimental.unary_unary(request, target, '/supplier.SupplierController/Update',
            supplier__pb2.Supplier.SerializeToString,
            supplier__pb2.Response.FromString,
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
        return grpc.experimental.unary_unary(request, target, '/supplier.SupplierController/Destroy',
            supplier__pb2.Supplier.SerializeToString,
            supplier__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def CreatePurchasePlan(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/supplier.SupplierController/CreatePurchasePlan',
            supplier__pb2.PurchasePlan.SerializeToString,
            supplier__pb2.PurchasePlan.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)