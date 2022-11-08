from django.test import TestCase, Client
from userprofile.models import Users

import json

from stock.models import StockRecord
from stock.services.stockprovider import StockService
from supplier.models import ListModel as Supplier, PurchasePlan

from asn.models import AsnListModel, AsnDetailModel


class TestClass(TestCase):

    def test_create_purchase_stock(self):
        pass
        # record = StockService.get_instance().create_purchased_stock(19, 1)
        # assert record
        # assert record.goods_id == 1
        # assert record.stock_qty == 19
        # assert record.stock_status == StockRecord.PURCHASED_STOCK

    def test_create_sorted_stock(self):
        pass
        # record = StockService.get_instance().create_sorted_stock(19, 1)
        # assert record
        # assert record.stock_id
        # assert record.stock_status == StockRecord.SORTED_STOCK
        # assert record.goods_id == 1
        # assert record.stock_qty == 19

    def test_create_asn(self):
        pass

    def _create_asn(self):
        pass


class TestAsnView(TestCase):

    OPEN_ID = '123'

    client = Client(HTTP_TOKEN='123')

    test_string = 'test'

    test_int = 1

    test_float = 1.0

    test_goods_id = 1

    def setUp(self) -> None:
        # setup_test_environment()
        test_ueser = Users.objects.create(
            user_id=1,
            appid='123',
            openid=self.OPEN_ID
        )
        asn = self._create_asn()

    def test_get_asn(self):
        res = self.client.get('/asn/list/', {'openid': '123'}, headers={'Authorization': 'Token {}'.format('123'), 'token': '123'})
        print(res.status_code)
        print(res.content)

    def test_create_asn(self):
        asn = self._create_asn_assert()

    def test_create_asn_and_purchase(self):
        asn = self._create_asn_assert()
        client = Client(HTTP_TOKEN=self.OPEN_ID)
        res = client.put('/asn/list/%s/' % asn.id, data={'id': asn.id, 'asn_status': 1, 'partial': True}, content_type="application/json")
        assert res.status_code == 200
        assert res.content
        asn = AsnListModel.objects.get(id=asn.id)
        self._assert_asn_status(asn, 1, StockRecord.PURCHASED_STOCK)

    def test_create_asn_and_pre_sorted(self):
        asn = self._create_asn_assert()
        client = Client(HTTP_TOKEN=self.OPEN_ID)
        res = client.put('/asn/list/%s/' % asn.id, data={'id': asn.id, 'asn_status': 2, 'partial': True}, content_type="application/json")
        assert res.status_code == 200
        assert res.content
        asn = AsnListModel.objects.get(id=asn.id)
        self._assert_asn_status(asn, 2, StockRecord.PURCHASED_STOCK)

    def test_create_asn_and_sorted(self):
        asn = self._create_asn_assert()
        client = Client(HTTP_TOKEN=self.OPEN_ID)
        res = client.put('/asn/list/%s/' % asn.id, data={'id': asn.id, 'asn_status': 2, 'partial': True}, content_type="application/json")
        assert res.status_code == 200
        assert res.content
        asn = AsnListModel.objects.get(id=asn.id)
        self._assert_asn_status(asn, 2, StockRecord.PURCHASED_STOCK)

        onhand_stock_before_sorted = {}
        self._get_onhand_stock_of_asn(asn, onhand_stock_before_sorted)

        res = client.put('/asn/list/%s/' % asn.id, data={'id': asn.id, 'asn_status': 3, 'partial': True}, content_type="application/json")
        assert res.status_code == 200
        asn = AsnListModel.objects.get(id=asn.id)
        self._assert_asn_status(asn, 3, StockRecord.SORTED_STOCK)

        onhand_stock_after_sorted = {}
        self._get_onhand_stock_of_asn(asn, onhand_stock_after_sorted)

        self._assert_stock_change(asn, onhand_stock_before_sorted, onhand_stock_after_sorted)

    def _assert_stock_change(self, asn, onhand_stock_before_sorted, onhand_stock_after_sorted):
        assert asn.asn_status == 3
        for details in asn.asn_details.all():
            goods_id = details.goods
            goods_actual_qty = details.goods_actual_qty
            goods_damage_qty = details.goods_damage_qty
            assert onhand_stock_after_sorted[goods_id] - onhand_stock_before_sorted[goods_id] == goods_actual_qty - goods_damage_qty

    def _get_onhand_stock_of_asn(self, asn, onhand_stock={}):
        goods_id_lists = []
        for detail in asn.asn_details.all():
            onhand_stock[detail.goods] = 0
            goods_id_lists.append(detail.goods)
        _onhand_stocks = StockService.get_instance().get_onhand_stock(goods_id_list=goods_id_lists)
        for _stock in _onhand_stocks:
            assert _stock.stock_status == StockRecord.ONHAND_STOCK
            onhand_stock[_stock.goods] = _stock.stock_qty

    def _assert_asn_status(self, asn, asn_status, stock_status):
        assert asn.asn_status == asn_status
        for detail in asn.asn_details.all():
            assert detail.stock
            assert detail.stock.stock_status == stock_status
            assert detail.stock.stock_qty == detail.goods_qty
            assert detail.stock.stock_qty == detail.goods_actual_qty
            assert detail.stock.goods_id == detail.goods

            self._assert_stock_record(detail.stock)

    def _assert_stock_record(self, stock_record):
        assert stock_record.stock_id
        _stock = StockService.get_instance().retrieve(stock_record.stock_id)
        assert _stock
        print('assert stock of id', stock_record.stock_id)
        assert _stock.id == stock_record.stock_id
        assert _stock.goods == stock_record.goods_id
        assert _stock.stock_qty == stock_record.stock_qty
        assert _stock.stock_status == stock_record.stock_status

    def _create_asn_assert(self):
        asn = self._create_asn()
        assert asn.asn_status == 0  # 待采购

        asn_dict = self._get_asn(asn.id)
        assert asn_dict['id'] == asn.id
        assert asn_dict['asn_code'] == asn.asn_code
        assert asn_dict['asn_status'] == asn.asn_status

        asn_details = asn_dict['details']
        for detail in asn.asn_details.all():
            assert detail.goods == self.test_int
            assert detail.purchase
            assert detail.goods_qty == self.test_int
            assert detail.goods_actual_qty == self.test_int
            assert detail.stock is None

            _detail = list(filter(lambda x: x['id'] == detail.id, asn_details))[0]
            assert _detail['goods'] == detail.goods
            assert _detail['id'] == detail.id
            assert _detail['goods_qty'] == detail.goods_qty
            assert _detail['goods_actual_qty'] == detail.goods_actual_qty
            assert _detail['stock'] == detail.stock
            assert _detail['purchase'] == detail.purchase.id
        return asn

    def _get_asn(self, asn_id):
        client = Client(HTTP_TOKEN=self.OPEN_ID)
        res = client.get('/asn/list/?asn_details=1')
        print('_get_asn: ', res.status_code)
        assert res.status_code == 200
        assert res.content
        content = json.loads(res.content)
        asn_list = content['results']
        return list(filter(lambda x: x['id'] == asn_id, asn_list))[0]

    def _create_supplier(self):
        return Supplier.objects.create(
            supplier_name='supplier_name_test',
            supplier_city='深圳',
        )

    def _create_asn(self):
        supplier = self._create_supplier()
        asn = AsnListModel.objects.create(
            asn_code='asn_code_test',
            asn_status=0,
            supplier=supplier,
            bar_code='asn_bar_code',
            openid=self.OPEN_ID,
            amend=False
        )
        self._add_asn_detail(asn, supplier)
        return asn

    def _create_purchase(self, supplier):
        purchase_plan = PurchasePlan.objects.create(
            image_url=self.test_string,
            supplier=supplier,
            price=0.1,
            url=self.test_string,
            tag=self.test_string
        )
        return purchase_plan

    def _add_asn_detail(self, asn, supplier):
        purchase = self._create_purchase(supplier)
        for i in range(10):
            asn_detail = AsnDetailModel.objects.create(
                asn=asn,
                goods=self.test_goods_id,
                purchase=purchase,
                goods_qty=self.test_int,
                goods_actual_qty=self.test_int,
                stock=None
            )
