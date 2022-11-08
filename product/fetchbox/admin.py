from django.contrib import admin

# Register your models here.
from fetchbox.models import FetchProductModel, FetchOptionModel, FetchOptionItemModel, FetchVariantModel, \
    FetchMediaModel, ShopeeRegionSettingsModel

admin.site.register(FetchProductModel)
admin.site.register(FetchOptionModel)
admin.site.register(FetchOptionItemModel)
admin.site.register(FetchVariantModel)
admin.site.register(FetchMediaModel)
admin.site.register(ShopeeRegionSettingsModel)
