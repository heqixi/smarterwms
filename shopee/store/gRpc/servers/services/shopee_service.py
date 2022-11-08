import logging

from django_grpc_framework import generics

from store.models import StoreProductModel as Products
from store.gRpc.servers.serializers.product_serializer import ProductSerializer

from store.gRpc.servers.protos.products import shopee_pb2

logger = logging.getLogger('ProductService')


class ProductService(generics.ModelService):
    queryset = Products.objects.all().order_by('-id')
    serializer_class = ProductSerializer

    def Query(self, request, context):
        publish_id = request.product_id
        if not isinstance(publish_id, str):
            return -1
        model_publish = ShopeeStorePublish.objects.filter(publish_id=publish_id).first()
        if not model_publish:
            logger.error('Can not find store publish %s ', publish_id)
            return -1
        global_product = model_publish.product
        return shopee_pb2.Product(id=global_product.id, product_name=global_product.name)

