from bitarray import test
from stock.models import StockListModel as Stock
from stock.models import StockBinModel as StockBin
from asn.models import AsnListModel as Asn
from goods.models import ListModel as Goods

from stock.serializers import StockListGetSerializer  as GetSer

# 测试生产的serializer 有没有问题
serializer = GetSer()
print(repr(serializer))

testStockBin = StockBin.objects.all()[0]
testAsn = Asn.objects.all()[0]
openid="90caa1b003a7a696e2c253157b105b99"

testStock = Stock(goods_code = "test_goods_code", goods_qty=100, asn=testAsn, stockBin=testStockBin, openid=openid)
testStock.save()

serializer = GetSer(testStock)

