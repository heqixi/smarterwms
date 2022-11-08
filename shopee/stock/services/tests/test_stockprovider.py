import unittest

from stock.services.stockprovider import StockService
from stock.gRpc.client.stock_service_client import CreateRequest, StockServiceClient as StockClient, StockStatus
from goods.gRpc.client.goods_service_stub import GoodsServiceClient as GoodsClient
from goods.gRpc.client.types.goods import CreateRequest as GoodsCreateReq


class TestCase(unittest.TestCase):

    def create_goods(self):
        res = GoodsClient.get_instance().Create(GoodsCreateReq(goods_code='test', goods_image='test_image_url', goods_weight=0.1))
        assert res.success
        return res.goods.id

    def test_add_shipping_stock(self):
        goods_id = self.create_goods()
        StockService.get_instance().add_shipping_stock(1, '123')

    def test_update_stock_qty(self):
        StockService.get_instance().update_stock_qty(2, 21)

    def test_ship_stock(self):
        StockService.get_instance().ship_reserve_stock(1)

    def test_ship_reserve_stock(self):
        StockService.get_instance().ship_reserve_stock(2)

    def test_create_stock(self):
        req = CreateRequest(goods=1, stock_qty=10, stock_status=StockStatus.ONHAND)
        res = StockClient.get_instance().Create(req)
        assert not res.success
        assert res.code == 2

        req = CreateRequest(goods=0, stock_qty=10, stock_status=StockStatus.ONHAND)
        res = StockClient.get_instance().Create(req)
        print(res.code, res.msg)
        assert res.success
        assert res.stock.id is not None
        assert res.stock.stock_qty == 10
        assert res.stock.stock_status == StockStatus.ONHAND



