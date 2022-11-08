import threading

import logging

from stock.models import StockRecord

from stock.gRpc.client.stock_service_client import StockServiceClient as StockClient, RetrieveRequest, QueryRequest

from stock.gRpc.client.stock_service_client import UpdateRequest as StockUpdateReq,\
    CreateRequest as StockCreateReq, BackStockReq

logger = logging.getLogger()

class StockService(object):
    __create_key = object()
    lock = threading.RLock()
    service = None

    def __init__(self, create_key):
        assert (create_key == StockService.__create_key),\
            "Stock Service is single instance, please use GlobalProductService.get_instance()"

    @classmethod
    def get_instance(cls):
        if cls.service is None:
            cls.lock.acquire()
            if cls.service is None:
                cls.service = cls(StockService.__create_key)
            cls.lock.release()
            return cls.service
        return cls.service

    # def create_purchased_stock(self, stock_qty: int, goods_id: int):
    #     return self.create_stock(stock_qty, goods_id, StockRecord.PURCHASED_STOCK)

    def create_damage_stock(self, stock_qty: int, goods_id: int):
        return self.create_stock(stock_qty, goods_id, StockRecord.DAMAGE_STOCK)

    def create_onhand_stock(self, stock_qty: int, goods_id: int):
        return self.create_stock(stock_qty, goods_id, StockRecord.ONHAND_STOCK)

    def update_stock(self, stock: StockRecord, stock_qty, stock_status):
        if stock_qty < 0:
            raise Exception('update stock illegal stock qty %s' % stock_qty)
        res = StockClient.get_instance().Update(
            StockUpdateReq(id=stock.stock_id, stock_qty=stock_qty, stock_status=stock_status))
        if res.success:
            stock.stock_qty = res.stock.stock_qty
            stock.stock_id = res.stock.id
            stock.stock_status = stock_status
            stock.save()
            return stock
        else:
            raise Exception('update stock qty fail, %s %s', res.code, res.msg)

    def update_stock_goods(self, stock: StockRecord, goods_id):
        """
        @stock: StockRecord
        @goods_id: 需要替换的goods_id
        """
        res = StockClient.get_instance().Update(StockUpdateReq(id=stock.stock_id, goods=goods_id))
        if res.success:
            stock.goods_id = goods_id
            stock.save()
            return stock
        raise Exception('Update stock goods fail, code:%s, msg: %s', res.code, res.msg)

    def delete_stock(self, stock: StockRecord):
        """
        @stock: StockRecord
        """
        res = StockClient.get_instance().Destroy(stock.stock_id)
        if res.success:
            stock.delete()
            return True
        else:
            logger.error('Delete stock fail, code:%s, msg: %s', res.code, res.msg)
            return False

    def retrieve(self, stock_id):
        res = StockClient.get_instance().Retrieve(stock_id)
        if res.success:
            return res.stock
        else:
            logger.error('retrieve stock fail, code: %s, msg: %s', res.code, res.msg)
            raise Exception(res.msg)
            # return None

    def get_onhand_stock(self, goods_id_list):
        query_req = QueryRequest(goods_id=goods_id_list, stock_status=[StockRecord.ONHAND_STOCK])
        return StockClient.get_instance().Query(query_req)

    def create_stock(self, stock_qty, goods_id, stock_status):
        """
        追加已经出货的库存
        @stock_qty: 库存数量
        @goods_id: 货物id。 优先使用goods_id查询货物是否存在
        @model_id: 订单中商品的model_id, 如果没有提供goods_id, 这通过此字段先查询关联的产品，在通过产品查询货物
        @return StockRecord
        """
        res = StockClient.get_instance().Create(
            StockCreateReq(goods=goods_id, stock_qty=stock_qty, stock_status=stock_status))
        if res.success:
            stock_record = StockRecord.objects.create(
                goods_id=res.stock.goods,
                goods_code=res.stock.goods_code,
                goods_image=res.stock.goods_image,
                stock_id=res.stock.id,
                stock_qty=stock_qty,
                stock_status=stock_status
            )
            stock_record.save()
            return stock_record
        else:
            logger.error('Create stock fail, %s, %s', res.code, res.msg)
            return None
