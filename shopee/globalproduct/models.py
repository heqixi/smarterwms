from base.models import BaseModel
from django.db import models
from store.models import StoreProductModel, StoreModel


class GlobalProductRelations(BaseModel):
    global_product_id = models.CharField(max_length=128, verbose_name='Global Product Id')
    product = models.ForeignKey(StoreProductModel, on_delete=models.CASCADE, related_name='shopee_product')
    store = models.ForeignKey(StoreModel, on_delete=models.CASCADE, related_name='tier_store')

    class Meta:
        db_table = 'global_product_relations'
        verbose_name = 'global_product_relations'
        verbose_name_plural = 'Global Product Relations'
        ordering = ['-create_time']