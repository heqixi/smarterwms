from django.contrib import admin

# Register your models here.
from order.models import ShopeeOrderModel, ShopeeOrderDetailModel, ShopeeOrderMessageModel, ShopeeOrderModifyModel

admin.site.register(ShopeeOrderModel)
admin.site.register(ShopeeOrderDetailModel)
admin.site.register(ShopeeOrderModifyModel)
admin.site.register(ShopeeOrderMessageModel)


