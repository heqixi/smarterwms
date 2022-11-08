
from django_grpc_framework import generics
from django.db.models import Q

from product.gRpc.server.serializers.product import ProductSerializer
from product.gRpc.server.types.request import ProductCreateSerializer, ProductRetrieveSerializer
from product.models import GlobalProduct as Product
from productpublish.models import ProductPublish
from product.gRpc.server.types.response import MissingParametersError, IllegalParameterError, \
    ProductNotFoundError, Success, UnknowError, ErrorBuilder

from product.gRpc.server.protos import product_pb2


class ProductService(generics.ModelService):
    """
    gRPC service that allows users to be retrieved or updated.
    """
    print('GoodsService in')
    queryset = Product.objects.all().order_by('-id')
    serializer_class = ProductSerializer

    def Update(self, request, context):
        product_id = request.id
        if product_id is None:
            return MissingParametersError('Missing parameter product id')
        instance = Product.objects.filter(id=product_id).first()
        if not instance:
            return ProductNotFoundError('Product of id %s not found' % product_id)
        serializer = self.get_serializer(instance, message=request, partial=True)
        if not serializer.is_valid(raise_exception=False):
            return IllegalParameterError(serializer.errors)
        try:
            self.perform_update(serializer)
        except Exception as exc:
            return UnicodeError(str(exc))
        else:
            return Success(instance).to_message()

    def Query(self, request, context):
        sku = request.sku
        publish_id = request.publish_id
        queryset = Product.objects.none()
        product_ids = []
        if publish_id and len(publish_id) > 0:
            relations = ProductPublish.objects.filter(publish_id=publish_id).all()
            for relation in relations:
                product_ids.append(relation.product.id)
        queryset = Product.objects.filter(Q(id__in=product_ids)).all()
        if sku and len(sku) > 0:
            queryset |= Product.objects.filter(Q(sku=sku) | Q(id__in=product_ids)).all()
        serializer = self.get_serializer(queryset, many=True)
        for message in serializer.message:
            yield message

    def Create(self, request, context):
        verifier = ProductCreateSerializer(request)
        if not verifier.is_valid():
            return ErrorBuilder(verifier.code, verifier.msg).to_message()
        success = verifier.save()
        if not success:
            return ErrorBuilder(code=verifier.code, msg=verifier.msg).to_message()
        product_details = verifier.encode()
        return product_pb2.ProductResponse(code=0, product=product_details.product, extra=product_details.extra)

    def Retrieve(self, request, context):
        serializer = ProductRetrieveSerializer(request)
        if not serializer.is_valid():
            return ErrorBuilder(code=serializer.code(), msg=serializer.msg()).to_message()

        success = serializer.save()
        if not success:
            return ErrorBuilder(code=serializer.code(), msg=serializer.msg()).to_message()
        return serializer.encode()

    def AddModel(self, request, context):
        raise NotImplementedError('Not Implement')
        # model_list = request.models
        # for model in model_list:
        #     if model.id:
        #         product = Product.objects.filter(id=model.id, is_delete=False).first()
        #         if not product:
        #             return ProductNotFoundError('Model of id %s not found' % model.id)

    def RemoveModel(self, request, context):
        raise NotImplementedError('Not Implement')













