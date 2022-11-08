from abc import ABC, abstractmethod

from product.models import GlobalProduct as Product
from product.gRpc.server.protos import product_pb2


def model_to_proto(product: Product):
    return product_pb2.Product(
        id=product.id,
        sku=product.sku,
        status=product.status,
        mode=product.mode,
        image=product.image,
        name=product.name,
        desc=product.desc,
        type=product.type,
        second_hand=product.second_hand,
        models=[model.id for model in product.models.all()]
    )


class Success(object):
    product: Product

    def __init__(self, product=None):
        self.product = product
        self.status = product_pb2.Response.Status.SUCCESS

    def to_message(self):
        product = self.product
        if not product:
            return product_pb2.Repsonse(status=self.status)
        return product_pb2.Response(status=self.status, product=model_to_proto(self.product))


class Error(ABC):
    msg: str

    @property
    @abstractmethod
    def code(self):
        raise NotImplementedError('Not Implement')

    @property
    @abstractmethod
    def msg(self):
        raise NotImplementedError('Not Implement')

    def to_message(self):
        return product_pb2.ProductResponse(code=self.code, msg=self.msg)


class UnknowError(Error):

    def __init__(self, msg='Unknow Error'):
        self.msg = msg

    @property
    def code(self):
        return product_pb2.Response.Code.UNKNOW


class ErrorBuilder(Error):

    def __init__(self, code=None, msg=''):
        self.code = code
        self.msg = msg

    def code(self):
        return self.code
    
    def msg(self):
        return self.msg


class ProductNotFoundError(Error):

    def __init__(self, msg='Product not found'):
        self.msg = msg

    @property
    def code(self):
        return product_pb2.Response.Code.PRODUCT_NOT_FOUND


class MissingParametersError(Error):

    def __init__(self, msg='Missing Parameters'):
        self.msg = msg

    @property
    def code(self):
        return product_pb2.Response.Code.MISSING_PARAMETERS


class IllegalParameterError(Error):

    def __init__(self, msg='Illegal Paramenter'):
        self.msg = msg

    @property
    def code(self):
        return product_pb2.Response.Code.ILLEGAL_PARAMETERS
