import logging
import threading
import time

from django.conf import settings
from django.db import transaction

from order.services.order_service import OrderService
from store.common import StoreType, PlatformType, StoreStatus
from store.models import StoreModel, StoreInfoModel
from store.services.dtos.shoppe_callback_dto import ShopeeCallbackDto
from store.services.product_service import ProductService
from utils import shopee, spg

logger = logging.getLogger()


class StoreService(object):
    """
    店铺服务，对外提供店铺相关操作功能
    """
    __create_key = object()
    lock = threading.RLock()
    service = None

    def __init__(self, create_key):
        assert (create_key == StoreService.__create_key), \
            "StoreService objects must be created using StoreService.get_instance"

    @classmethod
    def get_instance(cls):
        if cls.service is None:
            cls.lock.acquire()
            if cls.service is None:
                cls.service = cls(StoreService.__create_key)
            cls.lock.release()
            return cls.service
        return cls.service

    def get_store_by_uid(self, store_uid):
        store = StoreModel.objects.filter(uid=store_uid).first()
        if not store:
            return None
        store_dict = spg.django_model_to_dict(model=store)
        if store.type == StoreType.SHOP:
            store_dict['merchant'] = spg.django_model_to_dict(model=store.merchant)
        return store_dict

    def delete_store(self, store_id):
        logger.info('Store Delete: %s', store_id)
        store = StoreModel.objects.get(pk=store_id)
        StoreInfoModel.objects.filter(store=store).delete()
        store.status = StoreStatus.DELETE
        store.save()

    def get_all_store(self, openid=None, store_type=StoreType.SHOP, status=StoreStatus.NORMAL):
        if openid is None:
            return StoreModel.objects.filter(type=store_type, status=status).order_by('create_time')
        else:
            if store_type == 'all':
                return StoreModel.objects.filter(openid=openid, status=status).order_by('create_time')
            return StoreModel.objects.filter(openid=openid, type=store_type, status=status).order_by('create_time')

    def get_shopee_auth_url(self, user, partner_id, partner_key, store_id):
        if store_id is not None:
            auth_info = self.get_store_token_info(store_id=store_id).info_value
            partner_id = auth_info.get('partner_id')
            partner_key = auth_info.get('partner_key')
        if user is None or partner_id is None or partner_key is None:
            raise ValueError('Missing shopee auth params')

        current_time = int(time.time())
        host = settings.SHOPEE.get('host')
        redirect_url = settings.SHOPEE.get('redirect_url')
        auth_path = settings.SHOPEE.get('v2').get('auth_path')
        sign = shopee.get_sign(api_type=shopee.ApiType.PUBLIC, partner_id=partner_id,
                               partner_key=partner_key, path=auth_path, timest=current_time)
        secret_text = shopee.base64_encryption('%s,%s,%s' % (partner_id, partner_key, user))

        redirect_url = (redirect_url + "?secret=%s") % secret_text
        logger.info('redirect_url: %s', redirect_url)
        url = host + auth_path + "?partner_id=%s&timestamp=%s&sign=%s&redirect=%s" % (
            partner_id, current_time, sign, redirect_url)
        return url

    @transaction.atomic
    def shoppe_callback(self, dto: ShopeeCallbackDto):
        """
        Shopee 授权回调处理方法
        dto: 回调返回的数据
        """
        code = dto.code
        main_account_id = dto.main_account_id
        ciphertext = dto.secret

        ori_text = shopee.base64_decrypt(ciphertext)
        partner_list = ori_text.split(',')
        partner_id = partner_list[0]
        partner_key = partner_list[1]
        user_id = partner_list[2]
        user = None #TODO 抽象出User 模块，获取User
        openid = user.openid
        creator = user.name
        # Request Access Token
        token_ret = shopee.get_access_token(code, partner_id=partner_id,
                                            partner_key=partner_key, main_account_id=main_account_id)
        access_token = token_ret.get('access_token')
        refresh_token = token_ret.get('refresh_token')
        # Save Store Data
        merchant_store = None
        for merchant_id in token_ret.get('merchant_id_list'):
            if StoreModel.objects.filter(uid=merchant_id, type=StoreType.MERCHANT).exists():
                logger.warning('The merchant "%s" has been added, refresh data', merchant_id)
                merchant_store = StoreModel.objects.get(uid=merchant_id, type=StoreType.MERCHANT)
                merchant_store.openid = openid
                merchant_store.status = StoreStatus.NORMAL
                self.__update_openid(merchant_store)
                StoreInfoModel.objects.filter(store=merchant_store).delete()
            else:
                merchant_store = StoreModel(
                    name=merchant_id, uid=merchant_id, openid=openid,
                    platform=PlatformType.SHOPEE, type=StoreType.MERCHANT,
                    area='Default', creater=creator)
            merchant_store.save()
            info_value = {
                'partner_id': partner_id,
                'partner_key': partner_key,
                'access_token': access_token,
                'refresh_token': refresh_token
            }
            store_info = StoreInfoModel(store=merchant_store, info_key='auth', info_value=info_value,
                                        creater=merchant_store.creater, openid=merchant_store.openid)
            ret = shopee.request(url_key='merchant.get_merchant_info', merchant_id=merchant_id,
                                 method='GET', store_info=store_info)
            area = ret.get('merchant_region')
            area = area if area is not None else 'ZH'
            StoreModel.objects.filter(uid=merchant_id, type=StoreType.MERCHANT) \
                .update(name=ret.get('merchant_name'), area=area)
            store_info.save()
        for shop_id in token_ret.get('shop_id_list'):
            if StoreModel.objects.filter(uid=shop_id, type=StoreType.SHOP).exists():
                logger.warning('The shop "%s" has been added, refresh data', shop_id)
                store = StoreModel.objects.get(uid=shop_id, type=StoreType.SHOP)
                store.openid = openid
                store.status = StoreStatus.NORMAL
                self.__update_openid(store)
                StoreInfoModel.objects.filter(store=store).delete()
            else:
                store = StoreModel(name=shop_id, uid=shop_id, type=StoreType.SHOP, openid=openid,
                                   platform=PlatformType.SHOPEE, area='Default', creater=creator)
            if merchant_store:
                store.merchant = merchant_store
            store.save()
            info_value = {
                'partner_id': partner_id,
                'partner_key': partner_key,
                'access_token': access_token,
                'refresh_token': refresh_token
            }
            store_info = StoreInfoModel(store=store, info_key='auth', info_value=info_value,
                                        creater=store.creater, openid=store.openid)
            ret = shopee.request(url_key='shop.get_shop_info', shop_id=shop_id, method='GET', store_info=store_info)
            StoreModel.objects.filter(uid=shop_id, type=StoreType.SHOP).update(
                name=ret.get('shop_name'), area=ret.get('region'), status=StoreStatus.NORMAL
            )
            store_info.save()

    def get_store(self, store_id=None, shop_id=None, merchant_id=None):
        """
        通过ID获取店铺信息
        """
        if store_id is not None:
            store = StoreModel.objects.get(pk=store_id)
        elif shop_id is not None:
            store = StoreModel.objects.get(uid=shop_id, type=StoreType.SHOP)
        elif merchant_id is not None:
            store = StoreModel.objects.get(uid=merchant_id, type=StoreType.MERCHANT)
        else:
            raise ValueError('Missing required parameters')
        return store

    def get_store_token_info(self, store_id=None, shop_id=None, merchant_id=None):
        """
        获取指定商户，或店铺的AccessToken相关信息
        store_id、shop_id、merchant_id不能同时传
        """
        return self.get_store_info(store_id=store_id, shop_id=shop_id, merchant_id=merchant_id, key='auth')

    def get_store_info(self, store_id=None, shop_id=None, merchant_id=None, store=None, key=None):
        """
        获取店铺指定信息
        """
        if key is None:
            raise ValueError('Missing required parameters: KEY')
        if store is not None:
            _store = store
        else:
            _store = self.get_store(store_id=store_id, shop_id=shop_id, merchant_id=merchant_id)

        _store_info = StoreInfoModel.objects.get(store=_store, info_key=key)
        return _store_info

    def refresh_store_token(self, store_id, access_token, refresh_token):
        """
        刷新 Shopee token
        """
        store_info_auth = StoreInfoModel.objects.get(store=StoreModel.objects.get(pk=store_id), info_key='auth')
        store_info_auth.info_value['access_token'] = access_token
        store_info_auth.info_value['refresh_token'] = refresh_token
        store_info_auth.save()

    # 更新openid
    def __update_openid(self, store):
        OrderService.get_instance().update_openid(store)
        ProductService.get_instance().update_openid(store)
