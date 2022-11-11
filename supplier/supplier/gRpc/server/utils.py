
from supplier.models import PurchasePlan
from supplier.models import ListModel as Supplier
from supplier.gRpc.server.protos import supplier_pb2

def supplier_to_message(supplier: Supplier):
    return supplier_pb2.Supplier(
        id=supplier.id,
        supplier_name=supplier.supplier_name,
        supplier_city=supplier.supplier_city,
        supplier_address=supplier.supplier_address,
        supplier_contact=supplier.supplier_contact,
        supplier_manager=supplier.supplier_manager,
        supplier_level=supplier.supplier_level
    )


def purchase_to_message(purchase: PurchasePlan):
    goods = [setting.goods for setting in purchase.goods_settings.all()]
    return supplier_pb2.PurchasePlan(
        id=purchase.id,
        supplier=supplier_to_message(purchase.supplier),
        price=purchase.price,
        url=purchase.url,
        image_url=purchase.image_url,
        tag=purchase.tag,
        goods=goods
    )


