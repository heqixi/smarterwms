from rest_framework import serializers

from asn.models import AsnOrder 


class AsnOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = AsnOrder
        exclude = ['is_delete', 'openid', 'creater']
        read_only_fields = ['id', 'openid']


class AsnOrderPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = AsnOrder
        exclude = ['is_delete', ]
        read_only_fields = ['id', 'create_time', 'update_time', ]
