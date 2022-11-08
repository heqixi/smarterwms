import unittest

from store.models import StoreProductModel
from store.serializers import StoreGlobalProductEmitDataSerializer


class TestClass(unittest.TestCase):

    def test_get_global_product(self):
        # pass
        global_product = StoreProductModel.objects.get(id=1)
        serializer = StoreGlobalProductEmitDataSerializer(global_product)
        print(serializer.data)
