from django.db import models
from base.models import BaseModel

class ListModel(BaseModel):
    bin_name = models.CharField(max_length=255, verbose_name="Bin Name")
    bin_size = models.CharField(max_length=255, verbose_name="Bin Size")
    bin_property = models.CharField(max_length=11, verbose_name="Bin Property")
    empty_label = models.BooleanField(default=True, verbose_name="Empty Label")
    bar_code = models.CharField(max_length=255, verbose_name="Bar Code")

    class Meta:
        db_table = 'binset'
        verbose_name = 'data id'
        verbose_name_plural = "data id"
        ordering = ['bin_name']

    def __str__(self):
        return self.pk
