from django_filters import FilterSet
from .models import GlobalProduct


class GlobalProductFilter(FilterSet):
    class Meta:
        model = GlobalProduct
        fields = {
            "id": ['exact', 'iexact', 'gt', 'gte', 'lt', 'lte', 'isnull', 'in', 'range'],
            "sku": ['exact', 'iexact', 'contains', 'icontains'],
            "name": ['exact', 'iexact', 'contains', 'icontains'],
            "desc": ['exact', 'iexact', 'contains', 'icontains'],
            "status": ['exact', 'iexact', 'contains', 'icontains', 'in'],
            "image": ['exact', 'iexact', 'contains', 'icontains'],
            "creater": ['exact', 'iexact', 'contains', 'icontains'],
            "is_delete": ['exact', 'iexact'],
            "create_time": ['year', 'month', 'day', 'week_day', 'gt', 'gte', 'lt', 'lte', 'range'],
            "update_time": ['year', 'month', 'day', 'week_day', 'gt', 'gte', 'lt', 'lte', 'range']
        }
