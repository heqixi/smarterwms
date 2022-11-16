from django.db import models
from base.models import BaseModel

class ListModel(BaseModel):
    warehouse_name = models.CharField(max_length=255, verbose_name="Warehouse Name")
    warehouse_city = models.CharField(max_length=255, verbose_name="Warehouse City")
    warehouse_address = models.CharField(max_length=255, verbose_name="Warehouse Address")
    warehouse_contact = models.CharField(max_length=255, verbose_name="Warehouse Contact")
    warehouse_manager = models.CharField(max_length=255, verbose_name="Warehouse Manager")

    class Meta:
        db_table = 'warehouse'
        verbose_name = 'data id'
        verbose_name_plural = "data id"
        ordering = ['warehouse_name']

    def __str__(self):
        return self.pk
