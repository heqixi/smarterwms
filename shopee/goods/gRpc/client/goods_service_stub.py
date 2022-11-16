import threading
import grpc
from django.db import transaction

from goods.gRpc.client.protos import goods_pb2_grpc, goods_pb2
from goods.gRpc.client.types.goods import CreateRequest, UpdateRequest, CreateGroupRequest
from goods.gRpc.client.types.goods import Response
from goods.models import GoodsGroupRecord, GoodsRecord


class GoodsServiceClient(object):
    __create_key = object()
    lock = threading.RLock()
    client = None
    service_stub = None

    def __init__(self, create_key):
        assert (create_key == GoodsServiceClient.__create_key),\
            "Stock Service is single instance, please use GlobalProductService.get_instance()"
        channel = grpc.insecure_channel('192.168.31.237:50051')

        self.service_stub = goods_pb2_grpc.GoodsControllerStub(channel)

    @classmethod
    def get_instance(cls):
        if cls.client is None:
            cls.lock.acquire()
            if cls.client is None:
                cls.client = cls(GoodsServiceClient.__create_key)
            cls.lock.release()
            return cls.client
        return cls.client

    def Create(self, goods: CreateRequest):
        if not goods.is_valid():
            raise Exception('Illegal product')
        res = self.service_stub.Create(goods.to_message())
        return Response(res)

    def query(self, product_id):
        return self.service_stub.Query(goods_pb2.GoodsQueryRequest(product_id=str(product_id)))

    def retrieve(self, goods_id):
        if not isinstance(goods_id, int) or goods_id < 0:
            raise Exception('Fail to retrieve goods, illegal goods id %s'% goods_id)
        res = self.service_stub.Retrieve(goods_pb2.GoodsRetrieveRequest(id=goods_id))
        return Response(res)

    def update(self, req: UpdateRequest):
        if not req.is_valid():
            raise Exception('Illegal request')
        res = self.service_stub.Update(req.to_message())
        return Response(res)

    def destroy(self, goods_id):
        if goods_id is None or goods_id < 0:
            raise Exception('Illegal goods id')
        res = self.service_stub.Destroy(goods_pb2.Goods(id=goods_id))
        return Response(res)

    def list(self):
        return self.service_stub.List(goods_pb2.GoodsListRequest())

    def create_group(self, req: CreateGroupRequest):
        if not req.is_valid():
            raise Exception('create group illegal req')
        try:
            goods_group = self.service_stub.CreateGroup(req.to_message())
        except Exception as exc:
            print('create goods group remote exception,', exc)
            raise Exception('create goods group remote exception ')
        else:
            group_record = self._create_group_record(goods_group)
        return group_record

    @transaction.atomic
    def _create_group_record(self, goods_group):
        group_record = GoodsGroupRecord.objects.create(
            group_id=goods_group.id,
            name=goods_group.name
        )
        for goods in goods_group:
            self._create_goods_record(goods, group_record.id)

    def _create_goods_record(self, goods, group_id):
        return GoodsRecord.objects.create(
            goods_id=goods.id,
            goods_code=goods.goods_code,
            goods_image=goods.goods_image,
            group_id=group_id
        )
