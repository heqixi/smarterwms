from base.event_bus.bus import EventBus

GLOBAL_BUS = EventBus()

GLOBAL_PRODUCT_SYNC_EVENT = 'global_product_sync_event'
ORDER_SYNC_EVENT = 'order_sync_event'
ORDER_MODIFY_CREATE_EVENT = 'order_modify_create_event'
FETCH_PRODUCT_RECEIVE_EVENT = 'fetch_product_receive_event'

class GlobalEvent:

    class Asn:
        UPDATE_ANS_DETAIL_GOODS = 'UPDATE_ANS_DETAIL_GOODS'

    class ShopeeProduct:
        UPDATE_SHOPEE_PRODUCT_GLOBAL_PRODUCT = 'update_global_product_sku'
        CHANGE_SHOPEE_PRODUCT_GLOBAL_PRODUCT = 'change_shopee_product_global_product'

    class Stock:
        UPDATE_STOCK_GOODS = 'UPDATE_STOCK_GOODS'

    class GodosMedia:
        UPDATE_GOODS_MEDIA_GOODS = 'UPDATE_GOODS_MEDIA_GOODS'

    class Supplier:
        UPDATE_PURCHASE_PLAN_GOODS = 'UPDATE_PURCHASE_PLAN_GOODS'

    class ShopeePublish:
        ADD_DISCOUNT = 'add_shopee_discount'




