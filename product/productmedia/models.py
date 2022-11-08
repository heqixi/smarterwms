

from django.db import models


from base.models import BaseModel
from product.models import GlobalProduct, ProductOption

import logging

logger = logging.getLogger()


class Constants(object):
    MEDIA_TYPE_IMAGE = "image"

    MEDIA_TYPE_VIDEO = "video"

    MEDIA_TAG_VIDEO = "video"

    MEDIA_TAG_MAIN_IMAGE = "main_image"

    MEDIA_TAG_DESC_IMAGE = "desc_image"

    MEDIA_TAG_OPTION_IMAGE = 'option_image'

    MEDIA_TAG_SKU_IMAGE = 'sku_image'


MEDIA_TYPE_CHOICES = {
    (Constants.MEDIA_TYPE_VIDEO, 'Vedio'),
    (Constants.MEDIA_TYPE_IMAGE, 'Image')
}

MEDIA_TYPE_TAG = {
    (Constants.MEDIA_TAG_VIDEO, 'Video'),
    (Constants.MEDIA_TAG_MAIN_IMAGE, 'Main Image'),
    (Constants.MEDIA_TAG_DESC_IMAGE, 'Desc Image'),
    (Constants.MEDIA_TAG_SKU_IMAGE, 'Sku Image')
}


class Media(BaseModel):
    class RelativeFields(object):
        MEDIA_PRODUCTS = "MEDIA_PRODUCTS"

        MEDIA_GOODS = 'media_goods'

        SHOPEE_PUBLISH = 'shopee_publish'

        MEDIA_OPTIONS = 'media_options'

    file = models.FileField(upload_to='uploads/%Y/%m/%d/', default=None, null=True)

    class Meta:
        db_table = 'media'
        verbose_name = 'media'
        ordering = ['-update_time']

    def __str__(self):
        return str(self.pk)


class ProductMedia(BaseModel):
    class RelativeFields(object):
        MEDIA_PUBLISH = "media_publish"

    product = models.ForeignKey(GlobalProduct, default=None, null=True, on_delete=models.CASCADE, related_name=GlobalProduct.RelativeFields.PRODUCT_MEDIA, verbose_name="Media relaitve product")
    url = models.CharField(max_length=1024,  null=True, blank=True, verbose_name="Product Meida Url")
    media = models.ForeignKey(Media, default=None, null=True, on_delete=models.SET_NULL, related_name=Media.RelativeFields.MEDIA_PRODUCTS, verbose_name="Product Media")
    media_type = models.CharField(max_length=16, default=Constants.MEDIA_TYPE_IMAGE, choices=MEDIA_TYPE_CHOICES)
    media_tag = models.CharField(max_length=32, default=Constants.MEDIA_TAG_DESC_IMAGE, choices=MEDIA_TYPE_TAG, verbose_name="Product media tag")
    index = models.IntegerField(default=0, blank=True, verbose_name="Media Order")

    class Meta:
        db_table = 'productmedia'
        verbose_name = 'product media'
        ordering = ['index']

    def __str__(self):
        return str(self.pk)


class ProductOptionMedia(BaseModel):
    class RelativeFields(object):
        MEDIA_PUBLISH = "media_publish"

    media = models.ForeignKey(Media, default=None, null=True, on_delete=models.CASCADE,
                              related_name=Media.RelativeFields.MEDIA_OPTIONS, verbose_name="Product Media")
    option = models.ForeignKey(ProductOption, on_delete=models.CASCADE, related_name=ProductOption.RelativeFields.OPTION_MEDIA)
    url = models.CharField(max_length=1024, null=True, blank=True, verbose_name="Product Option Meida Url")

    class Meta:
        db_table = 'product_option_media'
        verbose_name = 'product_option_media'
        ordering = ['-update_time']