from stock.models import StockListModel
from django_grpc_framework import proto_serializers
from ..protos.stock import stock_pb2


class StockSerializer(proto_serializers.ModelProtoSerializer):
    class Meta:
        model = StockListModel
        proto_class = stock_pb2.Stock
        fields = ['id', 'goods', 'stock_qty', 'stock_status']