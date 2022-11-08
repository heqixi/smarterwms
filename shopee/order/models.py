from django.db import models
import logging

from base.models import BaseModel
from stock.models import StockRecord
from order.common import OrderHandleStatus
from store.models import StoreModel
from base.bustools import GLOBAL_BUS as bus

logger = logging.getLogger()


class ShopeeOrderModel(BaseModel):
    store = models.ForeignKey(StoreModel, on_delete=models.DO_NOTHING)
    order_sn = models.CharField(max_length=50, verbose_name="Order SN")
    order_status = models.CharField(max_length=50, verbose_name="Order Status")
    total_amount = models.FloatField(blank=True, null=True, verbose_name="Total Amount")
    actual_shipping_fee = models.FloatField(blank=True, null=True, verbose_name="Actual Shipping Fee")
    waybill_path = models.CharField(max_length=200, blank=True, null=True, verbose_name="Order Waybill Path")
    pay_time = models.DateTimeField(blank=True, null=True, verbose_name="Pay Time")
    days_to_ship = models.SmallIntegerField(verbose_name="Days To Ship")
    ship_by_date = models.DateTimeField(verbose_name="Ship By Date")
    buyer_user_id = models.CharField(blank=True, null=True, max_length=20, verbose_name="Buyer User Id")
    buyer_username = models.CharField(blank=True, null=True, max_length=100, verbose_name="Buyer Username")
    handle_status = models.SmallIntegerField(verbose_name='Order Handle Status', default=OrderHandleStatus.SHIPPED)

    class Meta:
        db_table = 'shopee_order'
        verbose_name = 'data id'
        verbose_name_plural = "data id"
        ordering = ['-id']

    def __str__(self):
        return str(self.pk)


class ShopeeOrderDetailModel(BaseModel):
    shopee_order = models.ForeignKey(ShopeeOrderModel, on_delete=models.CASCADE, related_name='order_detail')
    item_id = models.CharField(max_length=50, verbose_name='Item’s Unique identifier')
    item_name = models.CharField(max_length=250, verbose_name='Item Name')
    item_sku = models.CharField(max_length=50, verbose_name='Item Sku')
    # 仅能关联 保留库存
    stock = models.ForeignKey(StockRecord, default=None, null=True,
                              related_name=StockRecord.RelativeFields.STOCK_ORDER, on_delete=models.SET_NULL)
    model_id = models.CharField(max_length=50, verbose_name='Model ID', null=True)
    model_name = models.CharField(max_length=50, verbose_name='Model Name', null=True)
    model_sku = models.CharField(max_length=50, verbose_name='Model Sku', null=True)
    model_quantity_purchased = models.SmallIntegerField(verbose_name='Model Quantity Purchased')
    model_original_price = models.FloatField(verbose_name='Model Original Price')
    model_discounted_price = models.FloatField(verbose_name='Model Discounted Price')
    image_url = models.CharField(max_length=500, verbose_name='Image Url')

    class Meta:
        db_table = 'shopee_order_detail'
        verbose_name = 'shoppe_order_detail'
        verbose_name_plural = "Shoppe Order Detail"
        ordering = ['-id']

    def beforeSave(self, *args, **kwargs):
        logger.debug("shopee order before save ")
        bus.emit('order:shopeeOrderDetail:beforeSave', self)

    def __str__(self):
        return str(self.pk)


class ShopeeOrderModifyModel(BaseModel):
    """
    订单修订Model，用于修正出单的商品与数量
    """
    shopee_order = models.ForeignKey(ShopeeOrderModel, on_delete=models.CASCADE)
    # 1: 补发，2：替换
    modify_type = models.SmallIntegerField(verbose_name="Modify Type")
    # 全球货号
    global_sku = models.CharField(max_length=50, verbose_name='Global Sku')
    # 被替换的Model ID
    replaced_id = models.CharField(max_length=50, verbose_name='Model ID', null=True)
    # 被替换的SKU
    replaced_sku = models.CharField(max_length=50, verbose_name='Replaced Sku', null=True)
    # 数量
    quantity = models.IntegerField(verbose_name='Quantity', default=0)
    # 仅能关联 现有库存， 以采购库存
    stock = models.ForeignKey(StockRecord, default=None, null=True,
                              related_name='stock_order_modify', on_delete=models.SET_NULL)
    image_url = models.CharField(max_length=500, blank=True, verbose_name='Image Url')

    class Meta:
        db_table = 'shopee_order_modify'
        verbose_name = 'data id'
        verbose_name_plural = "data id"
        ordering = ['-id']

    def __str__(self):
        return self.pk


class ShopeeOrderMessageModel(BaseModel):
    shopee_order = models.ForeignKey(ShopeeOrderModel, on_delete=models.CASCADE)
    message = models.CharField(max_length=500, verbose_name="Message")
    # order.common.OrderMsgType
    type = models.SmallIntegerField(verbose_name="Message Type")
    # 标识，用于标识消息是否已读，或已处理
    mark = models.SmallIntegerField(verbose_name="Order Message Mark")

    class Meta:
        db_table = 'shopee_order_message'
        verbose_name = 'data id'
        verbose_name_plural = "data id"
        ordering = ['-id']

    def __str__(self):
        return self.pk


class ShopeeOrderRecordModel(BaseModel):
    """
    订单操作记录表
    """
    shopee_order = models.ForeignKey(ShopeeOrderModel, on_delete=models.CASCADE, related_name="recorded_order")
    batch_number = models.CharField(max_length=32, verbose_name="Record Batch Number")
    type = models.SmallIntegerField(verbose_name="Record Type")
    data = models.JSONField(max_length=255, null=True, blank=True, verbose_name="Record Data")
    create_time = models.DateTimeField(verbose_name="Create Time")

    class Meta:
        db_table = 'shopee_order_record'
        verbose_name = 'data id'
        verbose_name_plural = "data id"
        ordering = ['-id']

    def __str__(self):
        return self.pk


class ShopeeOrderPackageModel(BaseModel):

    shopee_order = models.ForeignKey(ShopeeOrderModel, on_delete=models.CASCADE, related_name="package_order")
    type = models.SmallIntegerField(verbose_name="Order Package Type")
    uid = models.IntegerField('ForeignKey Unique id')
    # 数量
    quantity = models.IntegerField(verbose_name='Quantity', default=0)
    # 仅能关联 现有库存， 以采购库存
    stock = models.ForeignKey(StockRecord, default=None, null=True,
                              related_name='stock_order_package', on_delete=models.SET_NULL)
    sku = models.CharField(max_length=50, verbose_name='Replaced Sku')
    image_url = models.CharField(max_length=500, blank=True, verbose_name='Image Url')

    class Meta:
        db_table = 'shopee_order_package'
        verbose_name = 'data id'
        verbose_name_plural = "data id"
        ordering = ['-id']

    def __str__(self):
        return self.pk