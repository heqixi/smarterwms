import json
from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.response import Response

from goodsunit.models import ListModel as goods_unit
from goodsclass.models import ListModel as goods_class
from goodsbrand.models import ListModel as goods_brand
from goodscolor.models import ListModel as goods_color
from goodsshape.models import ListModel as goods_shape
from goodsspecs.models import ListModel as goods_specs
from goodsorigin.models import ListModel as goods_origin
from .models import GoodsTag


class MyPageNumberPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = "max_page"
    max_page_size = 1000
    page_query_param = 'page'

    def get_paginated_response(self, data):
        goods_unit_list_data = goods_unit.objects.filter(
            openid=self.request.auth.openid, is_delete=False)
        goods_unit_list = []
        for i in range(len(goods_unit_list_data)):
            goods_unit_list.append(goods_unit_list_data[i].goods_unit)
        goods_class_list_data = goods_class.objects.filter(
            openid=self.request.auth.openid, is_delete=False)
        goods_class_list = []
        for i in range(len(goods_class_list_data)):
            goods_class_list.append(goods_class_list_data[i].goods_class)
        goods_brand_list_data = goods_brand.objects.filter(
            openid=self.request.auth.openid, is_delete=False)
        goods_brand_list = []
        for i in range(len(goods_brand_list_data)):
            goods_brand_list.append(goods_brand_list_data[i].goods_brand)
        goods_color_list_data = goods_color.objects.filter(
            openid=self.request.auth.openid, is_delete=False)
        goods_color_list = []
        for i in range(len(goods_color_list_data)):
            goods_color_list.append(goods_color_list_data[i].goods_color)
        goods_shape_list_data = goods_shape.objects.filter(
            openid=self.request.auth.openid, is_delete=False)
        goods_shape_list = []
        for i in range(len(goods_shape_list_data)):
            goods_shape_list.append(goods_shape_list_data[i].goods_shape)
        goods_specs_list_data = goods_specs.objects.filter(
            openid=self.request.auth.openid, is_delete=False)
        goods_specs_list = []
        for i in range(len(goods_specs_list_data)):
            goods_specs_list.append(goods_specs_list_data[i].goods_specs)
        goods_origin_list_data = goods_origin.objects.filter(
            openid=self.request.auth.openid, is_delete=False)
        goods_origin_list = []
        for i in range(len(goods_origin_list_data)):
            goods_origin_list.append(goods_origin_list_data[i].goods_origin)
        # TODO GOODS_DEPENDENCES
        # supplier_list_data = supplier.objects.filter(
        #     openid=self.request.auth.openid, is_delete=False)
        # supplier_list = []
        # for i in range(len(supplier_list_data)):
        #     supplier_list.append(
        #         {
        #             'supplier_name': supplier_list_data[i].supplier_name,
        #             'id': supplier_list_data[i].id
        #         })

        goods_tags_list = GoodsTag.objects.filter(
            openid=self.request.auth.openid, is_delete=False)
        tags_list = []
        for i in range(len(goods_tags_list)):
            tag_dict = {}
            tag_dict['id'] = goods_tags_list[i].id
            tag_dict['tag'] = goods_tags_list[i].tag
            goods_ids = []
            for goods in goods_tags_list[i].goods.all():
                goods_ids.append(goods.id)
            tag_dict['goods'] = goods_ids
            tags_list.append(tag_dict)

        return Response(OrderedDict([
            ('goods_unit_list', goods_unit_list),
            ('goods_class_list', goods_class_list),
            ('goods_brand_list', goods_brand_list),
            ('goods_color_list', goods_color_list),
            ('goods_shape_list', goods_shape_list),
            ('goods_specs_list', goods_specs_list),
            ('goods_origin_list', goods_origin_list),
            # ('supplier_list', supplier_list), TODO GOODS_DEPENDENCES
            ('tags_list', tags_list),
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))


class GoodsCursorPagination(LimitOffsetPagination):
    default_limit = 30
    limit_query_param = 'limit'
    offset_query_param = "offset"
    max_limit = 1000
    ordering ='-create_time'

    def get_paginated_response(self, data):
        from urllib.parse import urlparse
        print('get paginated response ', self.get_next_link(), self.get_previous_link())
        next_path = None
        if self.get_next_link():
            parsed_uri = urlparse(self.get_next_link())
            next_path = '{uri.path}?{uri.query}'.format(uri=parsed_uri)
        pre_path = None
        if self.get_previous_link():
            parsed_uri = urlparse(self.get_previous_link())
            pre_path = '{uri.path}?{uri.query}'.format(uri=parsed_uri)
        res = Response(OrderedDict([
            ('count', self.count),
            ('next', next_path),
            ('next_path', next_path),
            ('pre_path', pre_path),
            ('results', data)
        ]))
        print('get_paginated_response, count ', res.data['next'])
        return res

