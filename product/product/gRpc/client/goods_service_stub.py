import threading
import grpc

from product.gRpc.client.protos import goods_pb2_grpc
from product.gRpc.client.types.goods import GoodsCreateModel


class GoodsServiceClient(object):
    __create_key = object()
    lock = threading.RLock()
    client = None
    service_stub = None

    def __init__(self, create_key):
        assert (create_key == GoodsServiceClient.__create_key),\
            "Stock Service is single instance, please use GlobalProductService.get_instance()"
        channel = grpc.insecure_channel('localhost:50051')

        self.service_stub = goods_pb2_grpc.GoodsControllerStub(channel)

    @classmethod
    def get_instance(cls):
        if cls.client is None:
            cls.lock.acquire()
            if cls.client is None:
                cls.client = cls(GoodsServiceClient.__create_key)
            cls.lock.release()
            return cls.client
        return cls.client

    def Create(self, goods: GoodsCreateModel):
        if not goods.is_valid():
            raise Exception('Illegal product')
        return self.service_stub.Create(goods.to_proto_obj())



