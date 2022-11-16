from django.urls import path, re_path
from . import views

urlpatterns = [
path(r'', views.APIViewSet.as_view({"get": "list", "post": "create"}), name="goodsclass"),
# path(r'shopee', views.ShopeeCategoryView.as_view({"get": "list", "post": "create"}), name="shopee category"),
# path(r'shopee/refresh', views.ShopeeCategoryView.as_view({"get": "refresh_shopee_cateogry"}), name="shopee category_refresh"),
# path(r'shopee/root', views.ShopeeCategoryView.as_view({"get": "get_root"}), name="shopee category_get_root"),
# path(r'shopee/subcategory', views.ShopeeCategoryView.as_view({"get": "get_subcategory"}), name="shopee category_get_subcategory"),
# path(r'shopee/attribute', views.ShopeeCategoryView.as_view({"get": "get_category_attribute"}), name="shopee_get_category_attribute"),
# path(r'shopee/brands', views.ShopeeCategoryView.as_view({"get": "get_category_brands"}), name="shopee_get_category_brands"),
# path(r'shopee/category/template', views.ShopeeCategoryView.as_view({"get": "get_category_template", 'post': 'create_or_update_category_template'}), name="shopee_category_template"),
re_path(r'^(?P<pk>\d+)/$', views.APIViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
}), name="goodsclass_1")
]
