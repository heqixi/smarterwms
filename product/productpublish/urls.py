from django.urls import path,re_path

from . import views

urlpatterns = [
    # re_path(r'^(?P<pk>\d+)/$', views.EditPriceView.as_view({
    #     'get': 'retrieve',
    #     'put': 'update',
    #     'delete': 'destroy'
    # }), name="product_edit_price_1")
]
