from stock.models import StockListModel as Stock

from stock.gRpc.servers.protos.stock import stock_pb2
from stock.gRpc.servers.utils.Utils import stock_model_to_message


class Success(object):
    stock: Stock

    def __init__(self, stock=None):
        self.stock = stock
        self.status = stock_pb2.StockCommonResponse.Status.SUCCESS

    def to_proto(self):
        stock_proto = stock_model_to_message(self.stock)
        return stock_pb2.StockCommonResponse(stock=stock_proto, status=self.status)


class Error(object):

    msg: str

    @property
    def code(self):
        return stock_pb2.StockCommonResponse.Code.UNKNOW

    def to_proto(self):
        return stock_pb2.StockCommonResponse(
            status=stock_pb2.StockCommonResponse.Status.FAIL, code=self.code, msg=self.msg)


class UnknowError(Error):

    def __init__(self, msg='Unknow Error'):
        self.msg = msg

    @property
    def code(self):
        return stock_pb2.StockCommonResponse.Code.UNKNOW


class StockNotFoundError(Error):

    def __init__(self, msg='Stock not found'):
        self.msg = msg

    @property
    def code(self):
        return stock_pb2.StockCommonResponse.Code.STOCK_NOT_FOUND


class GoodsNotFoundError(Error):

    def __init__(self, msg='Goods not found'):
        self.msg = msg

    @property
    def code(self):
        return stock_pb2.StockCommonResponse.Code.GOODS_NOT_FOUND


class IllegalParametersError(Error):

    def __init__(self, msg='Illegal Parameters'):
        self.msg = msg

    @property
    def code(self):
        return stock_pb2.StockCommonResponse.Code.ILLEGAL_PARAMETERS


class MissingParametersError(Error):

    def __init__(self, msg='Missing Parameters'):
        self.msg = msg

    @property
    def code(self):
        return stock_pb2.StockCommonResponse.Code.MISSING_PARAMETERS


class IllegelStockStatusError(Error):

    def __init__(self, msg='Illegal stock status'):
        self.msg = msg

    @property
    def code(self):
        return stock_pb2.StockCommonResponse.Code.ILLEGAL_STOCK_STATUS


class NotEnoughStockError(Error):

    def __init__(self, msg='Not enouth stock'):
        self.msg = msg

    @property
    def code(self):
        return stock_pb2.StockCommonResponse.Code.NOT_ENOUGH_STOCK

