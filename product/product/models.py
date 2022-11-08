
from django.db import models
from base.models import BaseModel

PUBLISH = 'PB'
PUBLISH_READY = 'PR'
DELETE = 'DE'
EDIT = 'ED'


class GlobalProduct(BaseModel):

    PUBLISH = 'PB'
    PUBLISH_READY = 'PR'
    DELETE = 'DE'
    EDIT = 'ED'

    TYPE_MAIN = 1

    TYPE_MODEL = 2

    TYPE_CHOICES = [
        (TYPE_MAIN, 'Main Product'),
        (TYPE_MODEL, 'Product Model')
    ]

    MODE_SINGLE = 'SG'

    MODE_MULTIPLE = 'MT'

    STATUS_CHOICES = [
        (PUBLISH, 'Publish Goods'),
        (DELETE, 'Delete Goods'),
        (EDIT, 'Editing Goods'),
        (PUBLISH_READY, 'Publish Ready')
    ]

    MODE_CHOICES = [
        (MODE_SINGLE, 'Single Product'),
        (MODE_MULTIPLE, 'Multiple Variant')
    ]

    class RelativeFields(object):

        GOODS_RELATION = 'goods_relation'

        SHOPEE_PRODUCT = "shopee_product"

        PRODUCT_MEDIA = 'product_media'

        PRODUCT_SUPPLIER = 'product_supplier'

        PRODUCT_LOGISTIC = 'product_logistic'

        PRODUCT_SPECIFICATION = 'product_specification'

        PARIENT_PRODUCTS = 'parient_products'

        PRODUCT_CATEGORY = 'product_category'

        MODEL_OPTIONS = 'model_options'

        MODEL_STOCKS = 'model_stock'

        SHOPEE_GLOBAL_PUBLISH = 'shopee_global_publish'

        PRICE_INFO = 'price_info'

        PRICE_PUBLISH = 'price_publish'

        PUBLISH_PUBLISH = 'shopee_store_publish'

    sku = models.CharField(max_length=255, verbose_name="Product Sku")
    status = models.CharField(max_length=255, default=PUBLISH, choices=STATUS_CHOICES, verbose_name="Product Status")
    mode = models.CharField(max_length=255, default=MODE_MULTIPLE, choices=MODE_CHOICES, verbose_name="Product Mode")
    image = models.CharField(max_length=1024,  null=True, blank=True, verbose_name="Product Main Image Url")
    name = models.CharField(max_length=255,  blank=True, null=True, verbose_name="Product Name")
    desc = models.CharField(max_length=4096,  blank=True, null=True, verbose_name="Product Description")
    second_hand = models.BooleanField(default=False, verbose_name='Is Product Second Hand')
    type = models.SmallIntegerField(default=TYPE_MAIN, choices=TYPE_CHOICES, verbose_name='Global Product Type')
    models = models.ManyToManyField('self', symmetrical=False, blank=True,
                                    related_name=RelativeFields.PARIENT_PRODUCTS, limit_choices_to={"type": TYPE_MODEL})

    class Meta:
        db_table = 'globalproduct'
        verbose_name = 'global_product'
        verbose_name_plural = "Global Product"
        ordering = ['-create_time']


class GlobalProductGoodsRelation(BaseModel):
    product = models.ForeignKey(GlobalProduct, verbose_name='Product', on_delete=models.CASCADE,
                                related_name=GlobalProduct.RelativeFields.GOODS_RELATION, db_index=True, unique=True)
    goods_id = models.PositiveIntegerField(verbose_name='Goods Id of Product')

    confirm = models.BooleanField(default=False, verbose_name='Is Relation Confirm')

    class Meta:
        db_table = 'global_product_goods_relation'
        verbose_name = 'global_product_goods_relation'
        verbose_name_plural = "Global Product Goods Relation"
        unique_together = ['product_id', 'goods_id']
        ordering = ['-create_time']


class ProductModelStock(BaseModel):
    model = models.ForeignKey(GlobalProduct, on_delete=models.CASCADE,
                              related_name=GlobalProduct.RelativeFields.MODEL_STOCKS, limit_choices_to={"type": GlobalProduct.TYPE_MODEL})
    stock_qty = models.IntegerField(default=0, verbose_name='Model Stock')

    price = models.FloatField(default=0, verbose_name='Model Price')

    class Meta:
        db_table = 'globalproduct_model_stock'
        verbose_name = 'globalproduct_model_stock'
        verbose_name_plural = "Global Product Model Stock"
        ordering = ['-create_time']


class ProductSupplier(BaseModel):
    product = models.ForeignKey(GlobalProduct, verbose_name='Product', on_delete=models.CASCADE, related_name=GlobalProduct.RelativeFields.PRODUCT_SUPPLIER)
    url = models.URLField(null=True, blank=True, max_length=512, verbose_name="Product Supplier Url")
    logistics_costs = models.FloatField(default=0, verbose_name='Logistic costs')
    min_purchase_num = models.PositiveIntegerField(default=1, verbose_name='min_purchase_num')
    delivery_days = models.PositiveIntegerField(default=1, verbose_name='Delivery Days')
    supplier_city = models.CharField(max_length=50, null=True, blank=True, verbose_name='Supplier City')
    supplier_name = models.CharField(max_length=100, null=True, blank=True,  verbose_name='Company')

    class Meta:
        db_table = 'productsupplier'
        verbose_name = 'product_supplier'
        verbose_name_plural = "Global Product Supplier"
        ordering = ['-create_time']


class ProductLogistic(BaseModel):
    product = models.ForeignKey(GlobalProduct, verbose_name='Product', on_delete=models.CASCADE,
                                related_name=GlobalProduct.RelativeFields.PRODUCT_LOGISTIC)
    product_w = models.FloatField(blank=True, null=True, verbose_name="Product Width")
    product_h = models.FloatField(blank=True, null=True, verbose_name="Product Height")
    product_d = models.FloatField(blank=True, null=True, verbose_name="Product Depth")
    weight = models.FloatField(null=True, blank=True, verbose_name="Product Weight")
    days_deliver = models.IntegerField(default=3, blank=True, verbose_name="Day to delivery")

    class Meta:
        db_table = 'productlogistic'
        verbose_name = 'product_logistic'
        verbose_name_plural = "Product Logistic"
        ordering = ['-create_time']


class ProductSpecification(BaseModel):
    class RelativeFields(object):
        SPECIFICATION_OPTION = "specification_option"

    product = models.ForeignKey(GlobalProduct, verbose_name='Specification Product', on_delete=models.CASCADE,
                                related_name=GlobalProduct.RelativeFields.PRODUCT_SPECIFICATION)
    name = models.CharField(max_length=255, verbose_name="Specification Name")
    index = models.IntegerField(default=0, blank=True, verbose_name="Specification Order")

    class Meta:
        db_table = 'productspecification'
        verbose_name = 'product_specification'
        verbose_name_plural = "Product Specification"
        ordering = ['index']


class ProductOption(BaseModel):
    class RelativeFields(object):
        OPTION_MEDIA = "OPTION_MEDIA"

    specification = models.ForeignKey(ProductSpecification, verbose_name='Option Specification', on_delete=models.CASCADE,
                                related_name=ProductSpecification.RelativeFields.SPECIFICATION_OPTION)
    name = models.CharField(max_length=255, verbose_name="Specification Option Name")
    index = models.IntegerField(default=0, blank=True, verbose_name="Option Order")
    image = models.CharField(max_length=1024, null=True, blank=True, verbose_name="Option Image Url")
    models = models.ManyToManyField(GlobalProduct, symmetrical=False, blank=True,
                                    related_name=GlobalProduct.RelativeFields.MODEL_OPTIONS, limit_choices_to={"type": GlobalProduct.TYPE_MODEL})

    class Meta:
        db_table = 'product-specification-option'
        verbose_name = 'product_specification_option'
        verbose_name_plural = "Product Specification Option"
        ordering = ['index']
