
import unittest

from supplier.gRpc.supplier_client import SupplierClient, Supplier, CreatePurchasePlanReq


class TestCase(unittest.TestCase):

    def test_create_purchase_plan(self):
        supplier = Supplier(supplier_name='测试')
        req = CreatePurchasePlanReq(price=1.2, url='123', image_url='123', tag='test', goods=[1], supplier=supplier)
        res = SupplierClient.get_instance().create_purchase_plan(req)
        print(res)
        assert res.id
