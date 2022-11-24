from collections.abc import Sequence


from django.forms import model_to_dict
from django.db.models.functions import Coalesce
from django.db.models import Count, Q, Sum, F, Case, When, IntegerField

from rest_framework import viewsets

from base.profiler import profile

from .models import ListModel, GoodsTag
from . import serializers
from .page import MyPageNumberPagination, GoodsCursorPagination
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .filter import Filter, GoodsTagFilter
from rest_framework.exceptions import APIException

from rest_framework.response import Response

import logging


logger = logging.getLogger()


class SannerGoodsTagView(viewsets.ModelViewSet):
    """
    retrieve:
        Response a data retrieve（get）

    """

    pagination_class = MyPageNumberPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter, ]
    ordering_fields = ['id', "create_time", "update_time", ]
    filter_class = Filter
    lookup_field = 'bar_code'

    def get_project(self):
        try:
            bar_code = self.kwargs['bar_code']
            return bar_code
        except:
            return None

    def get_queryset(self):
        openid = self.request.META.get('HTTP_TOKEN')
        bar_code = self.get_project()
        if openid:
            if bar_code is None:
                return ListModel.objects.filter(openid=openid, is_delete=False)
            else:
                return ListModel.objects.filter(openid=openid, bar_code=bar_code, is_delete=False)
        else:
            return ListModel.objects.filter().none()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve', 'destroy']:
            return serializers.GoodsGetSerializer
        elif self.action in ['create']:
            return serializers.GoodsPostSerializer
        elif self.action in ['update']:
            return serializers.GoodsPostSerializer
        elif self.action in ['partial_update']:
            return serializers.GoodsPostSerializer
        else:
            return self.http_method_not_allowed(request=self.request)

    def retrieve(self, request, *args, **kwargs):
        raise APIException('Not implement')
        # data = self.request.GET.get('asn_code')
        # instance = self.get_object()
        # serializer = self.get_serializer(instance)
        # good_detail = AsnDetailModel.objects.filter(
        #     asn_code=data, goods_code=serializer.data['goods_code']).first()
        # if good_detail is None:
        #     raise APIException({"detail": "The product label does not exist"})
        # else:
        #     context = {}
        #     context['goods_code'] = good_detail.goods_code
        #     context['goods_actual_qty'] = good_detail.goods_actual_qty
        # return Response(context, status=200)


class APIViewSet(viewsets.ModelViewSet):
    """
        retrieve:
            Response a data list（get）

        list:
            Response a data list（all）

        create:
            Create a data line（post）

        delete:
            Delete a data line（delete)

        partial_update:
            Partial_update a data（patch：partial_update）

        update:
            Update a data（put：update）
    """
    pagination_class = GoodsCursorPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter, ]
    ordering_fields = ['id', "create_time", "update_time", ]
    filter_class = Filter

    def get_project(self):
        try:
            id = self.kwargs.get('pk')
            return id
        except:
            return None

    def parse_filter(self, filter_params):
        filterTupleList = []
        for filter in filter_params:
            field, condition = filter.split("__")
            filterTupleList.append((field, condition))
        return filterTupleList

    def parse_order(self, order_params):
        filterTupleList = []
        for order in order_params:
            field, by, reverse = order.split("__")
            filterTupleList.append((field, by, reverse))
        return filterTupleList

    def get_queryset(self):
        openid = self.request.META.get('HTTP_TOKEN')
        if not openid:
            raise APIException('No open id ')
            # return ListModel.objects.filter().none()
        id = self.get_project()
        id_in_params = self.request.query_params.getlist('id_in', [])
        exclude = self.request.query_params.getlist('exclude', [])
        filter_params = self.request.query_params.getlist('filter', None)
        order_params = self.request.query_params.getlist('order', None)
        search_params = self.request.query_params.getlist('search', None)
        stock_param = self.request.query_params.get('goods_stocks', None)
        queryset = ListModel.objects.filter(openid=openid, is_delete=False)
        if id is None:
            queryset = queryset.filter(openid=openid, is_delete=False)
        else:
            queryset = queryset.filter(openid=openid, id=id, is_delete=False)
        if exclude and len(exclude) > 0:
            queryset = queryset.exclude(id__in=exclude)
        if id_in_params and len(id_in_params) > 0:
            queryset = queryset.filter(id__in=id_in_params)
        if search_params:
            search_term = search_params[0]  # 暂时只支持一个搜素条件
            queryset = queryset.filter(
                Q(goods_code__contains=search_term) | Q(goods_name__contains=search_term)).distinct()

        if stock_param == 'aggregation':
            queryset = queryset.annotate(
                stock_damage=Coalesce(Sum('goods_stock__stock_qty', filter=Q(goods_stock__stock_status=-1)), 0))
            queryset = queryset.annotate(
                stock_purchased=Coalesce(Sum('goods_stock__stock_qty', filter=Q(goods_stock__stock_status=1)), 0))
            queryset = queryset.annotate(
                stock_sorted=Coalesce(Sum('goods_stock__stock_qty', filter=Q(goods_stock__stock_status=2)),
                                      0))
            queryset = queryset.annotate(
                stock_onhand=Coalesce(Sum('goods_stock__stock_qty', filter=Q(goods_stock__stock_status=3)),
                                      0))
            queryset = queryset.annotate(
                stock_reserve=Coalesce(Sum('goods_stock__stock_qty', filter=Q(goods_stock__stock_status=11)), 0))
            queryset = queryset.annotate(
                stock_ship=Coalesce(Sum('goods_stock__stock_qty', filter=Q(goods_stock__stock_status=12)), 0))
            queryset = queryset.annotate(stock_shortage=F('stock_reserve') - F('stock_onhand') - F('stock_purchased'))
        if filter_params:
            for field, condition in self.parse_filter(filter_params):
                if field == 'stock':
                    queryset = queryset.annotate(
                        stock_count=Count('goods_stock'))
                    if condition == 'notEmpty':
                        queryset = queryset.filter(stock_count__gt=0)
                    if condition == 'shortage':
                        queryset = queryset.filter(stock_shortage__gt=0)
        if order_params:
            for field, by, ordering in self.parse_order(order_params):
                if field == 'stock':
                    if by == 'shortage':
                        if ordering == 'desc':
                            queryset = queryset.order_by('-stock_shortage')
                        else:
                            queryset = queryset.order_by('stock_shortage')
        return queryset

    @profile('GoodsView:list')
    def list(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = serializer.data
            response = self.get_paginated_response(data)
            return response
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve', 'destroy']:
            return serializers.GoodsGetSerializer
        elif self.action in ['create']:
            return serializers.GoodsPostSerializer
        elif self.action in ['update']:
            return serializers.GoodsPostSerializer
        elif self.action in ['partial_update']:
            return serializers.GoodsPostSerializer
        else:
            return self.http_method_not_allowed(request=self.request)

    def create(self, request, *args, **kwargs):
      raise APIException('No Implement')

    def update(self, request, pk):
        openid = request.META.get('HTTP_TOKEN')
        qs = self.get_object()
        if qs.openid != openid:
            raise APIException(
                {"detail": "Cannot update data which not yours"})
        data = self.request.data
        if data.get('merge', None):  # 不能合并自己
            merge_to_id = data.get('merge_to', None)
            if not merge_to_id or merge_to_id == qs.id:
                raise APIException('Can not merge goods, id is null')
            if merge_to_id == qs.id:
                raise APIException('Can not merge to self')
            merge_to_goods = ListModel.objects.get(id=merge_to_id)
            product_relations = getattr(qs, ListModel.RelativeFields.PRODUCT_RELATION)
            for product_relation in product_relations.all():
                # 只需要迁移把关联的产品变体关联
                product_relation.goods = merge_to_goods
                product_relation.save()
            goods_stocks = getattr(qs, ListModel.RelativeFields.GOODS_STOCK)
            for stock in goods_stocks.all():
                stock.goods = merge_to_goods
                stock.save()
            goods_media = getattr(qs, ListModel.RelativeFields.GOODS_MEDIA)
            for meida in goods_media.all():
                meida.goods = merge_to_goods
                meida.save()
            purchase_plans = getattr(qs, ListModel.RelativeFields.GOODS_PURCHASES)
            for purchase in purchase_plans.all():
                purchase.goods = merge_to_goods
                purchase.save()
            asn_details = getattr(qs, ListModel.RelativeFields.GOODS_ASN_DETAIL)
            for asn_detail in asn_details.all():
                asn_detail.goods = merge_to_goods
                asn_detail.save()
            qs.is_delete = True
            qs.save()
        else:
            new_goods_code = data.get('goods_code', None)
            if new_goods_code:
                exist_goods = ListModel.objects.filter(goods_code=new_goods_code, openid=openid).first()
                if exist_goods and exist_goods.id != qs.id:
                    if data.get('merge_duplicate', None):
                        self.__merge_goods(qs, exist_goods.id)
                        return Response(model_to_dict(exist_goods), status=200)
                    else:
                        return Response({'status': 501, 'message': 'Dulicate Goods Code'}, status=500)
            serializer = self.get_serializer(qs, data=data, many=False, partial=data.get('partial', False))
            if not serializer.is_valid():
                logger.error("update goods fail ,data is invalid ", serializer.errors)
                raise Exception('Fail to update goods, data is invalid')
            serializer.save()  # 需要先保存
            goods_code_change = new_goods_code is not None and new_goods_code != qs.goods_code
            update_products = data.get('update_product', False)
            if goods_code_change and update_products:
                # TODO GOODS_DEPENDENCES
                raise Exception('Improper Dependence !')
                # models = getattr(qs, ListModel.RelativeFields.PRODUCT_MODELS)
                # update_publish = data.get('update_publish', False)
                # group_by_merchant = {}
                # for model in models:
                #     model.sku = new_goods_code
                #     model.save()
                #     if not update_publish:
                #         continue
                #     global_publishes = getattr(model, GlobalProduct.RelativeFields.SHOPEE_GLOBAL_PUBLISH).all()
                #     for global_publish in global_publishes:
                #         model_list = group_by_merchant.get(global_publish.merchant_id, [])
                #         model_list.append({'model_id': global_publish.publish_id, 'model_sku': new_goods_code})
                #         group_by_merchant[global_publish.merchant_id] = model_list
                # for merchant_id, model_list in group_by_merchant.items():
                #     GlobalService.get_instance().update_model_sku(merchant_id, model_list)
        return Response(data, status=200)

    def update_relations(self, request, *args, **kwargs):
        pass

    def __merge_goods(self, qs, merge_to_id):
        if not merge_to_id or merge_to_id == qs.id:
            raise APIException('Can not merge goods, id is null')
        if merge_to_id == qs.id:
            raise APIException('Can not merge to self')
        merge_to_goods = ListModel.objects.get(id=merge_to_id)
        # TODO GOODS_DEPENDENCES
        product_relations = getattr(qs, ListModel.RelativeFields.PRODUCT_RELATION)
        for product_relation in product_relations.all():
            # 只需要迁移把关联的产品变体关联
            product_relation.goods = merge_to_goods
            product_relation.save()
        goods_stocks = getattr(qs, ListModel.RelativeFields.GOODS_STOCK)
        for stock in goods_stocks.all():
            stock.goods = merge_to_goods
            stock.save()
        goods_media = getattr(qs, ListModel.RelativeFields.GOODS_MEDIA)
        for meida in goods_media.all():
            meida.goods = merge_to_goods
            meida.save()
        # TODO GOODS_DEPENDENCES
        # purchase_setting_relations = PurchasePlanGoodsSetting.objects.filter(goods_id=qs.id).all()
        # for settings in purchase_setting_relations:
        #     settings.goods = merge_to_goods
        #     settings.save()
        asn_details = getattr(qs, ListModel.RelativeFields.GOODS_ASN_DETAIL)
        for asn_detail in asn_details.all():
            asn_detail.goods = merge_to_goods
            asn_detail.save()
        qs.is_delete = True
        qs.save()

    def partial_update(self, request, pk):
        raise APIException("No Implement")

    def destroy(self, request, pk):
        openid = request.META.get('HTTP_TOKEN')
        qs = self.get_object()
        if qs.openid != openid:
            raise APIException(
                {"detail": "Cannot delete data which not yours"})
        else:
            # 关联的全球商品
            response = {'reason': '存在关联实体'}
            response['details'] = {'code': -1}
            response['details']['goods'] = model_to_dict(qs)
            goods_stocks = getattr(qs, ListModel.RelativeFields.GOODS_STOCK)
            if goods_stocks.count():
                stocks = []
                for stock in goods_stocks.all():
                    stocks.append(model_to_dict(stock))
                response['details']['stocks'] = stocks
            goods_medias = getattr(qs, ListModel.RelativeFields.GOODS_MEDIA)
            if goods_medias.count():
                medias = []
                for media in goods_medias.all():
                    medias.append(model_to_dict(media))
                response['details']['meidas'] = medias

            purchase_plan = getattr(qs, ListModel.RelativeFields.GOODS_PURCHASES)
            if purchase_plan.count():
                purchases = []
                for purchase in purchase_plan.all():
                    purchases.append({
                        'price': purchase.price,
                        'url': purchase.url,
                        'tag': purchase.tag,
                        'default': purchase.default
                    })
                response['details']['purchases'] = purchases

            goods_asn_details = getattr(qs, ListModel.RelativeFields.GOODS_ASN_DETAIL)
            if goods_asn_details.count():
                asn_details = []
                for detials in goods_asn_details.all():
                    asn_details.append(model_to_dict(detials))
                response['details']['asn_details'] = asn_details
            if product_relations.count() or goods_stocks.count() or goods_medias.count() or purchase_plan.count() or goods_asn_details.count():
                return Response(response, status=403)
            qs.is_delete = True
            qs.save()
            serializer = self.get_serializer(qs, many=False)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=200, headers=headers)


class GoodsTagView(viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend, OrderingFilter, ]
    ordering_fields = ['id', "create_time", "update_time", ]
    filter_class = GoodsTagFilter

    def get_project(self):
        try:
            id = self.kwargs.get('pk')
            return id
        except:
            return None

    def get_queryset(self):
        id = self.get_project()
        openid = self.request.META.get('HTTP_TOKEN')
        if openid:
            if id is None:
                return GoodsTag.objects.filter(openid=openid, is_delete=False)
            else:
                return GoodsTag.objects.filter(openid=openid, id=id, is_delete=False)
        else:
            return GoodsTag.objects.none()

    def get_serializer_class(self):
        if self.action in ['list']:
            return serializers.GoodsTagsGetSerialier
        if self.action in ['create', 'update', 'partial_update']:
            return serializers.GoodsTagsPostSerialier
        else:
            return self.http_method_not_allowed(request=self.request)

    def create(self, request, *args, **kwargs):
        openid = request.META.get('HTTP_TOKEN')
        data = self.request.data
        data['openid'] = openid
        serializer = self.get_serializer(data=data)
        if not serializer.is_valid():
            print(serializer.errors)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=200, headers=self.get_success_headers(serializer.data))

    def update(self, request, *args, **kwargs):
        datas = self.request.data
        print(datas)
        if not isinstance(datas, Sequence):
            dataSave = self._update(self.get_object(), datas)
        else:
            dataSave = []
            for data in datas:
                data_id = data.get('id', None)
                if not data_id:
                    raise APIException(
                        "You muse specifiy id to update goods tag")
                qs = GoodsTag.objects.filter(id=data_id).first()
                if not qs:
                    raise APIException(
                        "fail to update,  goods tag of id %s not exit !" % data_id)
                if not data.get('goods', None):
                    # 如果绑定的产品为空,则删除
                    qs.goods.clear()
                    qs.delete()
                else:
                    dataSave.append(self._update(qs, data))
        return Response(dataSave, status=200, headers=self.get_success_headers(dataSave))

    def _update(self, qs, data):
        openid = self.request.META.get('HTTP_TOKEN')
        if qs.openid != openid:
            raise APIException(
                {"detail": "Cannot update asn order which not yours"})
        partial = True if data.get('partial', None) else False
        serializer = self.get_serializer(qs, data=data, partial=partial)
        if not serializer.is_valid():
            print(serializer.errors)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data
