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
    path('shopee/publish/', include('publish.urls')),
    path('shopee/category/', include('category.urls')),
    path('store/', include('store.urls')),
    path('order/', include('order.urls')),
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

from store.gRpc.servers.protos.products import shopee_pb2_grpc
from store.gRpc.servers.services.shopee_service  import ProductService

def grpc_handlers(server):
    shopee_pb2_grpc.add_ProductServiceControllerServicer_to_server(ProductService.as_servicer(), server)




