from django.db import models
from base.models import BaseModel

class ListModel(BaseModel):
    goods_color = models.CharField(max_length=32, verbose_name="Goods Color")

    class Meta:
        db_table = 'goodscolor'
        verbose_name = 'data id'
        verbose_name_plural = "data id"
        ordering = ['goods_color']

    def __str__(self):
        return self.pk
