import threading
import grpc

from store.gRpc.servers.protos.goods import goods_pb2_grpc
from store.gRpc.servers.protos.goods import goods_pb2


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

    def retrive(self, pk):
        return self.service_stub.Retrieve(goods_pb2.GoodsRetrieveRequest(id=pk))

    def query_by_code(self, goods_code):
        return self.service_stub.Query(goods_pb2.GoodsQueryRequest(goods_code=goods_code))


