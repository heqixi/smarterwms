from django.db import models
from django.db import transaction

import logging

from base.models import BaseModel
from goods.models import ListModel as Goods

logger = logging.getLogger()


class StockListModel(BaseModel):
    class RelativeFields(object):
        STOCK_ORDER = "stock_order"

        STOCK_BIN = "stock_bin"

        STOCK_ASN = "stock_asn"

    class Constants(object):
        STATUS_DAMAGE = 0

        STATUS_PURCHASED = 1

        STATUS_SORTED = 2

        STATUS_ONHAND = 3

        STATUS_RESERVE = 11

        STATUS_SHIP = 12

        STATUS_BACK_ORDER = 13

    STOCK_STATUS = (
        (0, 'Damage Stock'),
        (1, 'Purchased Stock'),  # 已经采购的库存
        (2, 'Sorted Stock'),  # 已分拣库存
        (3, 'In Stock'),  # 现有库存
        (11, 'Reserve Stock'),  # 被锁定的库存
        (12, 'Ship Stock'),  # 已经发货的库存
        (13, 'Back Order Stock')
    )
    goods = models.ForeignKey(Goods, default=None, null=True, on_delete=models.CASCADE,
                              related_name=Goods.RelativeFields.GOODS_STOCK)
    stock_status = models.IntegerField(default=0, choices=STOCK_STATUS)
    stock_qty = models.BigIntegerField(default=0, verbose_name="goods entry Qty")

    class Meta:
        db_table = 'stocklist'
        verbose_name = 'data id'
        verbose_name_plural = "data id"
        ordering = ['-id']

    def __str__(self):
        return str(self.pk)

    @transaction.atomic
    def ship_reserve_stock(self):
        if self.stock_status == 12:
            return True
        if self.stock_status != 11:
            logger.warning('You must reserver stock before ship it')
            return False
        stock_on_hand = StockListModel.objects.filter(goods=self.goods, stock_status=3).first()
        if not stock_on_hand or stock_on_hand.stock_qty < self.stock_qty:
            logger.warning('Not enough stock to ship!')
            return False
        stock_on_hand.stock_qty -= self.stock_qty
        self.stock_status = 12
        self.save()
        stock_on_hand.save()
        return True

    @transaction.atomic
    def freed_stock(self):
        if self.stock_status == 12:
            # 已锁定，释放现有库存
            stock_on_hand = StockListModel.objects.filter(goods=self.goods, stock_status=3).first()
            if not stock_on_hand:
                stock_on_hand = StockListModel(goods=self.goods, stock_qty=0, stock_status=3)
            stock_on_hand.stock_qty += self.stock_qty
            stock_on_hand.save()
            self.stock_status = 11
            self.save()

    # def change_stock_staus(self, to=None, quantity=0, delete=False):
    #     if self.stock_status != 3:
    #         raise Exception("Only stock on hand is consumabnle!")
    #     if quantity > self.stock_qty:
    #         raise Exception("")

    @transaction.atomic
    def update_qty(self, qty):
        if qty <= 0:
            raise Exception("Stock qty must positive!")
        logger.info(" update qty of stock %s , goods_code: %s" % (self.id, qty))
        self.stock_qty = qty
        self.save()

    @transaction.atomic
    def update_goods(self, goods_code):
        goods = Goods.objects.filter(goods_code=goods_code).first()
        if not goods:
            logger.error("Try to update goods not exit, code: %s" % goods_code)
            raise Exception("Goods of code %s not exist" % goods_code)
        logger.error(" update goods of stock %s , goods_code: %s" % (self.id, goods_code))
        self.goods = goods
        self.save()


class StockBinModel(BaseModel):
    bin_name = models.CharField(max_length=255, verbose_name="Bin Name")
    stock = models.ForeignKey(StockListModel, default=None, null=True, on_delete=models.SET_NULL,
                              related_name=StockListModel.RelativeFields.STOCK_BIN,
                              limit_choices_to={'stock_status__exact': 1})
    bin_code = models.CharField(max_length=255, verbose_name="Goods Code")
    goods_qty = models.BigIntegerField(default=0, verbose_name="Binstock Qty")
    bin_size = models.CharField(max_length=255, verbose_name="Bin size")
    bin_property = models.CharField(
        max_length=255, verbose_name="Bin Property")
    t_code = models.CharField(max_length=255, verbose_name="Transaction Code")

    class Meta:
        db_table = 'stockbin'
        verbose_name = 'data id'
        verbose_name_plural = "data id"
        ordering = ['-id']

    def __str__(self):
        return str(self.pk)
