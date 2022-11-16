
import unittest

import grpc

from stock.gRpc.servers.protos import stock_bin_gen_pb2_grpc, stock_bin_gen_pb2

from stock.gRpc.servers.protos import stock_pb2_grpc, stock_pb2


class TestClass(unittest.TestCase):

    with grpc.insecure_channel('localhost:50051') as channel:
        print('chennel success')
        stub = stock_bin_gen_pb2_grpc.StockBinModelControllerStub(channel)
        res = stub.List(stock_bin_gen_pb2.StockBinModelListRequest())
        print('res, ', res)
        for user in res:
            print(user, end='')

    with grpc.insecure_channel('localhost:50051') as channel:
        stock_service_stub = stock_pb2_grpc.StockControllerStub(channel)
        res = stock_service_stub.Update(stock_pb2.StockUpdateRequest(id=953, goods=638))
        print(res)

    with grpc.insecure_channel('localhost:50051') as channel:
        stock_service_stub = stock_pb2_grpc.StockControllerStub(channel)
        res = stock_service_stub.Reserve(stock_pb2.StockReserveRequest(stock_qty=1, goods=53))
        print(res)

    with grpc.insecure_channel('localhost:50051') as channel:
        stock_service_stub = stock_pb2_grpc.StockControllerStub(channel)
        res = stock_service_stub.Back(stock_pb2.StockBackRequest(id=2, to_reserve=False))
        print(res)

    with grpc.insecure_channel('localhost:50051') as channel:
        stock_service_stub = stock_pb2_grpc.StockControllerStub(channel)
        res = stock_service_stub.Ship(stock_pb2.StockBackRequest(id=1))
        print(res)






