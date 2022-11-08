
import unittest
import time

from goods.gRpc.client.goods_service_stub import GoodsServiceClient as GoodsClient
from goods.gRpc.client.protos import goods_pb2
from goods.gRpc.client.types.goods import CreateRequest, UpdateRequest


class TestClass(unittest.TestCase):

    def test_query(self):
        res = GoodsClient.get_instance().query('123')
        count = 0
        for goods in res:
            print(goods)
            count += 1
        print('count...', count)

    def test_create(self):
        create_req = CreateRequest(goods_code='123', goods_weight=0.01)
        res = GoodsClient.get_instance().Create(create_req)
        assert not res.success
        assert res.code == goods_pb2.Response.Code.MISSING_PARAMETERS

        create_req.goods_image = 'abc'
        res = GoodsClient.get_instance().Create(create_req)
        assert not res.success
        assert res.code == goods_pb2.Response.Code.DUPLICATE_GOODS_CODE

    def test_destroy(self):
        goods_code = 'test_' + str(time.time())
        create_req = CreateRequest(goods_code=goods_code, goods_weight=0.01, goods_image='abc')

        res = GoodsClient.get_instance().Create(create_req)
        print(res.code, res.msg)
        assert res.success

        goods = res.goods

        res = GoodsClient.get_instance().destroy(goods.id)
        assert res.success

        # retrive
        goods_should_not_exist = GoodsClient.get_instance().retrieve(goods.id)
        assert not goods_should_not_exist.success
        assert goods_should_not_exist.code == goods_pb2.Response.Code.GOODS_NOT_FOUND

    def test_update(self):
        goods_code = 'test_' + str(time.time())
        create_req = CreateRequest(goods_code=goods_code, goods_weight=0.01, goods_image='abc')

        res = GoodsClient.get_instance().Create(create_req)
        print(res.code, res.msg)
        assert res.success

        assert res.goods.goods_code == goods_code

        goods = res.goods

        new_goods_code = goods.goods_code + '_update'
        new_goods_image = goods.goods_image + '_update'
        new_goods_weight = goods.goods_weight + 0.1
        new_goods_class = 'class_test_update'
        new_goods_w = 0.1

        update_req = UpdateRequest(
            id=goods.id,
            goods_code=new_goods_code,
            goods_image=new_goods_image,
            goods_weight=new_goods_weight,
            goods_class=new_goods_class,
            goods_w=new_goods_w
        )
        update_res = GoodsClient.get_instance().update(update_req)

        assert update_res.success
        goods_updated = update_res.goods
        assert goods_updated.goods_code == new_goods_code
        assert goods_updated.goods_image == new_goods_image
        assert goods_updated.goods_weight - new_goods_weight < 0.0001
        assert goods_updated.goods_w - new_goods_w < 0.001
        assert goods_updated.goods_class == new_goods_class

        goods_code = 'test_' + str(time.time())
        create_req = CreateRequest(goods_code=goods_code, goods_weight=0.01, goods_image='abc')
        res = GoodsClient.get_instance().Create(create_req)
        assert res.success

        another_goods = None
        exist_goods = GoodsClient.get_instance().list()
        max_goods_id = 0
        for goods_ in exist_goods:
            if goods_.id != goods.id:
                another_goods = goods_
            if goods_.id > max_goods_id:
                max_goods_id = goods_.id
        assert another_goods

        update_req = UpdateRequest(id=another_goods.id, goods_code=new_goods_code)
        res = GoodsClient.get_instance().update(update_req)
        assert not res.success
        assert res.code == goods_pb2.Response.Code.DUPLICATE_GOODS_CODE

        # test destroy
        res = GoodsClient.get_instance().destroy(goods_id=max_goods_id+1)
        assert not res.success
        assert res.code == goods_pb2.Response.Code.GOODS_NOT_FOUND

        res = GoodsClient.get_instance().destroy(goods.id)
        assert res.success

    def test_destroy_not_found(self):
        res = GoodsClient.get_instance().destroy(26)
        assert not res.success




