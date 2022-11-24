
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

    def get_group(self, goods: ListModel):
        groups = goods.goods_group.all()
        return [
            {
                'id': group.id,
                'name': group.name,
                'goods': [
                    {
                        'id': group_goods.id,
                        'goods_code': group_goods.goods_code,
                        'goods_image': group_goods.goods_image,
                        'goods_name': group_goods.goods_name
                    }
                    for group_goods in group.goods.all()
                ]
            } for group in groups]

    def get_fields(self):
        fields = super().get_fields()
        tags_param = self.context['request'].query_params.get('tags', None)
        group_param = self.context['request'].query_params.get('group', None)
        if tags_param:
            tags = GoodsTagsGetSerialier(source='goods_tags', many=True, required=False)
            fields['tags'] = tags
        if group_param:
            fields['group'] = serializers.SerializerMethodField('get_group')
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

