from django.test import TestCase

from stock.models import StockRecord
from stock.services.stockprovider import StockService, StockBean


class TestClass(TestCase):

    def setUp(self) -> None:
        pass
        # record = StockService.get_instance().add_shipping_stock(10, 1)

    def test_add_shipping_stock(self):
        test_goods_code = 'test_1'
        test_goods_image = 'test_goods_image'
        stock_bean = StockBean(stock_qty=10, goods_code=test_goods_code, goods_image=test_goods_image)
        record = StockService.get_instance().add_shipping_stock(stock_bean)
        self._assert_create_update(record, stock_bean, 12)

    def test_reserve_ship_back_stock(self):
        test_goods_code = 'test_goods_code_reserve_stock'
        test_goods_image = 'test_goods_image_reserve_stock'
        stock_bean = StockBean(stock_qty=10, goods_code=test_goods_code, goods_image=test_goods_image)
        record = StockService.get_instance().reserve_stock(stock_bean)
        record = self._assert_create_update(record, stock_bean, 11)

        stock_id = record.stock_id
        stock_qty = record.stock_qty
        stock_status = record.stock_status
        goods_id = record.goods_id
        goods_code = record.goods_code
        goods_image = record.goods_image

        onhand_stock_count = self._get_on_hand_stock(goods_id)
        if onhand_stock_count <= stock_qty:
            # make sure onhand stock count greater then stock qty to ship
            from stock.gRpc.client.stock_service_client import StockServiceClient as StockClient, CreateRequest
            res = StockClient.get_instance().Create(
                CreateRequest(goods_id=goods_id, stock_status=3, stock_qty=stock_qty + 1))
            assert res
            onhand_stock_count = self._get_on_hand_stock(goods_id)
        assert onhand_stock_count > stock_qty
        print('before ship goods_id', goods_id, onhand_stock_count)

        # ship stock
        record_ship = StockService.get_instance().ship_reserve_stock(record)
        print('after ship ', record_ship.stock_id, record_ship.stock_qty)
        assert record_ship.stock_id == stock_id
        assert record_ship.stock_status == StockRecord.SHIP_STOCK
        assert record_ship.stock_qty == stock_qty
        assert record_ship.goods_id == goods_id
        assert record_ship.goods_code == goods_code
        assert record_ship.goods_image == goods_image

        # check if current onhand stock qty == previous_onhand_count - ship qty
        shipped_qty = record_ship.stock_qty
        onhand_stock_count_after_ship = self._get_on_hand_stock(goods_id)
        assert onhand_stock_count_after_ship == onhand_stock_count - shipped_qty
        print('after ship goods_id', goods_id, onhand_stock_count_after_ship)

        # back stock
        to_reserve_qty = 1
        assert stock_qty > to_reserve_qty
        record_back = StockService.get_instance().back_stock(record_ship, to_reserve_qty)
        print('after back ', record_back.stock_id, record_back.stock_qty)
        assert record_back.stock_qty == to_reserve_qty
        assert record_back.stock_id == stock_id
        assert record_back.stock_status == StockRecord.RESERVE_STOCK
        assert record_back.goods_id == goods_id
        assert record_back.goods_code == goods_code
        assert record_back.goods_image == goods_image

        # When a stock is back, all stock that had shipped should back to onhand stock
        onhand_stock_count_after_back = self._get_on_hand_stock(goods_id)
        print('after back ship goods_id', goods_id, onhand_stock_count_after_ship)
        assert onhand_stock_count_after_back == onhand_stock_count_after_ship + shipped_qty


    def _get_on_hand_stock(self, goods_id):
        stocks = [stock for stock in StockService.get_instance().get_onhand(goods_id)]
        assert len(stocks) == 1  # For onhand stock, must exist one and only one stock object
        stock = stocks[0]
        assert stock.goods == goods_id
        assert stock.stock_status == 3  # onhand status
        assert stock.stock_qty >= 0
        return stocks[0].stock_qty

    def _assert_create_update(self, record: StockRecord, stock_bean: StockBean, stock_status):
        print('record ', record.goods_id, record.stock_qty, record.stock_id, record.stock_status)
        assert record is not None
        assert record.goods_id
        assert record.goods_code == stock_bean.goods_code
        assert record.stock_qty == stock_bean.stock_qty
        assert record.stock_status == stock_status

        stock = StockService.get_instance().retrieve(record.stock_id)
        assert stock.id == record.stock_id
        assert stock.stock_status == record.stock_status
        assert stock.stock_qty == record.stock_qty
        assert stock.goods_image == record.goods_image
        assert stock.goods_code == record.goods_code

        update_count = 5
        record_update_qty = StockService.get_instance().update_stock_qty(record, 5)
        print('goods code of stock ', record.goods_code, record_update_qty.goods_code)
        assert record_update_qty
        assert record_update_qty.stock_qty == update_count
        assert record_update_qty.stock_id == record.stock_id
        assert record_update_qty.stock_status == record.stock_status
        assert record_update_qty.goods_id == record.goods_id
        assert record_update_qty.goods_code == record.goods_code
        assert record_update_qty.goods_image == record.goods_image

        assert record_update_qty.goods_id != 1

        record_update_goods = StockService.get_instance().update_stock_goods(record, 1)
        print('goods code of stock ', record_update_goods.goods_code, record_update_qty.goods_code)
        assert record_update_goods
        assert record_update_goods.stock_qty == record_update_qty.stock_qty
        assert record_update_goods.stock_id == record_update_qty.stock_id
        assert record_update_goods.stock_status == record_update_qty.stock_status
        assert record_update_goods.goods_id == 1
        return record_update_goods

    def test_back_stock(self):
        record = StockRecord.objects.get(id=1)
        StockService.get_instance().back_stock(record, to_reserve_qty=10)

    def test_reserve(self):
        record = self._reserve(stock_qty=10, goods_id=1)
        print('record ', record.stock_id, record.stock_qty, record.goods_id)
        self._assert_exist(record)

    def test_reserve_and_ship(self):
        record = self._reserve(11, 1)
        self._assert_exist(record)

        self._ship(record)
        self._assert_ship(record)

    def test_ship_partial(self):
        record = self._reserve(11, 1)
        self._assert_exist(record)




    def test_ship_and_rollback(self):
        record = self._reserve(12, 1)


    def _ship(self, record):
        record = StockService.get_instance().ship_reserve_stock(record)
        self._assert_exist(record)

    def _assert_ship(self, record):
        stock = self._assert_exist(record)
        assert stock.stock_status == StockRecord.SHIP_STOCK

    def _reserve(self, stock_qty, goods_id):
        record = StockService.get_instance().reserve_stock(stock_qty, goods_id)
        assert record is not None
        assert record.stock_qty == stock_qty
        assert record.goods_id == goods_id
        assert record.stock_id
        assert record.stock_status == StockRecord.RESERVE_STOCK
        return record

    def _assert_exist(self, record):
        stock = StockService.get_instance().retrieve(record.stock_id)
        assert stock.stock_qty == record.stock_qty
        assert stock.id == record.stock_id
        assert stock.goods == record.goods_id
        assert stock.goods_code == record.goods_code
        assert stock.goods_image == record.goods_image
        assert stock.stock_status == record.stock_status
        return stock





