import threading

import logging

from stock.models import StockRecord

from stock.gRpc.client.stock_service_client import StockServiceClient as StockClient, Stock

from stock.gRpc.client.stock_service_client import UpdateRequest as StockUpdateReq, BackStockReq

logger = logging.getLogger()


class StockBean(object):
    """
    @stock_id: Unique id that identify a remote stock
    @stock_qty: The Quantity of the stock
    @goods_id: Unique id that identify the stock's goods object in data base
    @goods_sku: Unique readable string that represent the goods of stock.
    @goods_image: Image of the goods
    """
    stock_id = None

    stock_qty = None

    goods_id = None

    goods_code = None

    goods_image = None

    def __init__(self, stock_qty=None, goods_id=None, stock_id=None, goods_code=None, goods_image=None):
        self.stock_id = stock_id
        self.stock_qty = stock_qty
        self.goods_id = goods_id
        self.goods_code = goods_code
        self.goods_image = goods_image

    def set_stock_qty(self, qty):
        self.stock_qty = qty
        return self

    def set_goods_id(self, goods_id):
        self.goods_id = goods_id
        return self


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

    def add_shipping_stock(self, stock_bean: StockBean):
        """
        Create a stock that had been shipped. Usually, a stock must be created before the shipment of an order,
        but at abnormal situation, we may want to create a stock when an order had shipped but no stock was attached
        to that order

        @stock_bean: Object that can represent a remote stock or that can be used to create a stock
        @return StockRecord.
        """
        if not stock_bean.stock_qty:
            raise Exception('add shipping stock missing stock qty')
        goods_id = stock_bean.goods_id
        if not goods_id:
            if not (stock_bean.goods_code or stock_bean.goods_image):
                raise Exception('Add shipping stock missing goods_code or goods_image')

        res = StockClient.get_instance().Create(Stock(
            id=stock_bean.stock_id,
            stock_qty=stock_bean.stock_qty,
            stock_status=12,
            goods=stock_bean.goods_id,
            goods_code=stock_bean.goods_code,
            goods_image=stock_bean.goods_image
        ))
        if res.success:
            stock_record = StockRecord.objects.create(
                goods_id=res.stock.goods,
                goods_code=res.stock.goods_code,
                goods_image=res.stock.goods_image,
                stock_id=res.stock.id,
                stock_qty=res.stock.stock_qty,
                stock_status=res.stock.stock_status
            )
            stock_record.save()
            return stock_record
        else:
            logger.error('Create stock fail, %s, %s', res.code, res.msg)
            raise Exception('Create stock fail, code:%s, msg:%s' % (res.code, res.msg))

    def update_stock_qty(self, stock: StockRecord, stock_qty):
        res = StockClient.get_instance().Update(StockUpdateReq(id=stock.stock_id, stock_qty=stock_qty))
        if res.success:
            stock.stock_qty = stock_qty
            stock.save()
            return stock
        else:
            raise Exception('update stock qty fail, %s %s', res.code, res.msg)

    def ship_reserve_stock(self, stock: StockRecord):
        """
        @stock: StockRecord
        """
        res = StockClient.get_instance().Ship(stock.stock_id)
        if res.success:
            stock.stock_status = StockRecord.SHIP_STOCK
            stock.save()
            return stock
        else:
            raise Exception('ship reserve stock fail, code:%s, msg: %s', res.code, res.msg)

    def back_stock(self, stock: StockRecord, to_reserve_qty=None, to_onhand_qty=None, is_delete=False):
        """
         Rollback a stock on remote server
         @stock: StockRecord
         @to_reserve_qty: Stock quantity that rollback to reserve state, 0 <= to_reserve_qty <= stock.stock_qty
         @to_onhand_qty: Stock quantity that append to onhand stock, 0 <= to_onhand_qty <= stock.stock_qty
         Note:
             Both parameters of to_reserve_qty and to_onhand_qty have default value "None",
         means that to_reserve_qty or to_onhand_qty equals stock.stock_qty.
             Warning: to_reserve_qty and to_onhand_qty are independent, that means the following equation may NOT hold
             to_reserve_qty + to_onhand_qty == stock.stock_qty
        """
        if not stock.stock_status == StockRecord.SHIP_STOCK:
            raise Exception('Only ship stock can be rolled back')
        to_onhand_qty = stock.stock_qty if to_onhand_qty is None else to_onhand_qty
        req = BackStockReq(id=stock.stock_id, to_reserve_qty=to_reserve_qty, to_onhand_qty=to_onhand_qty, is_delete=is_delete)
        if not req.is_valid():
            raise Exception('Back stock illegal argument!')
        res = StockClient.get_instance().Back(req)
        if res.success:
            if not is_delete:
                stock.stock_qty = to_reserve_qty if to_reserve_qty is not None else stock.stock_qty
                stock.stock_status = StockRecord.RESERVE_STOCK
                stock.save()
            else:
                stock.delete()
            return stock
        raise Exception('Back stock fail code: %s, msg: %s' % (res.code, res.msg))

    def reserve_stock(self, stock_bean: StockBean):
        """
        追加已经出货的库存
        @stock_qty: 库存数量
        @goods_id: 货物id。 优先使用goods_id查询货物是否存在
        @model_id: 订单中商品的model_id, 如果没有提供goods_id, 这通过此字段先查询关联的产品，在通过产品查询货物
        @return StockRecord
        """

        goods_id = stock_bean.goods_id
        if not goods_id:
            if not (stock_bean.goods_code or stock_bean.goods_image):
                raise Exception('Add shipping stock missing goods_code or goods_image')
        res = StockClient.get_instance().Create(Stock(
            id=stock_bean.stock_id,
            stock_qty=stock_bean.stock_qty,
            stock_status=11,
            goods=stock_bean.goods_id,
            goods_code=stock_bean.goods_code,
            goods_image=stock_bean.goods_image
        ))
        if res.success:
            stock_record = StockRecord.objects.create(
                goods_id=res.stock.goods,
                goods_code=res.stock.goods_code,
                goods_image=res.stock.goods_image,
                stock_id=res.stock.id,
                stock_qty=res.stock.stock_qty,
                stock_status=StockRecord.RESERVE_STOCK
            )
            return stock_record
        else:
            raise Exception('ship reserve stock fail, code:%s, msg: %s', res.code, res.msg)

    def update_stock_goods(self, stock: StockRecord, goods_id):
        """
        @stock: StockRecord
        @goods_id: 需要替换的goods_id
        """
        res = StockClient.get_instance().Update(StockUpdateReq(id=stock.stock_id, goods=goods_id))
        if res.success:
            stock.goods_id = goods_id
            stock.goods_code = res.stock.goods_code
            stock.goods_image = res.stock.goods_image
            stock.save()
            return stock
        raise Exception('Update stock goods fail, code:%s, msg: %s', res.code, res.msg)

    def force_ship_stock(self, stock_record: StockRecord):
        """
        Force ship stock without consume stock on hand, just mark stock_status as SHIP_STOCK
        Case 1: if stock had shipped, may have consumed stock_on_hand, need to roll back stock on hand
        Case 2: if stock is reserved, just update stock_status as Ship
        """
        if stock_record.stock_status == StockRecord.SHIP_STOCK:
            # req = BackStockReq(id=stock_record.stock_id, to_reserve_qty=0, to_onhand_qty=stock_record.stock_qty)
            # if not req.is_valid():
            #     raise Exception('Force ship stock fail, back stock illegal argument!')
            # res = StockClient.get_instance().Back(req)
            # if not res.success:
            #     raise Exception('Force ship stock fail, bask stock fail, code: %s, msg: %s', res.code, res.msg)
            #
            stock_record = self.back_stock(stock_record, to_reserve_qty=0, to_onhand_qty=stock_record.stock_qty)
        res = StockClient.get_instance().Update(StockUpdateReq(id=stock_record.stock_id, stock_status=StockRecord.SHIP_STOCK))
        if res.success:
            stock_record.stock_status = StockRecord.SHIP_STOCK
            stock_record.save()
            return stock_record
        else:
            raise Exception('Force ship stock fail, code: %s, msg: %s', res.code, res.msg)

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

    def get_onhand(self, goods_id):
        """
        @goods_id: Id of stock's goods
        @return Stream of stock which goods's id is equal to goods_id
        """
        res = StockClient.get_instance().Query(goods_id=[goods_id], stock_status=[3])
        return res
