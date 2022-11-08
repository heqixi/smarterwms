import imp
from django.contrib import admin
from .models import ProductMedia, Media

# Register your models here.
admin.site.register(ProductMedia)
admin.site.register(Media)
