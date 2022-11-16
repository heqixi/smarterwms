
from rest_framework import serializers


from .models import ListModel, GoodsTag
from stock.models import StockListModel


class GoodsTagsGetSerialier(serializers.ModelSerializer):
    class Meta:
        model = GoodsTag
        exclude = ['openid', 'is_delete']


class GoodsTagsPostSerialier(serializers.ModelSerializer):
    class Meta:
        model = GoodsTag
        exclude = ['is_delete']
        read_only_fields = ['id', 'create_time', 'update_time', ]


class StockGetSerializer(serializers.ModelSerializer):
    create_time = serializers.DateTimeField(
        read_only=True, format='%Y-%m-%d %H:%M:%S')
    update_time = serializers.DateTimeField(
        read_only=True, format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = StockListModel
        exclude = ['openid']
        read_only_fields = ['id']


# class GoodsAsnListGetSerializer(serializers.ModelSerializer):
#     create_time = serializers.DateTimeField(
#         read_only=True, format='%Y-%m-%d %H:%M:%S')
#     update_time = serializers.DateTimeField(
#         read_only=True, format='%Y-%m-%d %H:%M:%S')
#
#     class Meta:
#         model = AsnListModel
#         exclude = ['openid', 'is_delete', ]
#         read_only_fields = ['id', 'openid', ]


# class GoodsAsnDetailGetSerializer(serializers.ModelSerializer):
#     create_time = serializers.DateTimeField(
#         read_only=True, format='%Y-%m-%d %H:%M:%S')
#     update_time = serializers.DateTimeField(
#         read_only=True, format='%Y-%m-%d %H:%M:%S')
#
#     def get_fields(self):
#         fields = super().get_fields()
#         asn_param = self.context['request'].query_params.get(
#             'asn_details', None)
#         if asn_param:
#             asn = GoodsAsnListGetSerializer()
#             fields['asn'] = asn
#         return fields
#
#     class Meta:
#         model = AsnDetailModel
#         exclude = ['openid', 'is_delete']
#         read_only_fields = ['id', 'openid']


class GoodsGetSerializer(serializers.ModelSerializer):
    stocks = serializers.SerializerMethodField('get_stocks')

    def get_stocks(self, instance):
        stock_param = self.context['request'].query_params.get('goods_stocks', None)
        if stock_param == 'aggregation':
            has_aggregation = not (getattr(instance, 'stock_damage', None) is None or
                                   getattr(instance, 'stock_purchased', None) is None or
                                   getattr(instance, 'stock_sorted', None) is None or
                                   getattr(instance, 'stock_onhand', None) is None or
                                   getattr(instance, 'stock_ship', None) is None
                                   )
            if not has_aggregation:
                # 还没有聚合，需要遍历聚合数据
                stock_damage = 0
                stock_purchased = 0
                stock_sorted = 0
                stock_onhand = 0
                stock_reserve = 0
                stock_ship = 0
                for stock in instance.goods_stock.all():
                    if stock.stock_status == StockListModel.Constants.STATUS_ONHAND:
                        stock_onhand += stock.stock_qty
                    elif stock.stock_status == StockListModel.Constants.STATUS_DAMAGE:
                        stock_damage += stock.stock_qty
                    elif stock.stock_status == StockListModel.Constants.STATUS_PURCHASED:
                        stock_purchased += stock.stock_qty
                    elif stock.stock_status == StockListModel.Constants.STATUS_SORTED:
                        stock_sorted += stock.stock_qty
                    elif stock.stock_status == StockListModel.Constants.STATUS_RESERVE:
                        stock_reserve += stock.stock_qty
                    elif stock.stock_status == StockListModel.Constants.STATUS_SHIP:
                        stock_ship += stock_ship
                return {
                    'stock_damage': stock_damage,
                    'stock_purchased': stock_purchased,
                    'stock_sorted': stock_sorted,
                    'stock_onhand': stock_onhand,
                    'stock_reserve': stock_reserve,
                    'stock_ship': stock_ship
                }
            return {
                'stock_damage': instance.stock_damage,
                'stock_purchased': instance.stock_purchased,
                'stock_sorted': instance.stock_sorted,
                'stock_onhand': instance.stock_onhand,
                'stock_reserve': instance.stock_reserve,
                'stock_ship': instance.stock_ship
            }
        else:
            return StockGetSerializer(source='goods_stock', context={'request': self.context['request']}, many=True,
                                      required=False).data

    def get_fields(self):
        fields = super().get_fields()
        asn_param = self.context['request'].query_params.get('asn_details', None)
        tags_param = self.context['request'].query_params.get('tags', None)
        if asn_param:
            # TODO GOODS_DEPENDENCES
            raise Exception('Improper dependences')
            # asn_details = GoodsAsnDetailGetSerializer(source='goods_asn_detail', many=True, required=False)
            # fields['asn_details'] = asn_details
        if tags_param:
            tags = GoodsTagsGetSerialier(source='goods_tags', many=True, required=False)
            fields['tags'] = tags
        return fields

    class Meta:
        model = ListModel
        exclude = ['openid', 'is_delete', 'create_time', 'update_time']
        read_only_fields = ['id']


class GoodsPostSerializer(serializers.ModelSerializer):

    class Meta:
        model = ListModel
        exclude = ['is_delete', ]
        read_only_fields = ['id', 'create_time', 'update_time', ]

    def create(self, validated_data):
        print("GoodsPostSerializer ,", validated_data)
        return ListModel.objects.create(**validated_data)

