
import grpc
from stock.gRpc.servers.protos import stock_bin_gen_pb2, stock_bin_gen_pb2_grpc

from ..protos import stock_bin_gen_pb2, stock_bin_gen_pb2_grpc

from stock.gRpc.servers.protos import stock_pb2_grpc, stock_pb2


with grpc.insecure_channel('localhost:50051') as channel:
    stub = stock_bin_gen_pb2_grpc.StockBinModelControllerStub(channel)
    for user in stub.List(stock_bin_gen_pb2.StockBinModelListRequest()):
        print(user, end='')

    stock_service_stub = stock_pb2_grpc.StockControllerStub(channel)
    res = stock_service_stub.Update(stock_pb2.StockUpdateRequest(id=1, stock_qty=10))

with grpc.insecure_channel('localhost:50051') as channel:
    stock_service_stub = stock_pb2_grpc.StockControllerStub(channel)
    res = stock_service_stub.Update(stock_pb2.StockUpdateRequest(id=1, stock_qty=35, goods=35, stock_status=12))
    print(res)



