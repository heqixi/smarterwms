
import datetime
import logging
import traceback

from order.common import OrderStatus
from order.services.order_service import OrderService
from store.common import StoreType, StoreStatus
from store.services.store_service import StoreService
from timer.executor import Task

logger = logging.getLogger()


class SyncOrderTask(Task):
    """
    每xx小时同步已处理、待处理本地订单状态和信息
    """
    id = 'SyncOrderTask'
    order_service = OrderService.get_instance()
    store_service = StoreService.get_instance()

    def job_id(self):
        return self.id

    def trigger_args(self):
        # 每xxx执行一次同步
        return {
            'trigger': 'interval',
            'hours': 1
        }

    def do_exec(self):
        try:
            logger.info('%s Start ...', self.id)
            stores = self.store_service.get_all_store(store_type=StoreType.SHOP, status=StoreStatus.NORMAL)

            for store in stores:
                orders = self.order_service.get_order_list(
                    store.uid, [OrderStatus.PROCESSED, OrderStatus.READY_TO_SHIP]
                )
                order_sn_list = []
                for order in orders:
                    order_sn_list.append(order.order_sn)
                self.order_service.sync_order_by_order_sn(store.uid, order_sn_list)
        except Exception as e:
            logging.info("Error: %s", e)


class SyncReadyToShipOrderTask(Task):
    """
    每xx分钟同步获取待发货订单
    """
    id = 'SyncReadyToShipOrderTask'
    order_service = OrderService.get_instance()
    store_service = StoreService.get_instance()

    def job_id(self):
        return self.id

    def trigger_args(self):
        return {
            'trigger': 'interval',
            'minutes': 30
            # 'seconds': 10
        }

    def do_exec(self):

        logger.info('%s Start ...', self.id)
        stores = self.store_service.get_all_store(store_type=StoreType.SHOP, status=StoreStatus.NORMAL)
        # now = datetime.datetime.now()
        # start_time = now + datetime.timedelta(hours=-now.hour, minutes=-now.minute, seconds=-now.second)
        # end_time = start_time + datetime.timedelta(days=1)
        # t_from = int(start_time.timestamp())
        # t_to = int(end_time.timestamp())
        # logger.info("start time: %s - end time: %s", t_from, t_to)
        for store in stores:
            try:
                self.order_service.sync_shipment_list(store.uid)
            except Exception as e:
                logger.warning('%s\n%s', e, traceback.format_exc())
