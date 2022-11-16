import time

from django.test import TestCase

from goods.models import GoodsRecord
from store.models import StoreModel, StoreProductModel, StoreProductMedia, StoreProductVariantModel, \
    StoreProductOptionModel, StoreProductOptionItemModel, ProductSupplierInfo


def _get_variant_image(variant: StoreProductVariantModel):
    index = variant.option_item_index.split(',')[0]
    option = variant.store_product.product_option.filter(index=0).first()
    first_option_item = StoreProductOptionItemModel.objects.filter(
        store_product=variant.store_product, index=index, store_product_option=option).first()
    return first_option_item.image_url if first_option_item else None


class TestClass(TestCase):

    def setUp(self) -> None:
        self.test_product_sku = 'test_product_sku_' + str(int(time.time()))
        product = self._create_store_product()

    def test_register_purchase_plan(self):
        from supplier.supplier_register import SupplierRegister
        print(self.test_product_sku)
        product = StoreProductModel.objects.filter(product_sku=self.test_product_sku).first()
        self._create_goods_group(product)
        purchase_record = SupplierRegister.get_instance().register_purchase_plan(product.id)
        assert purchase_record
        assert purchase_record.id
        assert purchase_record.purchase_id
        assert purchase_record.product_id == product.id

    def _create_goods_group(self, product: StoreProductModel):
        from goods.gRpc.client.goods_service_stub import GoodsServiceClient, CreateGroupRequest
        from goods.gRpc.client.types.goods import Goods
        goods = []
        for variant in product.product_variant.all():
            goods.append(Goods(
                goods_code=variant.model_sku,
                goods_image=_get_variant_image(variant)
            ))
        req = CreateGroupRequest(name=product.product_sku, goods=goods)
        group_record = GoodsServiceClient.get_instance().create_group(req)
        assert group_record
        assert group_record.id
        assert group_record.name == req.name
        goods_records = GoodsRecord.objects.filter(group_id=group_record.id).all()
        assert goods_records.count() == len(goods)
        for g in goods:
            goods_record = goods_records.filter(goods_code=g.goods_code).first()
            assert goods_record
            assert goods_record.goods_id
            assert goods_record.goods_image == g.goods_image

    def _create_store_product(self):
        StoreModel.objects.create(name='Merchant', uid='1', type=1, platform=1, area='CN', status=1)
        store_br = StoreModel.objects.create(name='Brazil', uid='2', type=2, platform=1, area='BR', status=1)
        product = StoreProductModel.objects.create(store=store_br,
                                                   product_id='1',
                                                   product_name=self.test_product_sku,
                                                   product_status='NORMAL',
                                                   product_sku='L-MJX-DZSB-020',
                                                   image_url='https://cf.shopee.com.br/file/4295f281893d835edb009320f7fceed1',
                                                   category_id=101034,
                                                   brand_id=0,
                                                   brand_name='NoBrand',
                                                   days_to_ship=3,
                                                   weight=0.01,
                                                   length=0.01,
                                                   height=0.01,
                                                   description='test'
                                                   )
        for i in range(8):
            StoreProductMedia.objects.create(
                openid=product.openid,
                creater=product.creater,
                store_product=product,
                type=2,
                url='https://cbu01.alicdn.com/img/ibank/O1CN01b2X34X26om1TzNIC6_!!2213968467709-0-cib.jpg_300x300.webp',
                index=i
            )
        for i in range(10):
            StoreProductVariantModel.objects.create(
                store_product=product,
                openid=product.openid,
                creater=product.creater,
                model_sku=product.product_sku + '_model_' + str(i),
                option_item_index=i
            )
        first_spec = StoreProductOptionModel.objects.create(
            store_product=product,
            name=product.product_sku + '_first_spec',
            index=0
        )
        for i in range(10):
            option = StoreProductOptionItemModel.objects.create(
                store_product=product,
                store_product_option=first_spec,
                name=product.product_sku + '_option_' + str(i),
                image_url='https://cbu01.alicdn.com/img/ibank/O1CN01zfd53n26om1TT9Xfo_!!2213968467709-0-cib.jpg_300x300.webp',
                index=i
            )
        second_spec = StoreProductOptionModel.objects.create(
            store_product=product,
            name=product.product_sku + '_second_spec',
            index=1
        )
        for i in range(15):
            option = StoreProductOptionItemModel.objects.create(
                store_product=product,
                store_product_option=second_spec,
                name=second_spec.name + '_option_' + str(i),
                image_url='',
                index=i
            )
        supplier_info = ProductSupplierInfo.objects.create(
            openid=product.openid,
            creater=product.creater,
            product=product,
            price=1.0,
            url='123'
        )
        return product



