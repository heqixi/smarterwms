
from django.db import transaction
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.exceptions import APIException
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response

from category.serializers import ProductAttributePostSerializer, ProductCategoryBrandPostSerializer
from globalproduct.gRpc.client.global_product import ProductServiceClient
from globalproduct.models import GlobalProductRelations
from store.common import StoreType
from store.models import StoreProductModel, StoreModel, StoreProductMedia, StoreProductOptionModel, \
    StoreProductOptionItemModel, StoreProductVariantModel, StoreProductVariantStock, StoreProductPriceInfoModel
from store.serializers import StoreGlobalProductListGetSerializer, StoreShopProductDetailSerializer
from store.services.store_service import StoreService
from utils.datasolve import parse_float
from .models import ProductCategoryAttribute, ProductCategoryBrand, ProductCategory
from .services.product_service import ProductPublishService

import logging
logger = logging.getLogger()


class GlobalProductView(viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend, OrderingFilter, ]
    ordering_fields = ['id', "create_time", "update_time", ]

    def get_project(self):
        try:
            id = self.kwargs.get('pk')
            return id
        except:
            return None

    def publish_to_shopee(self, request):
        data = self.request.data
        product_id = data.get('id', None)
        if not product_id:
            raise APIException('Must specify product id to publish ')
        stores = data.get('stores', None)
        if not stores:
            raise APIException('Must specify stores id to publish ')
        product = StoreProductModel.objects.filter(id=product_id).first()
        if not product:
            raise APIException('Can not find product of id %s ' % product_id)
        shop_of_same_merchant = []
        for store_uid in stores:
            store = StoreService.get_instance().get_store_by_uid(store_uid)
            if store['type'] == StoreType.SHOP:
                found = False
                for merchant, shopes in shop_of_same_merchant:
                    if merchant['id'] == store['merchant']['id']:
                        found = True
                        shopes.append(store)
                if not found:
                    shop_of_same_merchant.append((store['merchant'], [store]))
        for merchant, shopes in shop_of_same_merchant:
            ProductPublishService.get_instance().publish_shopee(product, merchant['uid'], shopes)
        return Response('success', status=200)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            raise Exception('Improper Denpendency') #TODO
            # return serializers.GlobalProductGetSerializers
        if self.action in ['create', 'update', 'partial_update', 'publish_to_shopee']:
            raise Exception('Improper Denpendency')  # TODO
            # return serializers.GlobalProductSerializers
        else:
            return self.http_method_not_allowed(request=self.request)

    def claim_global_product(self, request, *args, **kwargs):
        data = request.data
        print('claim product data ', data)
        global_product_ids = data.get('global_product_ids', [])
        store_id = data.get('store_id', [])
        force_update = data.get('force_update', False)
        if not global_product_ids:
            raise APIException('Missing global product id')
        if store_id is None:
            raise APIException('Missing merchant id')
        store = StoreModel.objects.filter(id=store_id).first()
        if not store:
            raise APIException('Store of id %s not found' % store_id)
        success_list = []
        fail_list = []
        res = {
            'success_list': success_list,
            'fail_list': fail_list
        }
        for global_product_id in global_product_ids:
            store_product = None
            global_relation = GlobalProductRelations.objects.filter(global_product_id=global_product_id, store=store, is_delete=False).first()
            if force_update or not (global_relation and global_relation.product):
                try:
                    store_product = ProductServiceClient.get_instance().create_from_global_product(
                        int(global_product_id),
                        store)
                except Exception as e:
                    fail_list.append({
                        'global_product_id': global_product_id,
                        'msg': str(e)
                    })
            else:
                store_product = global_relation.product
            if store_product:
                success_list.append({
                    'global_product_id': global_product_id,
                    'store_product_id': store_product.id
                })
        print('claim product res', res)
        return Response(res, status=200)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        data = request.data
        global_product_id = data.get('global_product_id', None)
        if not global_product_id:
            raise APIException('Missing global product id')
        store_id = None
        if data.get('merchant', None):
            store_id = data['merchant'].get('id', None)
        if not store_id:
            raise APIException('Missing store id')
        store = StoreModel.objects.get(id=store_id)
        global_relations = GlobalProductRelations.objects.filter(global_product_id=global_product_id, store=store).first()
        if not global_relations:
            product = self._create_shopee_product(data, store)
        else:
            product = global_relations.product
            product.product_name = data.get('name', product.product_name)
            product.product_sku = data.get('sku', product.product_sku)
            product.image_url = data.get('image', product.image_url)
            product.description = data.get('desc', product.description)
        logistic = data.get('logistic', None)
        if logistic:
            product.weight = parse_float(logistic.get('weight', None), product.weight)
            product.height = parse_float(logistic.get('product_h', None), product.height)
            product.width = parse_float(logistic.get('product_w', None), product.width)
            product.length = parse_float(logistic.get('product_d', None), product.length)
            product.days_to_ship = logistic.get('days_deliver', product.days_to_ship)
        product.save()
        self._create_or_update_product_detail(product=product, data=data)
        data = StoreShopProductDetailSerializer(product).data
        return Response(data, status=200)

    def update(self, request, *args, **kwargs):
        raise Exception('Improper denpendency') #TODO

    def _create_shopee_product(self, data, store):

        product = StoreProductModel.objects.create(
            openid=self.request.META.get('HTTP_TOKEN'),
            creater=self.request.META.get('HTTP_OPERATOR'),
            store=store,
            product_name=data.get('name', None),
            product_status=StoreProductModel.Status.EDIT,
            product_sku=data.get('sku', None),
            image_url=data.get('image', None),
            description=data.get('desc', None)
        )
        return product

    def clone_product(self, request, *args, **kwargs):
        product_id_to_clone = self.request.data
        logger.info('clone products %s', product_id_to_clone)
        open_id = self.request.auth.openid
        clone_products = []
        for product_id in product_id_to_clone:
            product = StoreProductModel.objects.filter(id=product_id, openid=open_id).first()
            if not product:
                raise APIException('Fail to clone product, Product of id %s not found')
            product_clone = ProductPublishService.get_instance().clone_product(product)
            clone_products.append(
                StoreGlobalProductListGetSerializer(product_clone, context={'request': self.request}).data)
        return Response(clone_products, status=200)

    @transaction.atomic
    def _create_or_update_product_detail(self, product, data):
        images_infos = data.get('images', None)
        if images_infos:
            self._create_or_update_images(product, images_infos)
        spec_info = data.get('specifications', None)
        if spec_info:
            self._create_or_update_spec(product, spec_info)
        models_info = data.get('models_info', None)
        if models_info:
            self._create_or_update_models(product, models_info)
        category_info = data.get('category', None)
        if category_info:
            self._create_or_update_category(product, category_info)

    def _create_or_update_images(self, product, images_infos):
        for image_info in images_infos:
            image_info['creater'] = product.creater
            image_info['openid'] = product.openid
            image_info['product'] = product.id
            image_index = image_info.get('index', None)
            url = image_info.get('url', None)
            if image_index is not None and url:
                image_instance = StoreProductMedia.objects.filter(store_product=product, index=image_index, type=2).first()
                if image_instance:
                    image_instance.url = url
                    image_instance.save()
                else:
                    image_instance = StoreProductMedia.objects.create(
                        openid=product.openid,
                        creater=product.creater,
                        store_product=product,
                        type=2,
                        url=url,
                        index=image_index
                    )
        return images_infos

    def _create_or_update_models(self, product, models_info):
        models = list(StoreProductVariantModel.objects.filter(store_product=product, is_delete=False).all())
        for data in models_info:
            options_index = data.get('options_index', None)
            if not options_index:
                raise Exception('Create/update model missing options index %s' % data.get('sku', None))
            model_match = [m for m in models if m.option_item_index == options_index]
            model_instance = model_match[0] if model_match else None
            if not model_instance:
                model_instance = StoreProductVariantModel.objects.create(
                    openid=product.openid,
                    creater=product.creater,
                    store_product=product,
                    model_sku=data.get('sku', None),
                    option_item_index=options_index
                )
            else:
                model_instance.model_sku = data.get('sku', model_instance.model_sku)
                model_instance.save()
            if not data.get('stock', None):
                continue
            stock = data.get('stock')
            if stock.get('stock_qty', None):
                stock_info = StoreProductVariantStock.objects.filter(variant=model_instance,
                                                                     is_delete=False).first()
                if not stock_info:
                    stock_info = StoreProductVariantStock.objects.create(
                        openid=product.openid,
                        creater=product.creater,
                        variant=model_instance,
                        current_stock=stock.get('stock_qty')
                    )
                else:
                    stock_info.current_stock = data.get('stock').get('stock_qty', stock_info.current_stock)
                    stock_info.save()
            if stock.get('price', None):
                price_info = StoreProductPriceInfoModel.objects.filter(variant=model_instance, is_delete=False).first()
                if not price_info:
                    price_info = StoreProductPriceInfoModel.objects.create(
                        openid=product.openid,
                        creater=product.creater,
                        variant=model_instance,
                        store_product=product,
                        original_price=stock.get('price')
                    )
                else:
                    price_info.original_price = stock.get('price')
                    price_info.save()

    def _create_or_update_spec(self, product, spec_info):
        for data in spec_info:
            index = data.get('index', None)
            name = data.get('name', None)
            if index is None:
                logger.error('can not create spec, missing index %s', name)
                raise APIException('Create spec missing index %s ' % name)
            if not name:
                logger.error('can not create spec, missing name %s', index)
                raise APIException('Create spec missing name %s ' % index)
            spec = StoreProductOptionModel.objects.filter(index=index, store_product=product).first()
            if not spec:
                spec = StoreProductOptionModel.objects.create(
                    openid=product.openid,
                    creater=product.creater,
                    store_product=product,
                    name=name,
                    index=index
                )
            else:
                spec.name = name
                spec.save()
            options = data.get('options', [])
            for option in options:
                self._create_or_update_option(product, spec, option)
        return spec_info

    def _create_or_update_category(self, product, category_info):
        print('create category ,', product.id, category_info.get('category_id', None))
        category_id = category_info.get('category_id', None)
        if not category_id:
            logger.warning('create or update category no category id')
            return
        category_instance = ProductCategory.objects.filter(product=product, is_delete=False).first()
        brand_info = category_info.get('brand', None)
        brand_instance = category_instance.brand if category_instance else None
        if not brand_instance:
            brand_id = brand_info.get('brand_id', 0) if brand_info else 0
            display_brand_name = brand_info.get('display_brand_name', 'NoBrand') if brand_info else 'NoBrand'
            brand_instance = ProductCategoryBrand.objects.create(
                openid=product.openid,
                creater=product.creater,
                brand_id=brand_id,
                display_brand_name=display_brand_name
            )
        if not category_instance:
            category_instance = ProductCategory.objects.create(
                openid=product.openid,
                creater=product.creater,
                merchant_id=product.store.uid,
                category_id=category_id,
                brand=brand_instance,
                product=product
            )
        else:
            category_instance.category_id = category_id
            category_instance.brand = brand_instance
            category_instance.save()

        ProductCategoryAttribute.objects.filter(Q(category_id=category_instance.id)).delete()
        attribute_values_info = category_info.get('attribute_values', None)
        if attribute_values_info:
            self._create_category_attribute(category_instance, attribute_values_info)

    def _create_product_media(self, product, image_info):
        logger.info('create prdocut media ', image_info)
        # file_string = image_info.get('file', None)
        # if not file_string:
        #     raise APIException("Can not create product meida ,file bytes string is None")
        # file_name = image_info.get('filename')
        # file_bytes = base64.b64decode(file_string)
        # if not file_string:
        #     raise APIException("Must provide media file while media id is None")
        # media = Media(
        #     file=ImageFile(io.BytesIO(file_bytes), name=file_name),
        #     openid=product.openid,
        #     creater=product.creater
        # )
        # media.save()
        # return media

    def _delete_spec(self, data):
        raise Exception('Improper denpendency')  # TODO
        # id = data.get('id', None)
        # if not id:
        #     raise APIException('Cant not delete specification , missing id')
        # spec = ProductSpecification.objects.get(id=id)
        # for option in getattr(spec, ProductSpecification.RelativeFields.SPECIFICATION_OPTION).all():
        #     option.models.clear()
        #     option.delete()
        # return spec.delete()

    def _create_or_update_option(self, product, spec, data):
        index = data.get('index', None)
        name = data.get('name', None)
        image_url = data.get('iamge', None)
        if index is None:
            logger.error('can not create option, missing index %s %s', spec.name, name)
            raise APIException('Create option missing indexndex %s %s' % (spec.name, name))
        if not name:
            logger.error('can not create option, missing name %s', spec.name, index)
            raise APIException('Create option missing name %s %s ' % (spec.name, index))
        option = StoreProductOptionItemModel.objects.filter(store_product=product, store_product_option=spec, index=index).first()
        if not option:
            option = StoreProductOptionItemModel.objects.create(
                openid=product.openid,
                creater=product.creater,
                store_product=product,
                store_product_option=spec,
                name=name,
                image_url=image_url,
                index=index
            )
        else:
            option.name = name
            option.image_url = image_url if image_url else option.image_url
            option.save()
        return option

    def get_price(self, request):
        raise Exception('Improper denpendency')  # TODO
        # ids = request.query_params.getlist('id', [])
        # shops = request.query_params.getlist('shop', [])
        # logger.info('get price of product %s for shops %s ', ids, shops)
        # if not ids or len(ids) == 0:
        #     APIException({"detail": "Must specify product id "})
        # price_infos = []
        # for id in ids:
        #     qs = GlobalProduct.objects.get(id=id)
        #     if qs.openid != self.request.auth.openid:
        #         raise APIException(
        #             {"detail": "Cannot delete data which not yours"})
        #     store_publishes = getattr(qs, GlobalProduct.RelativeFields.SHOPEE_STORE_PUBLISH).filter(Q(shop_id__in=shops)).all()
        #     for store_publish in store_publishes:
        #         models = None
        #         try:
        #             models = ProductService.get_instance()\
        #                 .get_product_shop_price(store_publish.shop_id, store_publish.publish_id)
        #         except Exception as exc:
        #             logger.error('get price info for product %s of shop %s fail, %s', qs.id, store_publish.shop_id, exc)
        #         if not models:
        #             continue
        #         discount_id = 0
        #         model_price = []
        #         for model in models:
        #             if model.get('promotion_id', -1) > 0:
        #                 discount_id = model['promotion_id']
        #             model_info = {
        #                 'current_price': model['price_info'][0]['current_price'],
        #                 'original_price': model['price_info'][0]['original_price'],
        #                 'discount': {'discount_id': discount_id},
        #                 'discount_id': discount_id,
        #                 'sku': model['model_sku'],
        #                 'model_id': model['model_id']
        #             }
        #             global_model_publish = ShopeeStorePublish.objects.filter(publish_id=model['model_id']).first()
        #             if global_model_publish:
        #                 global_model = global_model_publish.product
        #                 model_info['image'] = global_model.image
        #                 stock = getattr(global_model, GlobalProduct.RelativeFields.MODEL_STOCKS).first()
        #                 if stock:
        #                     model_info['stock'] = {'stock_qty': stock.stock_qty, 'price': stock.price}
        #             model_price.append(model_info)
        #
        #         logistic_info = getattr(qs, GlobalProduct.RelativeFields.PRODUCT_LOGISTIC).first()
        #         supplier = getattr(qs, GlobalProduct.RelativeFields.PRODUCT_SUPPLIER).first()
        #         price_info = {
        #             'item_id': store_publish.publish_id,
        #             'type': 'shopee',
        #             'store_id': store_publish.shop_id,
        #             'models': model_price,
        #             'discount': {'discount_id': discount_id, 'item_list':  [{'model_list': model_price}]},
        #             'supplier': ProductSupplierGetSerializers(supplier).data,
        #             'logistic': ProductLogisticGetSerializers(logistic_info).data,
        #             'id': qs.id,
        #             'sku': qs.sku,
        #             'image': qs.image
        #         }
        #         price_infos.append(price_info)
        # return Response(price_infos, status=200, headers=self.get_success_headers(""))

    def _create_or_update_category_brand(self, product, brand_info):
        id = brand_info.get('id', None)
        if id:
            brand_instance = ProductCategoryBrand.objects.get(id=id)
            serializer = ProductCategoryBrandPostSerializer(brand_instance, data=brand_info, partial=True)
        else:
            brand_info['creater'] = product.creater
            brand_info['openid'] = product.openid
            serializer = ProductCategoryBrandPostSerializer(data=brand_info)
        if not serializer.is_valid():
            logger.error('Fail to save category brand %s' % serializer.errors)
            raise APIException('Fail to save category brand')
        return serializer.save()

    def _create_category_attribute(self, category, attribute_values_info):
        logger.info('_create_or_update_category_attribute %s', attribute_values_info)
        for attribute_value in attribute_values_info:
            if not attribute_value.get('attribute_id', None):
                raise APIException(
                    'Missing attribute id for attribute value %s' % attribute_value.get('display_value_name', None))
            if not attribute_value.get('value_id', None):
                raise APIException(
                    'Missing valid id for attribute value %s' % attribute_value.get('display_value_name', None))
            if not attribute_value.get('display_value_name', None):
                raise APIException(
                    'Missing valid id for attribute display name %s' % attribute_value.get('attribute_id', None))
            attribute_value['category'] = category.id
            attribute_value['openid'] = category.openid
            attribute_value['creater'] = category.creater
            serializer = ProductAttributePostSerializer(data=attribute_value)
            if not serializer.is_valid():
                logger.error('Fail to save category attribute %s', serializer.errors)
                raise APIException('Fail to save category attribute')
            serializer.save()
