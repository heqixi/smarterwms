
from collections import OrderedDict

from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response


class GoodsCursorPagination(LimitOffsetPagination):
    default_limit = 30
    limit_query_param = 'limit'
    offset_query_param = "offset"
    max_limit = 1000
    ordering ='-create_time'

    def get_paginated_response(self, data):
        res = Response(OrderedDict([
            ('count', self.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))
        return res


class GlobalProductLimitPagination(LimitOffsetPagination):
    default_limit = 30
    limit_query_param = 'limit'
    offset_query_param = "offset"
    max_limit = 1000
    ordering ='-create_time'

    def get_paginated_response(self, data):
        print('GoodsCursorPagination get_paginated_response')
        return Response(OrderedDict([
            ('count', self.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))