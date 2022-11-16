from rest_framework import serializers
from .models import ListModel
from utils import datasolve


class GoodsclassGetSerializer(serializers.ModelSerializer):
    parents_class_id = serializers.CharField(read_only=True, required=False)
    goods_class = serializers.CharField(read_only=True, required=False)
    creater = serializers.CharField(read_only=True, required=False)
    create_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
    update_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
    class Meta:
        model = ListModel
        exclude = ['openid', 'is_delete', ]
        read_only_fields = ['id', ]


class GoodsclassPostSerializer(serializers.ModelSerializer):
    parents_class_id = serializers.CharField(read_only=False, required=False, validators=[datasolve.data_validate])
    openid = serializers.CharField(read_only=False, required=False, validators=[datasolve.openid_validate])
    goods_class = serializers.CharField(read_only=False,  required=True, validators=[datasolve.data_validate])
    creater = serializers.CharField(read_only=False, required=True, validators=[datasolve.data_validate])
    class Meta:
        model = ListModel
        exclude = ['is_delete', ]
        read_only_fields = ['id', 'create_time', 'update_time', ]


class GoodsclassUpdateSerializer(serializers.ModelSerializer):
    parents_class_id = serializers.CharField(read_only=False, required=False, validators=[datasolve.data_validate])
    goods_class = serializers.CharField(read_only=False, required=True, validators=[datasolve.data_validate])
    creater = serializers.CharField(read_only=False, required=True, validators=[datasolve.data_validate])
    class Meta:
        model = ListModel
        exclude = ['openid', 'is_delete', ]
        read_only_fields = ['id', 'create_time', 'update_time', ]


class GoodsclassPartialUpdateSerializer(serializers.ModelSerializer):
    parents_class_id = serializers.CharField(read_only=False, required=False, validators=[datasolve.data_validate])
    goods_class = serializers.CharField(read_only=False, required=False, validators=[datasolve.data_validate])
    creater = serializers.CharField(read_only=False, required=False, validators=[datasolve.data_validate])
    class Meta:
        model = ListModel
        exclude = ['openid', 'is_delete', 'create_time', 'update_time']
        read_only_fields = ['id']


# class ShopeeAttributePostSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = ShopeeAttribute
#         exclude = []
#         read_only_fields = ['id', 'create_time', 'update_time']
#
#
# class ShopeeAttributeGetSerializer(serializers.ModelSerializer):
#     attribute_value_list = serializers.SerializerMethodField('get_attribute_value_list')
#
#     def get_attribute_value_list(self, attribute: ShopeeAttribute):
#         attribute_values = getattr(attribute, ShopeeAttribute.RelativeFields.ATTRIBUTE_VALUES)
#         return ShopeeAttributeValueGetSerializer(attribute_values, many=True).data
#
#     class Meta:
#         model = ShopeeAttribute
#         exclude = ['openid']
#         read_only_fields = ['id', 'create_time', 'update_time']
#
#
# class ShopeeAttributeValueGetSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = ShopeeAttributeValue
#         exclude = ['openid', 'create_time', 'update_time', 'id']
#         read_only_fields = []
#
#
# class ShopeeAttributeValuePostSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ShopeeAttributeValue
#         exclude = []
#         read_only_fields = ['id', 'create_time', 'update_time']
#
#
# class ShopeeBrandPostSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = ShopeeCategoryBrand
#         exclude = []
#         read_only_fields = ['id', 'create_time', 'update_time']
#
#
# class ShopeeBrandGetSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = ShopeeCategoryBrand
#         exclude = ['openid', 'create_time', 'update_time', 'is_delete', 'creater', 'id']
#         read_only_fields = ['id']
#
#
# class ShopeeCategoryGetSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = ShopeeCategory
#         exclude = ['openid', 'create_time', 'update_time']
#         read_only_fields = ['id']
#
#
# class ShopeeCategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ShopeeCategory
#         exclude = []
#         read_only_fields = ['id', 'create_time', 'update_time']
#
#
# class ShopeeCategoryTemplateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ShopeeCategoryTemplate
#         exclude = []
#         read_only_fields = ['id', 'create_time', 'update_time']
#
#
# class ShopeeCategoryTemplateGetSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ShopeeCategoryTemplate
#         exclude = ['openid', 'create_time', 'update_time']
#         read_only_fields = ['id']
#
#
# class ShopeeCategoryTemplateAttributeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ShopeeCategoryTemplateAttribute
#         exclude = []
#         read_only_fields = ['id', 'create_time', 'update_time']
#
#
# class ShopeeCategoryTemplateAttributeGetSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ShopeeCategoryTemplateAttribute
#         exclude = ['openid', 'create_time', 'update_time']
#         read_only_fields = ['id']
