from product.models import GlobalProduct as Product
from django_grpc_framework import proto_serializers
from product.gRpc.server.protos import product_pb2


class ProductSerializer(proto_serializers.ModelProtoSerializer):
    class Meta:
        model = Product
        proto_class = product_pb2.Product
        fields = ['id', 'sku', 'status', 'mode', 'image', 'name', 'desc', 'type', 'second_hand', 'models']