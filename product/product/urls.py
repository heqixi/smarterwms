from django.urls import path, re_path
from . import views

urlpatterns = [
path(r'', views.GlobalProductView.as_view({"get": "list", "post": "create"}), name="product"),
path(r'clone', views.GlobalProductView.as_view({"post": "clone_product"}), name="clone_product"),
path(r'delete', views.GlobalProductView.as_view({"post": "delete_batch"}), name="product_delete_batch"),
path(r'bind_goods', views.GlobalProductView.as_view({"post": "bind_goods"}), name="product_bind_goods"),
path(r'unbind_goods', views.GlobalProductView.as_view({"post": "unbind_goods"}), name="product_unbind_goods"),
path(r'keyword_filter', views.GlobalProductView.as_view({"get": "get_keyword_filter"}), name="get_keyword_filter"),
re_path(r'^(?P<pk>\d+)/$', views.GlobalProductView.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
}), name="product_1")
]
