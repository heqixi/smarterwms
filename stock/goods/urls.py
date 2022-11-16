from django.urls import path, re_path
from . import views

urlpatterns = [
path(r'', views.APIViewSet.as_view({"get": "list", "post": "create"}), name="goods"),
path(r'tag/', views.GoodsTagView.as_view({"get": "list", "post": "create", 'put': 'update'}), name="goodsTag"),
re_path(r'tag/^(?P<pk>\d+)/', views.GoodsTagView.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
}), name="goods_tags_1"),
re_path(r'^(?P<pk>\d+)/', views.APIViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
}), name="goods_1"),
path(r'^(P<extra>\)', views.APIViewSet.as_view({"get": "list"}), name="goods_2"),
    path(r'goodstag/<str:bar_code>/',views.SannerGoodsTagView.as_view({"get":"retrieve"}))
]
