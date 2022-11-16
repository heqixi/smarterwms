from abc import ABC, abstractmethod

from goods.models import ListModel as Goods
from goods.gRpc.server.protos import goods_pb2


def model_to_proto(goods: Goods) -> goods_pb2.Goods:
    return goods_pb2.Goods(
        id=goods.id,
        goods_code=goods.goods_code,
        goods_image=goods.goods_image,
        goods_name=goods.goods_name,
        goods_desc=goods.goods_desc,
        goods_weight=goods.goods_weight,
        goods_w=goods.goods_w,
        goods_h=goods.goods_h,
        goods_d=goods.goods_d,
        goods_unit=goods.goods_unit,
        goods_class=goods.goods_class,
        goods_brand=goods.goods_brand,
        goods_color=goods.goods_color,
        bar_code=goods.bar_code
    )


class Success(object):
    goods: Goods

    def __init__(self, goods=None):
        self.goods = goods
        self.status = goods_pb2.Response.Status.SUCCESS

    def to_message(self):
        goods = self.goods
        if not goods:
            return goods_pb2.Repsonse(status=self.status)
        return goods_pb2.Response(status=self.status, goods=model_to_proto(self.goods))


class Error(ABC):
    msg: str

    @property
    @abstractmethod
    def code(self):
        raise NotImplementedError('Not Implement')

    def to_message(self):
        return goods_pb2.Response(status=goods_pb2.Response.Status.FAIL, code=self.code, msg=self.msg)


class UnknowError(Error):

    def __init__(self, msg='Unknow Error'):
        self.msg = msg

    @property
    def code(self):
        return goods_pb2.Response.Code.UNKNOW


class GoodsNotFoundError(Error):

    def __init__(self, msg='Goods not found'):
        self.msg = msg

    @property
    def code(self):
        return goods_pb2.Response.Code.GOODS_NOT_FOUND


class MissingParametersError(Error):

    def __init__(self, msg='Missing Parameters'):
        self.msg = msg

    @property
    def code(self):
        return goods_pb2.Response.Code.MISSING_PARAMETERS


class IllegalParameterError(Error):

    def __init__(self, msg='Illegal Paramenter'):
        self.msg = msg

    @property
    def code(self):
        return goods_pb2.Response.Code.ILLEGAL_PARAMETERS


class DuplicateGoodsCodeError(Error):

    def __init__(self, msg='Duplicate goods code'):
        self.msg = msg

    @property
    def code(self):
        return goods_pb2.Response.Code.DUPLICATE_GOODS_CODE


