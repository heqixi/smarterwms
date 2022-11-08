
import threading
import grpc

from base.gRpc.types.base import ProtoType
from asn.gRpc.client.protos.stock import stock_pb2_grpc, stock_pb2


class StockStatus(object):
    DAMAGE = 0

    PURCHASED = 1

    SORTED = 2

    ONHAND = 3

    RESERVE = 4

    SHIP = 5

    BACK_ORDER = 6


class Response(object):

    CODE_STOCK_NOT_FOUND = stock_pb2.StockCommonResponse.Code.STOCK_NOT_FOUND

    raw: stock_pb2.StockCommonResponse

    def __init__(self, raw_response):
        self.raw = raw_response

    @property
    def success(self):
        return self.raw.status == 0

    @property
    def code(self):
        return self.raw.code

    @property
    def msg(self):
        return self.raw.msg

    @property
    def stock(self):
        return self.raw.stock


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


class CreateRequest(ProtoType):

    goods: int
    stock_qty: int
    stock_status: int

    def __init__(self, **kwargs):
        self.goods = None
        self.stock_qty = None
        self.stock_status = None
        super().__init__(**kwargs)

    def to_message(self):
        return stock_pb2.Stock(goods=self.goods,
                               stock_qty=self.stock_qty, stock_status=self.stock_status)

    def is_valid(self):
        return self.is_not_negetive(self.goods, self.stock_qty, nullable=False)

    def from_message(self, *args):
        pass


class UpdateRequest(ProtoType):
    id: int
    goods: int
    stock_qty: int
    stock_status: int

    def to_message(self):
        return stock_pb2.Stock(id=self.id, goods=self.goods, stock_qty=self.stock_qty)

    def from_message(self, *args):
        pass

    def __init__(self, **kwargs):
        self.id = None
        self.stock_qty = None
        self.goods = None
        self.stock_status = None
        super().__init__(**kwargs)

    def is_valid(self):
        if not self.id or self.id < 0:
            return False
        if not self.is_not_negetive(self.goods, self.stock_qty, nullable=True):
            return False
        return True

    def to_proto(self):
        return stock_pb2.Stock(id=self.id, goods=self.goods,
                               stock_qty=self.stock_qty, stock_status=self.stock_status)


class RetrieveRequest(ProtoType):
    id: int

    def to_message(self):
        return stock_pb2.StockRetrieveRequest(id=self.id)

    def from_message(self, *args):
        pass

    def __init__(self, **kwargs):
        self.id = None
        super().__init__(**kwargs)

    def is_valid(self):
        if not self.id or self.id < 0:
            return False
        return True

    def to_proto(self):
        return stock_pb2.Stock(id=self.id, goods=self.goods,
                               stock_qty=self.stock_qty, stock_status=self.stock_status)


class BackStockReq(ProtoType):
    id: int
    to_reserve_qty: int
    to_onhand: int
    is_delete: bool

    def __init__(self, **kwargs):
        self.id = None
        self.to_reserve_qty = None
        self.to_onhand = None
        self.is_delete = False
        super().__init__(**kwargs)

    def is_valid(self):
        if not self.id or self.id < 0:
            return False
        return True

    def to_message(self):
        return stock_pb2.StockBackRequest(
            id=self.id,
            to_reserve_qty=self.to_reserve_qty,
            to_onhand=self.to_onhand,
            is_delete=self.is_delete
        )

    def from_message(self, *args):
        raise NotImplementedError('Not implement!')


class StockServiceClient(object):
    __create_key = object()
    lock = threading.RLock()
    client = None
    service_stub = None

    def __init__(self, create_key):
        assert (create_key == StockServiceClient.__create_key),\
            "Stock Service is single instance, please use GlobalProductService.get_instance()"
        channel = grpc.insecure_channel('localhost:50052')
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

    def Create(self, req: CreateRequest):
        if not req.is_valid():
            raise Exception('Can not create stock, illegal argument %s' % req)
        res = self.service_stub.Create(req.to_message())
        return Response(res)

    def List(self):
        return self.service_stub.List(stock_pb2.StockListRequest())

    def Retrieve(self, stock_id):
        if stock_id is None or stock_id < 0:
            raise Exception('Illegal argments, id')
        res = self.service_stub.Retrieve(stock_pb2.StockRetrieveRequest(id=stock_id))
        return Response(res)

    def Update(self, stock: UpdateRequest):
        if not stock.is_valid():
            raise Exception('Fail to update, Illegal stock %s'%stock)
        req = stock.to_message()
        print('Update Stock, ', req)
        res = self.service_stub.Update(stock.to_message())
        return Response(res)

    def Destroy(self, stock_id):
        if not stock_id or stock_id < 0:
            raise Exception('Fail to destroy stock, Illegal stock id %s' % stock_id)
        res = self.service_stub.Destroy(stock_pb2.Stock(id=stock_id))
        return Response(res)

    def Reserve(self, stock_qty, goods):
        if stock_qty is None or stock_qty <= 0:
            raise Exception('Fail to Reserve stock, illegal Stock qty %s'%stock_qty)
        if goods is None or goods < 0:
            raise Exception('Fail to Reser stock ,illegal goods %s'%goods)
        return self.service_stub.Reserve(stock_pb2.StockReserveRequest(stock_qty=stock_qty, goods=goods))

    def Back(self, req: BackStockReq):
        if not req.is_valid():
            raise Exception('Can not back stock, illegal argument!')
        res = self.service_stub.Back(req.to_message())
        return Response(res)

    def Ship(self, stock_id):
        if stock_id is None or stock_id < 0:
            raise Exception('Fail to ship stock , illegal stock %s' % stock_id)
        res = self.service_stub.Ship(stock_pb2.StockShipRequest(id=stock_id))
        return Response(res)




