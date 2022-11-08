from django_filters import FilterSet
from .models import ListModel, PurchasePlan


class Filter(FilterSet):
    class Meta:
        model = ListModel
        fields = {
            "id": ['exact', 'gt', 'gte', 'lt', 'lte', 'isnull', 'in', 'range'],
            "supplier_name": ['exact', 'iexact', 'contains', 'icontains'],
            "supplier_city": ['exact', 'iexact', 'contains', 'icontains'],
            "supplier_address": ['exact', 'iexact', 'contains', 'icontains'],
            "supplier_contact": ['exact', 'iexact', 'gt', 'gte', 'lt', 'lte', 'isnull', 'in', 'range'],
            "supplier_manager": ['exact', 'iexact', 'contains', 'icontains'],
            "supplier_level": ['exact', 'iexact', 'gt', 'gte', 'lt', 'lte', 'isnull', 'in', 'range'],
            "creater": ['exact', 'iexact', 'contains', 'icontains'],
            "is_delete": ['exact', 'iexact'],
            "create_time": ['year', 'month', 'day', 'week_day', 'gt', 'gte', 'lt', 'lte', 'range'],
            "update_time": ['year', 'month', 'day', 'week_day', 'gt', 'gte', 'lt', 'lte', 'range']
        }


class PurchasePlanFilter(FilterSet):
    class Meta:
        model = PurchasePlan
        fields = {
            "id": ['exact', 'gt', 'gte', 'lt', 'lte', 'isnull', 'in', 'range'],
            "supplier__id": ['exact', 'gt', 'gte', 'lt', 'lte', 'isnull', 'in', 'range'],
            "price": ['exact', 'gt', 'gte', 'lt', 'lte', 'isnull', 'in', 'range'],
            "url": ['exact', 'iexact', 'contains', 'icontains'],
            "tag": ['exact', 'iexact', 'contains', 'icontains'],
            "default": ['exact', 'iexact', 'contains', 'icontains'],
            "creater": ['exact', 'iexact', 'contains', 'icontains'],
            "is_delete": ['exact', 'iexact'],
            "create_time": ['year', 'month', 'day', 'week_day', 'gt', 'gte', 'lt', 'lte', 'range'],
            "update_time": ['year', 'month', 'day', 'week_day', 'gt', 'gte', 'lt', 'lte', 'range']
        }

