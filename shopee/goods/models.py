from django.db import models

from base.models import BaseModel


class GoodsGroupRecord(BaseModel):
    group_id = models.PositiveIntegerField(verbose_name='Goods Group ID')

    name = models.CharField(max_length=128, verbose_name='Goods group name')

    product_id = models.PositiveIntegerField(verbose_name='Relative Product ID')

    class Meta:
        db_table = 'goods_group_record'
        verbose_name = 'goods_group_record'
        verbose_name_plural = "Goods Group Record"
        ordering = ['-id']


class GoodsRecord(BaseModel):
    goods_id = models.PositiveIntegerField(verbose_name='Goods Id')

    goods_code = models.CharField(max_length=128, verbose_name='Goods Code')

    goods_image = models.CharField(max_length=1024, verbose_name='Goods image url')

    group_id = models.PositiveIntegerField(verbose_name='Goods group Id')



