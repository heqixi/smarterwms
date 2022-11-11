from django.db import models

from base.models import BaseModel
from store.common import StoreStatus, StoreType, StoreProductType


class StoreModel(BaseModel):
    name = models.CharField(max_length=255, verbose_name="Store Name")
    uid = models.CharField(max_length=50, verbose_name="Shop ID Or Merchant ID", db_index=True)
    # 店铺类型 1: 商户类型 2: 店铺类型
    type = models.SmallIntegerField(verbose_name="Store Type", db_index=True)
    platform = models.SmallIntegerField(verbose_name="Platform Type")
    area = models.CharField(max_length=50, verbose_name="Area Type")
    status = models.SmallIntegerField(default=StoreStatus.NORMAL, verbose_name="Store Status")
    merchant = models.ForeignKey(
        'self', limit_choices_to={type: StoreType.MERCHANT},
        on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        db_table = 'store'
        verbose_name = 'data id'
        verbose_name_plural = "data id"
        ordering = ['-id']

    def __str__(self):
        return str(self.pk)


class StoreInfoModel(BaseModel):
    store = models.ForeignKey('StoreModel', on_delete=models.CASCADE)
    info_key = models.CharField(max_length=20, verbose_name="Info Key")
    info_value = models.JSONField(max_length=255, verbose_name="Info Value")

    class Meta:
        db_table = 'store_info'
        verbose_name = 'data id'
        verbose_name_plural = "data id"
        ordering = ['-id']
        index_together = (
            ('store', 'info_key')
        )

    def __str__(self):
        return str(self.pk)


class StoreProductModel(BaseModel):
    """
    商品
    """
    class RelativeFields(object):
        STORE_PRODUCTS = "store_products"

        PRODUCT_CATEGORY = 'product_category'

        MODEL_STOCKS = 'model_stocks'

        PRODUCT_LOGISTIC = 'product_logistic'

        PRODUCT_MEDIA = 'product_media'

        PRODUCT_OPTION = 'product_option'

        PRODUCT_VARIANT = 'product_variant'

    class Status:
        NORMAL = 'NORMAL'
        DELETED = 'DELETED'
        UNLIST = 'UNLIST'
        BANNED = 'BANNED'
        EDIT = 'EDIT'
        PUBLISH_READY = 'PUBLISH_READY'

    store = models.ForeignKey(StoreModel, on_delete=models.CASCADE)
    product_id = models.CharField(max_length=50, null=True, verbose_name='Store product unique identifier', unique=True)
    product_name = models.CharField(max_length=250, verbose_name='Store product Name')
    # NORMAL, DELETED, UNLIST and BANNED. EDIT, PUBLISH_READY
    product_status = models.CharField(max_length=15, verbose_name='Store product Status')
    product_sku = models.CharField(max_length=100, verbose_name='Store product sku')
    image_url = models.CharField(max_length=500, verbose_name='Store product image url')
    category_id = models.IntegerField(default=0, verbose_name='Store product thumbnail url')
    brand_id = models.IntegerField(default=0, verbose_name='Store product brand id')
    brand_name = models.CharField(null=True, max_length=100, verbose_name='Store product brand name')
    days_to_ship = models.SmallIntegerField(default=3, verbose_name='Store product days to ship')
    weight = models.FloatField(null=True, verbose_name='Store product weight')
    length = models.IntegerField(null=True, blank=True, verbose_name='Store product length')
    width = models.IntegerField(null=True, blank=True, verbose_name='Store product width')
    height = models.IntegerField(null=True, blank=True, verbose_name='Store product height')
    description = models.TextField(null=True, blank=True, verbose_name='Store product description')
    shop_products = models.ManyToManyField(
        'self', blank=True, related_name='global_product', symmetrical=False,
        db_table='store_product_relations', limit_choices_to={"store__type__in": [StoreType.SHOP]})

    class Meta:
        db_table = 'store_product'
        verbose_name = 'data id'
        verbose_name_plural = "data id"
        ordering = ['-id']
        unique_together = (
            ('store', 'product_sku', 'product_status', 'product_id')
        )

    def __str__(self):
        return str(self.pk)


class StoreProductOptionModel(BaseModel):
    """
    全球店铺产品，规格信息
    """
    class RelativeFields(object):
        OPTION_ITEM = "option_item"

    store_product = models.ForeignKey(StoreProductModel, on_delete=models.CASCADE, related_name='product_option')
    name = models.CharField(max_length=100, verbose_name='Store Product Option Name')
    index = models.SmallIntegerField(verbose_name='Option Index')

    class Meta:
        db_table = 'store_product_option'
        verbose_name = 'data id'
        verbose_name_plural = "data id"
        ordering = ['-id']

    def __str__(self):
        return str(self.pk)


class StoreProductOptionItemModel(BaseModel):
    """
    全球店铺产品，规格选项信息
    """
    store_product = models.ForeignKey(StoreProductModel, on_delete=models.CASCADE, related_name='product_option_item')
    store_product_option = models.ForeignKey(StoreProductOptionModel, on_delete=models.CASCADE, related_name='option_item')
    name = models.CharField(max_length=100, verbose_name='Option Item Name')
    image_id = models.CharField(max_length=100, null=True, blank=True, verbose_name='Option Item Image Url')
    image_url = models.CharField(max_length=500, null=True, blank=True, verbose_name='Option Item Image Url')
    index = models.SmallIntegerField(verbose_name='Option Item Index')

    class Meta:
        db_table = 'store_product_option_item'
        verbose_name = 'data id'
        verbose_name_plural = "data id"
        unique_together = ['store_product_option', 'index']
        ordering = ['-id']

    def __str__(self):
        return str(self.pk)


class StoreProductVariantModel(BaseModel):
    """
    产品变体信息
    """
    store_product = models.ForeignKey(StoreProductModel, on_delete=models.CASCADE, related_name='product_variant')
    model_id = models.CharField(max_length=50, null=True, verbose_name='Store product model unique identifier', unique=True)
    model_sku = models.CharField(max_length=100, verbose_name='Store product model sku')
    promotion_id = models.CharField(max_length=50, null=True, blank=True, verbose_name='Model promotion id')
    option_item_index = models.CharField(max_length=64, verbose_name='Option item index')

    class Meta:
        db_table = 'store_product_variant'
        verbose_name = 'data id'
        verbose_name_plural = "data id"
        ordering = ['-id']

    def __str__(self):
        return str(self.pk)


class StoreProductMedia(BaseModel):
    TYPE_IMAGE = 2
    TYPE_VIDEO = 1
    """
    媒体资源
    """
    store_product = models.ForeignKey(StoreProductModel, on_delete=models.CASCADE,
                                      related_name=StoreProductModel.RelativeFields.PRODUCT_MEDIA)
    type = models.SmallIntegerField(verbose_name='Media Type')
    image_id = models.CharField(max_length=50, null=True, blank=True, verbose_name='Product image id')
    url = models.CharField(max_length=500, verbose_name='Product media url')
    index = models.SmallIntegerField(verbose_name='Product media index')

    class Meta:
        db_table = 'store_product_media'
        verbose_name = 'data id'
        verbose_name_plural = "data id"
        ordering = ['-id']

    def __str__(self):
        return str(self.pk)


class StoreProductPriceInfoModel(BaseModel):
    """
    产品价格信息表
    """
    store_product = models.ForeignKey(StoreProductModel, on_delete=models.CASCADE, related_name='product_price_info')
    # 类型分为主产品，还是变体
    type = models.SmallIntegerField(default=StoreProductType.VARIANTS, verbose_name='Price info type')
    # 当类型为变体时候，会保存变体关联
    variant = models.ForeignKey(StoreProductVariantModel, null=True, blank=True, on_delete=models.CASCADE, related_name='variant_price')
    original_price = models.FloatField(max_length=100, verbose_name='Store product original price')
    current_price = models.FloatField(null=True, blank=True, max_length=100, verbose_name='Store product current price')
    inflated_price_of_original_price = models.FloatField(null=True, blank=True, max_length=100, verbose_name='Inflated price of original price')
    inflated_price_of_current_price = models.FloatField(null=True, blank=True, max_length=100, verbose_name='Inflated price of current price')
    sip_item_price = models.FloatField(null=True, blank=True, max_length=100, verbose_name='Sip item price')
    sip_item_price_source = models.FloatField(null=True, blank=True, max_length=100, verbose_name='Sip item price source')
    currency = models.CharField(max_length=10, verbose_name='Currency')

    class Meta:
        db_table = 'store_product_price_info'
        verbose_name = 'data id'
        verbose_name_plural = "data id"
        ordering = ['-id']

    def __str__(self):
        return str(self.pk)


class StoreProductVariantStock(BaseModel):
    variant = models.ForeignKey(StoreProductVariantModel, on_delete=models.CASCADE, related_name='variant_stock')
    stock_type = models.SmallIntegerField(default=2, verbose_name='Stock Type')
    current_stock = models.IntegerField(default=0, verbose_name='Current stock')
    reserved_stock = models.IntegerField(default=0, verbose_name='Stock reserved for upcoming promotion')
    stock_location_id = models.CharField(default='', max_length=16, verbose_name='location_id of the stock')

    class Meta:
        db_table = 'store_product_variant_stock'
        verbose_name = 'store_product_variant_stock'
        verbose_name_plural = "store product variant stock"
        ordering = ['-id']


class StoreProductPackageModel(BaseModel):
    """
    产品组合信息表
    """
    name = models.CharField(max_length=100, verbose_name='Package Name')
    sku = models.CharField(max_length=50, verbose_name='Package Sku')
    product_type = models.SmallIntegerField(verbose_name='Package Product Type')
    uid = models.CharField(max_length=50, verbose_name='Product Unique ID', unique=True)

    class Meta:
        db_table = 'store_product_package'
        verbose_name = 'data id'
        verbose_name_plural = "data id"
        ordering = ['-id']

    def __str__(self):
        return self.pk


class StorePackageItemModel(BaseModel):
    """
    组合装产品
    """
    package = models.ForeignKey(StoreProductPackageModel, on_delete=models.CASCADE, related_name='package_item')
    uid = models.SmallIntegerField(verbose_name='Item Product Unique ID')
    product_type = models.SmallIntegerField(verbose_name='Item Product Type')
    sku = models.CharField(max_length=50, verbose_name='Item Sku')

    class Meta:
        db_table = 'store_product_package_item'
        verbose_name = 'data id'
        verbose_name_plural = "data id"
        ordering = ['-id']

    def __str__(self):
        return self.pk


class ShopeeRegionSettingsModel(BaseModel):
    """
    SHOPEE地区信息设置
    """
    area = models.CharField(max_length=50, verbose_name='Country/Region')
    short_area = models.CharField(max_length=50, verbose_name='Short Country/Region')
    currency = models.CharField(max_length=10, verbose_name='Currency')
    exchange_rate = models.FloatField(max_length=50, verbose_name='Exchange Rate')
    activity_rate = models.FloatField(max_length=50, verbose_name='Activity Rate')
    commission_rate = models.FloatField(max_length=50, verbose_name='Commission Rate')
    transaction_rate = models.FloatField(max_length=50, verbose_name='Transaction Rate')
    withdrawal_rate = models.FloatField(max_length=50, verbose_name='Withdrawal Rate')
    exchange_loss_rate = models.FloatField(max_length=50, verbose_name='Exchange Loss Rate')
    buyer_shipping = models.FloatField(max_length=50, verbose_name='Buyer Shipping')
    other_fee = models.FloatField(max_length=50, verbose_name='Other Fee')

    class Meta:
        db_table = 'shopee_fetch_region_settings'
        verbose_name = 'data id'
        verbose_name_plural = "data id"
        ordering = ['-create_time']

    def __str__(self):
        return str(self.pk)


class ShopeeLogisticsCalcModel(BaseModel):
    """
    Shopee国家/地区，物流计算信息表
    """
    region_settings = models.ForeignKey(
        ShopeeRegionSettingsModel, on_delete=models.CASCADE, related_name='region_logistics_calc')
    min_weight = models.FloatField(verbose_name='Min Weight')
    max_weight = models.FloatField(null=True, blank=True, verbose_name='Max Weight')
    # 1： 固定收费 | 2：阶段收费
    calc_type = models.SmallIntegerField(verbose_name='Logistics Calc Type')
    logistics_fee = models.FloatField(verbose_name='Logistics Fee')
    interval = models.FloatField(null=True, blank=True, verbose_name='Weight Interval')

    class Meta:
        db_table = 'shopee_logistics_calc'
        verbose_name = 'data id'
        verbose_name_plural = "data id"
        ordering = ['id']

    def __str__(self):
        return str(self.pk)


class ShopeeStoreRegionSetting(BaseModel):
    class RelativeFields(object):

        SETTING_STORES = 'setting_store'

    store_uid = models.CharField(max_length=64, verbose_name='Store UID')
    region_settings = models.ForeignKey(
        ShopeeRegionSettingsModel, on_delete=models.CASCADE, related_name=RelativeFields.SETTING_STORES)

    class Meta:
        db_table = 'shopee_store_profit_setting'
        verbose_name = 'shopee_store_profit_setting'
        verbose_name_plural = "shopee store profit setting"
        unique_together = ['store_uid', 'region_settings_id']
        ordering = ['id']


class ProductSupplierInfo(BaseModel):
    product = models.ForeignKey(StoreProductModel, verbose_name='Product', on_delete=models.CASCADE,
                                related_name='supplier_info')
    url = models.URLField(null=True, blank=True, max_length=512, verbose_name="Product Supplier Url")
    logistics_costs = models.FloatField(default=0, verbose_name='Logistic costs')
    min_purchase_num = models.PositiveIntegerField(default=1, verbose_name='min_purchase_num')
    delivery_days = models.PositiveIntegerField(default=1, verbose_name='Delivery Days')
    supplier_addr = models.CharField(max_length=50, null=True, blank=True, verbose_name='Supplier City')
    supplier_name = models.CharField(max_length=100, null=True, blank=True,  verbose_name='Company')

    class Meta:
        db_table = 'product_supplier_info'
        verbose_name = 'product_supplier_info'
        verbose_name_plural = "Global Product Supplier"
        ordering = ['-create_time']
