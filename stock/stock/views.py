from collections.abc import  Sequence

from django.db.models import Q
from rest_framework import viewsets

import logging

from base.bustools import GlobalEvent
from goods.models import ListModel as Goods
from .models import StockListModel, StockBinModel
from . import serializers
from utils.page import MyPageNumberPagination
from utils.md5 import Md5
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from .filter import StockListFilter, StockBinFilter
from rest_framework.exceptions import APIException
from stock.models import StockListModel as stocklist
from binset.models import ListModel as binset
from .serializers import FileListRenderSerializer, FileBinListRenderSerializer, StockListPostSerializer, \
    StockGetSerializer
from django.http import StreamingHttpResponse
from .files import FileListRenderCN, FileListRenderEN, FileBinListRenderCN, FileBinListRenderEN
from rest_framework.settings import api_settings
from base.bustools import GLOBAL_BUS as bus

logger = logging.getLogger()


class StockListViewSet(viewsets.ModelViewSet):
    """
        list:
            Response a data list（all）
    """
    pagination_class = MyPageNumberPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter, ]
    ordering_fields = ['id', "create_time", "update_time", ]
    filter_class = StockListFilter

    def get_project(self):
        try:
            id = self.kwargs.get('pk')
            return id
        except:
            return None

    def get_queryset(self):
        openid = self.request.META.get('HTTP_TOKEN')
        if openid:
            id = self.get_project()
            if id is None:
                return StockListModel.objects.filter(openid=openid)
            else:
                return StockListModel.objects.filter(openid=openid, id=id)
        else:
            return StockListModel.objects.none()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return serializers.StockListGetSerializer
        if self.action in ['create', 'update']:
            return serializers.StockListPostSerializer
        else:
            return self.http_method_not_allowed(request=self.request)

    def create(self, request, *agrs, **kwargs):
        data = request.data
        openid = self.request.META.get('HTTP_TOKEN')
        if not isinstance(data, Sequence):
            goods = data.get('goods', None)
            stock_id = data.get('id', None)
            if not goods and not stock_id:
                raise APIException('Must specify goods id or stock id when create/update stock')
            stock_instance = None
            if stock_id:
                stock_instance = StockListModel.objects.get(id=stock_id)
            else:
                stock_status = data.get('stock_status', None)
                if stock_status == StockListModel.Constants.STATUS_ONHAND:
                    # 现有库存只允许创建一个
                    stock_instance = StockListModel.objects.filter(goods_id=goods,
                                                                   stock_status=StockListModel.Constants.STATUS_ONHAND,
                                                                   openid=openid).first()
                if stock_status == StockListModel.Constants.STATUS_DAMAGE:
                    stock_instance = StockListModel.objects.filter(goods_id=goods,
                                                                   stock_status=StockListModel.Constants.STATUS_DAMAGE,
                                                                   openid=openid).first()
                    pre_damage_qty = stock_instance.stock_qty if stock_instance else 0
                    new_damage_qty = data.get('stock_qty', pre_damage_qty)
                    if new_damage_qty:
                        try:
                            new_damage_qty = int(new_damage_qty)
                            diff = new_damage_qty - pre_damage_qty
                            stock_onhand = StockListModel.objects.filter(goods_id=goods,
                                stock_status=StockListModel.Constants.STATUS_ONHAND, openid=openid).first()
                            if stock_onhand and 0 < diff:
                                stock_onhand.stock_qty -= min(diff, stock_onhand.stock_qty)
                                stock_onhand.save()
                        except Exception as exc:
                            logger.error('fail to parse stock qty ' % data.get('stock_qty'))
            if not stock_instance:
                data['openid'] = openid
                data['creater'] = self.request.META.get('HTTP_OPERATOR')
                saved_data = self._create(data)
            else:
                saved_data = self._update(data, stock_instance)
            headers = self.get_success_headers(saved_data)
            return Response(saved_data, status=200, headers=headers)
        save_data_list = []
        updated_goods_list = []
        for singleData in data:
            goods = singleData.get('goods', None)
            stock_id = singleData.get('id', None)
            if not goods and not stock_id:
                raise APIException('Must specify goods id or stock id when create/update stock')
            stock_instance = None
            if stock_id:
                stock_instance = StockListModel.objects.get(id=stock_id)
            else:
                stock_status = singleData.get('stock_status', None)
                if stock_status == StockListModel.Constants.STATUS_ONHAND or stock_status == StockListModel.Constants.STATUS_DAMAGE:
                    # 现有库存只允许创建一个
                    stock_instance = StockListModel.objects.filter(goods_id=goods,
                        stock_status=stock_status, openid=openid).first()
                if stock_status == StockListModel.Constants.STATUS_DAMAGE:
                    stock_instance = StockListModel.objects.filter(goods_id=goods,
                        stock_status=StockListModel.Constants.STATUS_DAMAGE, openid=openid).first()
            if not stock_instance:
                singleData['openid'] = openid
                singleData['creater'] = self.request.META.get('HTTP_OPERATOR')
                saved_data = self._create(singleData)
            else:
                saved_data = self._update(singleData, stock_instance)
            save_data_list.append(saved_data)

            # TODO ？？
            new_goods_code = singleData.get('new_goods_code', None)
            if new_goods_code:
                goods_to_update = Goods.objects.get(id=singleData.get('goods', None))
                goods_to_update.goods_code = new_goods_code
                goods_to_update.save()
                updated_goods_list.append(goods_to_update)
        headers = self.get_success_headers(save_data_list)
        return Response(save_data_list, status=200, headers=headers)

    def _create(self, data):
        data['openid'] = self.request.META.get('HTTP_TOKEN')
        qty = int(data.get('stock_qty', 0))
        if qty < 0:
            raise Exception('Can not create stock obj, stock qty must positive')
        status = data.get('stock_status', None)
        goods = data.get('goods', None)
        if status == StockListModel.Constants.STATUS_ONHAND:
            # 现有库存只允许创建一个
            exist_stock = StockListModel.objects.filter(Q(goods=goods) & Q(stock_status=status)).first()
            if exist_stock:
                exist_stock.stock_qty = qty
                exist_stock.save()
                serializer = StockGetSerializer(exist_stock)
                return serializer.data
        serializer = StockListPostSerializer(data=data)
        if not serializer.is_valid():
            print(serializer.errors)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data

    def update(self, request, *args, **kwargs):
        data = self.request.data
        qs = self.get_object()
        savedData = self._update(data, qs)
        headers = self.get_success_headers(savedData)
        return Response(savedData, status=200, headers=headers)

    def _update(self, data, qs):
        serializer = self.get_serializer(qs, data=data, many=False, partial=True)
        if not serializer.is_valid():
            print("update stock fail ,data is invalid ", serializer.errors)
        serializer.save()
        return serializer.data

    @bus.on(GlobalEvent.Stock.UPDATE_STOCK_GOODS)
    def _patchUpdate(dataList):
        print('_patchUpdate stock ', dataList)
        if not isinstance(dataList, Sequence):
            dataList = [dataList]
        afterSaved = []
        for data in dataList:
            id = data.get('id', None)
            if not id:
                raise Exception('Can not update stock, Illegal data id')
            instance = StockListModel.objects.get(id=id)
            partial = True if data.get('partial', None) else False
            serializer = StockListPostSerializer(instance, data=data, partial=partial)
            if not serializer.is_valid():
                raise Exception('Can not update stock, invalid data %s ' % serializer.errors)
            serializer.save()
            afterSaved.append(serializer.data)
        return afterSaved
    #
    # @bus.on(ORDER_MODIFY_CREATE_EVENT)
    # def reserveOrderModifyStock(modify: ShopeeOrderModifyModel, stock_status: int = 11):
    #     stock = modify.stock
    #     if not stock:
    #         if not modify.is_delete:
    #             goods = Goods.objects.filter(goods_code=modify.global_sku).first()
    #             stock = StockListModel.objects.create(
    #                 creater=modify.creater,
    #                 openid=modify.openid,
    #                 goods=goods,
    #                 stock_qty=modify.quantity,
    #                 stock_status=stock_status  # 预留库存
    #             )
    #             stock.save()
    #             modify.stock = stock
    #             modify.save()
    #     else:
    #         stock.update_qty(modify.quantity)
    #         modify.save()

    # @bus.on(ORDER_SYNC_EVENT)
    # def reserveStock(order: ShopeeOrderDetailModel, stock_status: int = 11):
    #     stock = order.stock
    #     if not stock:
    #         goods = Goods.objects.filter(goods_code=order.model_sku).first()
    #         if not goods:
    #             goods = Goods.objects.create(
    #                 creater=order.creater,
    #                 openid=order.openid,
    #                 goods_code=order.model_sku,
    #                 goods_name=order.model_name,
    #                 goods_image=order.image_url)
    #             goods.save()
    #         stock = StockListModel.objects.create(
    #             creater=order.creater,
    #             openid=order.openid,
    #             goods=goods,
    #             stock_qty=order.model_quantity_purchased,
    #             stock_status=stock_status  # 预留库存
    #         )
    #         order.stock = stock
    #         stock.save()
    #         order.save()
    #     else:
    #         stock.update_qty(order.model_quantity_purchased)
    #         order.save()
    #
    # def releaseStock(stock: StockListModel):
    #     if not stock:
    #         logger.warn("Try to release stock of None")
    #         return
    #     logger.info("Release stock of goods %s, status %s, qty %s" % (stock.goods, stock.stock_status, stock.stock_qty))
    #     stock.is_delete = True
    #     stock.save()


class StockBinViewSet(viewsets.ModelViewSet):
    """
        list:
            Response a data list（all）
    """
    pagination_class = MyPageNumberPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter, ]
    ordering_fields = ['id', "create_time", "update_time", ]
    filter_class = StockBinFilter

    def get_project(self):
        try:
            id = self.kwargs.get('pk')
            return id
        except:
            return None

    def get_queryset(self):
        openid = self.request.META.get('HTTP_TOKEN')
        if openid:
            id = self.get_project()
            if id is None:
                return StockBinModel.objects.filter(openid=openid)
            else:
                return StockBinModel.objects.filter(openid=openid, id=id)
        else:
            return StockBinModel.objects.none()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return serializers.StockBinGetSerializer
        elif self.action in ['create', 'update']:
            return serializers.StockBinPostSerializer
        else:
            return self.http_method_not_allowed(request=self.request)

    def create(self, request, pk):
        qs = self.get_object()
        openid = self.request.META.get('HTTP_TOKEN')
        if qs.openid != openid:
            raise APIException(
                {"detail": "Cannot update data which not yours"})
        else:
            data = self.request.data
            if 'bin_name' not in data and 'move_to_bin' not in data:
                raise APIException({"detail": "Please Enter The Bin Name"})
            else:
                current_bin_detail = binset.objects.filter(openid=openid,
                                                           bin_name=str(data['bin_name'])).first()
                move_to_bin_detail = binset.objects.filter(openid=openid,
                                                           bin_name=str(data['move_to_bin'])).first()
                goods_qty_change = stocklist.objects.filter(openid=openid,
                                                            goods_code=str(data['goods_code'])).first()
                if int(data['move_qty']) <= 0:
                    raise APIException({"detail": "Move QTY Must > 0"})
                else:
                    bin_move_qty_res = qs.goods_qty - qs.pick_qty - \
                                       qs.picked_qty - int(data['move_qty'])
                    if bin_move_qty_res > 0:
                        qs.goods_qty = qs.goods_qty - \
                                       qs.pick_qty - int(data['move_qty'])
                        if current_bin_detail.bin_property == 'Damage':
                            if move_to_bin_detail.bin_property == 'Damage':
                                pass
                            elif move_to_bin_detail.bin_property == 'Inspection':
                                goods_qty_change.damage_stock = goods_qty_change.damage_stock - \
                                                                int(data['move_qty'])
                                goods_qty_change.inspect_stock = goods_qty_change.inspect_stock + \
                                                                 int(data['move_qty'])
                            elif move_to_bin_detail.bin_property == 'Holding':
                                goods_qty_change.damage_stock = goods_qty_change.damage_stock - \
                                                                int(data['move_qty'])
                                goods_qty_change.hold_stock = goods_qty_change.hold_stock + \
                                                              int(data['move_qty'])
                            else:
                                goods_qty_change.damage_stock = goods_qty_change.damage_stock - \
                                                                int(data['move_qty'])
                                goods_qty_change.can_order_stock = goods_qty_change.can_order_stock + \
                                                                   int(data['move_qty'])
                        elif current_bin_detail.bin_property == 'Inspection':
                            if move_to_bin_detail.bin_property == 'Damage':
                                goods_qty_change.inspect_stock = goods_qty_change.inspect_stock - \
                                                                 int(data['move_qty'])
                                goods_qty_change.damage_stock = goods_qty_change.damage_stock + \
                                                                int(data['move_qty'])
                            elif move_to_bin_detail.bin_property == 'Inspection':
                                pass
                            elif move_to_bin_detail.bin_property == 'Holding':
                                goods_qty_change.inspect_stock = goods_qty_change.inspect_stock - \
                                                                 int(data['move_qty'])
                                goods_qty_change.hold_stock = goods_qty_change.hold_stock + \
                                                              int(data['move_qty'])
                            else:
                                goods_qty_change.inspect_stock = goods_qty_change.inspect_stock - \
                                                                 int(data['move_qty'])
                                goods_qty_change.can_order_stock = goods_qty_change.can_order_stock + \
                                                                   int(data['move_qty'])
                        elif current_bin_detail.bin_property == 'Holding':
                            if move_to_bin_detail.bin_property == 'Damage':
                                goods_qty_change.hold_stock = goods_qty_change.hold_stock - \
                                                              int(data['move_qty'])
                                goods_qty_change.damage_stock = goods_qty_change.damage_stock + \
                                                                int(data['move_qty'])
                            elif move_to_bin_detail.bin_property == 'Inspection':
                                goods_qty_change.hold_stock = goods_qty_change.hold_stock - \
                                                              int(data['move_qty'])
                                goods_qty_change.inspect_stock = goods_qty_change.inspect_stock + \
                                                                 int(data['move_qty'])
                            elif move_to_bin_detail.bin_property == 'Holding':
                                pass
                            else:
                                goods_qty_change.hold_stock = goods_qty_change.hold_stock - \
                                                              int(data['move_qty'])
                                goods_qty_change.can_order_stock = goods_qty_change.can_order_stock + \
                                                                   int(data['move_qty'])
                        else:
                            if move_to_bin_detail.bin_property == 'Damage':
                                goods_qty_change.can_order_stock = goods_qty_change.can_order_stock - \
                                                                   int(data['move_qty'])
                                goods_qty_change.damage_stock = goods_qty_change.damage_stock + \
                                                                int(data['move_qty'])
                            elif move_to_bin_detail.bin_property == 'Inspection':
                                goods_qty_change.can_order_stock = goods_qty_change.can_order_stock - \
                                                                   int(data['move_qty'])
                                goods_qty_change.inspect_stock = goods_qty_change.inspect_stock + \
                                                                 int(data['move_qty'])
                            elif move_to_bin_detail.bin_property == 'Holding':
                                goods_qty_change.can_order_stock = goods_qty_change.can_order_stock - \
                                                                   int(data['move_qty'])
                                goods_qty_change.hold_stock = goods_qty_change.hold_stock + \
                                                              int(data['move_qty'])
                            else:
                                pass
                        StockBinModel.objects.create(openid=openid,
                                                     bin_name=str(
                                                         data['move_to_bin']),
                                                     goods_code=str(
                                                         data['goods_code']),
                                                     goods_desc=goods_qty_change.goods_desc,
                                                     goods_qty=int(
                                                         data['move_qty']),
                                                     bin_size=move_to_bin_detail.bin_size,
                                                     bin_property=move_to_bin_detail.bin_property,
                                                     t_code=Md5.md5(
                                                         str(data['goods_code'])),
                                                     create_time=qs.create_time
                                                     )
                        if move_to_bin_detail.empty_label == True:
                            move_to_bin_detail.empty_label = False
                            move_to_bin_detail.save()
                        goods_qty_change.save()
                        qs.save()
                    elif bin_move_qty_res == 0:
                        qs.goods_qty = qs.picked_qty
                        if current_bin_detail.bin_property == 'Damage':
                            if move_to_bin_detail.bin_property == 'Damage':
                                pass
                            elif move_to_bin_detail.bin_property == 'Inspection':
                                goods_qty_change.damage_stock = goods_qty_change.damage_stock - \
                                                                int(data['move_qty'])
                                goods_qty_change.inspect_stock = goods_qty_change.inspect_stock + \
                                                                 int(data['move_qty'])
                            elif move_to_bin_detail.bin_property == 'Holding':
                                goods_qty_change.damage_stock = goods_qty_change.damage_stock - \
                                                                int(data['move_qty'])
                                goods_qty_change.hold_stock = goods_qty_change.hold_stock + \
                                                              int(data['move_qty'])
                            else:
                                goods_qty_change.damage_stock = goods_qty_change.damage_stock - \
                                                                int(data['move_qty'])
                                goods_qty_change.can_order_stock = goods_qty_change.can_order_stock + \
                                                                   int(data['move_qty'])
                        elif current_bin_detail.bin_property == 'Inspection':
                            if move_to_bin_detail.bin_property == 'Damage':
                                goods_qty_change.inspect_stock = goods_qty_change.inspect_stock - \
                                                                 int(data['move_qty'])
                                goods_qty_change.damage_stock = goods_qty_change.damage_stock + \
                                                                int(data['move_qty'])
                            elif move_to_bin_detail.bin_property == 'Inspection':
                                pass
                            elif move_to_bin_detail.bin_property == 'Holding':
                                goods_qty_change.inspect_stock = goods_qty_change.inspect_stock - \
                                                                 int(data['move_qty'])
                                goods_qty_change.hold_stock = goods_qty_change.hold_stock + \
                                                              int(data['move_qty'])
                            else:
                                goods_qty_change.inspect_stock = goods_qty_change.inspect_stock - \
                                                                 int(data['move_qty'])
                                goods_qty_change.can_order_stock = goods_qty_change.can_order_stock + \
                                                                   int(data['move_qty'])
                        elif current_bin_detail.bin_property == 'Holding':
                            if move_to_bin_detail.bin_property == 'Damage':
                                goods_qty_change.hold_stock = goods_qty_change.hold_stock - \
                                                              int(data['move_qty'])
                                goods_qty_change.damage_stock = goods_qty_change.damage_stock + \
                                                                int(data['move_qty'])
                            elif move_to_bin_detail.bin_property == 'Inspection':
                                goods_qty_change.hold_stock = goods_qty_change.hold_stock - \
                                                              int(data['move_qty'])
                                goods_qty_change.inspect_stock = goods_qty_change.inspect_stock + \
                                                                 int(data['move_qty'])
                            elif move_to_bin_detail.bin_property == 'Holding':
                                pass
                            else:
                                goods_qty_change.hold_stock = goods_qty_change.hold_stock - \
                                                              int(data['move_qty'])
                                goods_qty_change.can_order_stock = goods_qty_change.can_order_stock + \
                                                                   int(data['move_qty'])
                        else:
                            if move_to_bin_detail.bin_property == 'Damage':
                                goods_qty_change.can_order_stock = goods_qty_change.can_order_stock - \
                                                                   int(data['move_qty'])
                                goods_qty_change.damage_stock = goods_qty_change.damage_stock + \
                                                                int(data['move_qty'])
                            elif move_to_bin_detail.bin_property == 'Inspection':
                                goods_qty_change.can_order_stock = goods_qty_change.can_order_stock - \
                                                                   int(data['move_qty'])
                                goods_qty_change.inspect_stock = goods_qty_change.inspect_stock + \
                                                                 int(data['move_qty'])
                            elif move_to_bin_detail.bin_property == 'Holding':
                                goods_qty_change.can_order_stock = goods_qty_change.can_order_stock - \
                                                                   int(data['move_qty'])
                                goods_qty_change.hold_stock = goods_qty_change.hold_stock + \
                                                              int(data['move_qty'])
                            else:
                                pass
                        StockBinModel.objects.create(openid=openid,
                                                     bin_name=str(
                                                         data['move_to_bin']),
                                                     goods_code=str(
                                                         data['goods_code']),
                                                     goods_desc=goods_qty_change.goods_desc,
                                                     goods_qty=int(
                                                         data['move_qty']),
                                                     bin_size=move_to_bin_detail.bin_size,
                                                     bin_property=move_to_bin_detail.bin_property,
                                                     t_code=Md5.md5(
                                                         str(data['goods_code'])),
                                                     create_time=qs.create_time
                                                     )
                        if move_to_bin_detail.empty_label == True:
                            move_to_bin_detail.empty_label = False
                            move_to_bin_detail.save()
                        goods_qty_change.save()
                        if qs.goods_qty == 0:
                            qs.delete()
                        else:
                            qs.save()
                        if StockBinModel.objects.filter(openid=openid,
                                                        bin_name=str(data['bin_name'])).exists():
                            pass
                        else:
                            current_bin_detail.empty_label = True
                        current_bin_detail.save()
                    elif bin_move_qty_res < 0:
                        raise APIException(
                            {"detail": "Move Qty must < Bin Goods Qty"})
                    else:
                        pass
                headers = self.get_success_headers(data)
                return Response(data, status=200, headers=headers)

    def update(self, request, *args, **kwargs):
        qs = self.get_queryset()
        openid = self.request.META.get('HTTP_TOKEN')
        if qs[0].openid != openid:
            raise APIException(
                {"detail": "Cannot update data which not yours"})
        else:
            data = self.request.data
            for i in range(len(data)):
                if 'bin_name' not in data[i] and 'move_to_bin' not in data[i]:
                    raise APIException({"detail": "Please Enter The Bin Name"})
            for j in range(len(data)):
                current_bin_detail = binset.objects.filter(openid=openid,
                                                           bin_name=str(data[j]['bin_name'])).first()
                move_to_bin_detail = binset.objects.filter(openid=openid,
                                                           bin_name=str(data[j]['move_to_bin'])).first()
                goods_qty_change = stocklist.objects.filter(openid=openid,
                                                            goods_code=str(data[j]['goods_code'])).first()
                qs_project = qs.filter(t_code=data[j]['t_code'])
                if int(data[j]['move_qty']) <= 0:
                    raise APIException({"detail": "Move QTY Must > 0"})
                else:
                    bin_move_qty_res = qs_project.goods_qty - qs_project.pick_qty - qs_project.picked_qty - int(
                        data[j]['move_qty'])
                    if bin_move_qty_res > 0:
                        qs_project.goods_qty = qs_project.goods_qty - \
                                               qs_project.pick_qty - int(data[j]['move_qty'])
                        if current_bin_detail.bin_property == 'Damage':
                            if move_to_bin_detail.bin_property == 'Damage':
                                pass
                            elif move_to_bin_detail.bin_property == 'Inspection':
                                goods_qty_change.damage_stock = goods_qty_change.damage_stock - \
                                                                int(data[j]['move_qty'])
                                goods_qty_change.inspect_stock = goods_qty_change.inspect_stock + int(
                                    data[j]['move_qty'])
                            elif move_to_bin_detail.bin_property == 'Holding':
                                goods_qty_change.damage_stock = goods_qty_change.damage_stock - \
                                                                int(data[j]['move_qty'])
                                goods_qty_change.hold_stock = goods_qty_change.hold_stock + \
                                                              int(data[j]['move_qty'])
                            else:
                                goods_qty_change.damage_stock = goods_qty_change.damage_stock - \
                                                                int(data[j]['move_qty'])
                                goods_qty_change.can_order_stock = goods_qty_change.can_order_stock + int(
                                    data[j]['move_qty'])
                        elif current_bin_detail.bin_property == 'Inspection':
                            if move_to_bin_detail.bin_property == 'Damage':
                                goods_qty_change.inspect_stock = goods_qty_change.inspect_stock - int(
                                    data[j]['move_qty'])
                                goods_qty_change.damage_stock = goods_qty_change.damage_stock + \
                                                                int(data[j]['move_qty'])
                            elif move_to_bin_detail.bin_property == 'Inspection':
                                pass
                            elif move_to_bin_detail.bin_property == 'Holding':
                                goods_qty_change.inspect_stock = goods_qty_change.inspect_stock - int(
                                    data[j]['move_qty'])
                                goods_qty_change.hold_stock = goods_qty_change.hold_stock + \
                                                              int(data[j]['move_qty'])
                            else:
                                goods_qty_change.inspect_stock = goods_qty_change.inspect_stock - int(
                                    data[j]['move_qty'])
                                goods_qty_change.can_order_stock = goods_qty_change.can_order_stock + int(
                                    data[j]['move_qty'])
                        elif current_bin_detail.bin_property == 'Holding':
                            if move_to_bin_detail.bin_property == 'Damage':
                                goods_qty_change.hold_stock = goods_qty_change.hold_stock - \
                                                              int(data[j]['move_qty'])
                                goods_qty_change.damage_stock = goods_qty_change.damage_stock + \
                                                                int(data[j]['move_qty'])
                            elif move_to_bin_detail.bin_property == 'Inspection':
                                goods_qty_change.hold_stock = goods_qty_change.hold_stock - \
                                                              int(data[j]['move_qty'])
                                goods_qty_change.inspect_stock = goods_qty_change.inspect_stock + int(
                                    data[j]['move_qty'])
                            elif move_to_bin_detail.bin_property == 'Holding':
                                pass
                            else:
                                goods_qty_change.hold_stock = goods_qty_change.hold_stock - \
                                                              int(data[j]['move_qty'])
                                goods_qty_change.can_order_stock = goods_qty_change.can_order_stock + int(
                                    data[j]['move_qty'])
                        else:
                            if move_to_bin_detail.bin_property == 'Damage':
                                goods_qty_change.can_order_stock = goods_qty_change.can_order_stock - int(
                                    data[j]['move_qty'])
                                goods_qty_change.damage_stock = goods_qty_change.damage_stock + \
                                                                int(data[j]['move_qty'])
                            elif move_to_bin_detail.bin_property == 'Inspection':
                                goods_qty_change.can_order_stock = goods_qty_change.can_order_stock - int(
                                    data[j]['move_qty'])
                                goods_qty_change.inspect_stock = goods_qty_change.inspect_stock + int(
                                    data[j]['move_qty'])
                            elif move_to_bin_detail.bin_property == 'Holding':
                                goods_qty_change.can_order_stock = goods_qty_change.can_order_stock - int(
                                    data[j]['move_qty'])
                                goods_qty_change.hold_stock = goods_qty_change.hold_stock + \
                                                              int(data[j]['move_qty'])
                            else:
                                pass
                        StockBinModel.objects.create(openid=openid,
                                                     bin_name=str(
                                                         data[j]['move_to_bin']),
                                                     goods_code=str(
                                                         data[j]['goods_code']),
                                                     goods_desc=goods_qty_change.goods_desc,
                                                     goods_qty=int(
                                                         data[j]['move_qty']),
                                                     bin_size=move_to_bin_detail.bin_size,
                                                     bin_property=move_to_bin_detail.bin_property,
                                                     t_code=Md5.md5(
                                                         str(data[j]['goods_code'])),
                                                     create_time=qs_project.create_time
                                                     )
                        if move_to_bin_detail.empty_label == True:
                            move_to_bin_detail.empty_label = False
                            move_to_bin_detail.save()
                        goods_qty_change.save()
                        qs_project.save()
                    elif bin_move_qty_res == 0:
                        qs_project.goods_qty = qs_project.picked_qty
                        if current_bin_detail.bin_property == 'Damage':
                            if move_to_bin_detail.bin_property == 'Damage':
                                pass
                            elif move_to_bin_detail.bin_property == 'Inspection':
                                goods_qty_change.damage_stock = goods_qty_change.damage_stock - \
                                                                int(data[j]['move_qty'])
                                goods_qty_change.inspect_stock = goods_qty_change.inspect_stock + int(
                                    data[j]['move_qty'])
                            elif move_to_bin_detail.bin_property == 'Holding':
                                goods_qty_change.damage_stock = goods_qty_change.damage_stock - \
                                                                int(data[j]['move_qty'])
                                goods_qty_change.hold_stock = goods_qty_change.hold_stock + \
                                                              int(data[j]['move_qty'])
                            else:
                                goods_qty_change.damage_stock = goods_qty_change.damage_stock - \
                                                                int(data[j]['move_qty'])
                                goods_qty_change.can_order_stock = goods_qty_change.can_order_stock + int(
                                    data[j]['move_qty'])
                        elif current_bin_detail.bin_property == 'Inspection':
                            if move_to_bin_detail.bin_property == 'Damage':
                                goods_qty_change.inspect_stock = goods_qty_change.inspect_stock - int(
                                    data[j]['move_qty'])
                                goods_qty_change.damage_stock = goods_qty_change.damage_stock + \
                                                                int(data[j]['move_qty'])
                            elif move_to_bin_detail.bin_property == 'Inspection':
                                pass
                            elif move_to_bin_detail.bin_property == 'Holding':
                                goods_qty_change.inspect_stock = goods_qty_change.inspect_stock - int(
                                    data[j]['move_qty'])
                                goods_qty_change.hold_stock = goods_qty_change.hold_stock + \
                                                              int(data[j]['move_qty'])
                            else:
                                goods_qty_change.inspect_stock = goods_qty_change.inspect_stock - int(
                                    data[j]['move_qty'])
                                goods_qty_change.can_order_stock = goods_qty_change.can_order_stock + int(
                                    data[j]['move_qty'])
                        elif current_bin_detail.bin_property == 'Holding':
                            if move_to_bin_detail.bin_property == 'Damage':
                                goods_qty_change.hold_stock = goods_qty_change.hold_stock - \
                                                              int(data[j]['move_qty'])
                                goods_qty_change.damage_stock = goods_qty_change.damage_stock + \
                                                                int(data[j]['move_qty'])
                            elif move_to_bin_detail.bin_property == 'Inspection':
                                goods_qty_change.hold_stock = goods_qty_change.hold_stock - \
                                                              int(data[j]['move_qty'])
                                goods_qty_change.inspect_stock = goods_qty_change.inspect_stock + int(
                                    data[j]['move_qty'])
                            elif move_to_bin_detail.bin_property == 'Holding':
                                pass
                            else:
                                goods_qty_change.hold_stock = goods_qty_change.hold_stock - \
                                                              int(data[j]['move_qty'])
                                goods_qty_change.can_order_stock = goods_qty_change.can_order_stock + int(
                                    data[j]['move_qty'])
                        else:
                            if move_to_bin_detail.bin_property == 'Damage':
                                goods_qty_change.can_order_stock = goods_qty_change.can_order_stock - int(
                                    data[j]['move_qty'])
                                goods_qty_change.damage_stock = goods_qty_change.damage_stock + \
                                                                int(data[j]['move_qty'])
                            elif move_to_bin_detail.bin_property == 'Inspection':
                                goods_qty_change.can_order_stock = goods_qty_change.can_order_stock - int(
                                    data[j]['move_qty'])
                                goods_qty_change.inspect_stock = goods_qty_change.inspect_stock + int(
                                    data[j]['move_qty'])
                            elif move_to_bin_detail.bin_property == 'Holding':
                                goods_qty_change.can_order_stock = goods_qty_change.can_order_stock - int(
                                    data[j]['move_qty'])
                                goods_qty_change.hold_stock = goods_qty_change.hold_stock + \
                                                              int(data[j]['move_qty'])
                            else:
                                pass
                        StockBinModel.objects.create(openid=openid,
                                                     bin_name=str(
                                                         data[j]['move_to_bin']),
                                                     goods_code=str(
                                                         data[j]['goods_code']),
                                                     goods_desc=goods_qty_change.goods_desc,
                                                     goods_qty=int(
                                                         data[j]['move_qty']),
                                                     bin_size=move_to_bin_detail.bin_size,
                                                     bin_property=move_to_bin_detail.bin_property,
                                                     t_code=Md5.md5(
                                                         str(data[j]['goods_code'])),
                                                     create_time=qs_project.create_time
                                                     )
                        if move_to_bin_detail.empty_label == True:
                            move_to_bin_detail.empty_label = False
                            move_to_bin_detail.save()
                        goods_qty_change.save()
                        if qs_project.goods_qty == 0:
                            qs_project.delete()
                        else:
                            qs_project.save()
                        if StockBinModel.objects.filter(openid=openid,
                                                        bin_name=str(data[j]['bin_name'])).exists():
                            pass
                        else:
                            current_bin_detail.empty_label = True
                        current_bin_detail.save()
                    elif bin_move_qty_res < 0:
                        raise APIException(
                            {"detail": "Move Qty must < Bin Goods Qty"})
                    else:
                        pass
                headers = self.get_success_headers(data[j])
                return Response(data[j], status=200, headers=headers)


class FileListDownloadView(viewsets.ModelViewSet):
    renderer_classes = (FileListRenderCN,) + \
                       tuple(api_settings.DEFAULT_RENDERER_CLASSES)
    filter_backends = [DjangoFilterBackend, OrderingFilter, ]
    ordering_fields = ['id', "create_time", "update_time", ]
    filter_class = StockListFilter

    def get_project(self):
        try:
            id = self.kwargs.get('pk')
            return id
        except:
            return None

    def get_queryset(self):
        openid = self.request.META.get('HTTP_TOKEN')
        if self.request.user:
            id = self.get_project()
            if id is None:
                return StockListModel.objects.filter(openid=openid)
            else:
                return StockListModel.objects.filter(openid=openid, id=id)
        else:
            return StockListModel.objects.none()

    def get_serializer_class(self):
        if self.action in ['list']:
            return serializers.FileListRenderSerializer
        else:
            return self.http_method_not_allowed(request=self.request)

    def get_lang(self, data):
        lang = self.request.META.get('HTTP_LANGUAGE')
        if lang:
            if lang == 'zh-hans':
                return FileListRenderCN().render(data)
            else:
                return FileListRenderEN().render(data)
        else:
            return FileListRenderEN().render(data)

    def list(self, request, *args, **kwargs):
        from datetime import datetime
        dt = datetime.now()
        data = (
            FileListRenderSerializer(instance).data
            for instance in self.filter_queryset(self.get_queryset())
        )
        renderer = self.get_lang(data)
        response = StreamingHttpResponse(
            renderer,
            content_type="text/csv"
        )
        response['Content-Disposition'] = "attachment; filename='stocklist_{}.csv'".format(
            str(dt.strftime('%Y%m%d%H%M%S%f')))
        return response


class FileBinListDownloadView(viewsets.ModelViewSet):
    renderer_classes = (FileBinListRenderCN,) + \
                       tuple(api_settings.DEFAULT_RENDERER_CLASSES)
    filter_backends = [DjangoFilterBackend, OrderingFilter, ]
    ordering_fields = ['id', "create_time", "update_time", ]
    filter_class = StockBinFilter

    def get_project(self):
        try:
            id = self.kwargs.get('pk')
            return id
        except:
            return None

    def get_queryset(self):
        openid = self.request.META.get('HTTP_TOKEN')
        if self.request.user:
            id = self.get_project()
            if id is None:
                return StockBinModel.objects.filter(openid=openid)
            else:
                return StockBinModel.objects.filter(openid=openid, id=id)
        else:
            return StockBinModel.objects.none()

    def get_serializer_class(self):
        if self.action in ['list']:
            return serializers.FileBinListRenderSerializer
        else:
            return self.http_method_not_allowed(request=self.request)

    def get_lang(self, data):
        lang = self.request.META.get('HTTP_LANGUAGE')
        if lang:
            if lang == 'zh-hans':
                return FileBinListRenderCN().render(data)
            else:
                return FileBinListRenderEN().render(data)
        else:
            return FileBinListRenderEN().render(data)

    def list(self, request, *args, **kwargs):
        from datetime import datetime
        dt = datetime.now()
        data = (
            FileBinListRenderSerializer(instance).data
            for instance in self.filter_queryset(self.get_queryset())
        )
        renderer = self.get_lang(data)
        response = StreamingHttpResponse(
            renderer,
            content_type="text/csv"
        )
        response['Content-Disposition'] = "attachment; filename='stockbinlist_{}.csv'".format(
            str(dt.strftime('%Y%m%d%H%M%S%f')))
        return response
