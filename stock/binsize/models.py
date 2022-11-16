from django.db import models
from base.models import BaseModel

class ListModel(BaseModel):
    bin_size = models.CharField(max_length=255, verbose_name="Bin Name")
    bin_size_w = models.FloatField(default=0, verbose_name="Bin Width")
    bin_size_d = models.FloatField(default=0, verbose_name="Bin Depth")
    bin_size_h = models.FloatField(default=0, verbose_name="Bin Height")

    class Meta:
        db_table = 'binsize'
        verbose_name = 'data id'
        verbose_name_plural = "data id"
        ordering = ['-id']

    def __str__(self):
        return self.pk
