from stock.models import StockBinModel
from django_grpc_framework import proto_serializers
from ..protos import stock_bin_gen_pb2


class StockBinSerializer(proto_serializers.ModelProtoSerializer):
    class Meta:
        model = StockBinModel
        proto_class = stock_bin_gen_pb2.StockBinModel
        fields = ['id', 'bin_name']