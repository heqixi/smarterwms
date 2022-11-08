from django.db import models

from base.models import BaseModel


class StockRecord(BaseModel):

    class RelativeFields(object):
        STOCK_ORDER = "stock_order"

    RESERVE_STOCK = 11

    SHIP_STOCK = 12

    STOCK_STATUS = (
        (RESERVE_STOCK, 'Reserve Stock'),  # 被锁定的库存
        (SHIP_STOCK, 'Ship Stock'),  # 已经发货的库存
    )

    goods_id = models.PositiveIntegerField(verbose_name='goods id of stock record')

    goods_code = models.CharField(max_length=255, verbose_name="Goods Code", db_index=True)

    goods_image = models.CharField(max_length=1024,  null=True, blank=True, verbose_name="Goods Image Url")

    stock_id = models.PositiveIntegerField(verbose_name='stock id of stock record')

    stock_qty = models.IntegerField(default=0, verbose_name="stock qty")

    stock_status = models.IntegerField(default=RESERVE_STOCK, choices=STOCK_STATUS)

    class Meta:
        db_table = 'stock_record'
        verbose_name = 'stock_record'
        verbose_name_plural = "Stock Record"
        ordering = ['-id']


class ProductGoodsRelations(BaseModel):

    goods_id = models.PositiveIntegerField(verbose_name='Goods id of product')

    publish_id = models.PositiveIntegerField(verbose_name='Publish id of Shopee')

    class Meta:
        db_table = 'product_goods_relations'
        verbose_name = 'product_goods_relations'
        verbose_name_plural = 'Shopee Product Goods Relations'
        ordering = ['-id']
