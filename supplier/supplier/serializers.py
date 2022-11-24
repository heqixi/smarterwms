from rest_framework import serializers
from .models import ListModel, PurchasePlan
from utils import datasolve

import logging

logger = logging.getLogger()


class SupplierGetSerializer(serializers.ModelSerializer):
    create_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
    update_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')

    def get_fields(self):
        fields = super().get_fields()
        purchases = self.context['request'].query_params.get('supplier_purchases', None)
        if purchases:
            supplier_purchases = PurchasePlanGetSerializer(source=ListModel.RelativeFields.SUPPLIER_PURCHASES_UNDELETE, many=True, required=False)
            fields['supplier_purchases'] = supplier_purchases
        return fields

    class Meta:
        model = ListModel
        exclude = ['openid', 'is_delete']
        read_only_fields = ['id', 'openid', 'create_time', 'update_time', ]


class PurchasePlanGetSerializer(serializers.ModelSerializer):

    def get_goods_settings(self, purchase: PurchasePlan):
        res = []
        for goods_settings in purchase.goods_settings.all():
            res.append({
                "id": goods_settings.id,
                "goods": goods_settings.goods,
                "level": goods_settings.level
            })
        return res

    def get_fields(self):
        fields = super().get_fields()
        supplier_param = self.context['request'].query_params.get('supplier', None)
        goods_settings = self.context['request'].query_params.get('goods_settings', None)
        if supplier_param:
            supplier = SupplierGetSerializer(required=False)
            fields['supplier'] = supplier
        if goods_settings:
            fields['goods_settings'] = serializers.SerializerMethodField('get_goods_settings')
        return fields

    class Meta:
        model = PurchasePlan
        exclude = ['openid', 'create_time', 'update_time']
        read_only_fields = ['id', 'openid']


class PurchasePlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchasePlan
        exclude = ['openid']
        read_only_fields = ['id', 'openid', 'create_time', 'update_time']


class PurchasePlanPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchasePlan
        exclude = ['is_delete', ]
        read_only_fields = ['create_time', 'update_time']


class SupplierPostSerializer(serializers.ModelSerializer):
    # openid = serializers.CharField(read_only=False, required=False, validators=[datasolve.openid_validate])
    # supplier_name = serializers.CharField(read_only=False, required=True, validators=[datasolve.data_validate])
    # supplier_city = serializers.CharField(read_only=False, required=True, validators=[datasolve.data_validate])
    # supplier_address = serializers.CharField(read_only=False, required=True, validators=[datasolve.data_validate])
    # supplier_contact = serializers.CharField(read_only=False, required=True, validators=[datasolve.data_validate])
    # supplier_manager = serializers.CharField(read_only=False, required=True, validators=[datasolve.data_validate])
    # supplier_level = serializers.IntegerField(read_only=False, required=True, validators=[datasolve.data_validate])
    # creater = serializers.CharField(read_only=False, required=True, validators=[datasolve.data_validate])

    class Meta:
        model = ListModel
        exclude = ['is_delete', ]
        read_only_fields = ['id', 'create_time', 'update_time', ]


class SupplierUpdateSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(read_only=False, required=True, validators=[datasolve.data_validate])
    supplier_city = serializers.CharField(read_only=False, required=True, validators=[datasolve.data_validate])
    supplier_address = serializers.CharField(read_only=False, required=True, validators=[datasolve.data_validate])
    supplier_contact = serializers.CharField(read_only=False, required=True, validators=[datasolve.data_validate])
    supplier_manager = serializers.CharField(read_only=False, required=True, validators=[datasolve.data_validate])
    supplier_level = serializers.IntegerField(read_only=False, required=True, validators=[datasolve.data_validate])
    creater = serializers.CharField(read_only=False, required=True, validators=[datasolve.data_validate])
    class Meta:
        model = ListModel
        exclude = ['openid', 'is_delete', ]
        read_only_fields = ['id', 'create_time', 'update_time', ]


class SupplierPartialUpdateSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(read_only=False, required=False, validators=[datasolve.data_validate])
    supplier_city = serializers.CharField(read_only=False, required=False, validators=[datasolve.data_validate])
    supplier_address = serializers.CharField(read_only=False, required=False, validators=[datasolve.data_validate])
    supplier_contact = serializers.CharField(read_only=False, required=False, validators=[datasolve.data_validate])
    supplier_manager = serializers.CharField(read_only=False, required=False, validators=[datasolve.data_validate])
    supplier_level = serializers.IntegerField(read_only=False, required=False, validators=[datasolve.data_validate])
    creater = serializers.CharField(read_only=False, required=False, validators=[datasolve.data_validate])
    class Meta:
        model = ListModel
        exclude = ['openid', 'is_delete', ]
        read_only_fields = ['id', 'create_time', 'update_time', ]


class FileRenderSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(read_only=False, required=False)
    supplier_city = serializers.CharField(read_only=False, required=False)
    supplier_address = serializers.CharField(read_only=False, required=False)
    supplier_contact = serializers.CharField(read_only=False, required=False)
    supplier_manager = serializers.CharField(read_only=False, required=False)
    supplier_level = serializers.IntegerField(read_only=False, required=False)
    creater = serializers.CharField(read_only=False, required=False)
    create_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
    update_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = ListModel
        ref_name = 'SupplierFileRenderSerializer'
        exclude = ['openid', 'is_delete', ]
