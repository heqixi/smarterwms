from django.db import models

from base.models import BaseModel

class ListModel(BaseModel):
    staff_name = models.CharField(max_length=255, verbose_name="Staff Name")
    staff_type = models.CharField(max_length=255, verbose_name="Staff Type")
    check_code = models.IntegerField(default=8888, verbose_name="Check Code")
    error_check_code_counter = models.IntegerField(default=0,verbose_name='check_code error counter')
    is_lock = models.BooleanField(default=False,verbose_name='Whether the lock')
    class Meta:
        db_table = 'staff'
        verbose_name = 'data id'
        verbose_name_plural = "data id"
        ordering = ['staff_name']

    def __str__(self):
        return self.pk

class TypeListModel(BaseModel):
    staff_type = models.CharField(max_length=255, verbose_name="Staff Type")

    class Meta:
        db_table = 'stafftype'
        verbose_name = 'data id'
        verbose_name_plural = "data id"
        ordering = ['staff_type']

    def __str__(self):
        return self.pk
