from django_grpc_framework import generics

from supplier.gRpc.server.utils import purchase_to_message
from supplier.models import ListModel as Supplier, PurchasePlanGoodsSetting
from supplier.models import PurchasePlan
from supplier.gRpc.server.types.response import SupplierNotFoundError, MissingParametersError


class SupplierService(generics.ModelService):

    def CreatePurchasePlan(self, request, context):
        openid = ''
        creater = 'admin'
        supplier = request.supplier
        if supplier.id:
            supplier_obj = Supplier.objects.filter(id=supplier.id).first()
            if not supplier_obj:
                return SupplierNotFoundError('Supplier of id %s not found' % supplier.id).to_message()
        else:
            if not supplier.supplier_name:
                return MissingParametersError('Missing supplier name').to_message()
            supplier_obj = Supplier.objects.create(
                openid=openid,
                creater=creater,
                supplier_name=supplier.supplier_name
            )
        if not request.price:
            return MissingParametersError('Missing price').to_message()
        if not request.url:
            return MissingParametersError('Missing url').to_message()
        if not request.image_url:
            return MissingParametersError('Missing image url').to_message()
        purchase_plan = PurchasePlan.objects.create(
            openid=openid,
            creater=creater,
            supplier=supplier_obj,
            price=request.price,
            url=request.url,
            image_url=request.image_url
        )
        for goods_id in request.goods_id:
            exist_setting = PurchasePlanGoodsSetting.objects.filter(goods=goods_id).order_by('level').last()
            level = 0
            if exist_setting:
                level = exist_setting.level + 1
            PurchasePlanGoodsSetting.objects.create(
                openid=openid,
                creater=creater,
                plan=purchase_plan,
                goods=goods_id,
                level=level
            )
        return purchase_to_message(purchase_plan)


