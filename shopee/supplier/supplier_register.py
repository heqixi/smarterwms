import threading
import logging

from goods.models import GoodsGroupRecord, GoodsRecord
from supplier.models import PurchasePlanRecord
from supplier.gRpc.supplier_client import Supplier, SupplierClient, CreatePurchasePlanReq

logger = logging.getLogger()


class SupplierRegister(object):
    __create_key = object()
    lock = threading.RLock()
    client = None

    def __init__(self, create_key):
        assert (create_key == SupplierRegister.__create_key), \
            "Stock Service is single instance, please use SupplierClient.get_instance()"

    @classmethod
    def get_instance(cls):
        if cls.client is None:
            cls.lock.acquire()
            if cls.client is None:
                cls.client = cls(SupplierRegister.__create_key)
            cls.lock.release()
            return cls.client
        return cls.client

    def register_purchase_plan(self, product_id, force=False):
        from store.models import StoreProductModel, ProductSupplierInfo
        purchase_record = PurchasePlanRecord.objects.filter(product_id=product_id).first()
        if purchase_record:
            if not force:
                logger.warning('Purchase plan of product already register, purchase id %s ' % purchase_record.id)
                return purchase_record
        goods_group_record = GoodsGroupRecord.objects.filter('product_id').first()
        if not goods_group_record:
            logger.error('Missing goods group for product %s ', product_id)
            return None
        goods_of_group = GoodsRecord.objects.filter(group_id=goods_group_record.id).all()
        if not goods_of_group.exists():
            logger.error('No goods attached to group %s ' % goods_group_record.id)
            return None
        store_product = StoreProductModel.objects.filter(id=product_id).first()
        if not store_product:
            logger.error('Store product of id %s not found %s' % product_id)
            return None
        supplier_info = ProductSupplierInfo.objects.filter(product_id=product_id).first()
        if not supplier_info:
            logger.error('Missing supplier info of product %s '% product_id)
            return None
        goods = [goods_record.goods_id for goods_record in goods_of_group]
        supplier = Supplier(
            supplier_name=supplier_info.supplier_name
        )
        req = CreatePurchasePlanReq(
            price=supplier_info.get('price', None),
            url=supplier_info.get('url', None),
            image_url=store_product.image_url,
            tag=store_product.product_sku,
            goods=goods,
            supplier=supplier
        )
        try:
            res = SupplierClient.get_instance().create_purchase_plan(req)
        except Exception as e:
            logger.error('Register purchase plan fail %s', e)
            return None
        else:
            if not purchase_record:
                purchase_record = PurchasePlanRecord.objects.create(
                    openid=store_product.openid,
                    creater=store_product.creater,
                    purchase_id=res.id,
                    product_id=product_id
                )
            else:
                purchase_record.purchase_id = res.id
                purchase_record.save()
        return purchase_record





