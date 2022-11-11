from django.urls import path, re_path
from . import views

urlpatterns = [
path(r'', views.GlobalProductView.as_view({"get": "list", "post": "create"}), name="product"),
path(r'claim', views.GlobalProductView.as_view({"post": "claim_global_product"}), name="claim_global_product"),
path(r'media', views.GlobalProductView.as_view({"post": "publish_media"}), name="publish_media"),
path(r'product/clone', views.GlobalProductView.as_view({"post": "clone_product"}), name="clone_product"),
path(r'product/shop', views.GlobalProductView.as_view({"get": "get_shop_product"}), name="shop_product"),
path(r'product/price', views.GlobalProductView.as_view({"get": "get_price", "post": "update_price"}), name="product_price"),
path(r'product/publish', views.GlobalProductView.as_view({"post": "publish_to_shopee"}), name="product_publish_shopee"),
path(r'product/delete', views.GlobalProductView.as_view({"post": "delete_batch"}), name="product_delete_batch"),
re_path(r'^product/(?P<pk>\d+)/$', views.GlobalProductView.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
}), name="product_1"),
]
