from django.urls import path
from . import views

urlpatterns = [

    # Order
    path(r'', views.Order.as_view({"get": "list"}), name="order_list"),
    path(r'details', views.Order.as_view({"get": "get_order_details"}), name="order_details"),
    path(r'remark', views.Order.as_view({"post": "remark"}), name="order_remark"),
    path(r'apply_logistics', views.Order.as_view({"post": "apply_logistics"}), name="logistics_apply"),
    path(r'get_order_logistics_file', views.get_order_logistics_file, name="logistics_file"),
    path(r'stock_matching', views.Order.as_view({"post": "stock_matching"}), name="stock_matching"),
    path(r'sync', views.Order.as_view({"post": "sync"}), name="order_sync"),
    path(r'sync/shipment', views.Order.as_view({"post": "sync_shipment_list"}), name="sync_shipment_list"),
    path(r'shipment', views.Order.as_view({"post": "shipment"}), name="shipment"),
    path(r'forced_shipment', views.Order.as_view({"post": "forced_shipment"}), name="forced_shipment"),
    path(r'partially_shipment', views.Order.as_view({"post": "partially_shipment"}), name="partially_shipment"),
    path(r'modify', views.Order.as_view({"post": "order_modify"}), name="order_modify"),
    path(r'modify/delete', views.Order.as_view({"post": "delete_order_modify"}), name="delete_order_modify"),
    path(r'modify/change_goods', views.Order.as_view({"post": "change_goods"}), name="change_goods"),
    path(r'modify/freed_stock', views.Order.as_view({"post": "freed_stock"}), name="freed_stock"),
    path(r'modify/freed_model_stock', views.Order.as_view({"post": "freed_model_stock"}), name="freed_model_stock"),
    path(r'modify/model_stock_matching', views.Order.as_view({"post": "model_stock_matching"}), name="model_stock_matching"),

    path(r'package/toggle', views.Order.as_view({"post": "toggle_package"}), name="toggle_package"),
    path(r'package/cancel', views.Order.as_view({"post": "cancel_package"}), name="toggle_package"),

    # Order Record
    path(r'record', views.OrderRecord.as_view({"get": "list"}), name="order_record_list"),
]
