import unittest


import grpc

from product.gRpc.server.protos import goods_pb2_grpc
from product.gRpc.server.protos import goods_pb2


class TestClass(unittest.TestCase):

    def test_list(self):
        with grpc.insecure_channel('localhost:50051') as channel:
            stub = goods_pb2_grpc.GoodsControllerStub(channel)
            for user in stub.List(goods_pb2.GoodsListRequest()):
                print(user, end='')

    def test_update(self):
        with grpc.insecure_channel('localhost:50051') as channel:
            goods_service_stub = goods_pb2_grpc.GoodsControllerStub(channel)
            res = goods_service_stub.Update(goods_pb2.Goods(id=1, goods_desc='test', partial=True))
            print(res)



