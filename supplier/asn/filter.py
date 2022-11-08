from django_filters import FilterSet
from .models import AsnListModel, AsnDetailModel, AsnOrder

class AsnListFilter(FilterSet):
    class Meta:
        model = AsnListModel
        fields = {
            "id": ['exact', 'iexact', 'gt', 'gte', 'lt', 'lte', 'isnull', 'in', 'range'],
            "asn_code": ['exact', 'iexact', 'contains', 'icontains'],
            "asn_status": ['exact', 'iexact',  'gt', 'gte', 'lt', 'lte', 'isnull', 'in', 'range'],
            "total_weight": ['exact', 'iexact', 'gt', 'gte', 'lt', 'lte', 'isnull', 'in', 'range'],
            "total_cost": ['exact', 'iexact', 'gt', 'gte', 'lt', 'lte', 'isnull', 'in', 'range'],
            "supplier__id": ['exact', 'iexact', 'contains', 'icontains'],
            "creater": ['exact', 'iexact', 'contains', 'icontains'],
            "is_delete": ['exact', 'iexact'],
            "create_time": ['exact', 'iexact', 'year', 'month', 'day', 'week_day', 'gt', 'gte', 'lt', 'lte', 'range'],
            "update_time": ['exact', 'iexact', 'year', 'month', 'day', 'week_day', 'gt', 'gte', 'lt', 'lte', 'range']
        }

class AsnDetailFilter(FilterSet):
    class Meta:
        model = AsnDetailModel
        fields = {
            "id": ['exact', 'gt', 'gte', 'lt', 'lte', 'isnull', 'in', 'range'],
            "asn__id": ['exact', 'iexact', 'contains', 'icontains'],
            "goods__id": ['exact', 'iexact', 'contains', 'icontains'],
            "goods_qty": ['exact', 'iexact', 'gt', 'lt', 'gte', 'lte'],
            "goods_actual_qty": ['exact', 'iexact', 'gt', 'lt', 'gte', 'lte'],
            "goods_shortage_qty": ['exact', 'iexact', 'gt', 'lt', 'gte', 'lte'],
            "goods_more_qty": ['exact', 'iexact', 'gt', 'lt', 'gte', 'lte'],
            "goods_damage_qty": ['exact', 'iexact', 'gt', 'lt', 'gte', 'lte'],
            "goods_cost": ['exact', 'iexact', 'gt', 'gte', 'lt', 'lte', 'isnull', 'in', 'range'],
            "creater": ['exact', 'iexact', 'contains', 'icontains'],
            "is_delete": ['exact', 'iexact'],
            "create_time": ['year', 'month', 'day', 'week_day', 'gt', 'gte', 'lt', 'lte', 'range'],
            "update_time": ['year', 'month', 'day', 'week_day', 'gt', 'gte', 'lt', 'lte', 'range']
        }

class AsnOrderFilter(FilterSet):
    class Meta:
        model = AsnOrder
        fields = {
            "id": ['exact', 'gt', 'gte', 'lt', 'lte', 'isnull', 'in', 'range'],
            "asn__id": ['exact', 'iexact', 'contains', 'icontains'],
            "url": ['exact', 'iexact', 'contains', 'icontains'],
            "delivery_date": ['year', 'month', 'day', 'week_day', 'gt', 'gte', 'lt', 'lte', 'range'],
            "trans_name": ['exact', 'iexact', 'contains', 'icontains'],
            "trans_url": ['exact', 'iexact', 'contains', 'icontains'],
            "trans_phone": ['exact', 'iexact', 'contains', 'icontains'],
            "creater": ['exact', 'iexact', 'contains', 'icontains'],
            "is_delete": ['exact', 'iexact'],
            "create_time": ['year', 'month', 'day', 'week_day', 'gt', 'gte', 'lt', 'lte', 'range'],
            "update_time": ['year', 'month', 'day', 'week_day', 'gt', 'gte', 'lt', 'lte', 'range']
        }
