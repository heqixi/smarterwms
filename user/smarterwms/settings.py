from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
from django.core.management.utils import get_random_secret_key
get_random_secret_key()
SECRET_KEY = get_random_secret_key()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'base',
    'django_grpc_framework',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'staff.apps.StaffConfig',
    'userlogin.apps.UserloginConfig',
    'userprofile.apps.UserprofileConfig',
    'userregister.apps.UserregisterConfig',
    'throttle.apps.ThrottleConfig',
    'rest_framework',
    'django_filters',
    'silk',
    'drf_yasg',
    'corsheaders',
    'django_apscheduler'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'silk.middleware.SilkyMiddleware'
]
X_FRAME_OPTIONS = 'SAMEORIGIN'
ROOT_URLCONF = 'smarterwms.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'smarterwms.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases
# update
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'smarterwms-user',
        'USER': 'juyigou',
        'PASSWORD': '994821',
        'HOST': '127.0.0.1',
        'PORT': '5432'
    }
}



# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static_new').replace('\\', '/')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static').replace('\\', '/'),
]

PROFILE_LOG_BASE = os.path.join(BASE_DIR, 'stats_log').replace('\\', '/')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media').replace('\\', '/')

REST_FRAMEWORK = {
    # AttributeError: ‘AutoSchema’ object has no attribute ‘get_link’
    #'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.AutoSchema',
    # DEFAULT SET:
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.openapi.AutoSchema',
    # EXCEPTION:
    'EXCEPTION_HANDLER': 'utils.my_exceptions.custom_exception_handler',
    # Base API policies:
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework_csv.renderers.CSVRenderer',
        #'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser'
    ],
    # 'DEFAULT_AUTHENTICATION_CLASSES': ['utils.auth.Authtication', ],
    'DEFAULT_PERMISSION_CLASSES': ["utils.permission.Normalpermission", ],
    'DEFAULT_THROTTLE_CLASSES': ['utils.throttle.VisitThrottle', ],
    # 'DEFAULT_THROTTLE_RATES': ['utils.throttle.VisitThrottle', ],
    'DEFAULT_CONTENT_NEGOTIATION_CLASS': 'rest_framework.negotiation.DefaultContentNegotiation',
    'DEFAULT_METADATA_CLASS': 'rest_framework.metadata.SimpleMetadata',
    'DEFAULT_VERSIONING_CLASS': None,
    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    # 'PAGE_SIZE': 1,  # 默认 None
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        # 'django_filters.rest_framework.backends.DjangoFilterBackend',
    ],
    'SEARCH_PARAM': 'search',
    'ORDERING_PARAM': 'ordering',
    'NUM_PROXIES': None,
    # Versioning:
    'DEFAULT_VERSION': None,
    'ALLOWED_VERSIONS': None,
    'VERSION_PARAM': 'version',
    # Authentication:
    'UNAUTHENTICATED_USER': 'django.contrib.auth.models.AnonymousUser',
    'UNAUTHENTICATED_TOKEN': None,
    # View configuration:
    'VIEW_NAME_FUNCTION': 'rest_framework.views.get_view_name',
    'VIEW_DESCRIPTION_FUNCTION': 'rest_framework.views.get_view_description',
    'NON_FIELD_ERRORS_KEY': 'non_field_errors',
    # Testing
    'TEST_REQUEST_RENDERER_CLASSES': [
        'rest_framework.renderers.MultiPartRenderer',
        'rest_framework.renderers.JSONRenderer'
    ],
    'TEST_REQUEST_DEFAULT_FORMAT': 'multipart',
    # Hyperlink settings
    'URL_FORMAT_OVERRIDE': 'format',
    'FORMAT_SUFFIX_KWARG': 'format',
    'URL_FIELD_NAME': 'url',
    # Encoding
    'UNICODE_JSON': True,
    'COMPACT_JSON': True,
    'STRICT_JSON': True,
    'COERCE_DECIMAL_TO_STRING': True,
    'UPLOADED_FILES_USE_URL': True,
    # Browseable API
    'HTML_SELECT_CUTOFF': 1000,
    'HTML_SELECT_CUTOFF_TEXT': "More than {count} items...",
    # Schemas
    'SCHEMA_COERCE_PATH_PK': True,
    'SCHEMA_COERCE_METHOD_NAMES': {
        'retrieve': 'read',
        'destroy': 'delete'
    },
}

CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = ()

CORS_ALLOW_METHODS = (
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
    'VIEW',
)

CORS_ALLOW_HEADERS = (
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'token',
    'language',
    'operator',
    'device',
    'request-starttime'
)

import time

cur_path = os.path.dirname(os.path.realpath(__file__))  # log_path是存放日志的路径
log_path = os.path.join(os.path.dirname(cur_path), 'logs')
if not os.path.exists(log_path): os.mkdir(log_path)  # 如果不存在这个logs文件夹，就自动创建一个

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        # 日志格式
        'standard': {
            'format': '[%(asctime)s] [%(filename)s:%(lineno)d] [%(module)s:%(funcName)s] '
                      '[%(levelname)s]- %(message)s'},
        'simple': {  # 简单格式
            'format': '%(levelname)s %(message)s'
        },
    },
    # 过滤
    'filters': {
    },
    # 定义具体处理日志的方式
    'handlers': {
        # 默认记录所有日志
        'default': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(log_path, 'all-{}.log'.format(time.strftime('%Y-%m-%d'))),
            'maxBytes': 1024 * 1024 * 5,  # 文件大小
            'backupCount': 5,  # 备份数
            'formatter': 'standard',  # 输出格式
            'encoding': 'utf-8',  # 设置默认编码，否则打印出来汉字乱码
        },
        # 输出错误日志
        'error': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(log_path, 'error-{}.log'.format(time.strftime('%Y-%m-%d'))),
            'maxBytes': 1024 * 1024 * 5,  # 文件大小
            'backupCount': 5,  # 备份数
            'formatter': 'standard',  # 输出格式
            'encoding': 'utf-8',  # 设置默认编码
        },
        # 控制台输出
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
        # 输出info日志
        'info': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(log_path, 'info-{}.log'.format(time.strftime('%Y-%m-%d'))),
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 5,
            'formatter': 'standard',
            'encoding': 'utf-8',  # 设置默认编码
        },
    },
    # 配置用哪几种 handlers 来处理日志
    'loggers': {
        # 类型 为 django 处理所有类型的日志， 默认调用
        'django': {
            'handlers': ['default', 'console', 'info'],
            'level': 'INFO',
            'propagate': True
        },
        '': {
            'handlers': ['default', 'console', 'info'],
            'level': 'INFO',
            'propagate': True
        },
        # log 调用时需要当作参数传入
        # 'log': {
        #     'handlers': ['error', 'info', 'console', 'default'],
        #     'level': 'INFO',
        #     'propagate': True
        # },
    }
}

SHOPEE = {
    # 'host': 'https://partner.shopeemobile.com',
    # 'host': 'https://partner.test-stable.shopeemobile.com',
    'host': 'https://openplatform.shopee.cn/',
    'redirect_url': 'https://erp.superwms.website//store/callback',
    'callback_url': '/#/web/store',
    'shipping_doc_path': '/usr/juyigou/order_bills',
    'encode': 'utf-8',
    'v2': {
        'auth_path': '/api/v2/shop/auth_partner',
        'cancel_auth_path': "/api/v2/shop/cancel_auth_partner",
        'get_access_token': '/api/v2/auth/token/get',
        'refresh_access_token': '/api/v2/auth/access_token/get',
        'merchant.get_merchant_info': '/api/v2/merchant/get_merchant_info',
        'shop.get_shop_info': '/api/v2/shop/get_shop_info',
        'product.get_item_list': '/api/v2/product/get_item_list',
        'product.get_item_base_info': '/api/v2/product/get_item_base_info',
        'product.update_stock': '/api/v2/product/update_stock',
        'product.get_model_list': '/api/v2/product/get_model_list',
        'product.get_item_promotion': 'api/v2/product/get_item_promotion',
        'discount.get_discount': '/api/v2/discount/get_discount',
        'discount.update_discount_item': '/api/v2/discount/update_discount_item',
        'discount.get_discount_list': '/api/v2/discount/get_discount_list',
        'discount.add_discount_item': '/api/v2/discount/add_discount_item',
        'global_product.get_category': '/api/v2/global_product/get_category',
        'global_product.get_global_item_list': '/api/v2/global_product/get_global_item_list',
        'global_product.get_global_item_info': '/api/v2/global_product/get_global_item_info',
        'global_product.get_global_model_list': '/api/v2/global_product/get_global_model_list',
        'global_product.create_publish_task': '/api/v2/global_product/create_publish_task',
        'global_product.get_publish_task_result': '/api/v2/global_product/get_publish_task_result',
        'global_product.get_global_item_id': '/api/v2/global_product/get_global_item_id',
        'global_product.get_attributes': '/api/v2/global_product/get_attributes',
        'global_product.get_brand_list': '/api/v2/global_product/get_brand_list',
        'global_product.update_global_item': '/api/v2/global_product/update_global_item',
        'global_product.update_global_model': '/api/v2/global_product/update_global_model',
        'global_product.add_global_item': '/api/v2/global_product/add_global_item',
        'global_product.init_tier_variation': '/api/v2/global_product/init_tier_variation',
        'order.get_order_list': '/api/v2/order/get_order_list',
        'order.get_order_detail': '/api/v2/order/get_order_detail',
        'order.get_shipment_list': '/api/v2/order/get_shipment_list',
        'order.set_note': '/api/v2/order/set_note',
        'logistics.get_shipping_parameter': '/api/v2/logistics/get_shipping_parameter',
        'logistics.ship_order': '/api/v2/logistics/ship_order',
        'logistics.get_tracking_number': '/api/v2/logistics/get_tracking_number',
        'logistics.get_shipping_document_parameter': '/api/v2/logistics/get_shipping_document_parameter',
        'logistics.create_shipping_document': '/api/v2/logistics/create_shipping_document',
        'logistics.download_shipping_document': '/api/v2/logistics/download_shipping_document',
        'media_space.upload_image': '/api/v2/media_space/upload_image'
    },
    'keyword_filter': ['是否跨境出口专供货源', '售后服务', '是否进口', '加印LOGO', '加工定制', '是否专供外贸', '品牌', '是否外贸', '加工方式'
                       '是否专利货源', '产地', '货源类别', '主要下游平台', '主要销售地区', '是否支持一件代发']
}