from rest_framework import serializers
from asn.models import AsnListModel
from .asndetails import ASNDetailGetSerializer
from utils import datasolve
from supplier.serializers import SupplierGetSerializer
from asn.serializers.asnorder import AsnOrderSerializer


class ASNListGetSerializer(serializers.ModelSerializer):
    def get_fields(self):
        fields = super().get_fields()
        is_details = self.context['request'].query_params.get('asn_details', None)
        is_supplier = self.context['request'].query_params.get('asn_supplier', None)
        is_asn_order = self.context['request'].query_params.get('asn_order', None)
        if is_asn_order:
            asn_order = AsnOrderSerializer(source='asn_order', many=True, required=False)
            fields['order'] = asn_order
        if is_details:
            details = ASNDetailGetSerializer(source='asn_details', many=True, required=False)
            fields['details'] = details
        if is_supplier:
            supplier = SupplierGetSerializer(required=False)
            fields['supplier'] = supplier
        return fields

    class Meta:
        model = AsnListModel
        exclude = ['openid', 'is_delete', 'create_time', 'update_time']
        read_only_fields = ['id']


class ASNListPostSerializer(serializers.ModelSerializer):

    class Meta:
        model = AsnListModel
        exclude = ['is_delete', ]
        read_only_fields = ['id', 'create_time', 'update_time', ]


class ASNListUpdateSerializer(serializers.ModelSerializer):
    asn_code = serializers.CharField(read_only=False,  required=True, validators=[datasolve.asn_data_validate])

    class Meta:
        model = AsnListModel
        exclude = ['is_delete', ]
        read_only_fields = ['id', 'create_time', 'update_time', ]


class ASNListPartialUpdateSerializer(serializers.ModelSerializer):
    asn_code = serializers.CharField(read_only=False,  required=True, validators=[datasolve.asn_data_validate])

    class Meta:
        model = AsnListModel
        exclude = ['is_delete', ]
        read_only_fields = ['id', 'create_time', 'update_time', ]


class FileListRenderSerializer(serializers.ModelSerializer):
    asn_code = serializers.CharField(read_only=False, required=False)
    asn_status = serializers.IntegerField(read_only=False, required=False)
    total_weight = serializers.FloatField(read_only=False, required=False)
    total_volume = serializers.FloatField(read_only=False, required=False)
    total_cost = serializers.FloatField(read_only=False, required=False)
    supplier = serializers.CharField(read_only=False, required=False)
    creater = serializers.CharField(read_only=False, required=False)
    transportation_fee = serializers.JSONField(read_only=False, required=False)
    create_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
    update_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = AsnListModel
        ref_name = 'ASNFileListRenderSerializer'
        exclude = ['openid', 'is_delete', ]