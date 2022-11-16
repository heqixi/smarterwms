from django.db import models

from base.models import BaseModel


class PurchasePlanRecord(BaseModel):

    purchase_id = models.PositiveIntegerField(verbose_name='Purchase Plan id')

    product_id = models.PositiveIntegerField(verbose_name='Shopee global product instance id')

    class Meta:
        db_table = 'purchase_plan_record'
        verbose_name = 'purchase_plan_record'
        verbose_name_plural = 'Shopee Product Purchase Record'
        ordering = ['-id']
