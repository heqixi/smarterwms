from django.contrib import admin

# Register your models here.
from store.models import StoreModel, StoreInfoModel, StoreProductModel, StoreProductOptionModel, StoreProductOptionItemModel, StoreProductVariantModel, StoreProductMedia

admin.site.register(StoreModel)
admin.site.register(StoreInfoModel)
admin.site.register(StoreProductModel)
admin.site.register(StoreProductOptionModel)
admin.site.register(StoreProductOptionItemModel)
admin.site.register(StoreProductVariantModel)
admin.site.register(StoreProductMedia)

