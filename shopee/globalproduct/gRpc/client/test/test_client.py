import unittest
from store.gRpc.client.types.global_product import ProductDetails, Specification, ProductOption, Product, ProductStatus, ProductExtra
from store.gRpc.client.global_product import ProductServiceClient


class ProductTestClass(unittest.TestCase):

    def test_create(self):
        product = Product(sku='test', image='test', status=ProductStatus.PUBLISH)
        product_details = ProductDetails(product=product)
        res = ProductServiceClient.get_instance().create(product_details)
        print(res)

    def test_create_with_specification(self):
        product = Product(sku='test_3', image='test', status=ProductStatus.EDIT)
        options = [ProductOption(name='red', spec_index=0, index=0, image='abc'),
                   ProductOption(name='blue', spec_index=0, index=1, image='abc')]
        specification = Specification(name='color', index=0, options=options)
        product_details = ProductDetails(product=product, extra=ProductExtra(first_spec=specification))
        _message = product_details.to_message()
        assert _message.extra is not None
        print(_message.extra.secondSpec)
        # assert _message.extra.secondSpec is None
        res = ProductServiceClient.get_instance().create(product_details)
        print(res)

    def test_create_missing_product(self):
        res = ProductServiceClient.get_instance().create_raw()
        print(res)

    def test_create_missing_sku(self):
        product = Product(image='test', status=ProductStatus.PUBLISH)
        product_details = ProductDetails(product=product)
        res = ProductServiceClient.get_instance().create(product_details)
        print(res)