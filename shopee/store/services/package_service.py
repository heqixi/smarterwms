import logging
import threading

from django.db import transaction

from store.models import StoreProductPackageModel, StorePackageItemModel

logger = logging.getLogger()


class PackageService(object):
    """
    组合装服务
    """
    __create_key = object()
    lock = threading.RLock()
    service = None

    def __init__(self, create_key):
        assert (create_key == PackageService.__create_key), \
            "PackageService objects must be created using PackageService.get_instance"

    @classmethod
    def get_instance(cls):
        if cls.service is None:
            cls.lock.acquire()
            if cls.service is None:
                cls.service = cls(PackageService.__create_key)
            cls.lock.release()
            return cls.service
        return cls.service

    @transaction.atomic
    def remove_package(self, openid, package_id):
        StoreProductPackageModel.objects.get(openid=openid, pk=package_id).delete()

    @transaction.atomic
    def new_package(self, openid, creater, packages, items):
        for pkg in packages:
            if StoreProductPackageModel.objects.filter(openid=openid, sku=pkg.get('sku')).exists():
                logger.error('openid %s, Package %s existed', openid, pkg.get('sku'))
                raise ValueError('Package %s existed' % pkg.get('sku'))
            package = StoreProductPackageModel(
                openid=openid, creater=creater,
                sku=pkg.get('sku'), name=pkg.get('name'), uid=pkg.get('uid'),
                product_type=pkg.get('product_type')
            )
            package.save()
            for item in items:
                new_item = StorePackageItemModel(
                    openid=openid, creater=creator,
                    package=package, product_type=item.get('product_type'),
                    sku=item.get('sku'), uid=item.get('uid')
                )
                new_item.save()
