from django.contrib import admin
from django.conf import settings
from django.urls import path, include, re_path
from django.views.generic.base import TemplateView
from django.contrib.staticfiles.views import serve
from django.views.static import serve as static_serve
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from . import views

schema_view = get_schema_view(
    openapi.Info(
        title="SmarterWMS--API Docs",
        default_version='v2.1.0',
        description=
        """
        openid:
            Openid is the only mark of your data group, You should add it to you request headers.token .
        """
        ,
        terms_of_service="https://www.56yhz.com/",
        license=openapi.License(name="Apache License 2.0"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


def return_static(request, path, insecure=True, **kwargs):
    return serve(request, path, insecure, **kwargs)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='dist/spa/index.html')),
    path('vcheck/', views.vcheck, name='vcheck'),
    path('myip/', views.myip, name='myip'),
    path('staff/', include('staff.urls')),
    path('binset/', include('binset.urls')),
    path('binsize/', include('binsize.urls')),
    path('binproperty/', include('binproperty.urls')),
    path('stock/', include('stock.urls')),
    path('goods/', include('goods.urls')),
    path('goodsunit/', include('goodsunit.urls')),
    path('goodsclass/', include('goodsclass.urls')),
    path('goodscolor/', include('goodscolor.urls')),
    path('goodsbrand/', include('goodsbrand.urls')),
    path('goodsshape/', include('goodsshape.urls')),
    path('goodsspecs/', include('goodsspecs.urls')),
    path('goodsorigin/', include('goodsorigin.urls')),
    path('goodsmedia/', include('goodsmedia.urls')),
    path('login/', include('userlogin.urls')),
    path('register/', include('userregister.urls')),

    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    re_path(r'^favicon\.ico$', views.favicon, name='favicon'),
    re_path('^css/.*$', views.css, name='css'),
    re_path('^js/.*$', views.js, name='js'),
    re_path('^statics/.*$', views.statics, name='statics'),
    re_path('^fonts/.*$', views.fonts, name='fonts'),
    re_path(r'^robots.txt', views.robots, name='robots'),
    re_path(r'^static/(?P<path>.*)$', return_static, name='static'),
    re_path(r'^media/(?P<path>.*)$', static_serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('docs/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc')
]

urlpatterns += [re_path(r'^silk/', include('silk.urls', namespace='silk'))]


from stock.gRpc.servers.services.StockBinService import StockBinService
from stock.gRpc.servers.protos import stock_bin_gen_pb2_grpc

from stock.gRpc.servers.protos.stock import stock_pb2_grpc
from stock.gRpc.servers.services.StockService import StockService

from goods.gRpc.server.protos import goods_pb2_grpc
from goods.gRpc.server.services.GoodsService import GoodsService


def grpc_handlers(server):
    stock_bin_gen_pb2_grpc.add_StockBinModelControllerServicer_to_server(StockBinService.as_servicer(), server)
    stock_pb2_grpc.add_StockControllerServicer_to_server(StockService.as_servicer(), server)
    goods_pb2_grpc.add_GoodsControllerServicer_to_server(GoodsService.as_servicer(), server)


