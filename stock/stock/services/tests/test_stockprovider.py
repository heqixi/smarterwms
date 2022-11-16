import unittest

from stock.services.stockprovider import StockService


class TestCase(unittest.TestCase):

    def test_add_shipping_stock(self):
        StockService.get_instance().add_shipping_stock(1, 124169415169)