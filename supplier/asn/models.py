from django.db import models

from base.models import BaseModel
from stock.models import StockRecord
from supplier.models import ListModel as Supplier
from supplier.models import PurchasePlan

from stock.services.stockprovider import StockService

import datetime

import logging

logger = logging.getLogger()


class AsnListModel(BaseModel):
    class Relative_Fields(object):
        ANS_DETAILS = 'asn_details'

        ASN_ORDER = 'asn_order'

    asn_code = models.CharField(max_length=255, verbose_name="ASN Code")
    asn_status = models.BigIntegerField(
        default=0, verbose_name="ASN Status")  # 0 未购买 1 已购买未到 2 已到未分拣 3 已入库 4 漏发
    total_qty = models.BigIntegerField(
        default=0, verbose_name="Goods Quantity")
    total_weight = models.FloatField(default=0, verbose_name="Total Weight")
    total_cost = models.FloatField(default=0, verbose_name="Total Cost")
    supplier = models.ForeignKey(Supplier, default=None, null=True, on_delete=models.SET_NULL,
                                 related_name=Supplier.RelativeFields.SUPPLER_ASN, verbose_name="ASN Supllier")
    bar_code = models.CharField(max_length=255, verbose_name="Bar Code")
    amend = models.BooleanField(default=False, verbose_name='Amend Asn')

    class Meta:
        db_table = 'asnlist'
        verbose_name = 'data id'
        verbose_name_plural = "data id"
        ordering = ['-create_time']

    def __str__(self):
        return str(self.pk)

    def afterSave(self, *args, **kwargs):
        '''
        检查关联的asnD_details是否需要修改
        '''
        if not self.is_delete:
            asn_details = self.asn_details.all()
            for asn_details_model in asn_details:
                asn_details_model.check_stock()
                asn_details_model.save()


class AsnDetailModel(BaseModel):
    asn = models.ForeignKey(AsnListModel, default=None, null=True,
                            on_delete=models.SET_NULL, related_name=AsnListModel.Relative_Fields.ANS_DETAILS,
                            verbose_name="ASN")
    # goods = models.ForeignKey(Goods, null=True, default=None,
    #                           on_delete=models.SET_NULL, related_name=Goods.RelativeFields.GOODS_ASN_DETAIL)
    goods = models.PositiveIntegerField(verbose_name='Goods Id of AsnDetail')

    purchase = models.ForeignKey(PurchasePlan, default=None, null=True, on_delete=models.SET_NULL, related_name=PurchasePlan.Relative_Fields.PURCHASE_ASN_DETAILS,
                            verbose_name="Asn Detail Purchase ")

    goods_qty = models.IntegerField(default=0, verbose_name="Goods QTY")
    goods_actual_qty = models.IntegerField(default=0, verbose_name="Goods Actual QTY")
    goods_shortage_qty = models.IntegerField(default=0, verbose_name="Goods Shortage QTY")
    goods_more_qty = models.IntegerField(default=0, verbose_name="Goods More QTY")
    goods_damage_qty = models.IntegerField(default=0, verbose_name="Goods damage QTY")
    goods_cost = models.FloatField(default=0, verbose_name="Goods Cost")
    sorted = models.BooleanField(default=False, verbose_name="Is Sorted")
    # stock = models.PositiveIntegerField(verbose_name='Stock Id of AsnDetail')
    stock = models.ForeignKey(StockRecord, default=None, null=True, on_delete=models.SET_NULL,
                              related_name='stock_asn_detail')

    class Meta:
        db_table = 'asndetail'
        verbose_name = 'AsnDetailModel'
        verbose_name_plural = "Asn Detail Model"
        ordering = ['-id']

    def __str__(self):
        return str(self.pk)

    def check_stock(self):
        asn_status = self.asn.asn_status
        is_amend = self.asn.amend
        if asn_status == 0 or self.is_delete:
            # 未采购的不需要关联库存
            if self.goods_qty <= 0:
                logger.warning('Asn detail qty is 0')
            return
        stock = self.stock
        right_stock_status = 1 if asn_status == 1 or asn_status == 2 else 2 # 如果采购清单的状态是 1(已采购，待分拣),库存状态应该是已购买(未到货), 其他为2(已分拣)
        right_stock_qty = self.goods_qty if asn_status == 1 or asn_status == 2 else self.goods_actual_qty
        stock_status = stock.stock_status if stock else -1
        logger.info("check stock asn_status %s, stock status %s, sorted %s ", asn_status, stock_status, self.sorted)
        if not stock:
            stock = StockService.get_instance().create_stock(stock_qty=right_stock_qty, goods_id=self.goods,
                                                             stock_status=right_stock_status)
            self.stock = stock
        elif stock.stock_qty != right_stock_qty or stock.stock_status != right_stock_status:
            # stock.stock_qty = right_stock_qty
            # stock.stock_status = right_stock_status
            # stock.save()
            StockService.get_instance().update_stock(stock, right_stock_qty, right_stock_status)
            ## 如果是初次分拣，那么要累加到现有库存
            if asn_status == 3 and not self.sorted:
                if is_amend:
                    amend_to = AsnListModel.objects.filter(asn_code=self.asn.asn_code, amend=False).first()
                    if amend_to:
                        amend_to_detail = getattr(amend_to, AsnListModel.Relative_Fields.ANS_DETAILS).filter(goods_id=self.goods.id).first()
                        if amend_to_detail:
                            # 追加到漏发的记录
                            amend_to_detail.goods_actual_qty += self.goods_actual_qty
                            amend_to_detail.goods_shortage_qty = amend_to_detail.goods_qty - amend_to_detail.goods_actual_qty
                            amend_to_detail.save()
                onhand_stock_qty = self.goods_actual_qty - self.goods_damage_qty
                if onhand_stock_qty > 0:
                    StockService.get_instance().create_onhand_stock(onhand_stock_qty, self.goods)
                if self.goods_damage_qty > 0:
                    StockService.get_instance().create_damage_stock(self.goods_damage_qty, self.goods)
                self.sorted = True
        # 如果 asn 是 已经分拣，那么转换为已分拣
        else:
            logger.info("no need to update asn details stock")


class AsnOrder(BaseModel):
    ORDER_STATUS = (
        (0, '未发货'),
        (1, '运输中'),  # 待采购的库存
        (2, '已到达'),  # 已经采购的库存
        (3, '已签收'),  # 现有库存
        (-1, '已退回'),  # 被锁定的库存
    )
    asn = models.ForeignKey(AsnListModel, default=None, null=True,
                            on_delete=models.SET_NULL, related_name=AsnListModel.Relative_Fields.ASN_ORDER, verbose_name="ASN")
    url = models.CharField(max_length=1024, blank=True, null=True, verbose_name="Asn Order Url")
    status = models.IntegerField(
        default=0, choices=ORDER_STATUS, verbose_name="Order status")
    delivery_date = models.DateField(
        default=datetime.date.today, auto_now=False, auto_now_add=False, verbose_name="Delivery Date", null=True, blank=True)
    trans_name = models.CharField(
        default="", max_length=255, verbose_name="Transportation Name")
    trans_url = models.CharField(
        default="", max_length=512, verbose_name="Transportation Url")
    trans_phone = models.CharField(
        default="", max_length=128, verbose_name="Transportation Phone")
    item_cost = models.FloatField(default=0, verbose_name="Order Item Cost")
    trans_fee = models.FloatField(default=0, verbose_name="Order Transport fess")
    discount = models.FloatField(default=0, verbose_name="Order discount")

    class Meta:
        db_table = 'asnorder'
        verbose_name = 'asnorder'
        verbose_name_plural = "asn order"
        ordering = ['-id']

    def __str__(self):
        return str(self.pk)
