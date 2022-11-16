from rest_framework import serializers
from .models import StockListModel, StockBinModel
from goods.models import ListModel as Goods
from utils import datasolve
# from asn.models import AsnDetailModel


class GoodsGetSerializer(serializers.ModelSerializer):

    create_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
    update_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = Goods
        exclude = ['openid', 'is_delete', ]
        read_only_fields = ['id']

# class StockAasnDetailGetSerializer(serializers.ModelSerializer):
#     create_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
#     update_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
#
#     class Meta:
#         model = AsnDetailModel
#         exclude = ['openid', 'is_delete', ]
#         read_only_fields = ['id', 'openid']


class StockBinGetSerializer(serializers.ModelSerializer):
    bin_name = serializers.CharField(read_only=True, required=False)
    goods_code = serializers.CharField(read_only=True, required=False)
    goods_desc = serializers.CharField(read_only=True, required=False)
    goods_qty = serializers.IntegerField(read_only=True, required=False)
    pick_qty = serializers.IntegerField(read_only=True, required=False)
    picked_qty = serializers.IntegerField(read_only=True, required=False)
    bin_size = serializers.CharField(read_only=True, required=False)
    bin_property = serializers.CharField(read_only=True, required=False)
    qty = serializers.SerializerMethodField()
    t_code = serializers.CharField(read_only=True, required=False)
    create_time = serializers.DateTimeField(
        read_only=True, format='%Y-%m-%d %H:%M:%S')
    update_time = serializers.DateTimeField(
        read_only=True, format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = StockBinModel
        exclude = ['openid', ]
        read_only_fields = ['id', 'create_time', 'update_time', ]

    def get_qty(self, obj):
        return 0


class StockListGetSerializer(serializers.ModelSerializer):
    create_time = serializers.DateTimeField(
        read_only=True, format='%Y-%m-%d %H:%M:%S')
    update_time = serializers.DateTimeField(
        read_only=True, format='%Y-%m-%d %H:%M:%S')
    
    def get_fields(self):
        print("Stock list Get Ser")
        fields = super().get_fields()
        param_goods = self.context['request'].query_params.get('goods', None)
        param_order = self.context['request'].query_params.get('order', None)
        # param_supplier = self.context['request'].query_params.get('supplier', None)
        param_asn = self.context['request'].query_params.get('asn', None)
        param_stockBin = self.context['request'].query_params.get('stockBin', None)
        print("get stock list extra fields ", param_goods)
        if param_goods:
             goods = GoodsGetSerializer(many=False, read_only=True)
             fields['goods'] = goods
        if param_asn:
            raise Exception('Improper Denpendency')
            # asn = StockAasnDetailGetSerializer(source='stock_asn', many=True)
            # fields['asn'] = asn
        if param_stockBin:
            stockBin = StockBinGetSerializer(many=True)
            fields['stock_bin'] = stockBin
        print("Stock list Get Ser fields", fields)
        return fields

    class Meta:
        model = StockListModel
        exclude = ['openid', 'is_delete']
        read_only_fields = ['id']


class StockGetSerializer(serializers.ModelSerializer):

    create_time = serializers.DateTimeField(
        read_only=True, format='%Y-%m-%d %H:%M:%S')
    update_time = serializers.DateTimeField(
        read_only=True, format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = StockListModel
        exclude = ['openid', 'creater']
        read_only_fields = ['id']


class StockListPostSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = StockListModel
        exclude = []
        read_only_fields = ['id','create_time', 'update_time', ]


class StockBinPostSerializer(serializers.ModelSerializer):
    openid = serializers.CharField(read_only=False, required=False, validators=[
                                   datasolve.openid_validate])
    bin_name = serializers.CharField(read_only=True, required=False, validators=[
                                     datasolve.data_validate])
    move_to_bin = serializers.CharField(
        read_only=True, required=False, validators=[datasolve.data_validate])
    move_qty = serializers.CharField(read_only=True, required=False, validators=[
                                     datasolve.data_validate])
    class Meta:
        model = StockBinModel
        exclude = []
        read_only_fields = ['id', 'openid', 'create_time', 'update_time', ]


class FileBinListRenderSerializer(serializers.ModelSerializer):
    bin_name = serializers.CharField(read_only=False, required=False)
    goods_code = serializers.CharField(read_only=False, required=False)
    goods_desc = serializers.CharField(read_only=False, required=False)
    goods_qty = serializers.IntegerField(read_only=False, required=False)
    pick_qty = serializers.IntegerField(read_only=False, required=False)
    picked_qty = serializers.IntegerField(read_only=False, required=False)
    bin_size = serializers.CharField(read_only=False, required=False)
    bin_property = serializers.CharField(read_only=False, required=False)
    create_time = serializers.DateTimeField(
        read_only=True, format='%Y-%m-%d %H:%M:%S')
    update_time = serializers.DateTimeField(
        read_only=True, format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = StockBinModel
        ref_name = 'StockFileBinListRenderSerializer'
        exclude = ['openid', ]


class FileListRenderSerializer(serializers.ModelSerializer):
    goods_code = serializers.CharField(read_only=True, required=False)
    goods_desc = serializers.CharField(read_only=True, required=False)
    goods_qty = serializers.IntegerField(read_only=True, required=False)
    onhand_stock = serializers.IntegerField(read_only=True, required=False)
    can_order_stock = serializers.IntegerField(read_only=True, required=False)
    inspect_stock = serializers.IntegerField(read_only=True, required=False)
    hold_stock = serializers.IntegerField(read_only=True, required=False)
    damage_stock = serializers.IntegerField(read_only=True, required=False)
    asn_stock = serializers.IntegerField(read_only=True, required=False)
    dn_stock = serializers.IntegerField(read_only=True, required=False)
    pre_load_stock = serializers.IntegerField(read_only=True, required=False)
    pre_sort_stock = serializers.IntegerField(read_only=True, required=False)
    sorted_stock = serializers.IntegerField(read_only=True, required=False)
    pick_stock = serializers.IntegerField(read_only=True, required=False)
    picked_stock = serializers.IntegerField(read_only=True, required=False)
    back_order_stock = serializers.IntegerField(read_only=True, required=False)
    create_time = serializers.DateTimeField(
        read_only=True, format='%Y-%m-%d %H:%M:%S')
    update_time = serializers.DateTimeField(
        read_only=True, format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = StockListModel
        ref_name = 'StockFileListRenderSerializer'
        exclude = ['openid', ]
