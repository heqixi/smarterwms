import unittest

from stock.gRpc.client.stock_service_client import UpdateRequest, CreateRequest, StockStatus
from stock.gRpc.client.stock_service_client import StockServiceClient as StockClient
from goods.gRpc.client.types.goods import CreateRequest


class TestClass(unittest.TestCase):

    goods: int

    def test_update(self):
        stock = StockClient.get_instance().retrieve(stock_id=1)
        assert stock is not None
        StockClient.get_instance().Update(UpdateRequest(id=1, stock_qty=22))

    def test_list(self):
        res = StockClient.get_instance().List()
        count = 0
        for obj in res:
            count += 1
        print(count)
        assert count == 0

    def test_create(self):
        StockClient.get_instance().Create(CreateRequest(goods=0, stock_qty=1, stock_status=StockStatus.ONHAND))


