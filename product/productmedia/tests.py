from django.test import TestCase

# Create your tests here.
from .models import ListModel as GoodsMedia
from product.models import ListModel as Goods

testGoods = Goods(
    goods_code='1', 
    goods_desc="test product",
    goods_supplier="聚宜购",
    goods_weight=1.5,
    goods_w = 4,
    goods_d = 1,
    goods_h = 5,
    unit_volume = 0.1,
    goods_class = 'watch', 
    goods_brand = 'smael',
    goods_color = 'black',
    goods_shape = 'normal',
    goods_specs = 'product spec',
    goods_origin = 'shen zhen', 
    safety_stock = 100,
    goods_cost = 25,
    creater = 'admin',
    bar_code = 'bar code',
    openid = '2d2c01d1193285cd9c6b58c2ff3fd656',
    is_delete = False
    )

testGoods.save()

loadGoods = Goods.objects.all()[0]

media = GoodsMedia(
    url="url", 
    media_type='V', 
    media_tag='Video', 
    media_desc='media desc',
    relative_goods_id=loadGoods,
    openid='2d2c01d1193285cd9c6b58c2ff3fd656')

media.save()

