from django.urls import path, re_path
from . import views

urlpatterns = [
path(r'list/', views.AsnListViewSet.as_view({"get": "list", "post": "create"}), name="asnlist"),
re_path(r'^list/(?P<pk>\d+)/$', views.AsnListViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
}), name="asnlist_1"),
re_path(r'amend/', views.AsnListViewSet.as_view({'post': 'amend_asn'}), name="asnlist_amend"),
path(r'order/', views.AsnOrderView.as_view({"get": "list", "post": "create"}), name="asnorder"),
re_path(r'^order/(?P<pk>\d+)/$', views.AsnOrderView.as_view({
    'get': 'retrieve',
    'put': 'update',
    'delete': 'destroy'
}), name="asorder_1"),
path(r'detail/', views.AsnDetailViewSet.as_view({"get": "list", "post": "create", 'put': 'update'}), name="asndetail"),
re_path(r'^detail/(?P<pk>\d+)/$', views.AsnDetailViewSet.as_view({
    'get': 'retrieve',
}), name="asndetail_1"),
re_path(r'^viewprint/(?P<pk>\d+)/$', views.AsnViewPrintViewSet.as_view({
    'get': 'retrieve',
}), name="asnviewprint_1"),
path(r'filelist/', views.FileListDownloadView.as_view({"get": "list"}), name="asnfilelistdownload"),
path(r'filedetail/', views.FileDetailDownloadView.as_view({"get": "list"}), name="asnfiledetaildownload"),
]
