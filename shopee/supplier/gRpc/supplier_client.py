import threading

import grpc

from base.gRpc.types.base import ProtoType
from supplier.gRpc.protos import supplier_pb2, supplier_pb2_grpc

import logging

logger = logging.getLogger()


class Supplier(ProtoType):

    def __init__(self, **kwargs):
        self.id = None
        self.supplier_name = None
        self.supplier_city = None
        self.supplier_address = None
        self.supplier_contact = None
        self.supplier_manager = None
        self.supplier_level = None
        super(Supplier, self).__init__(**kwargs)

    def is_valid(self):
        is_valid = (self.id and self.id > 0) or self.is_not_empty(self.supplier_name)
        if not is_valid:
            raise Exception('Invalid supplier !')
        return is_valid

    def from_message(self, *args):
        pass

    def to_message(self):
        return supplier_pb2.Supplier(
            id=self.id,
            supplier_name=self.supplier_name,
            supplier_city=self.supplier_city,
            supplier_address=self.supplier_address,
            supplier_contact=self.supplier_contact,
            supplier_manager=self.supplier_manager,
            supplier_level=self.supplier_level
        )


class CreatePurchasePlanReq(ProtoType):

    def __init__(self, **kwargs):
        self.price = kwargs.get('price', None)
        self.url = kwargs.get('url', None)
        self.image_url = kwargs.get('image_url', None)
        self.tag = kwargs.get('tag', None)
        self.goods = kwargs.get('goods', None)
        self.supplier = kwargs.get('supplier', None)
        super().__init__(**kwargs)

    def is_valid(self):
        return self.is_not_negetive(self.price) and self.is_not_empty(self.url, self.image_url,
                                                                      self.goods) and self.supplier.is_valid()

    def from_message(self, *args):
        pass

    def to_message(self):
        return supplier_pb2.PurchasePlan(
            supplier=self.supplier.to_message(),
            price=self.price,
            url=self.url,
            image_url=self.image_url,
            tag=self.tag,
            goods=self.goods
        )


class SupplierClient(object):
    __create_key = object()
    lock = threading.RLock()
    client = None
    service_stub = None

    def __init__(self, create_key):
        assert (create_key == SupplierClient.__create_key), \
            "Stock Service is single instance, please use SupplierClient.get_instance()"
        channel = grpc.insecure_channel('192.168.2.75:50052')
        self.service_stub = supplier_pb2_grpc.SupplierControllerStub(channel)

    @classmethod
    def get_instance(cls):
        if cls.client is None:
            cls.lock.acquire()
            if cls.client is None:
                cls.client = cls(SupplierClient.__create_key)
            cls.lock.release()
            return cls.client
        return cls.client

    def create_purchase_plan(self, req: CreatePurchasePlanReq):
        if not req.is_valid():
            logger.error('create purchase plan, req ', req.price, req.url, req.image_url, req.goods)
            raise Exception('Invalid req')
        return self.service_stub.CreatePurchasePlan(req.to_message())
