from rest_framework import serializers

from publish.models import ProductCategory, ProductCategoryBrand, ProductCategoryAttribute
from .models import ShopeeCategory, ShopeeAttribute, ShopeeAttributeValue, ShopeeCategoryBrand, \
    ShopeeCategoryTemplate, ShopeeCategoryTemplateAttribute

class ShopeeAttributePostSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShopeeAttribute
        exclude = []
        read_only_fields = ['id', 'create_time', 'update_time']


class ShopeeAttributeGetSerializer(serializers.ModelSerializer):
    attribute_value_list = serializers.SerializerMethodField('get_attribute_value_list')

    def get_attribute_value_list(self, attribute: ShopeeAttribute):
        attribute_values = getattr(attribute, ShopeeAttribute.RelativeFields.ATTRIBUTE_VALUES)
        return ShopeeAttributeValueGetSerializer(attribute_values, many=True).data

    class Meta:
        model = ShopeeAttribute
        exclude = ['openid']
        read_only_fields = ['id', 'create_time', 'update_time']


class ShopeeAttributeValueGetSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShopeeAttributeValue
        exclude = ['openid', 'create_time', 'update_time', 'id']
        read_only_fields = []


class ShopeeAttributeValuePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopeeAttributeValue
        exclude = []
        read_only_fields = ['id', 'create_time', 'update_time']


class ShopeeBrandPostSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShopeeCategoryBrand
        exclude = []
        read_only_fields = ['id', 'create_time', 'update_time']


class ShopeeBrandGetSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShopeeCategoryBrand
        exclude = ['openid', 'create_time', 'update_time', 'is_delete', 'creater', 'id']
        read_only_fields = ['id']


class ShopeeCategoryGetSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShopeeCategory
        exclude = ['openid', 'create_time', 'update_time']
        read_only_fields = ['id']


class ShopeeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopeeCategory
        exclude = []
        read_only_fields = ['id', 'create_time', 'update_time']


class ShopeeCategoryTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopeeCategoryTemplate
        exclude = []
        read_only_fields = ['id', 'create_time', 'update_time']


class ShopeeCategoryTemplateGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopeeCategoryTemplate
        exclude = ['openid', 'create_time', 'update_time']
        read_only_fields = ['id']


class ShopeeCategoryTemplateAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopeeCategoryTemplateAttribute
        exclude = []
        read_only_fields = ['id', 'create_time', 'update_time']


class ShopeeCategoryTemplateAttributeGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopeeCategoryTemplateAttribute
        exclude = ['openid', 'create_time', 'update_time']
        read_only_fields = ['id']


class ProductCategoryPostSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductCategory
        exclude = []
        read_only_fields = ['id', 'create_time', 'update_time']


class ProductCategoryBrandPostSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductCategoryBrand
        exclude = []
        read_only_fields = ['id', 'create_time', 'update_time']


class ProductAttributePostSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductCategoryAttribute
        exclude = []
        read_only_fields = ['id', 'create_time', 'update_time']


class ProductAttributeGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategoryAttribute
        exclude = ['openid', 'create_time', 'update_time']
        read_only_fields = ['id', 'create_time', 'update_time']


class ProductCategoryBrandGetSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductCategoryBrand
        exclude = ['openid', 'creater', 'create_time', 'update_time']
        read_only_fields = ['id']
