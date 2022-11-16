from django.db import models
from base.models import BaseModel

class ListModel(BaseModel):
    bin_property = models.CharField(max_length=32, verbose_name="Bin property")

    class Meta:
        db_table = 'binproperty'
        verbose_name = 'data id'
        verbose_name_plural = "data id"
        ordering = ['bin_property']

    def __str__(self):
        return self.pk
