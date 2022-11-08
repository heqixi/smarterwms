
from django.db import models
from base.models import BaseModel


class ListModel(BaseModel):
    class RelativeFields(object):
        SUPPLIER_PURCHASES = "supplier_purchases"

        SUPPLIER_PURCHASES_UNDELETE = "supplier_purchases_undelete"

        SUPPLER_ASN = 'suppler_asn'

    supplier_name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Supplier Name")
    supplier_city = models.CharField(max_length=255,  blank=True, null=True, verbose_name="Supplier City")
    supplier_address = models.CharField(max_length=255,  blank=True, null=True, verbose_name="Supplier Address")
    supplier_contact = models.CharField(max_length=255,  blank=True, null=True, verbose_name="Supplier Contact")
    supplier_manager = models.CharField(max_length=255, blank=True, null=True, verbose_name="Supplier Manager")
    supplier_level = models.BigIntegerField(default=1, blank=True, null=True, verbose_name="Supplier Level")

    class Meta:
        db_table = 'supplier'
        verbose_name = 'data id'
        verbose_name_plural = "data id"
        ordering = ['supplier_name']

    def __str__(self):
        return str(self.pk)


'''
采购途径
'''


class PurchasePlan(BaseModel):
    class Relative_Fields(object):
        PURCHASE_ASN_DETAILS = 'purchase_asn_details'

        GOODS_SETTENGS = 'goods_settings'

    image_url = models.CharField(max_length=1024, verbose_name="Purchase Plan Image Url", blank=True, null=True, default=None)
    supplier = models.ForeignKey(ListModel, default=None, null=True, on_delete=models.SET_NULL,
                                 related_name=ListModel.RelativeFields.SUPPLIER_PURCHASES, verbose_name="Goods Supllier")
    price = models.FloatField(default=0, verbose_name="Goods Price")
    url = models.CharField(max_length=1024, verbose_name="Goods Url")
    default = models.BooleanField(default=False, verbose_name="Default Purchase Plan")
    tag = models.CharField(max_length=64, default='', blank=True, null=True, verbose_name="Purchase Tags")

    class Meta:
        db_table = 'purchasePlan'
        verbose_name = 'purchase Plan'
        verbose_name_plural = "Purchase Plan"
        ordering = ['-id']

    def __str__(self):
        return str(self.pk)


class PurchasePlanGoodsSetting(BaseModel):
    plan = models.ForeignKey(PurchasePlan, on_delete=models.CASCADE,
                             related_name=PurchasePlan.Relative_Fields.GOODS_SETTENGS)
    goods = models.PositiveIntegerField(verbose_name='goods id of PurchasePlan')
    level = models.PositiveIntegerField(default=0, verbose_name='Goods Purchase Plan Level')

    class Meta:
        db_table = 'purchasePlan_goods_setting'
        verbose_name = 'purchasePlan_goods_setting'
        verbose_name_plural = "Purchase Plan Goods Setting"
        unique_together = ['goods', 'level']
        ordering = ['-id']

