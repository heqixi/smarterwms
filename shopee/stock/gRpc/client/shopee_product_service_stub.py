import threading
import grpc

# from stock.gRpc.client.api import product_pb2_grpc, product_pb2


class ProductServiceClient(object):
    __create_key = object()
    lock = threading.RLock()
    client = None
    service_stub = None

    def __init__(self, create_key):
        assert (create_key == ProductServiceClient.__create_key),\
            "Stock Service is single instance, please use GlobalProductService.get_instance()"
        channel = grpc.insecure_channel('localhost:50051')

        # self.service_stub = product_pb2_grpc.ProductServiceControllerStub(channel)

    @classmethod
    def get_instance(cls):
        if cls.client is None:
            cls.lock.acquire()
            if cls.client is None:
                cls.client = cls(ProductServiceClient.__create_key)
            cls.lock.release()
            return cls.client
        return cls.client

    def query(self, global_product_id):
        if not isinstance(global_product_id, int) or global_product_id < 0:
            raise Exception('query product illegal product id')
        return self.service_stub.query(product_pb2.QueryRequest(product_id=global_product_id))


