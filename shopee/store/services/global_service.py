import logging
import threading
import time
import traceback

from django.db import transaction

from base.bustools import GLOBAL_BUS as bus, GLOBAL_PRODUCT_SYNC_EVENT
from store.common import StoreProductType, StoreType, MediaType
from store.models import StoreModel, StoreProductModel, StoreProductMedia, StoreProductVariantModel, \
    StoreProductOptionModel, StoreProductOptionItemModel, StoreProductPriceInfoModel, StoreProductVariantStock
from store.serializers import StoreGlobalProductEmitDataSerializer
from supplier.supplier_register import SupplierRegister
from utils import shopee, spg

logger = logging.getLogger()


class GlobalService(object):
    """
    商户全球产品服务，对外提供全球产品相关操作功能
    """
    __create_key = object()
    lock = threading.RLock()
    service = None

    def __init__(self, create_key):
        assert (create_key == GlobalService.__create_key), \
            "ProductService objects must be created using ProductService.get_instance"

    @classmethod
    def get_instance(cls):
        if cls.service is None:
            cls.lock.acquire()
            if cls.service is None:
                cls.service = cls(GlobalService.__create_key)
            cls.lock.release()
            return cls.service
        return cls.service

    def update_global_sku_by_openid(self, openid, global_product_list):
        if not openid:
            logger.error('Auth Error: openid can not be none')
            raise ValueError('Auth Error: openid can not be none')
        merchant_map = {}
        for product in global_product_list:
            store = product.store
            if openid != store.openid:
                logger.error('Auth Error: No permission to operate')
                raise ValueError('Auth Error: No permission to operate')
            if store.type == StoreType.MERCHANT:
                mg_list = merchant_map.get(store.uid)
                if not mg_list:
                    mg_list = []
                    merchant_map[store.uid] = mg_list
                mg_list.append(spg.django_model_to_dict(product))
            else:
                logger.error('Global Porudct Error, global id %s : type %s', product.id, store.type)
                raise ValueError('Global Porudct Error, global id %s : type %s' % (product.id, store.type))

        for merchant in merchant_map:
            self.update_global_sku(merchant, merchant_map.get(merchant))

    def update_global_sku(self, merchant_id, global_product_list):
        item_list = []
        merchant = StoreModel.objects.get(uid=merchant_id, type=StoreType.MERCHANT)
        for product in global_product_list:
            if merchant.openid != product.get('openid'):
                logger.error('No permission operation: %s', product)
                raise ValueError('No permission operation')
            item_list.append({
                'global_item_id': int(product.get('product_id')),
                'global_item_sku': product.get('product_sku')
            })
        if len(item_list) > 0:
            for item in item_list:
                self.__update_global_item(merchant_id, item)
                # TODO 是否需要通知修改Goods货号，待确定

    def update_model_sku(self, merchant_id, model_list):
        update_model_dict = {}
        merchant = StoreModel.objects.get(uid=merchant_id, type=StoreType.MERCHANT)
        for model in model_list:
            if merchant.openid != model.get('openid'):
                logger.error('No permission operation: %s', model)
                raise ValueError('No permission operation')
            product_id = model.get('product_id')
            if not product_id:
                variant = StoreProductVariantModel.objects.get(
                    store_product__store__uid=merchant_id, model_id=model.get('model_id'))
                product_id = variant.store_product.product_id
            update_model = update_model_dict.get(product_id)
            if not update_model:
                update_model = []
                update_model_dict[product_id] = update_model
            update_model.append({
                'global_model_id': int(model.get('model_id')),
                'global_model_sku': model.get('model_sku')
            })
        for product_id in update_model_dict:
            self.__update_global_model_sku(merchant_id, {
                'global_item_id': int(product_id),
                'global_model': update_model_dict.get(product_id)
            })
            # TODO 是否需要通知修改Goods model货号，待确定

    def __update_global_item(self, merchant_id, global_item_obj):
        """
        更新全球商品信息
        global_item_obj: obj格式如下
        {
            #必填
            'global_item_id': xxx,
            #需要更新的值
            'global_item_sku': 'xxx'
        }
        """
        global_product = StoreProductModel.objects.get(
            store__type=StoreType.MERCHANT, product_id=global_item_obj.get('global_item_id'))
        detail = self.get_global_product_detail(merchant_id, global_product.id)
        if global_item_obj.get('global_item_name') is not None:
            global_product.product_name = global_item_obj.get('global_item_name')
            detail['global_item_name'] = global_item_obj.get('global_item_name')
        if global_item_obj.get('global_item_sku') is not None:
            global_product.product_sku = global_item_obj.get('global_item_sku')
            detail['global_item_sku'] = global_item_obj.get('global_item_sku')
        if detail.get('dimension').get('package_length') <= 0 \
                or detail.get('dimension').get('package_width') \
                or detail.get('dimension').get('package_height'):
            # 移除物流信息
            del detail['dimension']
        logger.info('update_global_item: %s', detail)
        shopee.request(
            url_key='global_product.update_global_item',
            method='POST', merchant_id=merchant_id, params=detail)
        global_product.save()

    def __update_global_model_sku(self, merchant_id, global_model_obj):
        """
        更新全球商品的规格SKU
        merchant_id: 商户ID
        global_model_obj: obj格式如下
        {
            #必填
            'global_item_id': xxx,
            #必填
            'global_model': [
                {
                    'global_model_id': xxx,
                    'global_model_sku': 'xxx'
                }
            ]
        }
        """
        shopee.request(
            url_key='global_product.update_global_model',
            method='POST', merchant_id=merchant_id, params=global_model_obj)
        for model in global_model_obj.get('global_model'):
            global_model = StoreProductVariantModel.objects.get(
                store_product__store__type=StoreType.MERCHANT, model_id=model.get('global_model_id')
            )
            global_model.model_sku = model.get('global_model_sku')
            global_model.save()
        main_product = StoreProductModel.objects.get(
            product_id=global_model_obj.get('global_item_id'), store__type=StoreType.MERCHANT)
        bus.emit(GLOBAL_PRODUCT_SYNC_EVENT, StoreGlobalProductEmitDataSerializer(main_product).data)

    def get_global_brands(self, merchant_id, category_id):
        return self.__refresh_global_brands(merchant_id, category_id)

    def __refresh_global_brands(self, merchant_id, category_id):
        if merchant_id is None or category_id is None:
            raise ValueError('Missing get attributes params')
        offset = 1
        page_size = 100
        flag = True
        brand_list = []
        while flag:
            ret = shopee.request(
                url_key='global_product.get_brand_list', merchant_id=merchant_id, method='GET',
                params={'category_id': category_id,
                        'page_size': page_size, 'offset': offset, 'status': 1
                        })
            rep = ret.get('response')
            logger.info('get_global_brands: %s', rep)
            brand_list.extend(rep.get('brand_list'))
            flag = rep.get('has_next_page')
            offset = rep.get('next_offset') if flag else 1
        return brand_list

    def get_global_attributes(self, merchant_id, category_id, language='zh-hans'):
        if merchant_id is None or category_id is None or language is None:
            raise ValueError('Missing get attributes params')
        ret = shopee.request(
            url_key='global_product.get_attributes', merchant_id=merchant_id, method='GET',
            params={'language': language, 'category_id': category_id})
        return ret.get('response').get('attribute_list')

    def get_global_product_detail(self, merchant_id, global_product_id):
        global_product = StoreProductModel.objects.get(pk=global_product_id)
        ret = shopee.request(
            url_key='global_product.get_global_item_info', merchant_id=merchant_id, method='GET',
            params={'global_item_id_list': [global_product.product_id]})
        return ret.get('response').get('global_item_list')[0]

    # @transaction.atomic
    def sync_by_merchant(self, merchant_id):
        """
        通过商户 Merchant ID 同步全球商品
        """
        if merchant_id is None:
            raise ValueError('Missing merchant_id')
        start_time = int(time.time())
        logger.info('Sync Merchant: %s Start...', merchant_id)
        item_id_list = []
        flag = True
        logger.info('Sync all global products in the merchant %s', merchant_id)
        offset = ''
        while flag:
            ret = shopee.request(
                url_key='global_product.get_global_item_list', merchant_id=merchant_id, method='GET', params={
                    'offset': offset,
                    'page_size': 50
                })
            if ret.get('response') is None:
                flag = False
                offset = ''
            else:
                response = ret.get('response')
                logger.info('response: %s', response)
                # Batch save product
                if response.get('total_count') > 0:
                    if response.get('global_item_list') is not None:
                        for item in response.get('global_item_list'):
                            global_item_id = item.get('global_item_id')
                            # if not StoreProductModel.objects.filter(product_id=global_item_id).exists():
                            item_id_list.append(global_item_id)
                flag = response.get('has_next_page')
                offset = response.get('offset') if flag else ''

        self.refresh_global_product(merchant_id, item_id_list)
        end_time = int(time.time())
        logger.info('Sync Merchant: %s completion, Take %s s', merchant_id, (end_time - start_time))

    def sync_by_global_item_id(self, merchant_id, global_item_id):
        """
        通过Global Item ID 同步全球商品
        """
        if merchant_id is None or global_item_id is None:
            raise ValueError('Missing merchant_id or global_item_id')
        logger.info('Sync %s shop-specific global products %s', merchant_id, global_item_id)
        self.refresh_global_product(merchant_id, [global_item_id], self.emit_goods)

    def sync_by_shop_item_id(self, shop_store: StoreModel, item_id_list, callback=None):
        """
        通过发布的店铺产品 Item ID 同步全球商品数据，已同步的忽略
        """
        if shop_store is None:
            logger.error('Store error')
            raise ValueError('Store error')
        global_item_id_list = []
        merchant_store = shop_store.merchant
        merchant_id = merchant_store.uid
        item_map = []
        if shop_store.merchant is not None:
            max_len = 20
            for sub_list in self.__split_list(item_id_list, max_len):
                ret = shopee.request(
                    url_key='global_product.get_global_item_id', method='GET', merchant_id=merchant_id, params={
                        'shop_id': shop_store.uid,
                        'item_id_list': sub_list
                    })
                item_id_map = ret.get('response').get('item_id_map')
                item_map.extend(item_id_map)
                for item in item_id_map:
                    global_item_id = item.get('global_item_id')
                    global_item_id_list.append(global_item_id)
        error_list = self.refresh_global_product(merchant_id, global_item_id_list, callback)
        if len(error_list) > 0:
            logger.warning('Retry refresh global product error list %s, %s', len(error_list), error_list)
            for item_id in error_list:
                if len(self.refresh_global_product(merchant_id, [item_id], callback)) == 0:
                    logger.info('Retry refresh global product success %s', item_id)
                    error_list.remove(item_id)
            logger.warning('Retry refresh global product error list %s, %s', len(error_list), error_list)
            for item in item_map:
                if item.get('global_item_id') in error_list:
                    item_map.remove(item)
                    continue
        return item_map

    def emit_goods(self, global_product):
        pass
        # from globalproduct.gRpc.client.global_product import ProductServiceClient
        # try:
        #     product = ProductServiceClient.get_instance().create_from_shopee(
        #         StoreGlobalProductEmitDataSerializer(global_product).data)
        # except Exception as e:
        #     logger.warning('GLOBAL_PRODUCT_SYNC_EVENT Error: %s\n%s', e, traceback.format_exc())
        # else:
        #     if not product:
        #         logger.error('Create product %s fail %s' % global_product.product_sku)
        #     else:
        #         logger.info('Create product %s success', global_product.product_sku)

    def refresh_global_product(self, merchant_id, item_id_list, callback=None):
        """
        刷新全球产品数据
        """
        error_list = []
        if len(item_id_list) > 0:
            # Shopee最大限制为20
            max_len = 20
            store = StoreModel.objects.get(uid=merchant_id)
            for sub_list in self.__split_list(item_id_list, max_len):
                logger.info('Get %s Item Base Info %s', len(sub_list), sub_list)
                try:
                    ret = shopee.request(
                        url_key='global_product.get_global_item_info', merchant_id=merchant_id, method='GET',
                        params={'global_item_id_list': sub_list})
                    for item in ret.get('response').get('global_item_list'):
                        global_product = self.__save_product(store, item)
                        if callback:
                            try:
                                callback(global_product)
                            except Exception as e:
                                logger.warning('Callback Error: %s', e, traceback.format_exc())
                except Exception as e:
                    logger.warning('Refresh Global Product Error: %s\n%s', e, traceback.format_exc())
                    error_list.extend(sub_list)
        if len(error_list) > 0:
            logger.warning('Refresh Global Product Error List: %s, %s', len(error_list), error_list)
        return error_list

    @transaction.atomic
    def __save_product(self, store: StoreModel, item_data):
        """
        保存或刷新StoreProduct数据
        """
        # 设置
        logger.info('__save_product ', item_data)
        global_item_id = item_data.get('global_item_id')
        if StoreProductModel.objects.filter(product_id=global_item_id, store=store).exists():
            store_global_product = StoreProductModel.objects.get(
                product_id=global_item_id, store=store)
        else:
            store_global_product = StoreProductModel(product_id=global_item_id, store=store)
        store_global_product.openid = store.openid
        store_global_product.creater = store.creater
        store_global_product.product_name = item_data.get('global_item_name')
        store_global_product.product_sku = item_data.get('global_item_sku')
        store_global_product.product_status = item_data.get('global_item_status')
        if 'normal'.upper() == item_data.get('description_type').upper():
            store_global_product.description = item_data.get('description')
        elif 'extended'.upper() == item_data.get('description_type').upper():
            field_list = item_data.get('description_info').get('extended_description').get('field_list')
            store_global_product.description = ''
            for field in field_list:
                if field.get('field_type').upper() == 'text'.upper():
                    store_global_product.description += field.get('text')
        store_global_product.brand_id = item_data.get('brand').get('brand_id')
        store_global_product.brand_name = item_data.get('brand').get('original_brand_name')
        store_global_product.category_id = item_data.get('category_id')
        store_global_product.days_to_ship = item_data.get('pre_order').get('days_to_ship')
        store_global_product.weight = item_data.get('weight')
        store_global_product.length = item_data.get('dimension').get('package_length')
        store_global_product.width = item_data.get('dimension').get('package_width')
        store_global_product.height = item_data.get('dimension').get('package_height')
        store_global_product.image_url = item_data.get('image').get('image_url_list')[0]
        store_global_product.save()
        self.__save_product_media(store_global_product, item_data.get('image'), item_data.get('video'))
        self.__save_product_price_info(store_global_product, item_data.get('price_info'))
        if item_data.get('has_model'):
            # 获取规格Model List
            self.__save_prodcut_variants(store_global_product)
        return store_global_product

    def __save_product_price_info(self, product: StoreProductModel, price_infos):
        StoreProductPriceInfoModel.objects.filter(store_product=product, type=StoreProductType.MAIN).delete()
        if price_infos:
            for price_info in price_infos:
                price = StoreProductPriceInfoModel(store_product=product, type=StoreProductType.MAIN)
                price.openid = product.openid
                price.creater = product.creater
                price.original_price = price_info.get('original_price')
                price.sip_item_price = price_info.get('sip_item_price')
                price.sip_item_price_source = price_info.get('sip_item_price_source')
                price.currency = price_info.get('currency')
                price.save()

    def __save_prodcut_variants(self, product: StoreProductModel):
        ret = shopee.request(
            url_key='global_product.get_global_model_list', merchant_id=product.store.uid, method='GET', params={
                'global_item_id': product.product_id
            })
        resp = ret.get('response')
        # logger.info('product.get_model_list: %s', resp)
        tier_variation = resp.get('tier_variation')
        StoreProductVariantModel.objects.filter(store_product=product).delete()
        self.__save_product_option(product, tier_variation)
        model_list = resp.get('global_model')
        if model_list and len(model_list) > 0:
            for model in model_list:
                variants = StoreProductVariantModel(model_id=model.get('global_model_id'), store_product=product)
                variants.openid = product.openid
                variants.creater = product.creater
                tier_index = model.get('tier_index')
                index_str_list = []
                for index in tier_index:
                    index_str_list.append(str(index))
                variants.option_item_index = ','.join(index_str_list)
                variants.model_sku = model.get('global_model_sku')
                variants.save()
                self.__save_variant_price_info(variants, model.get('price_info'))
                self.__save_variant_stock_info(variants, model.get('stock_info'))

    def __save_variant_price_info(self, variant: StoreProductVariantModel, price_info):
        StoreProductPriceInfoModel.objects.filter(
            store_product=variant.store_product, variant=variant, type=StoreProductType.VARIANTS).delete()
        if price_info:
            price = StoreProductPriceInfoModel(
                store_product=variant.store_product, variant=variant, type=StoreProductType.VARIANTS
            )
            price.openid = variant.openid
            price.creater = variant.creater
            price.original_price = price_info.get('original_price')
            price.save()

    def __save_variant_stock_info(self, variant: StoreProductVariantModel, stock_info_list):
        StoreProductVariantStock.objects.filter(variant_id=variant.id).delete()
        for stock_info in stock_info_list:
            stock_instance = StoreProductVariantStock(
                variant=variant,
                stock_type=stock_info['stock_type'],
                current_stock=stock_info['current_stock'],
                reserved_stock=stock_info['reserved_stock'],
                stock_location_id=stock_info['stock_location_id'],
                openid=variant.openid,
                creater=variant.creater
            )
            stock_instance.save()

    def __save_product_option(self, product: StoreProductModel, tier_variation):
        StoreProductOptionModel.objects.filter(store_product=product).delete()
        StoreProductOptionItemModel.objects.filter(store_product=product).delete()
        for i, tv in enumerate(tier_variation):
            product_option = StoreProductOptionModel(store_product=product, name=tv.get('name'), index=i)
            product_option.save()
            option_item_list = tv.get('option_list')
            items = []
            for j, item in enumerate(option_item_list):
                option_item = StoreProductOptionItemModel(
                    openid=product.openid, creater=product.creater,
                    store_product=product, store_product_option=product_option,
                    name=item.get('option'), index=j)
                if item.get('image'):
                    option_item.image_id = item.get('image').get('image_id')
                    option_item.image_url = item.get('image').get('image_url')
                items.append(option_item)
            StoreProductOptionItemModel.objects.bulk_create(items)

    def __save_product_media(self, product: StoreProductModel, image, video):
        id_list = image.get('image_id_list')
        url_list = image.get('image_url_list')
        media_list = []
        StoreProductMedia.objects.filter(store_product=product).delete()
        if len(id_list) == len(url_list):
            for i, image_id in enumerate(id_list):
                media_list.append(
                    StoreProductMedia(
                        openid=product.openid, creater=product.creater,
                        store_product=product, type=MediaType.IMAGE,
                        url=url_list[i], image_id=id_list[i], index=i
                    )
                )
        if video:
            for i, v in enumerate(video):
                media_list.append(StoreProductMedia(
                    openid=product.openid, creater=product.creater,
                    store_product=product, type=MediaType.VIDEO, url=v.get('video_url'), index=i)
                )
                media_list.append(StoreProductMedia(
                    openid=product.openid, creater=product.creater,
                    store_product=product, type=MediaType.THUMBNAIL, url=v.get('thumbnail_url'), index=i)
                )
        if len(media_list) > 0:
            StoreProductMedia.objects.bulk_create(media_list)

    def get_global_model_list(self, merchant_id, global_item_id):
        ret = shopee.request('global_product.get_global_model_list',
                             merchant_id=merchant_id, method='GET', params={'global_item_id': global_item_id})
        logger.info('get global model list ret %s ' % ret)
        return (ret['response']['tier_variation'], ret['response']['global_model'])

    def publish_global_product(self, merchant_id, product_info):
        ret = shopee.request('global_product.add_global_item', merchant_id=merchant_id, method='POST',
                             params=product_info)
        logger.info('add global info ret %s ' % ret)
        global_item_id = ret['response']['global_item_id']
        return global_item_id

    def init_global_variation(self, merchant_id, variation_info):
        ret = shopee.request('global_product.init_tier_variation', merchant_id=merchant_id, method='POST',
                             params=variation_info)
        logger.info('init tier variation %s ' % ret)
        return True

    def register_supplier_info(self, item_id_list):
        from goods.gRpc.client.goods_service_stub import GoodsServiceClient, CreateGroupRequest
        from goods.gRpc.client.types.goods import Goods
        global_products = []
        for item_id in item_id_list:
            store_product = StoreProductModel.objects.filter(product_id=item_id).first()
            if not store_product:
                logger.error('register supplier info can not find product of item id %s', item_id)
                continue
            global_products.append(store_product.global_product.first())
        if not global_products:
            logger.warning('No global product of item id list found ', item_id_list)
        for global_product in global_products:
            goods = []
            for variant in global_product.product_variant.all():
                goods.append(Goods(
                    goods_code=variant.model_sku,
                    goods_image=self._get_variant_image(variant)
                ))
            req = CreateGroupRequest(name=global_product.product_sku, goods=goods, product_id=global_product.id)
            try:
                GoodsServiceClient.get_instance().create_group(req)
                SupplierRegister.get_instance().register_purchase_plan(product_id=global_product.id)
            except Exception as e:
                logger.error('Create goods group fail %s', e)
                continue

    def _get_variant_image(self, variant: StoreProductVariantModel):
        index = variant.option_item_index.split(',')[0]
        option = variant.store_product.product_option.filter(index=0).first()
        first_option_item = StoreProductOptionItemModel.objects.filter(
            store_product=variant.store_product, index=index, store_product_option=option).first()
        return first_option_item.image_url if first_option_item else None

    def __split_list(self, iterable, n=1):
        """
        按照指定数量, 分割list表
        """
        itl = len(iterable)
        for ndx in range(0, itl, n):
            it = iterable[ndx:min(ndx + n, itl)]
            yield it
