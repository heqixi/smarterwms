import logging
from collections.abc import Sequence

from django.db.models import Q
from rest_framework import viewsets

from publish.models import ProductCategory, ProductCategoryAttribute, ProductCategoryBrand
from store.services.global_service import GlobalService
from store.services.product_service import ProductService
from .models import ListModel, ShopeeCategory, ShopeeAttribute, ShopeeAttributeValue, ShopeeCategoryTemplate, \
    ShopeeCategoryTemplateAttribute
from . import serializers
from utils.page import MyPageNumberPagination
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from .filter import Filter
from rest_framework.exceptions import APIException

from .serializers import ShopeeCategorySerializer, ShopeeAttributeGetSerializer, ShopeeAttributePostSerializer, \
    ShopeeAttributeValuePostSerializer, ShopeeCategoryTemplateSerializer, ShopeeCategoryTemplateAttributeSerializer, \
    ProductCategoryPostSerializer, ProductCategoryBrandPostSerializer, ProductAttributePostSerializer
from .services.shopee import CategoryService

logger = logging.getLogger()


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
    pagination_class = MyPageNumberPagination
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
        if self.action in ['list', 'retrieve', 'destroy']:
            return serializers.GoodsclassGetSerializer
        elif self.action in ['create']:
            return serializers.GoodsclassPostSerializer
        elif self.action in ['update']:
            return serializers.GoodsclassUpdateSerializer
        elif self.action in ['partial_update']:
            return serializers.GoodsclassPartialUpdateSerializer
        else:
            return self.http_method_not_allowed(request=self.request)

    def create(self, request, *args, **kwargs):
        data = self.request.data
        data['openid'] = self.request.META.get('HTTP_TOKEN')
        if ListModel.objects.filter(openid=data['openid'], goods_class=data['goods_class'], is_delete=False).exists():
            raise APIException({"detail": "Data exists"})
        else:
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            headers = self.get_success_headers(serializer.data)
            print("Headers....", headers)
            return Response(serializer.data, status=200, headers=headers)

    def update(self, request, pk):
        qs = self.get_object()
        if qs.openid != request.META.get('HTTP_TOKEN'):
            raise APIException({"detail": "Cannot update data which not yours"})
        else:
            data = self.request.data
            serializer = self.get_serializer(qs, data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=200, headers=headers)

    def partial_update(self, request, pk):
        qs = self.get_object()
        print("qs", qs)
        if qs.openid != request.META.get('HTTP_TOKEN'):
            print("Cannot partial_update data which not yours")
            raise APIException({"detail": "Cannot partial_update data which not yours"})
        else:
            print("partial_update user ok")
            data = self.request.data
            serializer = self.get_serializer(qs, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            print("partial_update before save")
            serializer.save()
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=200, headers=headers)

    def destroy(self, request, pk):
        print("destory object ", request, ", pk", pk)
        qs = self.get_object()
        openid = self.request.META.get('HTTP_TOKEN')
        if qs.openid != openid:
            raise APIException({"detail": "Cannot delete data which not yours"})
        else:
            qs.is_delete = True
            qs.save()
            serializer = self.get_serializer(qs, many=False)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=200, headers=headers)


class ShopeeCategoryView(viewsets.ModelViewSet):
    ordering_fields = ['id', "create_time", "update_time", ]

    def get_project(self):
        try:
            id = self.kwargs.get('pk')
            return id
        except:
            return None

    def get_queryset(self):
        print("goods media get queryset")
        openid = self.request.META.get('HTTP_TOKEN')
        if openid:
            id = self.get_project()
            if id is None:
                return ShopeeCategory.objects.filter(openid=openid)
            else:
                return ShopeeCategory.objects.filter(openid=openid, id=id)
        else:
            raise APIException('Please offer openid')

    def get_serializer_class(self):
        if self.action in ['list', 'restrieve', 'destroy', 'get_root', 'get_subcategory']:
            return serializers.ShopeeCategoryGetSerializer
        elif self.action in ['create', 'update']:
            return serializers.ShopeeCategorySerializer
        else:
            return self.http_method_not_allowed(request=self.request)

    def create(self, request, *args, **kwargs):
        data = self.request.data
        if isinstance(self.request.data, Sequence):
            data = [data]
        if len(data) == 0:
            raise APIException({"detail": 'empty data'})
        save_data = []
        for category in data:
            serializer = ShopeeCategorySerializer(data=category)
            if not serializer.is_valid():
                raise APIException("Can not create shopee category, data is invalid")
            serializer.save()
            save_data.append(serializer.data)
        headers = self.get_success_headers("success")
        return Response(save_data, status=200, headers=headers)

    def update(self, request, pk):
        pass

    def partial_update(self, request, pk):
        pass

    def destroy(self, request, pk):
        raise APIException('Delete Shopee Category not implement !')

    def get_root(self, request):
        merchant_id = self.request.query_params.get('merchant_id', None)
        roots = ShopeeCategory.objects.filter(merchant_id=merchant_id, parent=None)
        if roots.count() <= 0:
            self.refresh_shopee_cateogry(self.request)
            roots = ShopeeCategory.objects.filter(merchant_id=merchant_id, parent=None)

        serializer = self.get_serializer(roots, many=True)
        data = serializer.data
        return Response(data, status=200)

    def get_subcategory(self, request):
        merchant_id = self.request.query_params.get('merchant_id', None)
        parent_id = self.request.query_params.get('id', None)
        sub_categories = ShopeeCategory.objects.filter(merchant_id=merchant_id, parent_id=parent_id)
        serializer = self.get_serializer(sub_categories, many=True)
        return Response(serializer.data, status=200)

    def get_category_attribute(self, request):
        merchant_id = self.request.query_params.get('merchant_id', None)
        category_id = self.request.query_params.get('id', None)
        brands = self.request.query_params.get('brands', None)
        openid = self.request.META.get('HTTP_TOKEN')
        result = {}
        if brands:
            brands = CategoryService.get_instance().get_category_brand(openid, merchant_id, category_id)
            result['brands'] = brands
        attributes = CategoryService.get_instance().get_category_attribute(openid, merchant_id, category_id)
        result['attributes'] = attributes
        return Response(result, status=200)

    def get_category_brands(self, request):
        merchant_id = self.request.query_params.get('merchant_id', None)
        category_id = self.request.query_params.get('id', None)
        openid = self.request.META.get('HTTP_TOKEN')
        brands = CategoryService.get_instance().get_category_brand(openid, merchant_id, category_id)
        return Response(brands, status=200)

    def refresh_shopee_cateogry(self, request):
        merchant_id = self.request.query_params.get('merchant_id', None)
        openid = self.request.META.get('HTTP_TOKEN')
        creater = self.request.META.get('HTTP_OPERATOR')
        category_list = CategoryService.get_instance().refresh_shopee_cateogry(merchant_id, openid, creater)
        return Response(category_list, status=200)

    def create_or_update_category_template(self, request, *args, **kwargs):
        data = self.request.data
        logger.info('create or update category template %s', data)
        template_id = data.get('id', None)
        if template_id:
            template = ShopeeCategoryTemplate.objects.get(id=template_id)
            template_name = data.get('template_name', None)
            if template_name:
                template_of_name = ShopeeCategoryTemplate.objects.filter(merchant_id=template.merchant_id, template_name=template_name).first()
                if template_of_name and template_name.id != template.id:
                    msg = 'Template of name %s exist' % template_name
                    return Response(msg, status=501)
            serializer = ShopeeCategoryTemplateSerializer(template, data=data, partial=True)
        else:
            data['openid'] = self.request.META.get('HTTP_TOKEN')
            data['creater'] = self.request.META.get('HTTP_OPERATOR')
            merchant_id = data.get('merchant_id', None)
            if not merchant_id:
                raise APIException('Missing merchant id, Can not save category template %s' % data)
            template_name = data.get('template_name', None)
            if not template_name:
                raise APIException('Missing template name, Can not save category template %s' % data)
            template_of_name = ShopeeCategoryTemplate.objects.filter(merchant_id=merchant_id, template_name=template_name).first()
            if template_of_name:
                msg = 'Template of name %s exist' % template_name
                return Response(msg, status=501)
            serializer = ShopeeCategoryTemplateSerializer(data=data)
        if not serializer.is_valid():
            raise APIException('Can not update or save template %s' % serializer.errors)
        instance = serializer.save()
        attributes = data.get('attributes', None)
        valid_attributes_id = [attribute['attribute_id'] for attribute in attributes]
        ShopeeCategoryTemplateAttribute.objects \
            .filter(Q(category_id=instance.id) & ~Q(attribute_id__in=valid_attributes_id)).delete()
        attribute_values_info = data.get('attribute_values', None)
        if attribute_values_info:
            self._create_or_update_template_attribute(instance, attribute_values_info)
        cateogory = CategoryService.get_instance().serialize_category_template(instance)
        return Response(cateogory, status=200)

    def _create_or_update_template_attribute(self, category: ShopeeCategoryTemplate, attribute_values_info: dict):
        for attribute_value in attribute_values_info:
            id = attribute_value.get('id', None)
            attribute_value_instance = None
            if id:
                attribute_value_instance = ShopeeCategoryTemplateAttribute.objects.get(id=id)
                if attribute_value.get('is_delete', False):
                    attribute_value_instance.delete()
                    continue
            if not attribute_value.get('multiple', False):
                attribute_id = attribute_value.get('attribute_id', None)
                if not attribute_id:
                    raise Exception('Fail to save  tample attribute value, missing attribute id %s ' % attribute_value)
                attribute_value_instance = ShopeeCategoryTemplateAttribute.objects\
                    .filter(openid=category.openid, category_id=category.id, attribute_id=attribute_id).first()
            if attribute_value_instance:
                serializer = ShopeeCategoryTemplateAttributeSerializer(attribute_value_instance, data=attribute_value, partial=True)
            else:
                if not category:
                    raise APIException('Can not save category attribute, missing category')
                attribute_value['category'] = category.id
                attribute_value['openid'] = category.openid
                attribute_value['creater'] = category.creater
                serializer = ShopeeCategoryTemplateAttributeSerializer(data=attribute_value)
            if not serializer.is_valid():
                logger.error('Fail to save category attribute %s' % serializer.errors)
                raise APIException('Fail to save category attribute')
            serializer.save()

    def get_category_template(self, request):
        merchant_id = self.request.query_params.get('merchant_id', None)
        openid = self.request.META.get('HTTP_TOKEN')
        category_templates = CategoryService.get_instance().get_category_template(openid=openid, merchant_id=merchant_id)
        return Response(category_templates, status=200)

    def build_shopee_category_tree(self, category_list):
        pass




