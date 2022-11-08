from django.urls import path
from . import views

urlpatterns = [
    path(r'', views.Fetch.as_view({"get": "list"}), name="fetch_list"),
    path(r'receive', views.Fetch.as_view({"post": "receive_product"}), name="receive_product"),
    path(r'check_repeat', views.Fetch.as_view({"get": "check_repeat"}), name="check_repeat"),
    path(r'upload', views.Fetch.as_view({'post': 'fetch_product'}), name="fetch_upload"),
    path(r'upload/file', views.Fetch.as_view({'post': 'fetch_file'}), name="fetch_file"),
    path(r'medias', views.Fetch.as_view({'get': 'get_fetch_medias'}), name="get_fetch_medias"),
]
