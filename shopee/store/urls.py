from django.urls import path, re_path
from . import views

urlpatterns = [
    # store routes
    path(r'', views.Store.as_view({"get": "list"}), name="store"),
    path(r'all/', views.Store.as_view({"get": "get_all_store"}), name="store_all"),
    path(r'auth/', views.Store.as_view({"get": "auth"}), name="auth"),
    path(r'refresh_token/', views.Store.as_view({"post": "refresh_token"}), name="refresh_token"),
    path(r'callback/', views.callback, name="callback"),
    re_path(r'^(?P<pk>\d+)/$', views.Store.as_view({
        'delete': 'destroy'
    }), name="staff_1"),

    # product routes
    path(r'discounts/', views.Store.as_view({"get": "get_discounts_list"}), name="store_discount"),
    path(r'product/', views.StoreProduct.as_view({"get": "list"}), name="product"),
    path(r'product/status', views.StoreProduct.as_view({"get": "get_prodcut_list"}), name="get_prodcut_list"),
    path(r'product/detail', views.StoreProduct.as_view({"get": "detail"}), name="product_detail"),
    path(r'product/sync', views.StoreProduct.as_view({"post": "sync"}), name="sync_product"),
    path(r'product/discount', views.StoreProduct.as_view({"post": "update_discount"}), name="update_discount"),
    # Global Product
    path(r'global/', views.StoreGlobalProduct.as_view({"get": "list"}), name="global_product"),
    path(r'global/delete', views.StoreGlobalProduct.as_view({"post": "delete"}), name="delete_global_product"),
    path(r'global/sync', views.StoreGlobalProduct.as_view({"post": "sync_global"}), name="sync_global_product"),
    path(r'global/update/global_sku', views.StoreGlobalProduct.as_view({"post": "update_global_sku"}), name="update_global_sku"),
    path(r'global/update/model_sku', views.StoreGlobalProduct.as_view({"post": "update_model_sku"}), name="update_model_sku"),
    path(r'global/details', views.StoreGlobalProduct.as_view(
        {"get": "get_global_product_details"}), name="get_global_details"),
    path(r'global/attributes', views.StoreGlobalProduct.as_view(
        {"get": "get_global_attributes"}), name="get_global_attributes"),
    path(r'global/brands', views.StoreGlobalProduct.as_view(
        {"get": "get_global_brands"}), name="get_global_brands"),
    path(r'global/category', views.StoreGlobalProduct.as_view({"get": "get_category"}), name="global_category"),

    path(r'package', views.StoreProductPackage.as_view({"get": "list"}), name="package_list"),
    path(r'package/new', views.StoreProductPackage.as_view({"post": "new_package"}), name="new_package"),
    path(r'package/remove', views.StoreProductPackage.as_view({"delete": "remove_package"}), name="remove_package"),
    path(r'area', views.RegionSettings.as_view({'get': 'list', 'post': 'create', 'delete': 'destroy'}),
         name="area_list")
]




