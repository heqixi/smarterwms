
import logging
import threading
import time
import traceback
from datetime import datetime, timedelta
from random import random

from django.db import transaction

from publish.models import ProductEditPrice
from store.services.global_service import GlobalService
from store.services.product_service import ProductService
from store.models import StoreProductModel
from timer.executor import Task, AsyncSchedulerExecutor

from .producthelper import ProductHelper


logger = logging.getLogger()


class PublishPriceTask(Task):
    id = 'PublishPriceTask'

    product = None

    store = None

    retry_times = 5

    run_times = 0

    def __init__(self, global_product: StoreProductModel, shop_product_id, store, retry_times=5):
        self.global_product = global_product
        self.shop_product_id = shop_product_id
        self.store = store
        self.retry_times = retry_times
        self.run_times = 0

    def job_id(self):
        return self.id + '_' + str(self.global_product.id) + '_' + str(self.store['uid'])

    def trigger_args(self):
        return {
            'trigger': 'interval',
            'minutes': 60,
            'replace_existing': True,
            'next_run_time': datetime.now() + timedelta(seconds=random.randint(30, 120))
        }

    def do_exec(self):
        try:

            logger.info('Job %s Start for %s times , publish %s price to %s, thread %s', self.id, self.run_times,
                        self.global_product.product_sku, self.store['uid'], threading.get_ident())
            if self.run_times >= self.retry_times:
                logger.error('Job %s have exceed max retry time, give up ', self.job_id())
                AsyncSchedulerExecutor.get_instance().remove(self.job_id())
            else:
                self.run_times += 1

            def pubilsh_discount(global_product):
                logger.info('local product has update, publish discount %s  %s', self.global_product.id, self.store['uid'])
                ProductPublishService.get_instance().pubish_shopee_discount(self.global_product, self.store)
            try:
                # First, sync shopee shop product (not shopee_global_product)
                ProductService.get_instance().refresh_product(self.store['uid'], [self.shop_product_id],
                                                              pubilsh_discount)
            except Exception as exc:
                logger.error('can not refresh product %s %s %s %s' % (
                    self.global_product.id, self.store['name'], self.shop_product_id, traceback.format_exc(exc)))
        except Exception as exc:
            logger.error('publish edit price error %s ', exc, traceback.format_exc())


class ShopeeStorePublishTask(Task):
    id_prefix = 'ShopeeStorePublishTask '

    product = None

    merchant_id = None

    store = None

    run_date = None

    task_id = None

    def __init__(self, product: StoreProductModel, merchant_id, task_id, store, run_date=datetime.now() + timedelta(seconds=10)):
        self.product = product
        self.merchant_id = merchant_id
        self.task_id = task_id
        self.store = store
        self.run_date = run_date

    def job_id(self):
        return self.id_prefix + '_' + str(self.product.id) + '_' + str(self.task_id)

    def trigger_args(self):
        return {
            'trigger': 'interval',
            'seconds': 5
        }

    def do_exec(self):
        from timer.executor import AsyncSchedulerExecutor
        try:
            logger.info('start query publish task status  %s of store %s', self.product.product_sku, self.store['uid'])
            publish_result = ProductService.get_instance().get_publish_task_result(self.task_id, self.merchant_id)
            if publish_result.get('publish_status', None) == 'success':
                AsyncSchedulerExecutor.get_instance().remove(self.job_id())
                logger.info('publish to store success %s ', publish_result)
                success = publish_result.get('success')
                item_id = success.get('item_id')
                for model in self.product.product_variant.all():
                    edit_price = ProductEditPrice.objects.filter(store_id=self.store['uid'], product_id=model.id).first()
                    if edit_price and edit_price.discount_id > 0:
                        edit_price.publish_ready = True
                        edit_price.published = False
                        edit_price.save()
                logger.info('ready to publish discoutn %s %s ', self.product.product_sku, self.store['uid'])
                price_publish_task = PublishPriceTask(self.product, item_id, self.store)
                AsyncSchedulerExecutor.get_instance().register(price_publish_task)
            elif publish_result.get('publish_status', None) == 'processing':
                logger.info('publish product %s to store %s is processing(审查中), %s ', self.product.id, self.store['name'], publish_result)
            elif publish_result.get('publish_status', None) == 'failed':
                AsyncSchedulerExecutor.get_instance().remove(self.job_id())
                reason = publish_result['failed']['failed_reason']
                logger.info('publish product %s to store %s fail, %s ' % (self.product.id, self.store['name'], reason))
        except Exception as exc:
            logger.error('fail to publish product %s to shop %s , %e' % (self.product.id, self.store, exc))


class ProductPublishService(object):
    __create_key = object()
    lock = threading.RLock()
    service = None

    def __init__(self, create_key):
        assert (
                create_key == ProductPublishService.__create_key), "Global Product Service is single instance, please use GlobalProductService.get_instance()"

    @classmethod
    def get_instance(cls):
        if cls.service is None:
            cls.lock.acquire()
            if cls.service is None:
                cls.service = cls(ProductPublishService.__create_key)
            cls.lock.release()
            return cls.service
        return cls.service

    # ------------------------------------------
    # Shopee Publish Relative Method
    # ------------------------------------------
    def publish_shopee(self, product: StoreProductModel, merchant_id, stores_to_publish=[]):
        global_publish_id = product.product_id
        if not global_publish_id:
            self.publish_golbal_product(product, merchant_id, stores_to_publish)
        elif len(stores_to_publish) > 0:
            self.publish_shopee_store_product(product, global_publish_id, merchant_id, stores_to_publish)

    def publish_shopee_store_product(self, product, global_publish_id, merchant_id, stores_to_publish):
        if len(stores_to_publish) > 0:
            (tier_variation, global_models) = GlobalService.get_instance().get_global_model_list(merchant_id, global_publish_id)
            for store in stores_to_publish:
                store_publish_id = ProductHelper.get_shopee_store_publish_id(product, store['uid'])
                if store_publish_id:
                    raise Exception('product %s has been publish to store  %s, %s' % (product.sku, store['name'], store_publish_id))
                self.publish_product_to_store(product, global_models, merchant_id, store)

    def publish_golbal_product(self, product: StoreProductModel, merchant_id, stores_to_publish=[]):
        if not (product.status == 'EDIT' or product.status == 'PUBLISH_READY'):
            raise Exception('product may have been publish %s  %s' % (product.id, product.status))
        main_product_info = ProductHelper.wrap_main_product_info(product, merchant_id)
        logger.info('publish global product ', main_product_info)
        (tier_variation, global_models, local_models) = ProductHelper.wrap_product_spec(product, merchant_id)
        logger.info('publish global product tir_variation %s, global_models  %s' % (tier_variation, global_models))
        global_item_id = GlobalService.get_instance().publish_global_product(merchant_id, main_product_info)
        product.status = StoreProductModel.Status.NORMAL
        product.product_id = global_item_id
        product.save()
        variation_info = {
            'tier_variation': tier_variation,
            'global_model': global_models,
            'global_item_id': global_item_id
        }
        ret = GlobalService.get_instance().init_global_variation(merchant_id, variation_info)
        logger.info(f"complete init global variation at {time.strftime('%X')}")
        if ret:
            (tier_variation, global_models) = GlobalService.get_instance().get_global_model_list(merchant_id, global_item_id)
            for global_model in global_models:
                global_model_id = global_model['global_model_id']
                model_tier_index = global_model['tier_index']
                local_model = list(filter(lambda x: x.option_item_index == model_tier_index, local_models))
                if not local_model:
                    raise Exception('Local model has publish, but not found in published global model')
                local_model = local_model[0]
                local_model.model_id = global_model_id
                local_model.save()
            if len(stores_to_publish) > 0:
                for store in stores_to_publish:
                    self.publish_product_to_store(product, global_models, merchant_id, store)

    def publish_product_to_store(self, product: StoreProductModel, shopee_global_models, merchant_id, store):
        if not product.product_status == 'NORMAL':
            raise Exception('product may have not been publish to global model yet %s  %s' % (product.id, product.product_status))
        publish_info = ProductHelper.wrap_product_price_info(product, shopee_global_models, store)
        logger.info('publish product to store , publish info %s', publish_info)
        task_id = ProductService.get_instance().create_publish_task(merchant_id, publish_info)

        publish_task = ShopeeStorePublishTask(product, merchant_id, task_id, store)
        AsyncSchedulerExecutor.get_instance().register(publish_task)

    def pubish_shopee_discount(self, global_product: StoreProductModel, store):
        shop_product = global_product.shop_products.filter(store_id=store['id']).first()
        if not shop_product:
            raise Exception('Shop product of global product %s not found ' % global_product.product_sku)
        discount_id, discount_model_list = ProductHelper.wrap_product_discount_info(global_product, shop_product)
        if len(discount_model_list) > 0:
            discount_item_list = [
                {'item_id':  shop_product.product_id, 'purchase_limit': 0, 'model_list': discount_model_list}]
            logger.info('update model discount %s %s %s ',  shop_product.product_id, discount_id, discount_model_list)
            ProductService.get_instance().add_discount_item(store['uid'], discount_id, discount_item_list)
            for model in global_product.product_variant.all():
                edit_price = ProductEditPrice.objects.filter(store_id=store['uid'], product_id=model.id).first()
                if edit_price and edit_price.discount_id > 0:
                    edit_price.publish_ready = False
                    edit_price.published = True
                    edit_price.save()
        else:
            logger.info('product %s has no model discount to publish to shop %s', global_product.id, store['uid'])

    # ------------------------------------------
    # Global Product Method
    # ------------------------------------------

    @transaction.atomic
    def clone_product(self, product: StoreProductModel):
        pass
        # try:
        #     ProductServiceClient.get_instance().create_from_shopee(StoreGlobalProductEmitDataSerializer(product).data)
        # except Exception as exec:
        #     logger.error('Fail to create global product when clone product')
