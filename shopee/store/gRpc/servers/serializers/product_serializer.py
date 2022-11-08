
from django_grpc_framework import proto_serializers

from store.models import StoreProductModel
from store.gRpc.servers.protos.products import shopee_pb2


class ProductSerializer(proto_serializers.ModelProtoSerializer):

    class Meta:
        model = StoreProductModel
        proto_class = shopee_pb2.Product
        fields = ['id', 'store', 'product_id', 'product_name']