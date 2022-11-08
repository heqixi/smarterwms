import logging
import threading

from django.db import transaction
from base.bustools import GLOBAL_BUS as bus, FETCH_PRODUCT_RECEIVE_EVENT
from fetchbox.common import MediaType, FetchProductStatus
from fetchbox.models import FetchProductModel, FetchOptionModel, FetchOptionItemModel, FetchVariantModel, FetchMediaModel
from fetchbox.serializers import FetchProductDetailsSerializer
from product.services.product_service import GlobalProductService

logger = logging.getLogger()


class FetchService(object):
    """
    采集服务
    """
    __create_key = object()
    lock = threading.RLock()
    service = None

    def __init__(self, create_key):
        assert (create_key == FetchService.__create_key), \
            "StoreService objects must be created using StoreService.get_instance"

    @classmethod
    def get_instance(cls):
        if cls.service is None:
            cls.lock.acquire()
            if cls.service is None:
                cls.service = cls(FetchService.__create_key)
            cls.lock.release()
            return cls.service
        return cls.service

    def receive_product(self, openid, creater, fetch_id):
        fetch_product = FetchProductModel.objects.get(pk=fetch_id, openid=openid)
        serializer = FetchProductDetailsSerializer(fetch_product)
        product = GlobalProductService.get_instance().create_product(serializer.data, openid, creater)
        fetch_product.status = FetchProductStatus.CLAIMED
        fetch_product.save()
        logger.info('serializer.data: %s', serializer.data)
        return product
        # bus.emit(FETCH_PRODUCT_RECEIVE_EVENT, serializer.data, openid, creater)

    @transaction.atomic
    def fetch_product(self, openid, fetch_data_list, refresh=False):
        logging.info('fetch_data: %s', fetch_data_list)
        for fetch_data in fetch_data_list:
            fetchs = FetchProductModel.objects.filter(url=fetch_data.get('url'))
            if fetchs.exists():
                if refresh:
                    self.__refresh_fetch_data(fetchs.first(), fetch_data)
                else:
                    logger.error('Repeat Fetch: %s', fetch_data.get('url'))
                    raise ValueError('Repeat Fetch')
            else:
                fetch_product = FetchProductModel(openid=openid, creater='')
                self.__refresh_fetch_data(fetch_product, fetch_data)

    def __refresh_fetch_data(self, fetch_product: FetchProductModel, fetch_data):
        fetch_product.name = fetch_data.get('name')
        fetch_product.url = fetch_data.get('url')
        fetch_product.price = fetch_data.get('price')
        fetch_product.company = fetch_data.get('company')
        fetch_product.logistics_city = fetch_data.get('logisticsCity')
        fetch_product.mix_purchase_qty = fetch_data.get('mixPurchaseQty')
        fetch_product.logistics_costs = fetch_data.get('logisticsCosts')
        fetch_product.status = FetchProductStatus.UNCLAIMED
        pack = fetch_data.get('pack')
        if pack:
            weight = pack.get('packWeight') if pack.get('packWeight') else pack.get('weight')
            fetch_product.weight = weight
            size = pack.get('size')
            if size:
                fetch_product.length = size.get('length')
                fetch_product.width = size.get('width')
                fetch_product.height = size.get('height')
        fetch_product.description = ''
        for item in fetch_data.get('description').get('attributes').items():
            fetch_product.description += '%s: %s\n' % (item[0], item[1])
        fetch_product.save()
        self.__save_variants_info(fetch_product, fetch_data.get('variants'))
        self.__save_media(fetch_product, fetch_data)
        return fetch_product

    def __save_media(self, fetch_product, fetch_data):
        media_data = fetch_data.get('media')
        if not media_data:
            logger.error('Missing Media data')
            raise ValueError('Missing Media data')
        FetchMediaModel.objects.filter(product=fetch_product).delete()
        medias = []
        for i, image_url in enumerate(media_data.get('images')):
            if i == 0:
                medias.append(FetchMediaModel(
                    product=fetch_product, url=image_url, type=MediaType.IMAGE, is_main=1,
                    openid=fetch_product.openid, creater=fetch_product.creater
                ))
            else:
                medias.append(FetchMediaModel(
                    product=fetch_product, url=image_url, type=MediaType.IMAGE, is_main=0,
                    openid=fetch_product.openid, creater=fetch_product.creater
                ))
        if media_data.get('video') and media_data.get('video').get('url'):
            medias.append(FetchMediaModel(
                product=fetch_product, url=media_data.get('video').get('url'),
                type=MediaType.VIDEO, is_main=1,
                openid=fetch_product.openid, creater=fetch_product.creater
            ))
        variants_data = fetch_data.get('variants')
        for item_data in variants_data.get('optionItemList')[0]:
            if item_data.get('image'):
                medias.append(FetchMediaModel(
                    product=fetch_product, url=item_data.get('image'),
                    type=MediaType.IMAGE, is_main=0,
                    openid=fetch_product.openid, creater=fetch_product.creater
                ))
        description = fetch_data.get('description')
        desc_images = description.get('images')
        if desc_images:
            for image_url in desc_images:
                medias.append(FetchMediaModel(
                    product=fetch_product, url=image_url,
                    type=MediaType.IMAGE, is_main=0,
                    openid=fetch_product.openid, creater=fetch_product.creater
                ))
        FetchMediaModel.objects.bulk_create(medias)

    def __save_variants_info(self, fetch_product, variants_data):
        if not variants_data:
            logger.error('Missing Variants Data')
            raise ValueError('Missing Variants Data')
        FetchOptionModel.objects.filter(product=fetch_product).delete()
        FetchVariantModel.objects.filter(product=fetch_product).delete()
        for i, option_name in enumerate(variants_data.get('options')):
            option = FetchOptionModel(
                product=fetch_product, name=option_name, index=i,
                openid=fetch_product.openid, creater=fetch_product.creater
            )
            option.save()
            items = []
            for i, item_data in enumerate(variants_data.get('optionItemList')[i]):
                items.append(FetchOptionItemModel(
                    product=fetch_product, option=option,
                    name=item_data.get('name'), image=item_data.get('image'),
                    openid=fetch_product.openid, creater=fetch_product.creater, index=i
                ))
            FetchOptionItemModel.objects.bulk_create(items)
        # 创建变体数据
        variants = []
        for variant_data in variants_data.get('models'):
            items_index = []
            for index in variant_data.get('itemIndex'):
                items_index.append(str(index))
            variants.append(FetchVariantModel(
                product=fetch_product, openid=fetch_product.openid, creater=fetch_product.creater,
                item_index=','.join(items_index), name=variant_data.get('name'),
                price=variant_data.get('price'), stock_qty=variant_data.get('stockQty')
            ))
        FetchVariantModel.objects.bulk_create(variants)

    def create_region_settings(self, openid, user_id, params):
        raise Exception('Improper Denpendency')  # TODO
        # area = params.get('area')
        # short_area = params.get('short_area')
        # currency = params.get('currency')
        # exchange_rate = params.get('exchange_rate') if params.get('exchange_rate') else 0
        # activity_rate = params.get('activity_rate') if params.get('activity_rate') else 0
        # commission_rate = params.get('commission_rate') if params.get('commission_rate') else 0
        # transaction_rate = params.get('transaction_rate') if params.get('transaction_rate') else 0
        # withdrawal_rate = params.get('withdrawal_rate') if params.get('withdrawal_rate') else 0
        # exchange_loss_rate = params.get('exchange_loss_rate') if params.get('exchange_loss_rate') else 0
        # buyer_shipping = params.get('buyer_shipping')
        # other_fee = params.get('other_fee')
        # if not area or not short_area or not currency or not buyer_shipping:
        #     raise ValueError('Missing params')
        #
        # region_id = params.get('id')
        # if region_id:
        #     region_settings = ShopeeRegionSettingsModel.objects.get(pk=region_id)
        #     ShopeeLogisticsCalcModel.objects.filter(region_settings=region_settings).delete()
        # else:
        #     region_settings = ShopeeRegionSettingsModel(openid=openid, creater='')
        # region_settings.area = area
        # region_settings.short_area = short_area
        # region_settings.currency = currency
        # region_settings.buyer_shipping = buyer_shipping
        # region_settings.other_fee = other_fee
        # region_settings.exchange_rate = exchange_rate
        # region_settings.activity_rate = activity_rate
        # region_settings.commission_rate = commission_rate
        # region_settings.transaction_rate = transaction_rate
        # region_settings.withdrawal_rate = withdrawal_rate
        # region_settings.exchange_loss_rate = exchange_loss_rate
        # region_settings.save()
        # logistics_calc_list = params.get('logistics_calc_list')
        # if logistics_calc_list and len(logistics_calc_list) > 0:
        #     for logistics_calc in logistics_calc_list:
        #         calc = ShopeeLogisticsCalcModel(region_settings=region_settings, openid=openid, creater='')
        #         calc.calc_type = logistics_calc.get('calc_type')
        #         calc.logistics_fee = logistics_calc.get('logistics_fee')
        #         calc.min_weight = logistics_calc.get('min_weight')
        #         calc.interval = logistics_calc.get('interval')
        #         max_weight = logistics_calc.get('max_weight')
        #         if max_weight:
        #             calc.max_weight = max_weight
        #         calc.save()
        # stores = params.get('stores')
        # all_store_settings = getattr(region_settings, ShopeeStoreRegionSetting.RelativeFields.SETTING_STORES).all()
        # if stores:
        #     for store_uid in stores:
        #         store_setting = all_store_settings.filter(store_uid=store_uid)
        #         if not store_setting:
        #             store_setting = ShopeeStoreRegionSetting(
        #                 store_uid=store_uid,
        #                 region_settings=region_settings,
        #                 openid=region_settings.openid,
        #                 creater=region_settings.creater
        #             )
        #             store_setting.save()
        # for store_setting in all_store_settings:
        #     found = False
        #     for store_uid in stores:
        #         if store_uid == store_setting.store_uid:
        #             found = True
        #             break
        #     if not found:
        #         store_setting.delete()

    def get_store_setting(self, store_uid):
        raise Exception('Improper Denpendency') #TODO
        # store_setting = ShopeeStoreRegionSetting.objects.filter(store_uid=store_uid).first()
        # if not store_setting:
        #     return None
        # region_setttings = store_setting.region_settings
        # return ShopeeRegionSettingsGetSerializer(region_setttings).data


