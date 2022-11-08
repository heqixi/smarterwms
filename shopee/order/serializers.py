
from rest_framework import serializers
from order.models import ShopeeOrderModel, ShopeeOrderDetailModel, ShopeeOrderModifyModel, ShopeeOrderRecordModel


class OrderListGetSerializer(serializers.ModelSerializer):

    order_sn = serializers.CharField(read_only=True, required=False)
    order_status = serializers.CharField(read_only=True, required=False)
    total_amount = serializers.FloatField(read_only=True, required=False)
    waybill_path = serializers.CharField(read_only=True, required=False)
    pay_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
    days_to_ship = serializers.IntegerField(read_only=True, required=False)
    ship_by_date = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
    buyer_user_id = serializers.CharField(read_only=True, required=False)
    buyer_username = serializers.CharField(read_only=True, required=False)
    create_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
    update_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = ShopeeOrderModel
        exclude = []
        read_only_fields = ['id']


class ShopeeOrderDetailGetSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShopeeOrderDetailModel
        exclude = []
        read_only_fields = ['id']


class ShopeeOrderRecordGetSerializer(serializers.ModelSerializer):

    create_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = ShopeeOrderRecordModel
        exclude = ['creater', 'openid', 'shopee_order', 'data']
        read_only_fields = ['batch_number', 'type', 'create_time']
