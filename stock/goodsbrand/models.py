from django.db import models
from base.models import BaseModel

class ListModel(BaseModel):
    goods_brand = models.CharField(max_length=32, verbose_name="Goods Brand")
    
    class Meta:
        db_table = 'goodsbrand'
        verbose_name = 'data id'
        verbose_name_plural = "data id"
        ordering = ['goods_brand']

    def __str__(self):
        return self.pk
