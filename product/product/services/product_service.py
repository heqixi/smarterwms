
import logging
import threading

from django.db import transaction

from product.models import GlobalProduct

from .fetchbox import FetchBoxHelper
from .producthelper import ProductHelper


logger = logging.getLogger()


class GlobalProductService(object):
    __create_key = object()
    lock = threading.RLock()
    service = None

    def __init__(self, create_key):
        assert (
                create_key == GlobalProductService.__create_key), "Global Product Service is single instance, please use GlobalProductService.get_instance()"

    @classmethod
    def get_instance(cls):
        if cls.service is None:
            cls.lock.acquire()
            if cls.service is None:
                cls.service = cls(GlobalProductService.__create_key)
            cls.lock.release()
            return cls.service
        return cls.service

    # ------------------------------------------
    # fectbox Relative Method
    # ------------------------------------------
    def create_product(self, product_info, openid, creater):
        product = FetchBoxHelper.create_product(product_info, openid, creater)
        return product

    # ------------------------------------------
    # Global Product Method
    # ------------------------------------------

    @transaction.atomic
    def clone_product(self, product: GlobalProduct):
        product_id = product.id
        product_clone = product
        product_clone.pk = None
        product_clone.status = 'ED'
        product_clone.save()
        product_clone.save()
        origin_product = GlobalProduct.objects.get(id=product_id)
        ProductHelper.clone_product_model_and_spec(product_clone, origin_product)
        ProductHelper.clone_product_media(product_clone, origin_product)
        ProductHelper.clone_product_logistic(product_clone, origin_product)
        ProductHelper.clone_product_supplier(product_clone, origin_product)
        return product_clone














