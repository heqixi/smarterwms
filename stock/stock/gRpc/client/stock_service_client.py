import threading

import grpc

from stock.gRpc.servers.protos.stock import stock_pb2_grpc, stock_pb2


class Stock:
    id: int
    goods: int
    stock_qty: int
    stock_status: int

    def __init__(self, id=None, goods=None, stock_qty=None, stock_status=None):
        self.id = id
        self.goods = goods
        self.stock_qty = stock_qty
        self.stock_status = stock_status

    def is_valid(self):
        raise NotImplementedError('Has not Implement')

    def is_non_negetive(self, *args, nullable=False):
        for field in args:
            if field is None and not nullable:
                return False
            if field and field < 0:
                return False
        return True

    def to_proto_obj(self):
        raise NotImplementedError('Has not Implement')


class StockCreateModel(Stock):

    def is_valid(self):
        return self.is_non_negetive(self.goods, self.stock_qty, self.stock_status, nullable=False)

    def to_proto_obj(self):
        return stock_pb2.Stock(goods=self.goods,
                               stock_qty=self.stock_qty, stock_status=self.stock_status)


class StockUpdateModel(Stock):

    def is_valid(self):
        if not self.id or self.id < 0:
            return False
        if not self.is_non_negetive(self.goods, self.stock_qty, nullable=True):
            return False
        return True

    def to_proto_obj(self):
        return stock_pb2.Stock(id=self.id, goods=self.goods,
                               stock_qty=self.stock_qty, stock_status=self.stock_status)


class StockServiceClient(object):
    __create_key = object()
    lock = threading.RLock()
    client = None
    service_stub = None

    def __init__(self, create_key):
        assert (create_key == StockServiceClient.__create_key),\
            "Stock Service is single instance, please use GlobalProductService.get_instance()"
        channel = grpc.insecure_channel('localhost:50051')

        self.service_stub = stock_pb2_grpc.StockControllerStub(channel)

    @classmethod
    def get_instance(cls):
        if cls.client is None:
            cls.lock.acquire()
            if cls.client is None:
                cls.client = cls(StockServiceClient.__create_key)
            cls.lock.release()
            return cls.client
        return cls.client

    def List(self):
        return self.service_stub.List(stock_pb2.StockListRequest())

    def Create(self, stock: Stock):
        if not stock.is_valid(partial=False):
            pass
        _stock = stock_pb2.Stock(goods=stock.goods, stock_qty=stock.stock_qty, stock_status=stock.stock_status)
        return self.service_stub.Create(_stock)

    def List(self):
        return self.service_stub.List(stock_pb2.StockListRequest())

    def Retrieve(self, stock_id):
        if stock_id is None or stock_id < 0:
            raise Exception('Illegal argments, id')
        return self.service_stub.Retrieve(stock_pb2.StockRetrieveRequest(id=stock_id))

    def Update(self, stock: Stock):
        if not stock.is_valid():
            raise Exception('Fail to update, Illegal stock %s'%stock)
        return self.service_stub.Update(stock.to_proto_obj())

    def Destroy(self, stock_id):
        if not stock_id or stock_id < 0:
            raise Exception('Fail to destroy stock, Illegal stock id %s'%stock_id)
        return self.service_stub.Destroy(stock_pb2.Stock(id=stock_id))

    def Reserve(self, stock_qty, goods):
        if stock_qty is None or stock_qty <= 0:
            raise Exception('Fail to Reserve stock, illegal Stock qty %s'%stock_qty)
        if goods is None or goods < 0:
            raise Exception('Fail to Reser stock ,illegal goods %s'%goods)
        return self.service_stub.Reserve(stock_pb2.StockReserveRequest(stock_qty=stock_qty, goods=goods))

    def Back(self, stock_id, to_reserve=False):
        if stock_id is None or stock_id < 0:
            raise Exception('Fail to back stock , illegal stock %s'%stock_id)
        return self.service_stub.Back(stock_pb2.StockBackRequest(id=stock_id, to_reserve=to_reserve))

    def Ship(self, stock_id):
        if stock_id is None or stock_id < 0:
            raise Exception('Fail to ship stock , illegal stock %s'%stock_id)
        return self.service_stub.Ship(stock_pb2.StockShipRequest(id=stock_id))




