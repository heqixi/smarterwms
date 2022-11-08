import base64
import hashlib
import hmac
import json
import logging
import os
import random
import time
import asyncio
import traceback

import httpx

import requests
from django.conf import settings
from httpx import ConnectTimeout

logger = logging.getLogger()

os.environ['NO_PROXY'] = settings.SHOPEE.get('redirect_url') \
    .replace('https://', '') \
    .replace("http://", '') \
    .replace("/store/callback", '')


async def async_request(url_key=None, shop_id=None, merchant_id=None, method=None, params=None, store_info=None,
                        *args, **kwargs):
    if merchant_id is not None:
        api_type = ApiType.MERCHANT
    else:
        api_type = ApiType.SHOP
    url = get_url(api_type=api_type, url_key=url_key, shop_id=shop_id, merchant_id=merchant_id, store_info=store_info)
    logger.info('Shopee Request Url: %s', url)
    if url is None:
        raise ValueError('URL can not be null')
    method = method.upper()
    try:
        user_agent = random.choice(user_agent_list)
        headers = {"User-Agent": user_agent}
        if method == 'GET':
            async with httpx.AsyncClient() as client:
                response = await client.get(url=url, params=params, headers=headers)
        elif method == 'POST':
            headers["Content-Type"] = "application/json"
            async with httpx.AsyncClient() as client:
                response = await client.post(url=url, json=params, headers=headers)
        elif method == 'PUT':
            async with httpx.AsyncClient() as client:
                response = await client.put(url=url, params=params, headers=headers)
        elif method == 'DELETE':
            async with httpx.AsyncClient() as client:
                response = await client.delete(url=url, params=params, headers=headers)
        else:
            raise ValueError('There is no way for the request')

        if response.status_code == 200:
            try:
                ret = json.loads(response.content)
                if ret.get('error') == 'error_auth':
                    # 刷新access_token
                    refresh_shop_token(shop_id=shop_id, merchant_id=merchant_id)
                    return await async_request(url_key=url_key, shop_id=shop_id, merchant_id=merchant_id, method=method,
                                               params=params)
                elif len(ret.get('error')) > 0:
                    logger.error('Shopee Request Error: %s', response.content)
                    raise ValueError('Request Error: %s, %s' % (ret.get('error'), ret.get('message')))
                else:
                    return ret
            except UnicodeDecodeError as e:
                logger.warning('The data format obtained is not JSON')
                return response.content
        else:
            logger.error('Shopee Request Error: %s', response.content)
            ret = json.loads(response.content)
            if ret.get('error') == 'error_auth':
                # 刷新access_token
                refresh_shop_token(shop_id=shop_id, merchant_id=merchant_id)
                return await async_request(url_key=url_key, shop_id=shop_id, merchant_id=merchant_id, method=method,
                                           params=params)
            else:
                raise ValueError('Request Error: Code:%s, Msg: %s' % (response.status_code, response.text))
    except ConnectTimeout as e:
        if not kwargs.get('retry'):
            logger.warning('Shpoee request retry connect')
            return await async_request(
                url_key=url_key, shop_id=shop_id, merchant_id=merchant_id, method=method, params=params, retry=1)
        else:
            logger.error('Shpoee retry connect timeout again error: %s', e, traceback.format_exc())
    except Exception as e:
        logger.error('Shopee Request Error: %s', e)
        raise e


def request(url_key=None, shop_id=None, merchant_id=None, method=None, params=None, store_info=None):
    return asyncio.run(async_request(
        url_key=url_key, shop_id=shop_id, merchant_id=merchant_id, method=method, params=params, store_info=store_info))


def get_url(api_type=None, url_key=None, shop_id=None, merchant_id=None, store_info=None):
    from store.services.store_service import StoreService
    host = settings.SHOPEE.get('host')
    if len(host) == 0:
        raise EnvironmentError('Please configure the "host" of Shopee in the settings file')
    path = get_path(url_key)

    if store_info is not None:
        _store_info = store_info
    elif shop_id is not None:
        _store_info = StoreService.get_instance().get_store_info(shop_id=shop_id, key='auth')
    elif merchant_id is not None:
        _store_info = StoreService.get_instance().get_store_info(merchant_id=merchant_id, key='auth')
    else:
        raise ValueError('Missing parameter')
    partner_id = _store_info.info_value.get('partner_id')
    partner_key = _store_info.info_value.get('partner_key')

    timest = int(time.time())

    sign = get_sign(api_type=api_type, partner_id=partner_id, partner_key=partner_key,
                    path=path, timest=timest, shop_id=shop_id, merchant_id=merchant_id,
                    access_token=_store_info.info_value.get('access_token')
                    )
    if api_type == ApiType.PUBLIC:
        url = host + path + "?partner_id=%s&timestamp=%s&sign=%s" % (partner_id, timest, sign)
    elif api_type == ApiType.SHOP:
        access_token = _store_info.info_value.get('access_token')
        url = host + path + "?partner_id=%s&shop_id=%s&timestamp=%s&access_token=%s&sign=%s" % (
            partner_id, shop_id, timest, access_token, sign
        )
    else:
        access_token = _store_info.info_value.get('access_token')
        url = host + path + "?partner_id=%s&merchant_id=%s&timestamp=%s&access_token=%s&sign=%s" % (
            partner_id, merchant_id, timest, access_token, sign
        )
    return url


def refresh_shop_token(shop_id=None, merchant_id=None):
    from store.services.store_service import StoreService
    store_info = StoreService.get_instance().get_store_token_info(shop_id=shop_id, merchant_id=merchant_id)
    partner_id = store_info.info_value.get('partner_id')
    refresh_token = store_info.info_value.get('refresh_token')
    params = {'partner_id': int(partner_id), 'refresh_token': refresh_token}
    if shop_id is not None:
        params['shop_id'] = int(shop_id)
    elif merchant_id is not None:
        params['merchant_id'] = int(merchant_id)
    else:
        raise ValueError('Missing shop_id or merchant_id')
    url = get_url(api_type=ApiType.PUBLIC, url_key='refresh_access_token', shop_id=shop_id,
                  merchant_id=merchant_id, store_info=store_info)
    logger.info('Refresh Token Url: %s', url)
    headers = {'Content-Type': 'application/json'}
    resp = requests.post(url, json=params, headers=headers)
    if resp.status_code == 200:
        ret = json.loads(resp.content)
        # Not Error
        if not ret.get('error').strip():
            StoreService.get_instance().refresh_store_token(
                store_id=store_info.store_id,
                access_token=ret.get('access_token'),
                refresh_token=ret.get('refresh_token')
            )
            logger.info('Refresh Token Success', ret)
        else:
            logger.error("Get Token Msg: %s", resp.content)
            raise ValueError(ret.get('message'))
    else:
        logger.error("Response Error: %s", resp.content)
        raise ValueError('Unknown Error: %s, Msg: %s' % resp.status_code)


def get_access_token(code, partner_id, partner_key, main_account_id=None, shop_id=None):
    timest = int(time.time())
    body = None
    if main_account_id is not None:
        body = {"code": code, 'partner_id': int(partner_id), 'partner_key': partner_key,
                'main_account_id': int(main_account_id)}
    if shop_id is not None:
        body = {"code": code, 'partner_id': int(partner_id), 'partner_key': partner_key,
                'shop_id': int(shop_id)}
    if body is None:
        raise ValueError('Get Access Token Request Params Error')

    host = settings.SHOPEE.get('host')
    path = get_path('get_access_token')
    sign = get_sign(api_type=ApiType.PUBLIC, partner_id=partner_id, partner_key=partner_key, path=path, timest=timest)
    url = host + path + "?partner_id=%s&timestamp=%s&sign=%s" % (partner_id, timest, sign)
    headers = {"Content-Type": "application/json"}
    resp = requests.post(url, json=body, headers=headers)
    if resp.status_code == 200:
        ret = json.loads(resp.content)
        # Not Error
        if not ret.get('error').strip():
            return ret
        else:
            logger.error("Get Token Msg: %s", resp.content)
            raise ValueError(ret.get('message'))
    else:
        raise ValueError('Unknown Error: %s, Msg: %s' % resp.status_code, resp.text)


def public_request(partner_id, partner_key, url_key, params, files):
    host = settings.SHOPEE.get('host')
    path = get_path(url_key)
    timest = int(time.time())
    sign = get_sign(api_type=ApiType.PUBLIC, partner_id=partner_id, partner_key=partner_key, path=path, timest=timest)
    url = host + path + "?partner_id=%s&timestamp=%s&sign=%s" % (partner_id, timest, sign)
    headers = {}
    resp = requests.post(url, data=params, files=files, headers=headers, allow_redirects=False)
    if resp.status_code == 200:
        ret = json.loads(resp.content)
        # Not Error
        if not ret.get('error').strip():
            return ret
        else:
            logger.error("Get Token Msg: %s", resp.content)
            raise ValueError(ret.get('message'))
    else:
        raise ValueError('Unknown Error: %s, Msg: %s' % resp.status_code, resp.text)


# 1:Public APIs: partner_id, api path, timestamp
# 2:Shop APIs: partner_id, api path, timestamp, access_token, shop_id
# 3:Merchant APIs: partner_id, api path, timestamp, access_token, merchant_id
def get_sign(api_type=None, partner_id=None,
             partner_key=None, path=None, timest=None, access_token=None, shop_id=None, merchant_id=None):
    encode = settings.SHOPEE.get('encode')
    if partner_id is None or path is None or timest is None:
        raise ValueError('Sign Base Params Error')
    if api_type == ApiType.PUBLIC:
        base_string = "%s%s%s" % (partner_id, path, timest)
    elif api_type == ApiType.SHOP:
        base_string = "%s%s%s%s%s" % (partner_id, path, timest, access_token, shop_id)
    elif api_type == ApiType.MERCHANT:
        base_string = "%s%s%s%s%s" % (partner_id, path, timest, access_token, merchant_id)
    else:
        raise ValueError('Unknown Shopee api_type: %s' % api_type)
    sign = hmac.new(partner_key.encode(encode), base_string.encode(encode), hashlib.sha256).hexdigest()
    return sign


def base64_encryption(ori_text):
    encode = settings.SHOPEE.get('encode')
    return base64.b64encode(ori_text.encode(encode)).decode(encode)


def base64_decrypt(ciphertext):
    encode = settings.SHOPEE.get('encode')
    return base64.b64decode(ciphertext.encode(encode)).decode(encode)


def get_param_dict(url):
    param_list = url.strip().split('?')[1].split('&')
    param_dict = {}
    for item in param_list:
        param_dict[item.split('=')[0]] = item.split('=')[1]
    return param_dict


# 通过 Url Key 获取Shopee请求路径
def get_path(url_key):
    if url_key is None:
        raise ValueError('Url Key can not be none')
    path = settings.SHOPEE.get('v2').get(url_key)
    if path is None:
        logger.error('Can’t find the corresponding path: %s', url_key)
        raise ValueError('There is no corresponding path %s, please check the URL configuration of Shopee')
    return path


# user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53'


# user_agent_list = [
#     "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36",
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
#     "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
#     "Mozilla/5.0 (Macintosh; U; PPC Mac OS X 10.5; en-US; rv:1.9.2.15) Gecko/20110303 Firefox/3.6.15",
#     ]

user_agent_list = [  # User-Agent池
    # Cent Browser 4.3.9.248，Chromium 86.0.4240.198，2021.01
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
    # Edge
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36 Edg/93.0.961.38',
    # 2021.09
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36 Edg/93.0.961.44',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36 Edg/93.0.961.47',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36 Edg/93.0.961.52',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36 Edg/94.0.992.31',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36 Edg/94.0.992.37',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36 Edg/94.0.992.38',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36 Edg/94.0.992.47',
    # 2021.10
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36 Edg/94.0.992.50',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36 Edg/95.0.1020.30',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36 Edg/95.0.1020.40',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36 Edg/95.0.1020.44',
    # 2021.11
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36 Edg/95.0.1020.53',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36 Edg/96.0.1054.29',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36 Edg/96.0.1054.34',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36 Edg/96.0.1054.41',
    # 2021.12
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36 Edg/96.0.1054.43',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36 Edg/96.0.1054.53',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.62',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36 Edg/97.0.1072.55',
    # 2022.01
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36 Edg/97.0.1072.62',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36 Edg/97.0.1072.69',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36 Edg/97.0.1072.76',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36 Edg/98.0.1108.43',
    # 2022.02
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36 Edg/98.0.1108.50',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 Edg/98.0.1108.55',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 Edg/98.0.1108.56',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 Edg/98.0.1108.62',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36 Edg/99.0.1150.30',
    # 2022.03
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36 Edg/99.0.1150.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36 Edg/99.0.1150.39',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36 Edg/99.0.1150.46',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36 Edg/99.0.1150.52',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36 Edg/99.0.1150.55',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36 Edg/100.0.1185.29',
    # 2022.04
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36 Edg/100.0.1185.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36 Edg/100.0.1185.39',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36 Edg/100.0.1185.44',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36 Edg/100.0.1185.50',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36 Edg/101.0.1210.32',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36 Edg/101.0.1210.39',
    # 2022.05
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.47',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.30',
    # 2022.06
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.33',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.39',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.124 Safari/537.36 Edg/102.0.1245.41',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.124 Safari/537.36 Edg/102.0.1245.44',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.53 Safari/537.36 Edg/103.0.1264.37',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.66 Safari/537.36 Edg/103.0.1264.44',
    # 2022.07
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36 Edg/103.0.1264.49',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36 Edg/103.0.1264.62',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 Edg/103.0.1264.71',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 Edg/103.0.1264.77',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.81 Safari/537.36 Edg/104.0.1293.47',
    # 2022.08
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.81 Safari/537.36 Edg/104.0.1293.54',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36 Edg/104.0.1293.63',

    # Chrome
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36',
    # 2021.10
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
    # 2021.11
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36',
    # 2021.12
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
    # 2022.01
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.81 Safari/537.36',
    # 2022.02
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
    # 2022.03
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36',
    # 2022.04
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36',
    # 2022.05
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.115 Safari/537.36',
    # 2022.06
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.53 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.66 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36',
    # 2022.07
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.81 Safari/537.36',
    # 2022.08
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36',

    # Chrome Beta
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.41 Safari/537.36',
    # 2021.09
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.17 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.32 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.40 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.49 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.18 Safari/537.36',
    # 2021.10
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.27 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.35 Safari/537.36',
    # 2021.11
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',

    # Firefox
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0',  # 2021.09
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0',  # 2021.10
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0',  # 2021.11
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0',  # 2021.12
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0',  # 2022.01
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0',  # 2022.02
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0',  # 2022.03
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0',  # 2022.04
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0',  # 2022.05
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/101.0',  # 2022.06
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0',  # 2022.06
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0',  # 2022.07
]

# Shopee API 请求类型
class ApiType:
    PUBLIC = 1
    SHOP = 2
    MERCHANT = 3
