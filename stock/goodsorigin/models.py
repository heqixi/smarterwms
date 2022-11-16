from django.db import models

from base.models import BaseModel

class ListModel(BaseModel):
    goods_origin = models.CharField(max_length=32, verbose_name="Goods Origin")

    class Meta:
        db_table = 'goodsorigin'
        verbose_name = 'data id'
        verbose_name_plural = "data id"
        ordering = ['goods_origin']

    def __str__(self):
        return self.pk
