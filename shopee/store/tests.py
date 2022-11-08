from django.test import TestCase

from store.models import StoreProductModel, StoreModel, StoreProductOptionModel, StoreProductOptionItemModel, \
    StoreProductMedia, StoreProductVariantModel
from store.serializers import StoreGlobalProductEmitDataSerializer
from globalproduct.gRpc.client.global_product import ProductServiceClient
from globalproduct.gRpc.client.types.global_product import ProductDetails, Product, ProductStatus, RetrieveRequest, \
    FieldSelector
from globalproduct.gRpc.client.protos import product_pb2


class TestClass(TestCase):

    def setUp(self):
        self._create_store_product()

    def _create_store_product(self):
        StoreModel.objects.create(name='Merchant', uid='1', type=1, platform=1, area='CN', status=1)
        store_br = StoreModel.objects.create(name='Brazil', uid='2', type=2, platform=1, area='BR', status=1)
        product = StoreProductModel.objects.create(store=store_br,
                                                   product_id='1',
                                                   product_name='test_1',
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

    def test_create_from_global_product(self):
        store = StoreModel.objects.get(uid='1')
        product = ProductServiceClient.get_instance().create_from_global_product(38, store)
        self._assert_store_product_and_global(product, 38)

    def test_get_global_product(self):
        global_product = StoreProductModel.objects.get(product_sku='L-MJX-DZSB-020')
        first_spec = StoreProductOptionModel.objects.get(store_product=global_product, index=0)
        first_spec_options = StoreProductOptionItemModel.objects.filter(store_product_option=first_spec).all()
        second_spec = StoreProductOptionModel.objects.get(store_product=global_product, index=1)
        second_spec_options = StoreProductOptionItemModel.objects.filter(store_product_option=second_spec).all()
        product_media = StoreProductMedia.objects.filter(store_product=global_product)
        assert product_media.count() == 8
        serializer = StoreGlobalProductEmitDataSerializer(global_product)
        product_details = ProductDetails.from_shopee_product(serializer.data)
        res = ProductServiceClient.get_instance().create(product_details)

        print(res.code, res.msg)

        assert res.code == product_pb2.ActionCode.SUCCESS
        assert res.product.id is not None
        assert res.product.name == global_product.product_name
        assert res.product.image == global_product.image_url
        assert res.product.sku == global_product.product_sku
        assert not res.product.second_hand
        assert res.product.desc == global_product.description

        # assert product media

        _first_spec = res.extra.firstSpec
        assert _first_spec.id is not None
        assert _first_spec.product_id == res.product.id
        assert _first_spec.name == first_spec.name
        assert _first_spec.index == first_spec.index

        for opt in first_spec_options:
            _opt = list(filter(lambda x: x.index == opt.index, _first_spec.options))[0]
            assert _opt.name == opt.name
            assert _opt.spec_index == _first_spec.id
            assert _opt.image == opt.image_url
            assert _opt.index == opt.index

        _second_spec = res.extra.secondSpec
        assert _second_spec.id is not None
        assert _second_spec.product_id == res.product.id
        assert _second_spec.name == second_spec.name
        assert _second_spec.index == second_spec.index

        for opt in second_spec_options:
            _opt = list(filter(lambda x: x.index == opt.index, _second_spec.options))[0]
            assert _opt.name == opt.name
            assert _opt.spec_index == _second_spec.id
            assert _opt.image == opt.image_url
            assert _opt.index == opt.index

    def test_product_retrive(self):
        global_product = StoreProductModel.objects.get(product_sku='L-MJX-DZSB-020')
        first_spec = StoreProductOptionModel.objects.get(store_product=global_product, index=0)
        first_spec_options = StoreProductOptionItemModel.objects.filter(store_product_option=first_spec).all()
        second_spec = StoreProductOptionModel.objects.get(store_product=global_product, index=1)
        second_spec_options = StoreProductOptionItemModel.objects.filter(store_product_option=second_spec).all()
        serializer = StoreGlobalProductEmitDataSerializer(global_product)
        product_details = ProductDetails.from_shopee_product(serializer.data)
        res = ProductServiceClient.get_instance().create(product_details)

        assert res.code == product_pb2.ActionCode.SUCCESS
        assert res.product.id is not None
        remote_product_id = res.product.id
        field_selector = FieldSelector(specification=True, option=True, models=True)
        retrieve_req = RetrieveRequest(id=remote_product_id, field_selector=field_selector)
        res = ProductServiceClient.get_instance().retrieve(retrieve_req)

        assert res.code == product_pb2.ActionCode.SUCCESS
        assert res.product.name == global_product.product_name
        assert res.product.image == global_product.image_url
        assert res.product.sku == global_product.product_sku
        assert res.product.second_hand == False
        assert res.product.desc == global_product.description

        _first_spec = res.extra.firstSpec
        assert _first_spec.id is not None
        assert _first_spec.product_id == res.product.id
        assert _first_spec.name == first_spec.name
        assert _first_spec.index == first_spec.index

        for opt in first_spec_options:
            _opt = list(filter(lambda x: x.index == opt.index, _first_spec.options))[0]
            assert _opt.name == opt.name
            assert _opt.spec_index == _first_spec.id

        _second_spec = res.extra.secondSpec
        assert _second_spec.id is not None
        assert _second_spec.product_id == res.product.id
        assert _second_spec.name == second_spec.name
        assert _second_spec.index == second_spec.index

        for opt in second_spec_options:
            _opt = list(filter(lambda x: x.index == opt.index, _second_spec.options))[0]
            assert _opt.name == opt.name
            assert _opt.spec_index == _second_spec.id

    def _assert_store_product_and_global(self, store_product, remote_product_id):

        first_spec = StoreProductOptionModel.objects.get(store_product=store_product, index=0)
        first_spec_options = StoreProductOptionItemModel.objects.filter(store_product_option=first_spec).all()
        second_spec = StoreProductOptionModel.objects.get(store_product=store_product, index=1)
        second_spec_options = StoreProductOptionItemModel.objects.filter(store_product_option=second_spec).all()

        field_selector = FieldSelector(specification=True, option=True, models=True, media=True)
        retrieve_req = RetrieveRequest(id=remote_product_id, field_selector=field_selector)
        res = ProductServiceClient.get_instance().retrieve(retrieve_req)

        assert res.code == product_pb2.ActionCode.SUCCESS
        assert res.product.name == store_product.product_name
        assert res.product.image == store_product.image_url
        assert res.product.sku == store_product.product_sku
        assert res.product.second_hand == False
        assert res.product.desc == store_product.description

        store_product_media_list = store_product.product_media.all()
        assert len(res.extra.media) == store_product_media_list.count()
        for global_media in res.extra.media:
            store_product_media = store_product_media_list.filter(type=global_media.type, index=global_media.index).first()
            assert store_product_media
            assert store_product_media.url == global_media.url

        variants = store_product.product_variant.all()
        for variant in variants:
            global_model = [m for m in res.extra.models if m.sku == variant.model_sku][0]
            assert global_model
            assert global_model.sku == variant.model_sku
            assert global_model.options_index == variant.option_item_index

            model_stock = variant.variant_stock.first()
            if model_stock or global_model.stock_qty is not None:
                assert model_stock.current_stock == global_model.stock_qty
            model_price = variant.variant_price.first()
            if model_price or global_model.price is not None:
                assert model_price.original_price == global_model.price

        _first_spec = res.extra.firstSpec
        assert _first_spec.id is not None
        assert _first_spec.product_id == res.product.id
        assert _first_spec.name == first_spec.name
        assert _first_spec.index == first_spec.index

        for opt in first_spec_options:
            _opt = list(filter(lambda x: x.index == opt.index, _first_spec.options))[0]
            assert _opt.name == opt.name
            assert _opt.spec_index == _first_spec.id

        _second_spec = res.extra.secondSpec
        assert _second_spec.id is not None
        assert _second_spec.product_id == res.product.id
        assert _second_spec.name == second_spec.name
        assert _second_spec.index == second_spec.index

        for opt in second_spec_options:
            _opt = list(filter(lambda x: x.index == opt.index, _second_spec.options))[0]
            assert _opt.name == opt.name
            assert _opt.spec_index == _second_spec.id


