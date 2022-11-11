from goods.models import GoodsGroupRecord
from store.models import StoreProductModel


def create_goods_group(global_product: StoreProductModel):
    goods_group_record = GoodsGroupRecord.objects.filter(product_id=global_product.product_id).first()
    if not goods_group_record.exist():
        pass
