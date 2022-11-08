from django.db import models

from base.models import BaseModel


class StockRecord(BaseModel):

    class RelativeFields(object):
        STOCK_ORDER = "stock_order"

    DAMAGE_STOCK = 0

    PURCHASED_STOCK = 1

    SORTED_STOCK = 2

    ONHAND_STOCK = 3

    STOCK_STATUS = (
        (DAMAGE_STOCK, 'Damage Stock'),
        (PURCHASED_STOCK, 'Purchased Stock'),  # 已经采购的库存
        (SORTED_STOCK, 'Sorted Stock'),  # 已分拣库存
        (ONHAND_STOCK, 'In Stock'),  # 现有库存
    )

    goods_id = models.PositiveIntegerField(verbose_name='goods id of stock record')

    goods_code = models.CharField(max_length=255, verbose_name="Goods Code", db_index=True)

    goods_image = models.CharField(max_length=1024,  null=True, blank=True, verbose_name="Goods Image Url")

    stock_id = models.PositiveIntegerField(verbose_name='stock id of stock record')

    stock_qty = models.IntegerField(default=0, verbose_name="stock qty")

    stock_status = models.IntegerField(default=None, null=True, choices=STOCK_STATUS)

    class Meta:
        db_table = 'stock_record'
        verbose_name = 'stock_record'
        verbose_name_plural = "Stock Record"
        ordering = ['-id']
