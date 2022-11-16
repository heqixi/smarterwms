from django.db import models

from base.models import BaseModel

class ListModel(BaseModel):
    goods_shape = models.CharField(max_length=32, verbose_name="Goods Shape")

    class Meta:
        db_table = 'goodsshape'
        verbose_name = 'data id'
        verbose_name_plural = "data id"
        ordering = ['goods_shape']

    def __str__(self):
        return self.pk
