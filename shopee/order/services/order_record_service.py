import datetime
import logging
import threading
import uuid

from django.db import connection

from order.models import ShopeeOrderRecordModel, ShopeeOrderModel
from utils import spg

logger = logging.getLogger()


class OrderRecordService(object):
    """
    订单服务，对外提供订单相关操作功能
    """
    __create_key = object()
    lock = threading.RLock()
    service = None

    def __init__(self, create_key):
        assert (create_key == OrderRecordService.__create_key), \
            "StoreService objects must be created using StoreService.get_instance"

    @classmethod
    def get_instance(cls):
        if cls.service is None:
            cls.lock.acquire()
            if cls.service is None:
                cls.service = cls(OrderRecordService.__create_key)
            cls.lock.release()
            return cls.service
        return cls.service

    def get_record_batch_info(self, openid, record_type=None):
        if not openid:
            logger.error('openid can not be none')
            raise ValueError('openid can not be none')
        kwargs = {'openid': openid}
        if record_type:
            kwargs['type'] = record_type

        sql = f"""
        SELECT batch_number, type, create_time 
        from {ShopeeOrderRecordModel._meta.db_table} 
        GROUP BY batch_number, type, create_time ORDER BY create_time DESC
        """
        data = spg.exec_sql(sql)
        logger.info('batch_info_list: %s', data)
        return data

    def record_order(self, order_sn_list, record_type):
        # {'order_sn': order.get('order_sn')}
        if order_sn_list and len(order_sn_list) > 0:
            record_list = []
            batch_num = ''.join(str(uuid.uuid4()).split('-'))
            create_time = datetime.datetime.now()
            for order_info in order_sn_list:
                order_sn = order_info.get('order_sn')
                order = ShopeeOrderModel.objects.get(order_sn=order_sn)
                record = ShopeeOrderRecordModel(
                    shopee_order=order, openid=order.openid, create_time=create_time,
                    creater=order.creater, type=record_type, batch_number=batch_num)
                record_list.append(record)
            ShopeeOrderRecordModel.objects.bulk_create(record_list)
