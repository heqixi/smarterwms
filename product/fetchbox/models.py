from django.db import models

# Create your models here.
from base.models import BaseModel


class FetchProductModel(BaseModel):
    """
    采集商品数据
    """
    name = models.CharField(max_length=100, verbose_name='Fetch Product Name')
    url = models.CharField(max_length=500, verbose_name='Fetch Url')
    price = models.FloatField(verbose_name='Price')
    company = models.CharField(null=True, blank=True, max_length=100, verbose_name='Company')
    logistics_city = models.CharField(max_length=50, verbose_name='Logistics City')
    mix_purchase_qty = models.IntegerField(verbose_name='Minimum purchase quantity')
    logistics_costs = models.FloatField(verbose_name='Logistics Costs')
    weight = models.FloatField(null=True, blank=True, verbose_name='Weight')
    length = models.SmallIntegerField(null=True, blank=True, verbose_name='Length')
    width = models.SmallIntegerField(null=True, blank=True, verbose_name='Width')
    height = models.SmallIntegerField(null=True, blank=True, verbose_name='Height')
    description = models.JSONField(verbose_name='Description')
    status = models.SmallIntegerField(null=True, blank=True, verbose_name='status')

    class Meta:
        db_table = 'fetch_product'
        verbose_name = 'data id'
        verbose_name_plural = "data id"
        ordering = ['-create_time']

    def __str__(self):
        return str(self.pk)


class FetchOptionModel(BaseModel):
    product = models.ForeignKey(FetchProductModel, on_delete=models.CASCADE, related_name='fetch_product_options')
    name = models.CharField(max_length=100, verbose_name='Option Name')
    index = models.SmallIntegerField(verbose_name='Option Index')

    class Meta:
        db_table = 'fetch_option'
        verbose_name = 'data id'
        verbose_name_plural = "data id"
        ordering = ['-create_time']

    def __str__(self):
        return str(self.pk)


class FetchOptionItemModel(BaseModel):
    product = models.ForeignKey(FetchProductModel, on_delete=models.CASCADE, related_name='fetch_product_option_items')
    option = models.ForeignKey(FetchOptionModel, on_delete=models.CASCADE, related_name='fetch_option_items')
    name = models.CharField(max_length=100, verbose_name='Option Item Name')
    image = models.CharField(max_length=500, null=True, blank=True, verbose_name='Option Item Image Url')
    index = models.SmallIntegerField(default=0, verbose_name='Option Item Index')

    class Meta:
        db_table = 'fetch_option_item'
        verbose_name = 'data id'
        verbose_name_plural = "data id"
        ordering = ['-create_time']

    def __str__(self):
        return str(self.pk)


class FetchVariantModel(BaseModel):
    product = models.ForeignKey(FetchProductModel, on_delete=models.CASCADE, related_name='fetch_product_variants')
    item_index = models.CharField(max_length=10, verbose_name='Option item index')
    name = models.CharField(max_length=100, verbose_name='Variant Name')
    price = models.FloatField(verbose_name='Variant Price')
    stock_qty = models.IntegerField(verbose_name='Variant Stock Qty')

    class Meta:
        db_table = 'fetch_variant'
        verbose_name = 'data id'
        verbose_name_plural = "data id"
        ordering = ['-create_time']

    def __str__(self):
        return str(self.pk)


class FetchMediaModel(BaseModel):
    product = models.ForeignKey(FetchProductModel, on_delete=models.CASCADE, related_name='fetch_product_medias')
    type = models.SmallIntegerField(verbose_name='Media Type')
    url = models.CharField(max_length=500, verbose_name='Media Url')
    is_main = models.SmallIntegerField(verbose_name='Is Main Media')

    class Meta:
        db_table = 'fetch_media'
        verbose_name = 'data id'
        verbose_name_plural = "data id"
        ordering = ['-create_time']

    def __str__(self):
        return str(self.pk)


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


