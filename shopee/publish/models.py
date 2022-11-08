
from django.db import models
from base.models import BaseModel
from store.models import StoreProductModel, StoreProductVariantModel


class ProductEditPrice(BaseModel):
    class RelativeFields(object):

        PUBLISH_PRICE = 'publish_price'

    product = models.ForeignKey(StoreProductVariantModel, verbose_name='Product Price Info', on_delete=models.CASCADE,
                    related_name='edit_price')
    store_id = models.CharField(max_length=64, verbose_name="The price of Shop")
    current_price = models.FloatField(default=0, verbose_name='Current price')
    original_price = models.FloatField(default=0, verbose_name='Original price')
    currency = models.CharField(max_length=32, verbose_name='Currency')
    discount_id = models.BigIntegerField(default=0, verbose_name='活动ID')
    published = models.BooleanField(default=False, verbose_name='Is Price Publish')
    publish_ready = models.BooleanField(default=False, verbose_name='Is Price Publish Ready')

    class Meta:
        db_table ='product_edit_price'
        verbose_name ='product_edit_price'
        unique_together = ['product_id', 'store_id']
        ordering = ['-create_time']


class ProductOptionConfig(BaseModel):
    model = models.ForeignKey(StoreProductModel, on_delete=models.CASCADE,
                              related_name=StoreProductModel.RelativeFields.MODEL_STOCKS)
    stock_qty = models.IntegerField(default=0, verbose_name='Model Stock')

    price = models.FloatField(default=0, verbose_name='Model Price')

    class Meta:
        db_table = 'globalproduct_model_stock'
        verbose_name = 'globalproduct_model_stock'
        verbose_name_plural = "Global Product Model Stock"
        ordering = ['-create_time']


class ProductCategoryBrand(BaseModel):
    class RelativeFields(object):

        PRODUCT_CATEGORIES = "brand_category"

    brand_id = models.IntegerField(default=0, verbose_name="Brand ID")

    display_brand_name = models.CharField(max_length=64, verbose_name="Brand Name")


class ProductCategory(BaseModel):
    class RelativeFields(object):

        ATTRIBUTES = "attributes"

    MERCHANT_TYPE_SHOPEE = 'shopee'

    MERCHANT_TYPE_CHOICES = [
        (MERCHANT_TYPE_SHOPEE, 'shopee category')
    ]

    product = models.ForeignKey(StoreProductModel, verbose_name='Product Price Info', on_delete=models.CASCADE,
                    related_name=StoreProductModel.RelativeFields.PRODUCT_CATEGORY)

    merchant_type = models.CharField(max_length=16, default=MERCHANT_TYPE_SHOPEE, choices=MERCHANT_TYPE_CHOICES,
                                     verbose_name="Shopee Category merchant id")

    merchant_id = models.CharField(max_length=64, verbose_name="Shopee Category merchant id")

    category_id = models.IntegerField(default=0, verbose_name="Shopee Category ID")

    brand = models.ForeignKey(ProductCategoryBrand, on_delete=models.SET_NULL, default=None, null=True, blank=True,
                              related_name=ProductCategoryBrand.RelativeFields.PRODUCT_CATEGORIES)

    class Meta:
        db_table ='product_category'
        verbose_name ='product_category'
        verbose_name_plural = "Product Category"
        unique_together = ['product_id', 'merchant_type', 'merchant_id']
        ordering = ['-create_time']


class ProductCategoryAttribute(BaseModel):
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name=ProductCategory.RelativeFields.ATTRIBUTES)

    attribute_id = models.CharField(max_length=64, verbose_name="Category Attribute id")

    display_value_name = models.CharField(max_length=32, verbose_name="Category Attribute value")

    value_id = models.IntegerField(default=-1, verbose_name="Attribute Value Id")

    multiple = models.BooleanField(default=False, verbose_name="Is Multiple")

    class Meta:
        db_table ='product_category_attribute'
        verbose_name ='product_category_attribute'
        verbose_name_plural = "Product Category attribute"
        ordering = ['-create_time']


class ProductLogistic(BaseModel):
    product = models.ForeignKey(StoreProductModel, verbose_name='Product', on_delete=models.CASCADE,
                                related_name=StoreProductModel.RelativeFields.PRODUCT_LOGISTIC)
    product_w = models.FloatField(blank=True, null=True, verbose_name="Product Width")
    product_h = models.FloatField(blank=True, null=True, verbose_name="Product Height")
    product_d = models.FloatField(blank=True, null=True, verbose_name="Product Depth")
    weight = models.FloatField(null=True, blank=True, verbose_name="Product Weight")
    days_deliver = models.IntegerField(default=3, blank=True, verbose_name="Day to delivery")

    class Meta:
        db_table = 'product_logistic'
        verbose_name = 'product_logistic'
        verbose_name_plural = "Product Logistic"
        ordering = ['-create_time']


class ProductMediaPublish(BaseModel):

    merchant_id = models.CharField(max_length=64, verbose_name="Product Media merchant id")

    publish_id = models.CharField(max_length=128, verbose_name="Product Media Publish id")

    publish_url = models.CharField(max_length=1024, null=True, blank=True, verbose_name="Product Meida Publish Url")

    source_url = models.CharField(max_length=1024, null=True, blank=True, verbose_name="Product Meida Source Url")

    class Meta:
        db_table = 'product_media_publish'
        verbose_name = 'product_media_publish'
        unique_together = ['publish_id']
        ordering = ['-create_time']

