import datetime
import logging
import traceback

from store.common import StoreType, StoreStatus
from store.models import StoreModel, StoreInfoModel
from timer.executor import Task
from utils import shopee

logger = logging.getLogger()


class RefreshTokenTask(Task):
    """
    定时刷新Token，避免超时
    """
    id = 'RefreshTokenTask'

    def job_id(self):
        return self.id

    def trigger_args(self):
        return {
            'trigger': 'interval',
            'hours': 1
            # 'minutes': 30
            # 'seconds': 10
        }

    def do_exec(self):
        stores = StoreModel.objects.filter(status=StoreStatus.NORMAL)
        for store in stores:
            try:
                store_info = StoreInfoModel.objects.get(store=store, info_key='auth')
                duration = int((datetime.datetime.now() - store_info.update_time).seconds / 3600)
                logger.info('Refresh Token, store: %s, duration: %s', store.uid, duration)
                if duration >= 2:
                    if store.type == StoreType.SHOP:
                        shopee.refresh_shop_token(shop_id=store.uid)
                    if store.type == StoreType.MERCHANT:
                        shopee.refresh_shop_token(merchant_id=store.uid)
            except Exception as e:
                logger.error('%s\n%s', e, traceback.format_exc())
