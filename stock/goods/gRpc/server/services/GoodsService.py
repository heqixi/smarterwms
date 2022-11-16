from django.db import transaction

from goods.gRpc.server.utils import goods_group_to_message
from goods.models import ListModel as Goods, GlobalProductGoodsRelation, GoodsGroup
from django_grpc_framework import generics
from goods.gRpc.server.serializers.GoodsSerializer import GoodsSerializer
from goods.gRpc.server.protos import goods_pb2

from goods.gRpc.server.types.response import Success, GoodsNotFoundError,\
    MissingParametersError, IllegalParameterError, UnknowError, DuplicateGoodsCodeError


class GoodsService(generics.ModelService):
    """
    gRPC service that allows users to be retrieved or updated.
    """
    print('GoodsService in')
    queryset = Goods.objects.all().order_by('-id')
    serializer_class = GoodsSerializer

    def Update(self, request, context):
        instance = self.get_object()
        if not instance:
            return GoodsNotFoundError('Goods not found').to_message()
        serializer = self.get_serializer(instance, message=request, partial=True)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
        except Exception as exc:
            print(exc)
            return UnknowError(str(exc)).to_message()
        else:
            goods = Goods.objects.get(id=instance.id)
            return Success(goods).to_message()

    def Query(self, request, context):
        product_id = request.product_id
        goods_list = []
        if product_id:
          relations = GlobalProductGoodsRelation.objects.filter(product_id=product_id, is_delete=False).select_related('goods')
          for relation in relations:
              goods_list.append(relation.goods)
        if not goods_list:
            return []
        for goods in goods_list:
            goods_proto = goods_pb2.Goods(
                id=goods.id,
                goods_code=goods.goods_code,
                goods_name=goods.goods_name,
                goods_desc=goods.goods_desc,
                goods_weight=goods.goods_weight,
                goods_w=goods.goods_w,
                goods_d=goods.goods_d,
                goods_h=goods.goods_h,
                goods_unit=goods.goods_unit,
                goods_class=goods.goods_class,
                goods_brand=goods.goods_brand,
                goods_color=goods.goods_color,
                bar_code=goods.bar_code
            )
            yield goods_proto

    def Create(self, request, context):
        goods_code = request.goods_code
        if not goods_code:
            return MissingParametersError('Missing goods code').to_message()
        goods_image = request.goods_image
        if not goods_image or len(goods_image) <= 0:
            return MissingParametersError('Missing goods image').to_message()
        goods_weight = request.goods_weight
        if goods_weight is None:
            return MissingParametersError('Missing goods weight').to_message()
        if Goods.objects.filter(goods_code=goods_code).exists():
            return DuplicateGoodsCodeError('Goods of code %s exist' % goods_code).to_message()
        serializer = self.get_serializer(message=request, partial=True)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as exc:
            return IllegalParameterError(str(exc)).to_message()
        else:
            goods = serializer.save()
            return Success(goods).to_message()

    def Destroy(self, request, context):
        print('destroy goods')
        goods_id = request.id
        if goods_id is None:
            return MissingParametersError('Missing goods id')
        goods = Goods.objects.filter(id=goods_id).first()
        if not goods:
            return GoodsNotFoundError('Goods not found')
        goods.is_delete = True
        goods.save()
        return Success(goods).to_message()

    def Retrieve(self, request, context):
        print('Retrieve goods')
        goods_id = request.id
        if goods_id is None:
            return MissingParametersError('Missing goods id').to_message()
        goods = Goods.objects.filter(id=goods_id, is_delete=False).first()
        if not goods:
            return GoodsNotFoundError('Goods of id %s not found' % goods_id).to_message()
        print('retrieve goods code', goods.goods_code)
        return Success(goods).to_message()

    @transaction.atomic
    def CreateGroup(self, request, context):
        print('Create goods group ')
        openid = 'c240c14ea66ef48bc3c5645735a715af'
        creater = 'admin'
        group_name = request.name
        if not group_name:
            return MissingParametersError('Missing group name').to_message()
        goods_list = [goods for goods in request.goods]
        if not goods_list:
            return MissingParametersError('Missing goods list').to_message()
        goods_obj_list = []
        for goods in goods_list:
            if goods.id:
                goods_obj = Goods.objects.filter(id=goods.id).first()
                if not goods_obj:
                    return GoodsNotFoundError('Create goods group goods of id %s not found' % goods.id)
            else:
                if not (goods.goods_code and goods.goods_image):
                    return MissingParametersError('Missing goods sku or goods image').to_message()
                goods_obj = Goods.objects.filter(goods_code=goods.goods_code, openid=openid).first()
                if not goods:
                    goods_obj = Goods.objects.create(
                        openid=openid,
                        creater=creater,
                        goods_code=goods.goods_code,
                        goods_image=goods.goods_image
                    )
            goods_obj_list.append(goods_obj)
        goods_group = GoodsGroup.objects.create(
            openid=openid,
            creater=creater,
            name=group_name
        )
        for goods_obj in goods_obj_list:
            goods_group.goods.add(goods_obj)
        goods_group.save()
        return goods_group_to_message(goods_group)









