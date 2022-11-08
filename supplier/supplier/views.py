from django.db import transaction
from rest_framework import viewsets
from .models import ListModel, PurchasePlan, PurchasePlanGoodsSetting
from . import serializers
from utils.page import MyPageNumberPagination
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from .filter import Filter, PurchasePlanFilter
from rest_framework.exceptions import APIException
from .serializers import FileRenderSerializer, PurchasePlanGetSerializer, PurchasePlanPostSerializer, \
    PurchasePlanSerializer
from django.http import StreamingHttpResponse
from .files import FileRenderCN, FileRenderEN
from rest_framework.settings import api_settings
from django.db.models import Prefetch

import logging

logger = logging.getLogger()


class APIViewSet(viewsets.ModelViewSet):
    """
        retrieve:
            Response a data （get）

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
    pagination_class = MyPageNumberPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter, ]
    ordering_fields = ['id', "create_time", "update_time", ]
    filter_class = Filter

    def get_all_supplier(self, request):
        openid = self.request.META.get('HTTP_TOKEN')
        if openid:
            query_set = ListModel.objects.prefetch_related(
                Prefetch(ListModel.RelativeFields.SUPPLIER_PURCHASES,
                         queryset=PurchasePlan.objects.filter(is_delete=False),
                         to_attr=ListModel.RelativeFields.SUPPLIER_PURCHASES_UNDELETE)
            )
            id = self.get_project()
            if id is None:
                query_set = query_set.filter(openid=openid, is_delete=False)
            else:
                query_set = query_set.filter(openid=openid, id=id, is_delete=False)
            supplier_list = []
            for supplier in query_set:
                serializer = serializers.SupplierGetSerializer(supplier)
                serializer.context['request'] = request
                data = serializer.data
                supplier_list.append(data)
            headers = self.get_success_headers(supplier_list)
            return Response(supplier_list, status=200, headers=headers)
        else:
            raise ValueError('用户未登录')

    def get_project(self):
        try:
            id = self.kwargs.get('pk')
            return id
        except:
            return None

    def get_queryset(self):
        openid = self.request.META.get('HTTP_TOKEN')
        if openid:
            query_set = ListModel.objects.prefetch_related(
                Prefetch(ListModel.RelativeFields.SUPPLIER_PURCHASES,
                         queryset=PurchasePlan.objects.filter(is_delete=False),
                         to_attr=ListModel.RelativeFields.SUPPLIER_PURCHASES_UNDELETE)
            )
            id = self.get_project()
            if id is None:
                query_set = query_set.filter(openid=openid, is_delete=False)
            else:
                query_set = query_set.filter(openid=openid, id=id, is_delete=False)
            return query_set
        else:
            return ListModel.objects.none()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve', 'destroy']:
            return serializers.SupplierGetSerializer
        elif self.action in ['create']:
            return serializers.SupplierPostSerializer
        elif self.action in ['update']:
            return serializers.SupplierUpdateSerializer
        elif self.action in ['partial_update']:
            return serializers.SupplierPartialUpdateSerializer
        else:
            return self.http_method_not_allowed(request=self.request)

    def create(self, request, *args, **kwargs):
        openid = self.request.META.get('HTTP_TOKEN')
        data = self.request.data
        data['openid'] = openid
        if ListModel.objects.filter(openid=data['openid'], supplier_name=data['supplier_name'],
                                    is_delete=False).exists():
            raise APIException({"detail": "Data exists"})
        else:
            serializer = self.get_serializer(data=data)
            if not serializer.is_valid():
                print("create supplier fail ", serializer.errors)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=200, headers=headers)

    def update(self, request, pk):
        openid = self.request.META.get('HTTP_TOKEN')
        qs = self.get_object()
        if qs.openid != openid:
            raise APIException({"detail": "Cannot update data which not yours"})
        else:
            data = self.request.data
            serializer = self.get_serializer(qs, data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=200, headers=headers)

    def partial_update(self, request, pk):
        openid = self.request.META.get('HTTP_TOKEN')
        qs = self.get_object()
        if qs.openid != openid:
            raise APIException({"detail": "Cannot partial_update data which not yours"})
        else:
            data = self.request.data
            serializer = self.get_serializer(qs, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=200, headers=headers)

    def destroy(self, request, pk):
        openid = self.request.META.get('HTTP_TOKEN')
        qs = self.get_object()
        if qs.openid != openid:
            raise APIException({"detail": "Cannot delete data which not yours"})
        else:
            qs.is_delete = True
            qs.save()
            serializer = self.get_serializer(qs, many=False)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=200, headers=headers)


class FileDownloadView(viewsets.ModelViewSet):
    renderer_classes = (FileRenderCN,) + tuple(api_settings.DEFAULT_RENDERER_CLASSES)
    filter_backends = [DjangoFilterBackend, OrderingFilter, ]
    ordering_fields = ['id', "create_time", "update_time", ]
    filter_class = Filter

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
                return ListModel.objects.filter(openid=openid, is_delete=False)
            else:
                return ListModel.objects.filter(openid=openid, id=id, is_delete=False)
        else:
            return ListModel.objects.none()

    def get_serializer_class(self):
        if self.action in ['list']:
            return serializers.FileRenderSerializer
        else:
            return self.http_method_not_allowed(request=self.request)

    def get_lang(self, data):
        lang = self.request.META.get('HTTP_LANGUAGE')
        if lang:
            if lang == 'zh-hans':
                return FileRenderCN().render(data)
            else:
                return FileRenderEN().render(data)
        else:
            return FileRenderEN().render(data)

    def list(self, request, *args, **kwargs):
        from datetime import datetime
        dt = datetime.now()
        data = (
            FileRenderSerializer(instance).data
            for instance in self.filter_queryset(self.get_queryset())
        )
        renderer = self.get_lang(data)
        response = StreamingHttpResponse(
            renderer,
            content_type="text/csv"
        )
        response['Content-Disposition'] = "attachment; filename='supplier_{}.csv'".format(
            str(dt.strftime('%Y%m%d%H%M%S%f')))
        return response


class PurchasePlanView(viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend, OrderingFilter, ]
    ordering_fields = ['id', "create_time", "update_time", ]
    filter_class = PurchasePlanFilter

    def get_project(self):
        try:
            id = self.kwargs.get('pk')
            return id
        except:
            return None

    def get_queryset(self):
        print('PurchasePlanView get query set ')
        openid = self.request.META.get('HTTP_TOKEN')
        if not openid:
            raise APIException('Please offer openid')
        queryset = PurchasePlan.objects.filter(openid=openid, is_delete=False)
        id = self.get_project()
        if id is not None:
            queryset = queryset.filter(id=id)
        goods = self.request.query_params.getlist('goods', None)
        if goods:
            queryset = queryset.prefetch_related('goods_settings').filter(goods_settengs__goods__in=goods) # goods_settengs是错别字，先别修改
        return queryset

    def get_serializer_class(self):
        if self.action in ['list']:
            return PurchasePlanGetSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return PurchasePlanPostSerializer
        else:
            return self.http_method_not_allowed(request=self.request)

    def create(self, request, *args, **kwargs):
        data = self.request.data
        print("create purchase plan", data)
        logger.info("create purchase plan", data)
        openid = self.request.META.get('HTTP_TOKEN')
        if not openid:
            raise APIException('Please offer openid')
        data['openid'] = openid
        serializer = self.get_serializer(data=data)
        if not serializer.is_valid():
            logger.error(serializer.errors)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=200, headers=self.get_success_headers(serializer.data))

    def update(self, request, *args, **kwargs):
        openid = self.request.META.get('HTTP_TOKEN')
        if not openid:
            raise APIException("Please offer openid")
        data = self.request.data
        print("update purchase plan", data)
        purchase_id = data.get('id', None)
        qs = None
        if purchase_id:
            qs = PurchasePlan.objects.get(id=purchase_id)
        if qs and qs.openid != openid:
            raise APIException(
                {"detail": "Cannot update asn order which not yours"})
        goods_ids = data.get('goods', None)
        if goods_ids and data.get('add', None):
            for goods_id in goods_ids:
                # goods = Goods.objects.get(id=goods_id)
                exist_settings = PurchasePlanGoodsSetting.objects.filter(goods_id=goods_id, openid=qs.openid).all()
                max_level = -1
                for exist_setting in exist_settings:
                    max_level = max(exist_setting.level, max_level)
                purchase_setting = PurchasePlanGoodsSetting(
                    plan=qs,
                    goods=goods_id,
                    level=max_level + 1,
                    creater=self.request.META.get('HTTP_OPERATOR'),
                    openid=openid
                )
                purchase_setting.save()
        elif goods_ids and data.get('remove', None):
            for goods_id in goods_ids:
                exist_settings = PurchasePlanGoodsSetting.objects.filter(goods=goods_id, plan=qs.id).all()
                for exist_setting in exist_settings:
                    exist_setting.delete()
        else:
            if qs:
                serializer = self.get_serializer(qs, data=data, partial=data.get('partial', True))
            else:
                data['openid'] = openid
                data['creater'] = self.request.META.get('HTTP_OPERATOR')
                serializer = self.get_serializer(data=data)
            if not serializer.is_valid():
                logger.error(serializer.errors)
            serializer.is_valid(raise_exception=True)
            qs = serializer.save()
        get_serializer = PurchasePlanGetSerializer(qs, context={'request': self.request})
        return Response(get_serializer.data, status=200, headers=self.get_success_headers(""))

    @transaction.atomic
    def set_default_purchase(self, request, *args, **kwargs):
        openid = self.request.META.get('HTTP_TOKEN')
        if not openid:
            raise APIException("Please offer openid")
        data = self.request.data
        goods = data.get('goods', None)
        purchase = data.get('purchase', None)
        if not goods or not purchase:
            raise APIException('Set default purchase missing goods %s or purchase %s' % (goods, purchase))
        setting_to_set_default = PurchasePlanGoodsSetting.objects.filter(goods=goods, plan=purchase, is_delete=False).first()
        all_settings = PurchasePlanGoodsSetting.objects.filter(goods=goods, is_delete=False).order_by('-level')
        if not setting_to_set_default:
            setting_to_set_default = PurchasePlanGoodsSetting(
                goods=goods,
                plan=PurchasePlan.objects.get(id=purchase),
                openid=openid,
                creater=self.request.META.get('HTTP_OPERATOR'),
                level=all_settings.count()
            )
            setting_to_set_default.save()
        all_settings = PurchasePlanGoodsSetting.objects.filter(goods=goods, is_delete=False).order_by('-level')
        if all_settings.count() <= 1:
            return Response('success', status=200)
        if setting_to_set_default.level == 0:
            return Response('success', status=200)
        current_level = setting_to_set_default.level
        setting_to_set_default.level = all_settings.count() + 1
        setting_to_set_default.save() #先临时设置level, 因为有唯一性约束 (goods, level)
        for setting in all_settings.all():
            if setting.id == setting_to_set_default.id or setting.level > current_level:
                continue
            setting.level += 1
            setting.save()
        setting_to_set_default.level = 0
        setting_to_set_default.save()
        return Response('success', status=200)

    def destroy(self, request, pk):
        qs = self.get_object()
        openid = self.request.META.get('HTTP_TOKEN')
        if qs.openid != openid:
            raise APIException(
                {"detail": "Cannot delete data which not yours"})
        else:
            print('delete purchase id ', qs.id)
            qs.is_delete = True
            qs.save()
            serializer = PurchasePlanSerializer(qs)
            return Response({"status": 200, "data": serializer.data}, status=200, headers=self.get_success_headers(""))
