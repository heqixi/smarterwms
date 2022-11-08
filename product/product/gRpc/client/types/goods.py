
from abc import ABC

from base.gRpc.types.base import ProtoType
from product.gRpc.client.protos import goods_pb2


class Goods(ProtoType, ABC):
    id: int
    goods_code: int
    goods_name: str
    goods_desc: str
    goods_weight: float
    goods_w: float
    goods_d: float
    goods_h: float
    goods_unit: str
    goods_class: str
    goods_brand: str
    goods_color: str
    bar_code: str

    def __init__(self, **kwargs):
        self.id = None
        self.goods_code = None
        self.goods_name = None
        self.goods_desc = None
        self.goods_weight = None
        self.goods_w = None
        self.goods_d = None
        self.goods_h = None
        self.goods_unit = None
        self.goods_class = None
        self.goods_brand = None
        self.goods_color = None
        self.bar_code = None
        super().__init__(**kwargs)

    def is_valid(self):
        raise NotImplementedError('Has not Implement')


class GoodsCreateModel(Goods):

    def is_valid(self):
        return self.is_not_empty(self.goods_code) and self.is_not_negetive(self.goods_weight)

    def to_proto_obj(self):
        return goods_pb2.Goods(
            goods_code=self.goods_code,
            goods_name=self.goods_name,
            goods_desc=self.goods_desc,
            goods_weight=self.goods_weight,
            goods_w=self.goods_w,
            goods_d=self.goods_d,
            goods_h=self.goods_h,
            goods_unit=self.goods_unit,
            goods_class=self.goods_class,
            goods_brand=self.goods_brand,
            goods_color=self.goods_color,
            bar_code=self.bar_code
        )


class GoodsUpdateModel(Goods):
    def is_valid(self):
        return self.is_not_negetive(self.id) and self.is_not_empty(
            self.goods_code) and self.is_not_negetive(self.goods_weight, nullable=True)

    def to_proto_obj(self):
        return goods_pb2.Goods(
            id=self.id,
            goods_code=self.goods_code,
            goods_name=self.goods_name,
            goods_desc=self.goods_desc,
            goods_weight=self.goods_weight,
            goods_w=self.goods_w,
            goods_d=self.goods_d,
            goods_h=self.goods_h,
            goods_unit=self.goods_unit,
            goods_class=self.goods_class,
            goods_brand=self.goods_brand,
            goods_color=self.goods_color,
            bar_code=self.bar_code
        )



