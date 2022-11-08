
from collections.abc import Sequence
import logging

from django.db import transaction
from rest_framework import viewsets

from base.profiler import profile
from .asnHelper import AsnHelper
from .models import AsnListModel, AsnDetailModel, AsnOrder
from . import serializers
from .page import MyPageNumberPaginationASNList
from utils.page import MyPageNumberPagination
from utils.fbmsg import FBMsg
from utils.md5 import Md5
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from .filter import AsnListFilter, AsnDetailFilter, AsnOrderFilter
from rest_framework.exceptions import APIException
from django.db.models import Q
from django.http import StreamingHttpResponse
from django.utils import timezone
from .files import FileListRenderCN, FileListRenderEN, FileDetailRenderCN, FileDetailRenderEN
from rest_framework.settings import api_settings
from dateutil.relativedelta import relativedelta
from .serializers.asndetails import ASNDetailPostSerializer, ASNDetailUpdateSerializer,FileDetailRenderSerializer,ASNDetailGetSerializer
from .serializers.asn import ASNListPartialUpdateSerializer, ASNListPostSerializer,FileListRenderSerializer,ASNListGetSerializer
from .serializers.asnorder import AsnOrderSerializer, AsnOrderPostSerializer

logger = logging.getLogger()


class AsnListViewSet(viewsets.ModelViewSet):
    """
        retrieve:
            Response a data list（get）

        list:
            Response a data list（all）

        create:
            Create a data line（post）

        delete:
            Delete a data line（delete)

    """
    pagination_class = MyPageNumberPaginationASNList
    filter_backends = [DjangoFilterBackend, OrderingFilter, ]
    ordering_fields = ['id', "create_time", "update_time", ]
    filter_class = AsnListFilter

    def get_project(self):
        try:
            id = self.kwargs.get('pk')
            return id
        except:
            return None

    def get_queryset(self):
        id = self.get_project()
        openid = self.request.META.get('HTTP_TOKEN')
        if not openid:
            raise Exception('Please offer openid')
            # return AsnListModel.objects.none()
        if id is None:
            queryset = AsnListModel.objects.filter(openid=openid, is_delete=False)
        else:
            queryset = AsnListModel.objects.filter(Q(openid=openid, id=id, is_delete=False))
        asn_status = self.request.query_params.get('asn_status', None)
        if asn_status is not None:
            queryset = queryset.filter(asn_status=asn_status)
        return queryset

    @profile('AsnView:list')
    def list(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            return response
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve', 'destroy']:
            return ASNListGetSerializer
        elif self.action in ['create']:
            return ASNListPostSerializer
        elif self.action in ['update']:
            return ASNListPostSerializer
        elif self.action in ['partial_update']:
            return ASNListPartialUpdateSerializer
        else:
            return self.http_method_not_allowed(request=self.request)

    def notice_lang(self):
        return FBMsg(self.request.META.get('HTTP_LANGUAGE'))

    def create(self, request, *args, **kwargs):
        datas = self.request.data
        logger.info('create or update asn obj and asn detials %s', datas)
        if not isinstance(datas, Sequence):
            datas = [datas]
        openid = self.request.META.get('HTTP_TOKEN')
        for data in datas:
            data['openid'] = openid
            id = data.get('id', None)
            if id:
                asn_instance = AsnListModel.objects.get(id=id)
                self._update(asn_instance, data)
            else:
                asn_instance = self._create(data)
                data['id'] = asn_instance.id
            # 保存detail
            ans_details = data.get('details', None)
            if not ans_details:
                continue
            for details_data in ans_details:
                details_data['openid'] = openid
                details_id = details_data.get('id', None)
                if details_id:
                    goods_qty = details_data.get('goods_qty', 1)
                    detail_instance = AsnDetailModel.objects.get(id=details_id)
                    if goods_qty == 0 and asn_instance.asn_status == 0:
                        detail_instance.delete()
                    else:
                        self._update_asn_details(detail_instance, details_data)
                else:
                    details_data['openid'] = asn_instance.openid
                    details_data['creater'] = asn_instance.creater
                    details_data['asn'] = asn_instance.id
                    serializer = ASNDetailPostSerializer(data=details_data)
                    if not serializer.is_valid():
                        logger.error("fail to save asn detail goods ", serializer.errors)
                        return Response(serializer.errors, status=500)
                    serializer.is_valid(raise_exception=True)
                    details_instance = serializer.save()
                    details_data['id'] = details_instance.id
        headers = self.get_success_headers(datas)
        return Response(datas, status=200, headers=headers)

    @transaction.atomic
    def amend_asn(self, request, *args, **kwargs):
        data = self.request.data
        asn_id = data.get('asn', None)
        if not asn_id:
            raise APIException('Amend asn missing asn id')
        asn = AsnListModel.objects.filter(id=asn_id, is_delete=False).first()
        if not asn or asn.asn_status != 3:
            raise APIException('Only asn in stock can be amend %s'%asn.asn_status)
        details = data.get('details', None)
        if not details:
            return AsnListModel('Amend asn missing details')
        AsnHelper.amend_asn(asn, details)
        return Response('success', status=200)

    def update(self, request, *args, **kwargs):
        qs = self.get_object()
        self._update(qs, self.request.data)
        return Response(self.request.data, status=200)

    @transaction.atomic
    def destroy(self, request, pk):
        openid = self.request.META.get('HTTP_TOKEN')
        qs = self.get_object()
        logger.info("delete asn obj, %s, %s", qs.asn_status, qs.id)
        if qs.openid != openid:
            raise APIException({"detail": "Cannot delete data which not yours"})
        if qs.asn_status == 0:
            # 还未下单的采购单, 只需删除关联的采购单明细
            for asnDetails in qs.asn_details.all():
                asnDetails.is_delete = True
                asnDetails.save()
        else:
            '''
            已经下单的采购单，需要删除的信息
            1. 关联的采购明细 AsnDetailModel
            2. 采购明细关联的库存 Stock
            3. 采购单关联的订单 AsnOrder
            '''
            for asnDetails in qs.asn_details.all():
                stock_model = asnDetails.stock
                if stock_model:
                    asnDetails.stock = None
                    asnDetails.save()
                    stock_model.delete()
                asnDetails.is_delete = True
                asnDetails.save()
            for asnOrder in qs.asn_order.all():
                asnOrder.is_delete = True
                asnOrder.save()

        qs.is_delete = True
        qs.save()
        serializer = self.get_serializer(qs, many=False)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=200, headers=headers)
    
    def _create(self, data):
        openid = self.request.META.get('HTTP_TOKEN')
        data['openid'] = openid
        if not data['asn_code']:
            qs_set = AsnListModel.objects.filter(openid=openid, is_delete=False)
            order_day = str(timezone.now().strftime('%Y%m%d'))
            if len(qs_set) > 0:
                asn_last_code = qs_set.order_by('-id').first().asn_code
                if str(asn_last_code[3:11]) == order_day:
                    order_create_no = str(int(asn_last_code[11:]) + 1)
                    data['asn_code'] = 'ASN' + order_day + order_create_no
                else:
                    data['asn_code'] = 'ASN' + order_day + '1'
            else:
                data['asn_code'] = 'ASN' + order_day + '1'
        data['bar_code'] = Md5.md5(data['asn_code'])
        serializer = self.get_serializer(data=data)
        if not serializer.is_valid():
            logger.info('Can not create asn object, data is invalid ', serializer.errors)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return instance

    def _update(self, instance, data):
        openid = self.request.META.get('HTTP_TOKEN')
        if instance.openid != openid:
            raise APIException({"detail": "Cannot partial_update data which not yours"})
        serializer = ASNListPostSerializer(instance, data=data, partial=data.get('partial', False))
        if not serializer.is_valid():
            logger.error("fail to update asn obj, data is not valid %s ", serializer.errors)
            raise APIException("fail to update asn obj, data is not valid")
        instance = serializer.save()
        return instance
    
    def _update_asn_details(self, instance, data):
        serializer = ASNDetailUpdateSerializer(instance, data=data,
                                               partial=data.get('partial', False))
        if not serializer.is_valid():
            msg = "asn detail, %s data  not valid "
            logger.error("asn detail, %s data  not valid %s", serializer.errors)
            raise APIException(msg)
        serializer.save()
        return serializer.data


class AsnDetailViewSet(viewsets.ModelViewSet):
    """
        retrieve:
            Response a data list（get）

        list:
            Response a data list（all）

        create:
            Create a data line（post）

        update:
            Update a data（put：update）
    """
    pagination_class = MyPageNumberPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter, ]
    ordering_fields = ['id', "create_time", "update_time", ]
    filter_class = AsnDetailFilter

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
                return AsnDetailModel.objects.filter(openid=openid, is_delete=False)
            else:
                return AsnDetailModel.objects.filter(openid=openid, id=id, is_delete=False)
        else:
            return AsnDetailModel.objects.none()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ASNDetailGetSerializer
        elif self.action in ['create']:
            return ASNDetailPostSerializer
        elif self.action in ['update']:
            return ASNDetailUpdateSerializer
        else:
            return self.http_method_not_allowed(request=self.request)

    def create(self, request, *args, **kwargs):
        raise NotImplementedError

    def partial_update(self, request, *args, **kwargs):
        qs = self.get_object()
        if qs.openid != self.request.META.get('HTTP_TOKEN'):
            raise APIException(
                {"detail": "Cannot partial_update data which not yours"})
        data = self.request.data
        serializer = self.get_serializer(qs, data=data, partial=True)
        if not serializer.is_valid():
            raise APIException("can not update object , data is invalid")
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=200, headers=headers)

    def update(self, request, *args, **kwargs):
       raise NotImplementedError


class AsnViewPrintViewSet(viewsets.ModelViewSet):
    """
        retrieve:
            Response a data list（get）
    """
    pagination_class = MyPageNumberPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter, ]
    ordering_fields = ['id', "create_time", "update_time", ]
    filter_class = AsnListFilter

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
                return AsnListModel.objects.filter(openid=openid, is_delete=False)
            else:
                return AsnListModel.objects.filter(openid=openid, id=id, is_delete=False)
        else:
            return AsnListModel.objects.none()

    def get_serializer_class(self):
        if self.action in ['retrieve']:
            return ASNDetailGetSerializer
        else:
            return self.http_method_not_allowed(request=self.request)

    def retrieve(self, request, pk):
        raise NotImplementedError


class FileListDownloadView(viewsets.ModelViewSet):
    renderer_classes = (FileListRenderCN, ) + tuple(api_settings.DEFAULT_RENDERER_CLASSES)
    filter_backends = [DjangoFilterBackend, OrderingFilter, ]
    ordering_fields = ['id', "create_time", "update_time", ]
    filter_class = AsnListFilter

    def get_project(self):
        try:
            id = self.kwargs.get('pk')
            return id
        except:
            return None

    def get_queryset(self):
        openid = self.request.META.get('HTTP_TOKEN')
        if openid:
            empty_qs = AsnListModel.objects.filter(Q(openid=openid, asn_status=1, is_delete=False) & Q(supplier=''))
            cur_date = timezone.now()
            date_check = relativedelta(day=1)
            if len(empty_qs) > 0:
                for i in range(len(empty_qs)):
                    if empty_qs[i].create_time <= cur_date - date_check:
                        empty_qs[i].delete()
            id = self.get_project()
            if id is None:
                return AsnListModel.objects.filter(Q(openid=openid, is_delete=False) & ~Q(supplier=''))
            else:
                return AsnListModel.objects.filter(Q(openid=openid, id=id, is_delete=False) & ~Q(supplier=''))
        else:
            return AsnListModel.objects.none()

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
        response['Content-Disposition'] = "attachment; filename='asnlist_{}.csv'".format(str(dt.strftime('%Y%m%d%H%M%S%f')))
        return response

class FileDetailDownloadView(viewsets.ModelViewSet):
    serializer_class = FileDetailRenderSerializer
    renderer_classes = (FileDetailRenderCN, ) + tuple(api_settings.DEFAULT_RENDERER_CLASSES)
    filter_backends = [DjangoFilterBackend, OrderingFilter, ]
    ordering_fields = ['id', "create_time", "update_time", ]
    filter_class = AsnDetailFilter

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
                return AsnDetailModel.objects.filter(openid=openid, is_delete=False)
            else:
                return AsnDetailModel.objects.filter(openid=openid, id=id, is_delete=False)
        else:
            return AsnDetailModel.objects.none()

    def get_serializer_class(self):
        if self.action == 'list':
            return FileDetailRenderSerializer
        else:
            return self.http_method_not_allowed(request=self.request)

    def get_lang(self, data):
        lang = self.request.META.get('HTTP_LANGUAGE')
        if lang:
            if lang == 'zh-hans':
                return FileDetailRenderCN().render(data)
            else:
                return FileDetailRenderEN().render(data)
        else:
            return FileDetailRenderEN().render(data)

    def list(self, request, *args, **kwargs):
        from datetime import datetime
        dt = datetime.now()
        data = (
            FileDetailRenderSerializer(instance).data
            for instance in self.filter_queryset(self.get_queryset())
        )
        renderer = self.get_lang(data)
        response = StreamingHttpResponse(
            renderer,
            content_type="text/csv"
        )
        response['Content-Disposition'] = "attachment; filename='asndetail_{}.csv'".format(str(dt.strftime('%Y%m%d%H%M%S%f')))
        return response


class AsnOrderView(viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend, OrderingFilter, ]
    ordering_fields = ['id', "create_time", "update_time", ]
    filter_class = AsnOrderFilter

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
                return AsnOrder.objects.filter(openid=openid, is_delete=False)
            else:
                return AsnOrder.objects.filter(openid=openid, id=id, is_delete=False)
        else:
            return AsnOrder.objects.none()

    def get_serializer_class(self):
        if self.action in ['list']:
            return AsnOrderSerializer
        if self.action in ['create','update', 'partial_update']:
            return AsnOrderPostSerializer
        else:
            return self.http_method_not_allowed(request=self.request)
    
    def create(self, request, *args, **kwargs):
        openid = self.request.META.get('HTTP_TOKEN')
        data = self.request.data
        print("create asn order ", data)
        logger.debug("create asn order ", data)
        data['openid'] = openid
        serializer = self.get_serializer(data=data)
        if not serializer.is_valid():
            print(serializer.errors)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=200, headers=self.get_success_headers(serializer.data))

    def update(self, request, *args, **kwargs):
        qs = self.get_object()
        openid = self.request.META.get('HTTP_TOKEN')
        if qs.openid != openid:
            raise APIException(
                {"detail": "Cannot update asn order which not yours"})
        data = self.request.data
        print("update asn order ", data)
        partial = True if data['partial'] else False
        serializer = self.get_serializer(qs, data=data, partial=partial)
        if not serializer.is_valid():
            print(serializer.errors)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=200, headers=self.get_success_headers(serializer.data))
        

