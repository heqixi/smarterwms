from django_filters import FilterSet
from .models import StockListModel, StockBinModel

class StockListFilter(FilterSet):
    class Meta:
        model = StockListModel
        fields = {
            "id": ['exact', 'iexact', 'gt', 'gte', 'lt', 'lte', 'isnull', 'in', 'range'],
            "goods__goods_code": ['exact', 'iexact', 'contains', 'icontains'],
            "stock_status": ['exact', 'iexact', 'gt', 'gte', 'lt', 'lte', 'range'],
            "stock_qty": ['exact', 'iexact', 'gt', 'gte', 'lt', 'lte', 'range'],
            "create_time": ['year', 'month', 'day', 'week_day', 'gt', 'gte', 'lt', 'lte', 'range'],
            "update_time": ['year', 'month', 'day', 'week_day', 'gt', 'gte', 'lt', 'lte', 'range']
        }

class StockBinFilter(FilterSet):
    class Meta:
        model = StockBinModel
        fields = {
            "id": ['exact', 'iexact', 'gt', 'gte', 'lt', 'lte', 'isnull', 'in', 'range'],
            "stock__id":['exact', 'iexact', 'gt', 'gte', 'lt', 'lte', 'isnull', 'in', 'range'],
            "bin_name": ['exact', 'iexact', 'contains', 'icontains'],
            "bin_code": ['exact', 'iexact', 'contains', 'icontains'],
            "goods_qty": ['exact', 'iexact', 'gt', 'gte', 'lt', 'lte', 'range'],
            "bin_size": ['exact', 'iexact', 'contains', 'icontains'],
            "bin_property": ['exact', 'iexact', 'contains', 'icontains'],
            "t_code": ['exact', 'iexact'],
            "create_time": ['year', 'month', 'day', 'week_day', 'gt', 'gte', 'lt', 'lte', 'range'],
            "update_time": ['year', 'month', 'day', 'week_day', 'gt', 'gte', 'lt', 'lte', 'range']
        }
