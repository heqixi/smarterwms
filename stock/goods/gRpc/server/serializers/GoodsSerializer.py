from goods.models import ListModel as Goods
from django_grpc_framework import proto_serializers
from goods.gRpc.server.protos import goods_pb2


class GoodsSerializer(proto_serializers.ModelProtoSerializer):
    class Meta:
        model = Goods
        proto_class = goods_pb2.Goods
        fields = ['id', 'goods_code', 'goods_image', 'goods_name', 'goods_weight', 'goods_w', 'goods_d',
                  'goods_h', 'goods_unit', 'goods_class', 'goods_brand', 'goods_color', 'bar_code']