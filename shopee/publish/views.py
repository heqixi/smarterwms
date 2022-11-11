
from django.db import transaction
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.exceptions import APIException
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response

from globalproduct.gRpc.client.global_product import ProductServiceClient
from globalproduct.models import GlobalProductRelations
from store.common import StoreType
from store.models import StoreProductModel, StoreModel, StoreProductPriceInfoModel, StoreProductMedia
from store.serializers import StoreGlobalProductListGetSerializer, StoreShopProductDetailSerializer
from store.services.store_service import StoreService
from utils.datasolve import parse_float
from .services.product_service import ProductPublishService

import logging

from .services.producthelper import ProductHelper

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

    def get_queryset(self):
        openid = self.request.META.get('HTTP_TOKEN')
        return StoreProductModel.objects.filter(openid=openid)

    def publish_to_shopee(self, request):
        data = request.data
        product_id = data.get('id', None)
        if not product_id:
            raise APIException('Must specify product id to publish ')
        stores = data.get('stores', None)
        if not stores:
            raise APIException('Must specify stores id to publish ')
        product = StoreProductModel.objects.filter(id=product_id).first()
        if not product:
            raise APIException('Can not find product of id %s ' % product_id)
        store_group_by_merchant = []
        for store_id in stores:
            store = StoreModel.objects.get(id=store_id)
            if store.type == StoreType.SHOP:
                found = False
                for merchant, stores in store_group_by_merchant:
                    if merchant.id == store.merchant.id:
                        found = True
                        stores.append(store)
                if not found:
                    store_group_by_merchant.append((store.merchant, [store]))
        for merchant, stores in store_group_by_merchant:
            ProductPublishService.get_instance().publish_shopee(product, merchant.uid, stores)
        return Response('success', status=200)

    # def get_serializer_class(self):
    #     if self.action in ['list', 'retrieve']:
    #         raise Exception('Improper Denpendency') #TODO
    #         # return serializers.GlobalProductGetSerializers
    #     if self.action in ['create', 'update', 'partial_update', 'publish_to_shopee', 'update_price']:
    #         return serializers.GlobalProductSerializers
    #     else:
    #         return self.http_method_not_allowed(request=self.request)

    def retrieve(self, request, *args, **kwargs):
        store_product = self.get_object()
        product_json = StoreShopProductDetailSerializer(store_product).data
        return Response(product_json, status=200)

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
        product_id = data.get('id', None)
        if not product_id:
            raise APIException('Missing product id')
        store_id = None
        if data.get('merchant', None):
            store_id = data['merchant'].get('id', None)
        if not store_id:
            raise APIException('Missing store id')
        store = StoreModel.objects.get(id=store_id)
        product = StoreProductModel.objects.filter(id=product_id).first()
        if not product:
            product = self._create_shopee_product(data, store)
        else:
            product.product_name = data.get('name', product.product_name)
            product.product_sku = data.get('sku', product.product_sku)
            product.image_url = data.get('image', product.image_url)
            product.description = data.get('desc', product.description)
            product.product_status = data.get('status', product.product_status)
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
            product_status=data.get('status', StoreProductModel.Status.EDIT),
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
            ProductHelper.create_or_update_images(product, images_infos)
        spec_info = data.get('specifications', None)
        if spec_info:
            ProductHelper.create_or_update_spec(product, spec_info)
        models_info = data.get('models_info', None)
        if models_info:
            ProductHelper.create_or_update_models(product, models_info)
        category_info = data.get('category', None)
        if category_info:
            ProductHelper.create_or_update_category(product, category_info)
        supplier_info = data.get('supplier', None)
        if supplier_info:
            ProductHelper.create_or_update_supplier_info(product, supplier_info)

    def _create_product_media(self, product, image_info):
        logger.info('create prdocut media ', image_info) # TODO

    def get_price(self, request):
        raise Exception('Improper denpendency')  # TODO

    def get_shop_product(self, request, *args, **kwargs):
        shop_ids = self.request.query_params.get('stop_id', '').split(',')
        global_product_id = self.request.query_params.get('id', None)
        if not global_product_id:
            raise APIException('Missing global product id')
        global_product = StoreProductModel.objects.get(id=global_product_id)
        shop_products = []
        for shop_id in shop_ids:
            store = StoreModel.objects.get(id=shop_id)
            shop_product = global_product.shop_products.filter(store_id=shop_id).first()
            if not shop_product:
                shop_product = ProductHelper.global_product_to_shop_product(global_product, store)
            serializer = StoreShopProductDetailSerializer(shop_product, context={'request': request})
            shop_products.append(serializer.data)
        print(global_product.shop_products.count())
        serializer = StoreGlobalProductListGetSerializer(global_product, context={'request': request})
        global_product_json = serializer.data
        global_product_json['shop_products'] = shop_products
        return Response(global_product_json, status=200)

    @transaction.atomic
    def update_price(self, request, *args, **kwargs):
        shop_products = request.data
        for shop_product in shop_products:
            shop_product_instance = StoreProductModel.objects.get(id=shop_product['id'])
            for variant in shop_product['variants']:
                variant_instance = shop_product_instance.product_variant.filter(id=variant['id']).first()
                if not variant_instance:
                    raise APIException('Can not find variant %s ' % variant['id'])
                variant_instance.promotion_id = variant.get('promotion_id', variant_instance.promotion_id)
                variant_instance.save()
                price_info = variant['price_info']
                if not price_info:
                    raise APIException('Variant %s missing price info' % variant['id'])
                price_info_id = price_info.get('id', None)
                original_price = price_info.get('original_price', None)
                current_price = price_info.get('current_price', None)
                if not (original_price and current_price):
                    raise APIException('Variant %s price info original/current price not set ' % variant['id'])
                if not price_info_id:
                    price_info_instance = StoreProductPriceInfoModel.objects.create(
                        openid=shop_product_instance.openid,
                        creater=shop_product_instance.creater,
                        store_product=shop_product_instance,
                        type=1,
                        variant=variant_instance,
                        original_price=original_price,
                        current_price=current_price,
                    )
                else:
                    price_info_instance = variant_instance.variant_price.filter(id=price_info_id).first()
                    price_info_instance.original_price = original_price
                    price_info_instance.current_price = current_price
                    price_info_instance.save()
        return Response('', status=200)

    @transaction.atomic
    def publish_media(self, request, *args, **kwargs):
        data = request.data
        product_media = data.get('product_media', None)
        option_media = data.get('option_media', None)
        self._publish_product_meida(product_media)
        self._publish_option_media(option_media)
        return Response('success', 200)

    def _publish_product_meida(self, product_media_list: []):
        for product_media in product_media_list:
            ProductHelper.upload_product_image(product_media)

    def _publish_option_media(self, option_media_list:[]):
        for option_media in option_media_list:
            ProductHelper.upload_option_image(option_media)



