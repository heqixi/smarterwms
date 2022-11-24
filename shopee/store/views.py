import logging
import threading
import traceback

from django.conf import settings
from django.db import transaction
from django.http import HttpResponseRedirect, HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response

from store.services.fetchservice import FetchService
from store.common import StoreType, StoreStatus
from store.models import StoreModel, StoreProductModel, StoreProductVariantModel, StoreProductPackageModel, \
    ShopeeRegionSettingsModel, ShopeeStoreRegionSetting
from store.page import MyPageNumberPagination
from store.serializers import StoreListGetSerializer, StoreProductListGetSerializer, \
    StoreGlobalProductListGetSerializer, StoreProductVariantListGetSerializer, StoreProductPackageGetListSerializer, \
    ShopeeRegionSettingsGetSerializer
from store.services.dtos.shoppe_callback_dto import ShopeeCallbackDto
from store.services.global_service import GlobalService
from store.services.package_service import PackageService
from store.services.product_service import ProductService
from store.services.store_service import StoreService
from utils import spg, shopee

logger = logging.getLogger()


class Store(viewsets.ModelViewSet):
    pagination_class = MyPageNumberPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['id', "create_time", "update_time"]
    serializer_class = StoreListGetSerializer
    queryset = StoreModel.objects.all().order_by('-id')
    store_service = StoreService.get_instance()

    def get_queryset(self):
        params = spg.parse_params(self.request)
        openid = self.request.META.get('HTTP_TOKEN')
        ordering = params.get('ordering')
        ordering = ordering if ordering is not None else '-id'
        return StoreModel.objects.filter(openid=openid, status=StoreStatus.NORMAL).order_by(ordering)

    def get_all_store(self, request):
        try:
            params = spg.parse_params(request)
            store_type = params.get('type')
            status = params.get('status')
            with_setting = params.get('profit_settings')
            status = status if params.get('status') is not None else StoreStatus.NORMAL
            openid = request.META.get('HTTP_TOKEN')
            store_list = self.store_service.get_all_store(openid, store_type, status)
            store_dicts = spg.django_model_to_dict(model_list=store_list)
            if with_setting:
                for store_dict in store_dicts:
                    store_setting = ShopeeStoreRegionSetting.objects.filter(store_uid=store_dict['uid']).first()
                    if store_setting:
                        region_setttings = store_setting.region_settings
                        profit_setting = ShopeeRegionSettingsGetSerializer(region_setttings).data
                    else:
                        profit_setting = None
                    store_dict['profit_setting'] = profit_setting
            result = spg.to_json_str(store_dicts)
            return HttpResponse(result, content_type='application/json')
        except Exception as e:
            logger.error('%s\n%s', e, traceback.format_exc())
            return HttpResponse(e, status=500)

    def auth(self, request):
        data = spg.parse_params(request)
        partner_id = data.get('partnerId')
        partner_key = data.get('partnerKey')
        store_id = data.get('storeId')
        user_id = 1  # TODO
        url = self.store_service.get_shopee_auth_url(user_id, partner_id, partner_key, store_id)
        return Response({'url': url}, status=200)

    def destroy(self, request, pk):
        qs = self.get_object()
        self.store_service.delete_store(pk)
        serializer = self.get_serializer(qs, many=False)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=200, headers=headers)

    def refresh_token(self, request):
        try:
            data = spg.parse_params(request)
            store_id = data.get('storeId')
            store = StoreModel.objects.get(pk=store_id)
            if store.type == StoreType.SHOP:
                shopee.refresh_shop_token(shop_id=store.uid)
            if store.type == StoreType.MERCHANT:
                shopee.refresh_shop_token(merchant_id=store.uid)
            return Response('Refresh token success', status=200)
        except Exception as e:
            logger.error('Refresh token error: %s', traceback.format_exc())
            return Response('Refresh token failed', status=500)

    def get_discounts_list(self, request):
        openid = self.request.META.get('HTTP_TOKEN')
        store_id = self.request.query_params.get('store_id', None)
        status = self.request.query_params.get('status', None)
        if not status:
            status = 'ongoing' #默认只获取进行中的
        if not store_id:
            raise Exception("Fail to get discount list, missing store_id ")
        store = StoreModel.objects.get(uid=store_id) #虽然变量名是store_id, 实际是上 uid
        if store.openid != openid:
            raise Exception("Cant not get discount list which are not yours")
        discount_list = ProductService.get_instance().get_discount_list(store_id, status)
        return Response(discount_list, status=200)


class StoreGlobalProduct(viewsets.ModelViewSet):
    """
    商户全球产品控制层
    """
    pagination_class = MyPageNumberPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['id', "create_time", "update_time"]
    global_service: GlobalService = GlobalService.get_instance()

    def get_serializer_class(self):
        query_type = spg.parse_params(self.request).get('type')
        if query_type == '1':
            return StoreGlobalProductListGetSerializer
        else:
            return StoreProductVariantListGetSerializer

    def get_queryset(self):
        params = spg.parse_params(self.request)
        print('get query set')
        query_type = params.get('type')
        ordering = params.get('ordering')
        merchant_id = params.get('merchant_id')
        global_item_sku = params.get('global_item_sku')
        global_item_id = params.get('global_item_id')
        product_status = params.get('product_status')
        ordering = ordering if ordering is not None else '-id'
        if query_type == '1':
            kwargs = {
                'store__type': StoreType.MERCHANT,
                'is_delete': False
            }
            if merchant_id:
                kwargs['store__uid'] = merchant_id
            if global_item_sku:
                kwargs['product_sku__contains'] = global_item_sku
            if global_item_id:
                kwargs['product_id'] = global_item_id
            if product_status:
                kwargs['product_status__in'] = product_status.split(',')
            return StoreProductModel.objects.filter(**kwargs).order_by(ordering)
        else:
            kwargs = {
                'store_product__store__type': StoreType.MERCHANT,
            }
            if merchant_id:
                kwargs['store_product__store__uid'] = merchant_id
            if global_item_sku:
                kwargs['store_product__product_sku__contains'] = global_item_sku
            if global_item_id:
                kwargs['store_product__product_id'] = global_item_id
            model_id = params.get('model_id')
            if model_id:
                kwargs['model_id'] = model_id
            model_sku = params.get('model_sku')
            if model_sku:
                kwargs['model_sku__contains'] = model_sku
            return StoreProductVariantModel.objects.filter(**kwargs).order_by(ordering)

    def sync_global(self, request):
        try:
            params = spg.parse_params(request)
            merchant_id = params.get('merchant_id')
            item_id = params.get('item_id')
            if item_id is not None:
                self.global_service.sync_by_global_item_id(merchant_id, item_id)
            else:
                threading.Thread(
                    target=self.global_service.sync_by_merchant,
                    args=(merchant_id,)
                ).start()
            return HttpResponse('Syncing global products success', status=200)
        except Exception as e:
            logger.error('%s\n%s', e, traceback.format_exc())
            return HttpResponse('Sync Global Product Error', status=500)

    def get_global_product_details(self, request):
        try:
            params = spg.parse_params(request)
            openid = request.META.get('HTTP_TOKEN')
            merchant_id = params.get('merchant_id')
            if StoreModel.objects.get(type=StoreType.MERCHANT, uid=merchant_id).openid == openid:
                global_product_id = params.get('global_product_id')
                details = self.global_service.get_global_product_detail(merchant_id, global_product_id)
                return HttpResponse(spg.to_json_str(details), content_type='application/json', status=200)
            else:
                logger.error('Not authorized to perform this operation')
                return HttpResponse('Not authorized to perform this operation', status=500)
        except Exception as e:
            logger.error('%s\n%s', e, traceback.format_exc())
            return HttpResponse('Get Global Details Error', status=500)

    def get_global_brands(self, request):
        try:
            params = spg.parse_params(request)
            openid = request.META.get('HTTP_TOKEN')
            merchant_id = params.get('merchant_id')
            category_id = params.get('category_id')
            language = params.get('language')
            if StoreModel.objects.get(type=StoreType.MERCHANT, uid=merchant_id).openid == openid:
                brands = self.global_service.get_global_brands(merchant_id, category_id, language)
                return HttpResponse(spg.to_json_str(brands), content_type='application/json', status=200)
            else:
                logger.error('Not authorized to perform this operation')
                return HttpResponse('Not authorized to perform this operation', status=500)
        except Exception as e:
            logger.error('%s\n%s', e, traceback.format_exc())
            return HttpResponse('Get Global Brands Error', status=500)

    def get_global_attributes(self, request):
        try:
            params = spg.parse_params(request)
            openid = request.META.get('HTTP_TOKEN')
            merchant_id = params.get('merchant_id')
            category_id = params.get('category_id')
            language = params.get('language')
            if StoreModel.objects.get(type=StoreType.MERCHANT, uid=merchant_id).openid == openid:
                attributes = self.global_service.get_global_attributes(merchant_id, category_id, language)
                return HttpResponse(spg.to_json_str(attributes), content_type='application/json', status=200)
            else:
                logger.error('Not authorized to perform this operation')
                return HttpResponse('Not authorized to perform this operation', status=500)
        except Exception as e:
            logger.error('%s\n%s', e, traceback.format_exc())
            return HttpResponse('Get Global Attributes Error', status=500)

    def update_global_sku(self, request):
        try:
            params = spg.parse_params(request)
            merchant_id = params.get('merchant_id')
            global_product_list = params.get('global_product_list')
            self.global_service.update_global_sku(merchant_id, global_product_list)
            return HttpResponse('Update Global Sku Success', content_type='application/json', status=200)
        except Exception as e:
            logger.error('%s\n%s', e, traceback.format_exc())
            return HttpResponse('Update Global Sku Error', status=500)

    def update_model_sku(self, request):
        try:
            params = spg.parse_params(request)
            merchant_id = params.get('merchant_id')
            model_list = params.get('model_list')
            self.global_service.update_model_sku(merchant_id, model_list)
            return HttpResponse('Update Global Model Sku Success', content_type='application/json', status=200)
        except Exception as e:
            logger.error('%s\n%s', e, traceback.format_exc())
            return HttpResponse('Update Global Model Sku Error', status=500)

    def get_category(self, request):
        merchant_id = self.request.query_params('merchant_id', None)
        logger.info('get category ', merchant_id)
        if not merchant_id:
            return HttpResponse('Must specifiy merchant id to get category', status=500)
        category_list = ProductService.get_instance().get_category(merchant_id)
        return HttpResponse(category_list, status=200)

    def upload_image(self, image, scene="normal"):
        if not image:
            return HttpResponse('Must specifiy image file to update', status=500)
        image_info = ProductService.get_instance().upload_image(image, scene)
        return HttpResponse(image_info, status=200)

    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        openid = self.request.META.get('HTTP_TOKEN')
        for id in request.data:
            global_product = StoreProductModel.objects.filter(id=id).first()
            if global_product.openid != openid:
                return HttpResponse('Can not delete product which is not yours', status=500)
            global_product.is_delete = True
            for variant in global_product.product_variant.all():
                variant.is_delete = True
                variant.save()
            global_product.save()
        return HttpResponse('success', status=200)


class StoreProduct(viewsets.ModelViewSet):
    """
    店铺产品控制层
    """
    pagination_class = MyPageNumberPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['id', "create_time", "update_time"]
    serializer_class = StoreProductListGetSerializer
    product_service = ProductService.get_instance()

    def get_serializer_class(self):
        query_type = spg.parse_params(self.request).get('type')
        if query_type == '1':
            return StoreProductListGetSerializer
        else:
            return StoreProductVariantListGetSerializer

    def get_queryset(self):
        params = spg.parse_params(self.request)
        query_type = params.get('type')
        shop_id = params.get('shop_id')
        item_sku = params.get('item_sku')
        item_id = params.get('item_id')
        ordering = params.get('ordering', '-id')
        if query_type == '1':
            kwargs = {
                'store__type': StoreType.SHOP
            }
            if shop_id:
                kwargs['store__uid'] = shop_id
            if item_sku:
                kwargs['product_sku__contains'] = item_sku
            if item_id:
                kwargs['product_id'] = item_id
            return StoreProductModel.objects.filter(**kwargs).order_by(ordering)
        else:
            kwargs = {
                'store_product__store__type': StoreType.SHOP
            }
            if shop_id:
                kwargs['store_product__store__uid'] = shop_id
            if item_sku:
                kwargs['store_product__product_sku__contains'] = item_sku
            if item_id:
                kwargs['store_product__product_id'] = item_id
            model_id = params.get('model_id')
            if model_id:
                kwargs['model_id'] = model_id
            model_sku = params.get('model_sku')
            if model_sku:
                kwargs['model_sku__contains'] = model_sku
            return StoreProductVariantModel.objects.filter(**kwargs).order_by(ordering)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def detail(self, request):
        params = spg.parse_params(request)
        self.product_service.get_product_detail(params.get('id'))
        return Response('Success', status=200)

    def sync(self, request):
        try:
            params = spg.parse_params(request)
            shop_id = params.get('shop_id')
            item_id = params.get('item_id')
            if item_id is not None:
                self.product_service.sync_by_item_id(shop_id, item_id)
            else:
                threading.Thread(target=self.product_service.sync_by_shop, args=(shop_id,)).start()
            return HttpResponse('Syncing products success', status=200)
        except Exception as e:
            logger.error('%s\n%s', e, traceback.format_exc())
            return HttpResponse('Sync Shop Product Error', status=500)

    def update_discount(self, request):
        discounts = self.request.data
        models_num = 0
        for shopee_discount in discounts:
            for item in shopee_discount['item_list']:
                models_num += len(item['model_list'])
        update_num = 0
        for shopee_discount in discounts:
            if shopee_discount.get('add', False):
                count = ProductService.get_instance().add_discount_item(shopee_discount['store_id'],
                    shopee_discount['discount_id'], shopee_discount['item_list'])
                update_num += count
            else:
                count = ProductService.get_instance().update_discount_items(shopee_discount['store_id'],
                    shopee_discount['discount_id'], shopee_discount['item_list'])
                update_num += count
        return HttpResponse(update_num, status=200)

    def get_prodcut_list(self, request):
        try:
            params = spg.parse_params(request)
            shop_id = params.get('shop_id')
            product_status = params.get('product_status')
            openid = request.META.get('HTTP_TOKEN')
            ret = self.product_service.get_prodcut_list(openid, shop_id, product_status)
            return HttpResponse(spg.to_json_str(ret), content_type='application/json', status=200)
        except Exception as e:
            logger.error('%s\n%s', e, traceback.format_exc())
            return HttpResponse('Sync Shop Product Error', status=500)


class StoreProductPackage(viewsets.ModelViewSet):
    """
    组合装产品控制层
    """
    pagination_class = MyPageNumberPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['id', "create_time", "update_time"]
    serializer_class = StoreProductPackageGetListSerializer
    package_service = PackageService.get_instance()

    def get_queryset(self):
        params = spg.parse_params(self.request)
        openid = self.request.META.get('HTTP_TOKEN')
        kwargs = {
            'openid': openid
        }
        sku = params.get('sku')
        if sku:
            kwargs['sku__contains'] = sku
        return StoreProductPackageModel.objects.filter(**kwargs).order_by('create_time')

    def remove_package(self, request):
        try:
            params = spg.parse_params(request)
            package_id = params.get('package_id')
            openid = request.META.get('HTTP_TOKEN')
            self.package_service.remove_package(openid, package_id)
            return HttpResponse('Remove package success', status=200)
        except Exception as e:
            logger.error('Remove package Error %s\n%s', e, traceback.format_exc())
            return HttpResponse('Remove package Error', status=500)

    def new_package(self, request):
        try:
            params = spg.parse_params(request)
            packages = params.get('packages')
            items = params.get('items')
            openid = request.META.get('HTTP_TOKEN')
            creater = self.request.META.get('HTTP_OPERATOR')
            self.package_service.new_package(openid, creater, packages, items)
            return HttpResponse('New package success', status=200)
        except Exception as e:
            logger.error('New package Error %s\n%s', e, traceback.format_exc())
            return HttpResponse('New package Error', status=500)


class RegionSettings(viewsets.ModelViewSet):
    pagination_class = MyPageNumberPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['id', "create_time", "update_time"]
    serializer_class = ShopeeRegionSettingsGetSerializer

    def get_queryset(self):
        params = spg.parse_params(self.request)
        openid = self.request.META.get('HTTP_TOKEN')
        kwargs = {'openid': openid}
        area = params.get('area')
        store = params.get('store')
        if area:
            kwargs['area__contains'] = area
        if store:
            kwargs['setting_store__store_uid'] = store
        return ShopeeRegionSettingsModel.objects.filter(**kwargs).order_by('-id')

    def create(self, request, *args, **kwargs):
        try:
            params = spg.parse_params(self.request)
            openid = request.META.get('HTTP_TOKEN')
            FetchService.get_instance().create_region_settings(openid, params)
            return HttpResponse('Save region settings success', status=200)
        except Exception as e:
            logger.error("Save region settings error: %s\n%s", e, traceback.format_exc())
            return HttpResponse('Save region settings error: %s' % e, content_type='text/html', status=500)

    def destroy(self, request, *args, **kwargs):
        params = spg.parse_params(self.request)
        region_id = params.get('id')
        openid = request.META.get('HTTP_TOKEN')
        ShopeeRegionSettingsModel.objects.get(openid=openid, id=region_id).delete()
        return HttpResponse('Save region settings success', status=200)


def callback(request):
    """
    Shopee 授权回调
    """
    try:
        data = request.GET.dict()
        logger.info('Shopee Call Back Data: %s', data)
        # dto = ShopeeCallbackDto()
        dto = ShopeeCallbackDto.dict_to_object(data)
        # dto.__dict__.update(json.loads(data))
        StoreService.get_instance().shoppe_callback(dto)
        return HttpResponseRedirect(settings.SHOPEE.get('callback_url'))
    except Exception as e:
        logger.error('Shopee Call Back Error: %s\n%s', e, traceback.format_exc())
        return HttpResponseRedirect('/')


