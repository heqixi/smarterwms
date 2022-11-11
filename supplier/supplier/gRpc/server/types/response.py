from abc import ABC, abstractmethod

from supplier.gRpc.server.protos import supplier_pb2


class Error(ABC):
    msg: str

    @property
    @abstractmethod
    def code(self):
        raise NotImplementedError('Not Implement')

    def to_message(self):
        return supplier_pb2.Response(code=self.code, msg=self.msg)


class UnknowError(Error):

    def __init__(self, msg='Unknow Error'):
        self.msg = msg

    @property
    def code(self):
        return supplier_pb2.Response.Code.UNKNOW


class SupplierNotFoundError(Error):

    def __init__(self, msg='Goods not found'):
        self.msg = msg

    @property
    def code(self):
        return supplier_pb2.Code.SUPPLIER_NOT_FOUND


class MissingParametersError(Error):

    def __init__(self, msg='Missing Parameters'):
        self.msg = msg

    @property
    def code(self):
        return supplier_pb2.Code.MISSING_PARAMETERS


class IllegalParameterError(Error):

    def __init__(self, msg='Illegal Paramenter'):
        self.msg = msg

    @property
    def code(self):
        return supplier_pb2.Code.ILLEGAL_PARAMETERS
