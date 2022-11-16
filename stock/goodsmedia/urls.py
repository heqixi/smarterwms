from django.urls import path, re_path

from . import views

urlpatterns = [

    path(r'image/', views.MediaView.as_view({"get": "list", "post": "create"}), name='image'),

    path(r'', views.APIViewSet.as_view({"get":"list", "post":"create"}), name='goodsmedia'),
    path(r'upload/', views.APIViewSet.as_view({"post":"receivedFile"}), name='goodsmedia recieve'),
    re_path(r'^(?P<pk>\d+)/$', views.APIViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
}), name="goodsclass_1")

]
