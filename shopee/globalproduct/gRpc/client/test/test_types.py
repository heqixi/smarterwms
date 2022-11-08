import unittest

from store.gRpc.client.types.global_product import Product, ProductOption, ProductStatus, ProductExtra, \
    ProductDetails
from store.gRpc.client.global_product import ProductServiceClient as Client
from store.gRpc.client.types.global_product import QueryRequest

from store.gRpc.client.types.global_product import Specification
from store.models import StoreProductModel
from store.serializers import StoreGlobalProductEmitDataSerializer


class TestClient(unittest.TestCase):

    def test_product_query(self):
        products = Client.get_instance().query_by_sku(QueryRequest(sku='儿童手表', publish_id='2'))
        # print(len(products))
        count = 0
        for product in products:
            count += 1
            print(product)
        print(count)

    def test_query_by_publish_id(self):
        products = Client.get_instance().query(QueryRequest(publish_id='123'))
        count = 0
        for product in products:
            count += 1
            print(product)
        print(count)

    def test_specification(self):
        spec = Specification(id=1, product_id=2, name='test_1', index=1)
        spec.is_valid(True)
        print(spec.to_message())

        spec = Specification(id=1)
        spec.is_valid(True)
        print(spec.to_message())

        spec = Specification(product_id=2, name='test')
        spec.is_valid(True)
        print(spec.to_message())

    def test_option(self):
        spec = Specification(id=1, product_id=2, name='test_1', index=1)
        option = ProductOption(id=1, specification=spec)
        option.is_valid(True)

        spec = Specification(product_id=2)
        option.specification = spec
        option.id = None
        option.is_valid(True)

    def test_product(self):
        product = Product(id=1, sku='test', status=ProductStatus.PUBLISH, image='test')
        product.is_valid(True)

        product.id = None
        product.is_valid(True)

        product.sku = None
        product.is_valid(True)

        product.sku = 'test'
        product.image = None
        product.is_valid(True)

    def test_product_extra(self):
        speces = [Specification(i) for i in range(2)]
        options = [ProductOption(i) for i in range(2)]
        models = [Product(id=i) for i in range(50)]
        extra = ProductExtra(specifications=speces, options=options, models=models)
        extra.is_valid(True)

        print(extra.to_message())

    def test_product_details(self):
        product = Product(id=1)
        extra = None
        product_details = ProductDetails(product=product, extra=extra)

        product_details.is_valid(True)

        global_product = StoreProductModel.objects.get(id=1)
        serializer = StoreGlobalProductEmitDataSerializer(global_product)
        print(serializer.data)



