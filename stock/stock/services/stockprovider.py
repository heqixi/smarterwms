import threading

import logging

from goods.models import ListModel as Goods
from stock.models import StockListModel

from stock.gRpc.client.stock_service_client import StockServiceClient as StockClient
from stock.gRpc.client.shopee_product_service_stub import ProductServiceClient as ProductClient

from stock.gRpc.client.stock_service_client import StockUpdateModel as UpdateStock, StockCreateModel as CreateStock

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

    def add_shipping_stock(self, stock_qty: int, model_id: str):
        if stock_qty <= 0:
            raise Exception('Reserve stock qty must positive')
        global_product = ProductClient.get_instance().query(model_id)
        stock = StockClient.get_instance().Create(CreateStock(goods=global_product.id, stock_qty=stock_qty,
                                                         stock_status=StockListModel.Constants.STATUS_SHIP))
        # stock = self._generate_stock(stock_qty, StockListModel.Constants.STATUS_SHIP, model)
        print('add_shipping_stock ', stock)
        return stock.id

    def update_stock_qty(self, stock_id, stock_qty):
        # stock = StockListModel.objects.get(id=stock_id)
        # if not (stock.stock_status == StockListModel.Constants.STATUS_SHIP or stock.stock_status == StockListModel.Constants.STATUS_RESERVE):
        #     logger.warning('Not allow to update %s ', stock.stock_status)
        #     return False
        # stock.stock_qty = stock_qty
        # stock.save()
        StockClient.get_instance().Update(UpdateStock(id=1, stock_qty=21))
        return True

    def ship_reserve_stock(self, stock_id):
        stock = StockListModel.objects.get(id=stock_id)
        if stock.stock_status == StockListModel.Constants.STATUS_SHIP:
            return True
        if stock.stock_status != StockListModel.Constants.STATUS_RESERVE:
            logger.warning('You must reserver stock before ship it')
            return False
        if stock.stock_qty > 0:
            stock_on_hand = StockListModel.objects.filter(goods=stock.goods, stock_status=StockListModel.Constants.STATUS_ONHAND).first()
            if not stock_on_hand or stock_on_hand.stock_qty < stock.stock_qty:
                logger.warning('Not enough stock to ship!')
                return False
            stock_on_hand.stock_qty -= stock.stock_qty
            stock_on_hand.save()
        stock.stock_status = StockListModel.Constants.STATUS_SHIP
        stock.save()
        return True

    def back_stock(self, stock: StockListModel, to_reserve_qty=None, to_onhand_qty=0, is_delete=False):
        assert stock.stock_status == 12
        goods_of_stock = stock.goods
        if not goods_of_stock:
            logger.warning('Can not find goods of stock to be backward %s ', stock.id)
            raise Exception('Illegal stock status, missing goods')
        if to_onhand_qty > 0:
            stock_on_hand = StockListModel.objects.filter(goods_id=goods_of_stock.id,
                                                          stock_status=StockListModel.Constants.STATUS_ONHAND).first()
            if not stock_on_hand:
                logger.warning('backward stock %s, no on_hand stock instance !')
                stock_on_hand = StockListModel(
                    creater=stock.creater,
                    openid=stock.openid,
                    goods=goods_of_stock,
                    stock_qty=to_onhand_qty,
                    stock_status=StockListModel.Constants.STATUS_ONHAND  # 预留库存
                )
            else:
                stock_on_hand.stock_qty += stock.stock_qty
            stock_on_hand.save()
        if not is_delete:
            to_reserve_qty = to_reserve_qty if to_reserve_qty else stock.stock_qty
            stock.stock_qty = to_reserve_qty
            stock.stock_status = StockListModel.Constants.STATUS_RESERVE
            stock.save()
        else:
            stock.delete()
        return stock

    def reserve_goods_stock(self, stock_qty: int, goods: Goods):
        stock = StockListModel.objects.create(
            creater=goods.creater,
            openid=goods.openid,
            goods=goods,
            stock_qty=stock_qty,
            stock_status=StockListModel.Constants.STATUS_RESERVE
        )
        return stock

    def reserve_order_stock(self, stock_qty: int, publish_id: str, openid: str):
        raise Exception('Improper denpencies')
        # if stock_qty < 0:
        #     raise Exception('Reserve stock qty must positive')
        # model_publish = ShopeeStorePublish.objects.filter(publish_id=publish_id, openid=openid).first()
        # if not model_publish:
        #     logger.error('Can not find store publish %s ', publish_id)
        #     return -1
        # model = model_publish.product
        # stock = self._generate_stock(stock_qty, StockListModel.Constants.STATUS_RESERVE, model)
        # return stock.id

    def update_stock_goods(self, stock_id, goods_id, openid):
        stock = StockListModel.objects.filter(id=stock_id, openid=openid).first()
        stock_goods = stock.goods
        if not stock.goods.id == goods_id:
            stock_goods = Goods.objects.filter(id=goods_id, openid=openid).first()
            if not stock_goods:
                logger.warning('Can not change godos , goods of id not exist %s', goods_id)
                return False
            stock.goods = stock_goods
        stock.goods = stock_goods
        stock.save()
        return True

    # def _generate_stock(self, stock_qty: int, stock_status, model: GlobalProduct):
    #     goods_product_relation = getattr(model, GlobalProduct.RelativeFields.GOODS_RELATION).first()
    #     goods_of_model = None
    #     if goods_product_relation:
    #         goods_of_model = goods_product_relation.goods
    #     if not goods_of_model:
    #         logger.warning('Local model has not bind to goods %s %s', model.id, model.sku)
    #         goods_of_model = Goods.objects.filter(goods_code=model.sku, openid=model.openid).first()
    #         if not goods_of_model:
    #             goods_of_model = Goods(
    #                 goods_code=model.sku,
    #                 goods_image=model.image,
    #                 goods_name=model.name,
    #                 openid=model.openid,
    #                 creater=model.creater
    #             )
    #             goods_of_model.save()
    #     if not goods_product_relation:
    #         goods_product_relation = GlobalProductGoodsRelation(
    #             product=model,
    #             goods=goods_of_model,
    #             confirm=False,
    #             openid=model.openid,
    #             creater=model.creater
    #         )
    #         goods_product_relation.save()
    #
    #     stock = StockListModel.objects.create(
    #         creater=model.creater,
    #         openid=model.openid,
    #         goods=goods_of_model,
    #         stock_qty=stock_qty,
    #         stock_status=stock_status
    #     )
    #     stock.save()
    #     return stock

    def _update_stock_remote(self, ):
        pass







