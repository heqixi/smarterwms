import logging
import threading

from django.db import transaction
from base.bustools import GLOBAL_BUS as bus, FETCH_PRODUCT_RECEIVE_EVENT

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

    def create_region_settings(self, openid, params):
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


