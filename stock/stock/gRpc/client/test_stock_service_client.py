import unittest

from stock.gRpc.client.stock_service_client import StockUpdateModel
from stock.gRpc.client.stock_service_client import StockServiceClient as Client


class TestClass(unittest.TestCase):

    goods: int

    def test_i(self):
        _stock = StockUpdateModel(1)
        assert _stock.is_valid()

    def test_update(self):
        stock = Client.get_instance().Retrieve(stock_id=1)
        assert stock is not None
        Client.get_instance().Update(StockUpdateModel(id=1, stock_qty=22))

    def test_list(self):
        res = Client.get_instance().List()
        count = 0
        for obj in res:
            count += 1
        print(count)
        assert count == 951

