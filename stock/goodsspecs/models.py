from django.db import models
from base.models import BaseModel

class ListModel(BaseModel):
    goods_specs = models.CharField(max_length=32, verbose_name="Goods Specs")

    class Meta:
        db_table = 'goodsspecs'
        verbose_name = 'data id'
        verbose_name_plural = "data id"
        ordering = ['goods_specs']

    def __str__(self):
        return self.pk
