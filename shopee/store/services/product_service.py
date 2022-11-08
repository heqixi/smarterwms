import asyncio
import logging
import threading
import time
import traceback

from django.db import transaction

from store.common import StoreType, MediaType, StoreProductType, StoreProductStatus, StoreStatus
from store.models import StoreProductModel, StoreModel, StoreProductMedia, StoreProductOptionItemModel, \
    StoreProductOptionModel, StoreProductVariantModel, StoreProductPriceInfoModel
from store.services.global_service import GlobalService
from utils import shopee, spg

logger = logging.getLogger()


class ProductService(object):
    """
    店铺产品服务，对外提供店铺产品相关操作功能
    """
    __create_key = object()
    lock = threading.RLock()
    service = None

    def __init__(self, create_key):
        assert (create_key == ProductService.__create_key), \
            "ProductService objects must be created using ProductService.get_instance"

    @classmethod
    def get_instance(cls):
        if cls.service is None:
            cls.lock.acquire()
            if cls.service is None:
                cls.service = cls(ProductService.__create_key)
            cls.lock.release()
            return cls.service
        return cls.service

    def get_prodcut_list(self, openid, shop_id=None, product_status: StoreProductStatus = StoreProductStatus.NORMAL):
        return asyncio.run(self.get_prodcut_list_by_async_gather(openid, shop_id, product_status))

    async def get_prodcut_list_by_async_gather(self, openid, shop_id=None, product_status: StoreProductStatus = StoreProductStatus.NORMAL):
        data = []
        tasks = []
        if shop_id:
            task = asyncio.create_task(self.get_shop_prodcut_list_by_async(shop_id, product_status))
            tasks.append(task)
        else:
            for store in StoreModel.objects.filter(openid=openid, status=StoreStatus.NORMAL, type=StoreType.SHOP):
                task = asyncio.create_task(self.get_shop_prodcut_list_by_async(store.uid, product_status))
                tasks.append(task)
        results = await asyncio.gather(*tasks)
        for result in results:
            data.append(result)
        return data

    async def get_shop_prodcut_list_by_async(
            self, shop_id, product_status: StoreProductStatus = StoreProductStatus.NORMAL):
        if not shop_id:
            raise ValueError('Shop ID can not be None')
        item_list = []
        flag = True
        logger.info('Get shop %s products by status', shop_id)
        offset = 1
        while flag:
            ret = await asyncio.create_task(
                shopee.async_request(url_key='product.get_item_list', shop_id=shop_id, method='GET', params={
                    'offset': offset,
                    'page_size': 50,
                    'item_status': [product_status]
                })
            )
            if ret.get('response') is None:
                flag = False
                offset = 1
            else:
                response = ret.get('response')
                logger.info('response: %s', response)
                # Batch save product
                if response.get('total_count') > 0:
                    if response.get('item') is not None:
                        for item in response.get('item'):
                            item_list.append({
                                'shop_id': shop_id,
                                'item_id': item.get('item_id'),
                                'item_status': item.get('item_status')
                            })
                flag = response.get('has_next_page')
                offset = response.get('next_offset') if flag else 1
        return item_list

    def get_product_detail(self, product_id):
        """
        通过ID获取产品详情
        """
        return None

    def update_openid(self, store: StoreModel):
        StoreProductModel.objects.filter(store=store).update(openid=store.openid, creater=store.creater)

    # @transaction.atomic
    def sync_by_shop(self, shop_id):
        """
        同步店铺产品
        """
        if shop_id is None:
            raise ValueError('Missing shop_id')
        start_time = int(time.time())
        logger.info('Sync Shop: %s Start...', shop_id)
        item_id_list = []
        flag = True
        logger.info('Sync all products in the shop %s', shop_id)
        offset = 1
        while flag:
            ret = shopee.request(url_key='product.get_item_list', shop_id=shop_id, method='GET', params={
                'offset': offset,
                'page_size': 50,
                'item_status': ['NORMAL', 'BANNED', 'DELETED', 'UNLIST']
            })
            if ret.get('response') is None:
                flag = False
                offset = 1
            else:
                response = ret.get('response')
                logger.info('response: %s', response)
                # Batch save product
                if response.get('total_count') > 0:
                    if response.get('item') is not None:
                        for item in response.get('item'):
                            item_id = item.get('item_id')
                            # if not StoreProductModel.objects.filter(product_id=item_id).exists():
                            item_id_list.append(item_id)
                flag = response.get('has_next_page')
                offset = response.get('next_offset') if flag else 1

        self.refresh_product(shop_id, item_id_list, GlobalService.get_instance().emit_goods)
        end_time = int(time.time())
        logger.info('Sync Shop: %s completion, Take %s s', shop_id, (end_time - start_time))

    def sync_by_item_id(self, shop_id, item_id):
        if shop_id is None or item_id is None:
            raise ValueError('Missing shop_id or item_id')
        logger.info('Sync %s shop-specific products %s', shop_id, item_id)
        self.refresh_product(shop_id, [item_id], GlobalService.get_instance().emit_goods)

    def sync_global_product_by_item(self, shop_store: StoreModel, item_list):
        shop_item_id_list = []
        for item in item_list:
            if not StoreProductModel.objects.filter(
                    store=shop_store, product_id=item.get('item_id')).exists():
                shop_item_id_list.append(item.get('item_id'))
            elif not StoreProductModel.objects.get(
                    store=shop_store, product_id=item.get('item_id')).global_product.first():
                shop_item_id_list.append(item.get('item_id'))
        self.refresh_product(shop_store.uid, shop_item_id_list, GlobalService.get_instance().emit_goods)

    def get_product_shop_price(self, shop_id, item_id):
        ret = shopee.request(url_key='product.get_model_list', shop_id=shop_id, method='GET',
                             params={'item_id': item_id})
        models = ret.get('response').get('model')
        return models

    def update_discount_items(self, shop_id, discount_id, item_list):
        ret = shopee.request(url_key='discount.update_discount_item', shop_id=shop_id, method='POST',
                             params={'discount_id': discount_id, 'item_list': item_list})
        logger.info('update discount items,  %s', ret)
        return ret['response']['count']

    def add_discount_item(self, shop_id, discount_id, item_list):
        ret = shopee.request(url_key='discount.add_discount_item', shop_id=shop_id, method='POST',
                             params={'discount_id': discount_id, 'item_list': item_list})
        logger.info('add discount items,  %s', ret)
        return ret['response']['count']

    def get_discount_list(self, shop_id, status='ongoing'):
        ret = shopee.request(url_key='discount.get_discount_list', shop_id=shop_id, method='GET',
                             params={'discount_status': status, 'page_no': 1, 'page_size': 100})
        logger.info('get discount list ', ret)
        return ret['response']['discount_list']

    def get_product_price_info(self, shop_id, item_id_list):
        info_list = []
        if len(item_id_list) > 0:
            for item_id in item_id_list:
                ret = shopee.request(url_key='discount.get_discount', shop_id=shop_id, method='GET',
                                     params={'item_id': item_id})
                info_list.append(ret.get('response').get('model'))
        return info_list

    def refresh_product(self, shop_id, item_id_list, callback=None):
        if len(item_id_list) > 0:
            # Shopee最大限制为50
            max_len = 50
            store = StoreModel.objects.get(uid=shop_id)
            item_list = []
            for sub_list in self.__split_list(item_id_list, max_len):
                logger.info('Get %s Item Base Info %s  %s', len(sub_list), shop_id, sub_list)
                ret = shopee.request(url_key='product.get_item_base_info', shop_id=shop_id, method='GET',
                                     params={'item_id_list': sub_list})
                for item in ret.get('response').get('item_list'):
                    self.__save_product(store, item)
                    item_list.append(item)
            global_product_list = []
            item_map = GlobalService.get_instance().sync_by_shop_item_id(
                store, item_id_list, lambda global_product: global_product_list.append(global_product))
            self.link_global_product(store, item_map)
            if callback:
                try:
                    for gp in global_product_list:
                        callback(gp)
                except Exception as e:
                    logger.warning('Refresh Product Callback Error: %s\n%s', e, traceback.format_exc())

    def link_global_product(self, store: StoreModel, item_list):
        """
        关联全球商品-店铺商品
        """
        for item in item_list:
            g_product = StoreProductModel.objects.filter(
                store=store.merchant, product_id=item.get('global_item_id')).first()
            if g_product:
                product = StoreProductModel.objects.get(store=store, product_id=item.get('item_id'))
                if not g_product.shop_products.filter(product_id=product.product_id).exists():
                    g_product.shop_products.add(product)
                    g_product.save()
            else:
                logger.error('global product: %s not exist', item.get('global_item_id'))

    def get_product_store_price(self, shop_id, product_id):
        store_product = StoreProductModel.objects.filter(product_id=product_id).first()
        if not store_product:
            try:
                self.refresh_product(shop_id, product_id)
            except Exception as exc:
                logger.error('refresh product fail %s ', exc)
            finally:
                return []
        model_prices = []
        for variant in store_product.product_variant.all():
            model_price = spg.django_model_to_dict(model=variant.variant_price.first())
            model_prices.append(model_price)
        return model_prices

    def get_variant_store_price(self, model_id):
        variant = StoreProductVariantModel.objects.filter(model_id=model_id).first()
        if not variant:
            return None
        return spg.django_model_to_dict(model=variant.variant_price.first())

    @transaction.atomic
    def __save_product(self, store: StoreModel, item_data):
        """
        保存或刷新StoreProduct数据
        """
        # 设置
        item_id = item_data.get('item_id')
        if StoreProductModel.objects.filter(product_id=item_id, store=store).exists():
            store_product = StoreProductModel.objects.get(product_id=item_id, store=store)
        else:
            store_product = StoreProductModel(product_id=item_id, store=store)
        logger.info('product data ', item_data)
        store_product.openid = store.openid
        store_product.creater = store.creater
        store_product.product_name = item_data.get('item_name')
        store_product.product_sku = item_data.get('item_sku')
        store_product.product_status = item_data.get('item_status')
        if 'normal'.upper() == item_data.get('description_type').upper():
            store_product.description = item_data.get('description')
        elif 'extended'.upper() == item_data.get('description_type').upper():
            field_list = item_data.get('description_info').get('extended_description').get('field_list')
            store_product.description = ''
            for field in field_list:
                if field.get('field_type').upper() == 'text'.upper():
                    store_product.description += field.get('text')
        store_product.brand_id = item_data.get('brand').get('brand_id')
        store_product.brand_name = item_data.get('brand').get('original_brand_name')
        store_product.category_id = item_data.get('category_id')
        store_product.days_to_ship = item_data.get('pre_order').get('days_to_ship')
        store_product.weight = item_data.get('weight')
        store_product.length = item_data.get('dimension').get('package_length')
        store_product.width = item_data.get('dimension').get('package_width')
        store_product.height = item_data.get('dimension').get('package_height')
        store_product.image_url = item_data.get('image').get('image_url_list')[0]
        store_product.save()
        self.__save_product_media(store_product, item_data.get('image'), item_data.get('video_info'))
        self.__save_prodouct_price_info(store_product, item_data.get('price_info'))
        if item_data.get('has_model'):
            # 获取规格Model List
            self.__save_prodcut_variants(store_product)
        return store_product

    def __save_prodouct_price_info(self, product: StoreProductModel, price_infos):
        StoreProductPriceInfoModel.objects.filter(store_product=product, type=StoreProductType.MAIN).delete()
        if price_infos:
            for price_info in price_infos:
                price = StoreProductPriceInfoModel(store_product=product, type=StoreProductType.MAIN)
                price.openid = product.openid
                price.creater = product.creater
                price.original_price = price_info.get('original_price')
                price.current_price = price_info.get('current_price')
                price.inflated_price_of_original_price = price_info.get('inflated_price_of_original_price')
                price.inflated_price_of_current_price = price_info.get('inflated_price_of_current_price')
                price.sip_item_price = price_info.get('sip_item_price')
                price.sip_item_price_source = price_info.get('sip_item_price_source')
                price.currency = price_info.get('currency')
                price.save()

    def __save_prodcut_variants(self, product: StoreProductModel):
        ret = shopee.request(
            url_key='product.get_model_list', shop_id=product.store.uid, method='GET', params={
                'item_id': product.product_id
            })
        resp = ret.get('response')
        tier_variation = resp.get('tier_variation')
        self.__save_product_option(product, tier_variation)
        StoreProductVariantModel.objects.filter(store_product=product).delete()
        model_list = resp.get('model')
        if model_list and len(model_list) > 0:
            for model in model_list:
                variants = StoreProductVariantModel(model_id=model.get('model_id'), store_product=product)
                variants.openid = product.openid
                variants.creater = product.creater
                tier_index = model.get('tier_index')
                index_str_list = []
                for index in tier_index:
                    index_str_list.append(str(index))
                variants.option_item_index = ','.join(index_str_list)
                variants.promotion_id = model.get('promotion_id')
                variants.model_sku = model.get('model_sku')
                variants.save()
                self.__save_variant_price_info(variants, model.get('price_info'))

    def __save_variant_price_info(self, variant: StoreProductVariantModel, price_infos):
        StoreProductPriceInfoModel.objects.filter(
            store_product=variant.store_product, variant=variant, type=StoreProductType.VARIANTS).delete()
        for price_info in price_infos:
            price = StoreProductPriceInfoModel(
                store_product=variant.store_product, variant=variant, type=StoreProductType.VARIANTS)
            price.openid = variant.openid
            price.creater = variant.creater
            price.original_price = price_info.get('original_price')
            price.current_price = price_info.get('current_price')
            price.inflated_price_of_original_price = price_info.get('inflated_price_of_original_price')
            price.inflated_price_of_current_price = price_info.get('inflated_price_of_current_price')
            price.sip_item_price = price_info.get('sip_item_price')
            price.sip_item_price_source = price_info.get('sip_item_price_source')
            price.currency = price_info.get('currency')
            price.save()

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
                        store_product=product, type=MediaType.IMAGE,
                        url=url_list[i], image_id=id_list[i], index=i
                    )
                )
        if video:
            for i, v in enumerate(video):
                media_list.append(StoreProductMedia(
                    store_product=product, type=MediaType.VIDEO, url=v.get('video_url'), index=i)
                )
                media_list.append(StoreProductMedia(
                    store_product=product, type=MediaType.THUMBNAIL, url=v.get('thumbnail_url'), index=i)
                )
        if len(media_list) > 0:
            StoreProductMedia.objects.bulk_create(media_list)

    def __split_list(self, iterable, n=1):
        """
        按照指定数量, 分割list表
        """
        itl = len(iterable)
        for ndx in range(0, itl, n):
            it = iterable[ndx:min(ndx + n, itl)]
            yield it

    def get_category(self, merchant_id, language='zh-hans'):
        ret = shopee.request('global_product.get_category', merchant_id=merchant_id, method='GET',
                             params={'language': language})
        logger.info('get category %s', ret)
        return ret['response']['category_list']

    def get_category_attribute(self, merchant_id, category_id, language='zh-hans'):
        ret = shopee.request()

    def upload_image(self, files, openid, scene="normal"):
        from store.services.store_service import StoreService
        store = StoreModel.objects.get(openid=openid, type=StoreType.MERCHANT)
        token = StoreService.get_instance().get_store_token_info(store_id=store.id).info_value
        ret = shopee.public_request(token['partner_id'], token['partner_key'], 'media_space.upload_image',
                                    {'scene': scene}, files=files)
        return ret['response']['image_info']

    def add_global_item(self, merchant_id, product_info):
        ret = shopee.request('global_product.add_global_item', merchant_id=merchant_id, method='POST',
                             params=product_info)
        logger.info('add global info ret %s ' % ret)
        return ret['response']['global_item_id']

    def init_tier_variation(self, merchant_id, variation_info):
        ret = shopee.request('global_product.init_tier_variation', merchant_id=merchant_id, method='POST',
                             params=variation_info)
        logger.info('init tier variation %s ' % ret)
        return True

    def create_publish_task(self, merchant_id, publish_info):
        ret = shopee.request('global_product.create_publish_task', merchant_id=merchant_id, method='POST',
                             params=publish_info)
        logger.info('create tier variation %s ' % ret)
        return ret['response']['publish_task_id']

    def get_publish_task_result(self, publish_task_id, merchant_id):
        ret = shopee.request('global_product.get_publish_task_result', merchant_id=merchant_id,
                             method='GET', params={'publish_task_id': publish_task_id})
        logger.info('get publish task result %s ' % ret['response'])
        return ret['response']

    def get_store_model_list(self, item_id, shop_id):
        ret = shopee.request('product.get_model_list', shop_id=shop_id, method='GET', params={
            'item_id': item_id
        })
        logger.info('get store model list %s ' % ret)
        return (ret['response']['tier_variation'], ret['response']['model'])

