from django.db import models

from base.models import BaseModel


class ListModel(BaseModel):
    parents_class_id = models.CharField(max_length=256, default="", null=True, blank=True, verbose_name="Goods Parents Class IDS")
    goods_class = models.CharField(max_length=32, verbose_name="Goods Class")

    class Meta:
        db_table = 'goodsclass'
        verbose_name = 'data id'
        verbose_name_plural = "data id"
        ordering = ['goods_class']

    def __str__(self):
        return str(self.pk)


class ShopeeCategory(BaseModel):
    class RelativeFields(object):
        SUB_CATEGORY = "SUB_CATEGORY"

        ATTRIBUTES = 'attributes'

    merchant_id = models.CharField(max_length=64, verbose_name="Shopee Category merchant id")

    category_id = models.IntegerField(default=0, verbose_name="Shopee Category ID")

    original_category_name = models.CharField(max_length=256, verbose_name="Shopee Category Original Display Name")

    display_category_name = models.CharField(max_length=256, verbose_name="Shopee Category Display Name")

    parent = models.ForeignKey('self', on_delete=models.CASCADE, default=None, null=True, related_name=RelativeFields.SUB_CATEGORY)

    has_children = models.BooleanField(default=False, verbose_name="Has Children")

    class Meta:
        db_table = 'shopeecategory'
        verbose_name = 'shopee_category'
        verbose_name_plural = "Shopee Category"
        unique_together = ['openid', 'merchant_id', 'category_id']
        ordering = ['-create_time']

    def __str__(self):
        return str(self.pk)


class ShopeeAttribute(BaseModel):
    class RelativeFields(object):

        ATTRIBUTE_VALUES = 'attribute_values'

    INT_TYPE = 'INT_TYPE'
    STRING_TYPE = 'STRING_TYPE'
    ENUM_TYPE = 'ENUM_TYPE'
    FLOAT_TYPE = 'FLOAT_TYPE'
    DATE_TYPE = 'DATE_TYPE'
    TIMESTAMP_TYPE = 'TIMESTAMP_TYPE'
    NO_VALIDATE_TYPE = 'NO_VALIDATE_TYPE'

    VALIDATE_TYPES = [
        (INT_TYPE, 'int_type'),
        (STRING_TYPE, 'string_type'),
        (ENUM_TYPE, 'enum_type'),
        (FLOAT_TYPE, 'float_type'),
        (DATE_TYPE, 'date_type'),
        (TIMESTAMP_TYPE, 'timestamp_type'),
        (NO_VALIDATE_TYPE, 'no_validate_type')
    ]

    FORMAT_TYPE_NORMAL = 'NORMAL'

    FORMAT_TYPE_QUANTITATIVE = 'QUANTITATIVE'

    FORMAT_TYPE_CHOICES = [
        (FORMAT_TYPE_NORMAL, 'normal'),
        (FORMAT_TYPE_QUANTITATIVE, 'quantitative')
    ]

    YEAR_MONTH_DATE = 'YEAR_MONTH_DATE'

    YEAR_MONTH = 'YEAR_MONTH'

    DATE_FORMAT_TYPE_CHOICES = [
        (YEAR_MONTH_DATE, 'year_month_date'),
        (YEAR_MONTH, 'year_month')
    ]

    DROP_DOWN = 'DROP_DOWN'

    MULTIPLE_SELECT = 'MULTIPLE_SELECT'

    TEXT_FILED = 'TEXT_FILED'

    COMBO_BOX = 'COMBO_BOX'

    MULTIPLE_SELECT_COMBO_BOX = 'MULTIPLE_SELECT_COMBO_BOX'

    INPUT_TYPE_CHOICES = [
        (DROP_DOWN, 'drop_down'),
        (MULTIPLE_SELECT, 'multiple_select'),
        (TEXT_FILED, 'text_filed'),
        (COMBO_BOX, 'combo_box'),
        (MULTIPLE_SELECT_COMBO_BOX, 'multiple_select_combo_box')
    ]

    category_id = models.IntegerField(default=0, verbose_name="Shopee Category ID")

    attribute_id = models.CharField(max_length=64, verbose_name="Shopee Attribute id")

    original_attribute_name = models.CharField(max_length=256, verbose_name="Shopee Attribute Name")

    display_attribute_name = models.CharField(max_length=256, verbose_name="Shopee Attribute Display Name")

    is_mandatory = models.BooleanField(default=False, verbose_name="Is mandatory")

    input_validation_type = models.CharField(max_length=32, default=STRING_TYPE, choices=VALIDATE_TYPES, verbose_name="Shopee Attribute input validate type")

    format_type = models.CharField(max_length=16, default=FORMAT_TYPE_NORMAL, choices=FORMAT_TYPE_CHOICES)

    date_format_type = models.CharField(max_length=32, default=YEAR_MONTH_DATE, choices=DATE_FORMAT_TYPE_CHOICES)

    input_type = models.CharField(max_length=32, default=DROP_DOWN, choices=INPUT_TYPE_CHOICES)

    attribute_unit = models.JSONField(max_length=64, default=[], verbose_name='attribute unit')

    class Meta:
        db_table = 'shopee_attribute'
        verbose_name = 'shopee_attribute'
        verbose_name_plural = "Shopee attribute"
        unique_together = ['openid', 'category_id', 'attribute_id']
        ordering = ['-create_time']

    def __str__(self):
        return str(self.pk)


class ShopeeAttributeValue(BaseModel):

    attribute = models.ForeignKey(ShopeeAttribute, on_delete=models.CASCADE,
                                  verbose_name="Shopee Attribute Value", related_name=ShopeeAttribute.RelativeFields.ATTRIBUTE_VALUES)

    value_id = models.IntegerField(verbose_name="Shopee Attribute Value Id")

    original_value_name = models.CharField(max_length=64, verbose_name="Shopee Attribute Value Name")

    display_value_name = models.CharField(max_length=128, verbose_name="Shopee Attribute Display Name")

    value_unit = models.CharField(max_length=64, default=None, blank=True, null=True, verbose_name="Shopee Attribute Unit")

    parent_attribute_list = models.JSONField(max_length=256, default=[], verbose_name="Parent Attribute List([parent_attribute_id, parent_value_id])")

    parent_brand_list = models.JSONField(max_length=256, default=[], verbose_name="Parent Brand List([parent_brand_id])")

    mandatory_region = models.JSONField(max_length=128, default=[], verbose_name="Mandatory Region")

    max_input_value_number = models.SmallIntegerField(default=1)

    class Meta:
        db_table = 'shopee_attribute_value'
        verbose_name = 'shopee_attribute_value'
        verbose_name_plural = "Shopee Attribute Value"
        unique_together = ['openid', 'attribute_id', 'value_id']
        ordering = ['-create_time']

    def __str__(self):
        return str(self.pk)


class ShopeeCategoryBrand(BaseModel):

    DROP_DOWN = 'DROP_DOWN'

    MULTIPLE_SELECT = 'MULTIPLE_SELECT'

    TEXT_FILED = 'TEXT_FILED'

    COMBO_BOX = 'COMBO_BOX'

    MULTIPLE_SELECT_COMBO_BOX = 'MULTIPLE_SELECT_COMBO_BOX'

    INPUT_TYPE_CHOICES = [
        (DROP_DOWN, 'drop_down'),
        (MULTIPLE_SELECT, 'multiple_select'),
        (TEXT_FILED, 'text_filed'),
        (COMBO_BOX, 'combo_box'),
        (MULTIPLE_SELECT_COMBO_BOX, 'multiple_select_combo_box')
    ]

    merchant_id = models.CharField(max_length=64, verbose_name="Shopee Category merchant id")

    category_id = models.IntegerField(default=0, verbose_name="Shopee Category ID")

    brand_id = models.IntegerField(default=0, verbose_name="Shopee Brand ID")

    original_brand_name = models.CharField(max_length=64, verbose_name="Shopee Brand Name")

    display_brand_name = models.CharField(max_length=64, verbose_name="Shopee Brand Display Name")

    is_mandatory = models.BooleanField(default=False, verbose_name="Is mandatory")

    input_type = models.CharField(max_length=32, default=DROP_DOWN, choices=INPUT_TYPE_CHOICES)

    class Meta:
        db_table = 'shopee_category_brand'
        verbose_name = 'shopee_category_brand'
        verbose_name_plural = "Shopee Category Brand"
        unique_together = ['openid', 'merchant_id', 'category_id', 'brand_id']
        ordering = ['-create_time']


class ShopeeCategoryTemplate(BaseModel):
    class RelativeFields(object):

        ATTRIBUTES = "attributes"

    merchant_id = models.CharField(max_length=64, verbose_name="Shopee Category merchant id")

    category_id = models.IntegerField(default=0, verbose_name="Shopee Category ID")

    brand_id = models.IntegerField(default=0, verbose_name="Brand ID")

    display_brand_name = models.CharField(max_length=64, verbose_name="Brand Name")

    template_name = models.CharField(max_length=64, verbose_name="Shopee Category templaate name")

    class Meta:
        db_table = 'shopee_category_template'
        verbose_name = 'shopee_category_template'
        verbose_name_plural = "Shopee Category Template"
        unique_together = ['merchant_id', 'template_name']
        ordering = ['-create_time']


class ShopeeCategoryTemplateAttribute(BaseModel):

    category = models.ForeignKey(ShopeeCategoryTemplate, on_delete=models.CASCADE, related_name=ShopeeCategoryTemplate.RelativeFields.ATTRIBUTES)

    attribute_id = models.CharField(max_length=64, verbose_name="Category Attribute id")

    display_value_name = models.CharField(max_length=32, verbose_name="Category Attribute value")

    value_id = models.IntegerField(default=-1, verbose_name="Attribute Value Id")

    multiple = models.BooleanField(default=False, verbose_name="Is Multiple")

    class Meta:
        db_table = 'shopee_category_template_attribute'
        verbose_name = 'shopee_category_template_attribute'
        verbose_name_plural = "Shopee Category Template Attribute"
        ordering = ['-create_time']