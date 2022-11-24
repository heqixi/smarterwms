
from django.db import models
from base.models import BaseModel

PUBLISH = 'PB'
PUBLISH_READY = 'PR'
DELETE = 'DE'
EDIT = 'ED'


class ListModel(BaseModel):
    STATUS_CHOICES = [
        (PUBLISH, 'Publish Goods'),
        (DELETE, 'Delete Goods'),
        (EDIT, 'Editing Goods')
    ]

    class RelativeFields(object):
        GOODS_STOCK = "goods_stock"
        
        GOODS_MEDIA = "goods_media"

        GOODS_PURCHASES_SETTING = "goods_purchases_settings"

        PRODUCT_MODELS = "product_models"

        PRODUCT_RELATION = 'product_relation'

        GOODS_ASN_DETAIL = "goods_asn_detail"

    goods_code = models.CharField(max_length=255, verbose_name="Goods Name", db_index=True)
    goods_image = models.CharField(max_length=1024,  null=True, blank=True, verbose_name="Goods Main Image Url")
    goods_name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Goods Name")
    goods_desc = models.CharField(max_length=4096,  null=True, blank=True, verbose_name="Goods Description")
    goods_weight = models.FloatField(default=0, verbose_name="Goods Weight")
    goods_w = models.FloatField(default=0, blank=True, verbose_name="Goods Width")
    goods_d = models.FloatField(default=0, blank=True, verbose_name="Goods Depth")
    goods_h = models.FloatField(default=0, blank=True, verbose_name="Goods Height")
    goods_unit = models.CharField(max_length=255,  null=True, blank=True, verbose_name="Goods Unit")
    goods_class = models.CharField(max_length=255, null=True, blank=True, verbose_name="Goods Class")
    goods_brand = models.CharField(max_length=255, null=True, blank=True, verbose_name="Goods Brand")
    goods_color = models.CharField(max_length=255, null=True, blank=True, verbose_name="Goods Color")
    bar_code = models.CharField(max_length=255, null=True, blank=True, verbose_name="Bar Code")

    class Meta:
        db_table = 'goods'
        verbose_name = 'data id'
        verbose_name_plural = "data id"
        ordering = ['-create_time']
        unique_together = ['openid', 'goods_code']

    def __str__(self):
        return str(self.pk)

    def save(self, *args, **kwargs):
        super(ListModel, self).save(*args, **kwargs)


class GoodsGroup(BaseModel):
    goods = models.ManyToManyField(ListModel, null=True, related_name='goods_group')
    name = models.CharField(max_length=128, verbose_name='Goods group name')

    class Meta:
        db_table = 'goods_group'
        verbose_name = 'goods_group'


class GlobalProductGoodsRelation(BaseModel):
    product_id = models.PositiveIntegerField(verbose_name='Product Id')
    goods = models.ForeignKey(ListModel, on_delete=models.CASCADE, related_name=ListModel.RelativeFields.PRODUCT_RELATION, db_index=True)

    confirm = models.BooleanField(default=False, verbose_name='Is Relation Confirm')

    class Meta:
        db_table = 'global_product_goods_relation'
        verbose_name = 'global_product_goods_relation'
        verbose_name_plural = "Global Product Goods Relation"
        unique_together = ['product_id', 'goods_id']
        ordering = ['-create_time']


class GoodsTag(BaseModel):
    goods = models.ManyToManyField(ListModel, related_name="goods_tags")
    tag = models.CharField(max_length=255,  blank=True, verbose_name="Goods Name")

    class Meta:
        db_table='goodstag'
        verbose_name='goods_tag'
        verbose_name_plural="Goods Tag"
        ordering = ['-create_time']

    def __str__(self):
        return str(self.pk)
