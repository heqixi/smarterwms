from django.db import models

# Create your models here.
from base.models import BaseModel
from product.models import GlobalProduct


class ProductPublish(BaseModel):
    SHOP_TYPE_SHOPEE = 'shopee'

    product = models.ForeignKey(GlobalProduct, verbose_name='Publish Product', on_delete=models.CASCADE,
                                related_name=GlobalProduct.RelativeFields.PUBLISH_PUBLISH)

    shop_id = models.CharField(max_length=64, verbose_name='Publish shop id')
    shop_type = models.CharField(default=SHOP_TYPE_SHOPEE, max_length=16, verbose_name='Publish shop type')
    publish_id = models.CharField(max_length=64, verbose_name="Product Publish ID")

    class Meta:
        db_table = 'shopee_store_publish'
        verbose_name = 'shopee_store_publish'
        unique_together = ['product_id', 'shop_id']
        ordering = ['-create_time']

