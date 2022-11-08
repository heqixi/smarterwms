import threading
import grpc
import logging

from django.db import transaction

from globalproduct.gRpc.client.protos import product_pb2_grpc, product_pb2
from globalproduct.gRpc.client.types.global_product import QueryRequest, ProductDetails, RetrieveRequest, \
    ProductResponse, FieldSelector
from globalproduct.models import GlobalProductRelations
from store.models import StoreProductModel, StoreProductOptionModel, StoreProductOptionItemModel, \
    StoreProductVariantModel, StoreProductVariantStock, StoreProductPriceInfoModel, StoreProductMedia

logger = logging.getLogger()


class ProductServiceClient(object):
    __create_key = object()
    lock = threading.RLock()
    client = None
    service_stub = None

    def __init__(self, create_key):
        assert (create_key == ProductServiceClient.__create_key), \
            "Stock Service is single instance, please use GlobalProductService.get_instance()"
        channel = grpc.insecure_channel('192.168.2.75:50053')
        self.service_stub = product_pb2_grpc.ProductControllerStub(channel)

    @classmethod
    def get_instance(cls):
        if cls.client is None:
            cls.lock.acquire()
            if cls.client is None:
                cls.client = cls(ProductServiceClient.__create_key)
            cls.lock.release()
            return cls.client
        return cls.client

    def query_by_sku(self, query: QueryRequest):
        if not query.is_valid():
            raise Exception('Illegal query')
        return self.service_stub.Query(query.to_message())

    def query(self, query: QueryRequest):
        if not query.is_valid():
            raise Exception('Illelga query')
        return self.service_stub.Query(query.to_message())

    def retrieve(self, req: RetrieveRequest):
        if not req.is_valid():
            raise Exception('Can not retrieve product, msg: %s' % req.msg)
        response_message = self.service_stub.Retrieve(req.to_message())
        return ProductResponse(response_message)

    def create(self, product_details: ProductDetails):
        if not product_details.is_valid(True):
            raise Exception('Illegal product details')
        res = self.service_stub.Create(product_details.to_message())
        return ProductResponse(res)

    def create_from_shopee(self, shopee_product: dict):
        global_product_id = None
        global_product_relation = GlobalProductRelations.objects.filter(product_id=shopee_product['id']).first()
        if global_product_relation:
            global_product_id = global_product_relation.global_product_id
            # store_product = StoreProductModel.objects.get(id=shopee_product['id'])
            # sync = False
            # for shop_product in store_product.shop_products.all():
            #     shop_product_relation = GlobalProductRelations.objects.filter(
            #         product_id=shop_product.id).first()
            #     if not shop_product_relation:
            #         sync = True
            #         break
            # if not sync:
            #     # TODO
            #     logger.info('global relations exists, no need to sync %s ', shopee_product['id'])
            #     return True
        product_details = ProductDetails.from_shopee_product(shopee_product, global_product_id)
        if product_details.is_valid(True):
            message = self.service_stub.Create(product_details.to_message())
            res = ProductResponse(message)
            if res.success:
                store_product = StoreProductModel.objects.get(id=shopee_product['id'])
                self._bind_global_product(store_product, res.product.id)
            else:
                raise Exception('create product from shopee fail!')
            return res.product

    def get_by_shopee_product(self, shopee_product: StoreProductModel, ):
        global_product_relations = GlobalProductRelations.objects.filter(product=shopee_product).first()
        if not global_product_relations:
            raise Exception('Get by shopee product fail, no related global product')
        global_product_id = global_product_relations.global_product_id
        fields = FieldSelector(specification=True, option=True, models=True)
        return self.retrieve(RetrieveRequest(id=global_product_id,field_selector=fields))

    def create_raw(self):
        res = self.service_stub.Create(product_pb2.ProductDetails())
        return res

    def _bind_global_product(self, store_product: StoreProductModel, global_product_id):
        global_product_relations = GlobalProductRelations.objects.filter(product=store_product).first()
        if not global_product_relations:
            global_product_relation = GlobalProductRelations.objects.create(
                openid=store_product.openid,
                creater=store_product.creater,
                global_product_id=global_product_id,
                product=store_product,
                store=store_product.store
            )
        for shop_product in store_product.shop_products.all():
            self._bind_global_product(shop_product, global_product_id)

    @transaction.atomic
    def create_from_global_product(self, global_product_id, store):
        field_selector = FieldSelector(specification=True, option=True, models=True, media=True)
        req = RetrieveRequest(id=global_product_id, field_selector=field_selector)
        res = self.retrieve(req)
        if not res.success:
            raise Exception('Fail to retrive global product of id %s, code: %s, msg: %s' % (global_product_id, res.code, res.msg))
        else:
            logger.info('create from global product success')
            gp_extra = res.extra
            global_product_relation = GlobalProductRelations.objects.filter(global_product_id=global_product_id, store=store).first()
            if global_product_relation and global_product_relation.product:
                store_product = global_product_relation.product
            else:
                store_product = self._create_store_product_from_gp(res.product, store)
                GlobalProductRelations.objects.create(
                    openid=store_product.openid,
                    creater=store_product.creater,
                    global_product_id=global_product_id,
                    product=store_product,
                    store=store
                )
            if gp_extra.media:
                self._create_product_media_from_gp(store_product, gp_extra.media)
            gp_extra_first_spec = gp_extra.firstSpec
            if gp_extra_first_spec:
                self._create_spec_from_gp(store_product, gp_extra_first_spec)
            gp_extra_second_spec = gp_extra.secondSpec
            if gp_extra_second_spec:
                self._create_spec_from_gp(store_product, gp_extra_second_spec)
            gp_models = gp_extra.models
            if gp_models:
                self._create_models_from_gp(store_product, gp_models)
            return store_product

    def _create_store_product_from_gp(self, product, store):
        store_product = StoreProductModel.objects.create(
            store=store,
            product_name=product.name,
            product_status=StoreProductModel.Status.EDIT,
            product_sku=product.sku,
            image_url=product.image,
            description=product.desc,
            openid=store.openid,
            creater=store.creater
        )
        return store_product

    def _create_spec_from_gp(self, store_product: StoreProductModel, spec):
        spec_obj = StoreProductOptionModel.objects.filter(store_product=store_product, index=spec.index).first()
        if not spec_obj:
            spec_obj = StoreProductOptionModel.objects.create(
                openid=store_product.openid,
                creater=store_product.creater,
                name=spec.name,
                index=spec.index,
                store_product=store_product
            )
        else:
            spec_obj.name = spec.name
            spec_obj.save()
        if spec.options:
            spec_options = StoreProductOptionItemModel.objects.filter(store_product=store_product, store_product_option=spec_obj)
            for option in spec.options:
                option_of_index = spec_options.filter(index=option.index)
                if not option_of_index:
                    StoreProductOptionItemModel.objects.create(
                        openid=store_product.openid,
                        creater=store_product.creater,
                        name=option.name,
                        index=option.index,
                        image_url=option.image,
                        store_product=store_product,
                        store_product_option=spec_obj
                    )
                else:
                    option_of_index.name = option.name
                    option_of_index.image_url = option.image,
                    option_of_index.save()
        return spec

    def _create_models_from_gp(self, store_product: StoreProductModel, gp_models):
        variants_of_product = StoreProductVariantModel.objects.filter(store_product=store_product)
        for gp_model in gp_models:
            options_index = gp_model.options_index
            if not options_index:
                raise Exception('gp_model missing option index sku: %s' % gp_model.sku)
            for index in options_index.split(','):
                if not StoreProductOptionItemModel.objects.filter(store_product=store_product, index=index).exists():
                    raise Exception('gp_model of option index %s not found or created' % index)
            variant = variants_of_product.filter(model_sku=gp_model.sku).first()
            if not variant:
                variant = StoreProductVariantModel.objects.create(
                    openid=store_product.openid,
                    creater=store_product.creater,
                    model_sku=gp_model.sku,
                    option_item_index=gp_model.options_index,
                    store_product=store_product
                )
            else:
                variant.option_item_index = gp_model.options_index
                variant.save()
            variant_stock = variant.variant_stock.filter(is_delete=False).first()
            if not variant_stock:
                StoreProductVariantStock.objects.create(
                    openid=store_product.openid,
                    creater=store_product.creater,
                    current_stock=gp_model.stock_qty,
                    variant=variant
                )
            else:
                variant_stock.current_stock = gp_model.stock_qty
                variant_stock.save()
            variant_price_info = variant.variant_price.filter(is_delete=False).first()
            if not variant_price_info:
                StoreProductPriceInfoModel.objects.create(
                    openid=store_product.openid,
                    creater=store_product.creater,
                    original_price=gp_model.price,
                    store_product=store_product,
                    variant=variant
                )
            else:
                variant_price_info.original_price = gp_model.price

    def _create_product_media_from_gp(self, store_product, media_list):
        store_product_media = getattr(store_product, StoreProductModel.RelativeFields.PRODUCT_MEDIA)
        for global_media in media_list:
            _media = store_product_media.filter(index=global_media.index, type=global_media.type).first()
            if not _media:
                _media = StoreProductMedia.objects.create(
                    openid=store_product.openid,
                    creater=store_product.creater,
                    store_product=store_product,
                    url=global_media.url,
                    index=global_media.index,
                    type=global_media.type
                )
            else:
                _media.url = global_media.url
                _media.save()





