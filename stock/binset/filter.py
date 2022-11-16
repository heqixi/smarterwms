from django_filters import FilterSet
from .models import ListModel

class Filter(FilterSet):
    class Meta:
        model = ListModel
        fields = {
            "id": ['exact', 'iexact', 'gt', 'gte', 'lt', 'lte', 'isnull', 'in', 'range', ],
            "bin_name": ['exact', 'iexact', 'contains', 'icontains'],
            "bin_size": ['exact', 'iexact', 'contains', 'icontains'],
            "bin_property": ['exact', 'iexact', 'contains', 'icontains'],
            "empty_label": ['exact', 'iexact'],
            "creater": ['exact', 'iexact', 'contains', 'icontains'],
            "is_delete": ['exact', 'iexact'],
            "create_time": ['year', 'month', 'day', 'week_day', 'gt', 'gte', 'lt', 'lte', 'range'],
            "update_time": ['year', 'month', 'day', 'week_day', 'gt', 'gte', 'lt', 'lte', 'range']
        }
