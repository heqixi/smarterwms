import base64
import logging
import os
import traceback

from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework import viewsets

from fetchbox.models import FetchProductModel, FetchMediaModel
from fetchbox.page import MyPageNumberPagination
from rest_framework.filters import OrderingFilter

from fetchbox.serializers import FetchProductGetSerializer
from fetchbox.services.fetchservice import FetchService
from smarterwms.settings import BASE_DIR
from utils import spg

logger = logging.getLogger()


class Fetch(viewsets.ModelViewSet):
    pagination_class = MyPageNumberPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['id', "create_time", "update_time"]
    serializer_class = FetchProductGetSerializer
    fetch_service = FetchService.get_instance()

    def get_queryset(self):
        params = spg.parse_params(self.request)
        openid = self.request.META.get('HTTP_TOKEN')
        kwargs = {'openid': openid}
        name = params.get('name')
        if name:
            kwargs['name__contains'] = name
        return FetchProductModel.objects.filter(**kwargs).order_by('-id')

    def check_repeat(self, request):
        try:
            params = spg.parse_params(request)
            url = params.get('url')
            openid = self.request.META.get('HTTP_TOKEN')
            return HttpResponse(FetchProductModel.objects.filter(url=url, openid=openid).count(), status=200)
        except Exception as e:
            logger.error("check_repeat error: %s\n%s", e, traceback.format_exc())
            return HttpResponse('check_repeat error: %s' % e, content_type='text/html', status=500)

    def receive_product(self, request):
        try:
            params = spg.parse_params(request)
            fetch_list = params.get('fetch_list')
            openid = self.request.META.get('HTTP_TOKEN')
            creater = self.request.META.get('HTTP_OPERATOR')
            product_ids = []
            for fetch_id in fetch_list:
                product = self.fetch_service.receive_product(openid, creater, fetch_id)
                product_ids.append(product.id)
            print('receive product ', product_ids)
            return Response(product_ids, status=200)
        except Exception as e:
            logger.error("receive product error: %s\n%s", e, traceback.format_exc())
            return HttpResponse('receive product error: %s' % e, content_type='text/html', status=500)

    def fetch_product(self, request):
        try:
            params = spg.parse_params(request)
            openid = self.request.META.get('HTTP_TOKEN')
            fetch_data_list = params.get('fetch_data_list')
            refresh = params.get('refresh')
            if refresh == 1:
                self.fetch_service.fetch_product(openid, fetch_data_list, True)
            else:
                self.fetch_service.fetch_product(openid, fetch_data_list)
            return HttpResponse('fetch product success', status=200)
        except Exception as e:
            logger.error("fetch product error: %s\n%s", e, traceback.format_exc())
            return HttpResponse('fetch product error: %s' % e, content_type='text/html', status=500)

    def get_fetch_medias(self, request):
        try:
            params = spg.parse_params(request)
            fetch_id = params.get('fetch_id')
            openid = self.request.META.get('HTTP_TOKEN')
            medias = FetchMediaModel.objects.filter(openid=openid, product=fetch_id)
            return HttpResponse(spg.to_json_str(spg.django_model_to_dict(model_list=medias)), content_type='application/json', status=200)
        except Exception as e:
            logger.error("get fetch medias error: %s\n%s", e, traceback.format_exc())
            return HttpResponse('get fetch medias error: %s' % e, content_type='text/html', status=500)

    def fetch_file(self, request):
        params = spg.parse_params(request)
        base64_str = params.get('base64')
        filename = params.get('filename')
        if base64_str:
            dir = os.path.join(BASE_DIR, 'logs')
            logger.info('dir: %s', dir)
            with open(os.path.join(dir, filename), 'wb+') as f:
                f.write(base64.b64decode(base64_str))
        return HttpResponse('upload file success', status=200)

