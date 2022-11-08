import json
import os

from django.conf import settings
from django.db import connection
from django.forms import model_to_dict
from django.http import QueryDict
from rest_framework.request import Request


# 查找本地订单物流面单
def search_order_bill(order_sn):
    shipping_doc_path = settings.SHOPEE.get('shipping_doc_path')
    for root, sub_dirs, files in os.walk(shipping_doc_path):
        for special_file in files:
            if special_file == (order_sn + '.pdf'):
                return os.path.join(root, special_file)
    return None


def to_json_str(obj):
    return json.dumps(obj)


def django_model_to_dict(model=None, model_list=None):
    if model is not None:
        return model_to_dict(model)
    elif model_list is not None:
        d_list = []
        for model in model_list:
            d_list.append(model_to_dict(model))
        return d_list
    else:
        raise ValueError('Missing model or model_list')


# parse django http params
def parse_params(request):
    if not isinstance(request, Request):
        return {}
    query_params = request.query_params
    if isinstance(query_params, QueryDict):
        query_params = query_params.dict()
    result_data = request.data
    if isinstance(result_data, QueryDict):
        result_data = result_data.dict()
    if query_params != {}:
        return query_params
    else:
        return result_data


def exec_sql(sql):
    with connection.cursor() as cursor:
        cursor.execute(sql)
        columns = [col[0] for col in cursor.description]
        data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return data