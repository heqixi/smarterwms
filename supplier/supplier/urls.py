from django.urls import path, re_path
from . import views

urlpatterns = [
path(r'', views.APIViewSet.as_view({"get": "list", "post": "create"}), name="supplier"),
path(r'all', views.APIViewSet.as_view({"get": "get_all_supplier"}), name="get_all_supplier"),
path(r'purchase/', views.PurchasePlanView.as_view({"get": "list", "post": "update"}), name="purchase"),
path(r'purchase/goods', views.PurchasePlanView.as_view({"get": "get_goods", "post": "update"}), name="get_goods"),
path(r'purchase/set_default', views.PurchasePlanView.as_view({"post": "set_default_purchase"}), name="purchase_set_default"),
path(r'file/', views.FileDownloadView.as_view({"get": "list"}), name="supplierfiledownload"),
re_path(r'^(?P<pk>\d+)/$', views.APIViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
}), name="supplier_1"),
re_path(r'^purchase/(?P<pk>\d+)/$', views.PurchasePlanView.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
}), name="supplier_1")

]
