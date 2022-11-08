from abc import abstractmethod

from django.db import models


# Create your models here.
class BaseModel(models.Model):
    creater = models.CharField(max_length=255, verbose_name="Who created")
    openid = models.CharField(max_length=255, verbose_name="Openid")
    is_delete = models.BooleanField(default=False, verbose_name='Delete Label')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="Create Time")
    update_time = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name="Update Time")

    class Meta:
        abstract = True

    def beforeSave(self, *args, **kwargs):
        # print("eventCount ", GLOBAL_BUS.event_count)
        # GLOBAL_BUS.emit("model_before_save", self.__class__.__name__, self)
        pass

    def afterSave(self, *args, **kwargs):
        # GLOBAL_BUS.emit("model:after:save", self.__class__.__name__, self)
        pass

    def save(self, *args, **kwargs):
        self.beforeSave(*args, **kwargs)
        super(BaseModel, self).save(*args, **kwargs)
        self.afterSave(*args, **kwargs)
