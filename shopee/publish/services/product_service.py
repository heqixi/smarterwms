
import logging
import threading
import time
from datetime import datetime, timedelta

from django.db import transaction

from store.services.global_service import GlobalService
from store.services.product_service import ProductService
from store.models import StoreProductModel
from timer.executor import Task, AsyncSchedulerExecutor

from .producthelper import ProductHelper


logger = logging.getLogger()


class ShopeeStorePublishTask(Task):
    id_prefix = 'ShopeeStorePublishTask '

    product = None

    merchant_id = None

    store = None

    run_date = None

    task_id = None

    def __init__(self, product: StoreProductModel, merchant_id, task_id, run_date=datetime.now() + timedelta(seconds=10)):
        self.product = product
        self.product_publish_status = 0  # -1: fail; 0: processing; 1:success
        self.merchant_id = merchant_id
        self.task_id = task_id
        self.retry_times = 0
        self.store = product.store
        self.run_date = run_date

    def job_id(self):
        return self.id_prefix + '_' + str(self.product.id) + '_' + str(self.task_id)

    def trigger_args(self):
        return {
            'trigger': 'interval',
            'seconds': 10
        }

    def do_exec(self):
        from timer.executor import AsyncSchedulerExecutor
        logger.info('start query publish task status  %s of store %s, %s', self.product.product_sku, self.store.uid,
                    self.product_publish_status)
        try:
            if self.retry_times > 3:
                logger.warning('Task fail, remove task, ', self.job_id())
                AsyncSchedulerExecutor.get_instance().remove(self.job_id())
            if self.product_publish_status == 0:
                self.product_publish_status = self._get_product_publish_result()
            if self.product_publish_status == 1:
                self.retry_times = 0
                # wait another period to publish discount
                # return
            elif self.product_publish_status == -1:
                AsyncSchedulerExecutor.get_instance().remove(self.job_id())
            else:
                self.retry_times += 1
            if self.product_publish_status == 1:
                success = self._publish_discount(self.product)
                if not success:
                    self.retry_times += 1
                else:
                    AsyncSchedulerExecutor.get_instance().remove(self.job_id())
        except Exception as exc:
            print('Task exec ', exc)

    def _publish_discount(self, store_product):
        discount_id, discount_model_list = ProductHelper.wrap_product_discount_info(store_product)
        if len(discount_model_list) > 0:
            discount_item_list = [
                {'item_id': store_product.product_id, 'purchase_limit': 0, 'model_list': discount_model_list}]
            logger.info('update model discount %s %s %s ', store_product.product_id, discount_id,
                        discount_model_list)
            success_count = ProductService.get_instance().add_discount_item(store_product.store.uid, discount_id,
                                                                            discount_item_list)
            return success_count > 0
        else:
            logger.info('product %s has no model discount to publish to shop %s', store_product.product_sku,
                        store_product.store.name)
            return False

    def _get_product_publish_result(self):
        publish_result = ProductService.get_instance().get_publish_task_result(self.task_id, self.merchant_id)
        if publish_result.get('publish_status', None) == 'success':
            logger.info('publish to store success %s ', publish_result)
            success = publish_result.get('success')
            item_id = success.get('item_id')
            self.product.product_id = item_id
            self.product.save()
            _, store_model_list = ProductService.get_instance().get_store_model_list(item_id, self.store.uid)
            for variant in self.product.product_variant.all():
                match_models = [model for model in store_model_list if
                                ','.join([str(index) for index in model.get('tier_index')]) == variant.option_item_index]
                if len(match_models) <= 0:
                    logger.error('local variant of option item index not publish %s ', variant.option_item_index)
                    continue
                variant.model_id = match_models[0].get('model_id')
                variant.save()
            return 1
        elif publish_result.get('publish_status', None) == 'processing':
            logger.info('publish product %s to store %s is processing(审查中), %s ', self.product.id, self.store.name,
                        publish_result)
            return 0
        elif publish_result.get('publish_status', None) == 'failed':
            reason = publish_result['failed']['failed_reason']
            logger.info('publish product %s to store %s fail, %s ' % (self.product.id, self.store.name, reason))
            return -1


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
        if not product.product_id:
            self.publish_golbal_product(product, merchant_id, stores_to_publish)
        elif len(stores_to_publish) > 0:
            self.publish_shopee_store_product(product, merchant_id, stores_to_publish)

    def publish_shopee_store_product(self, product, merchant_id, stores_to_publish):
        if len(stores_to_publish) <= 0:
            raise Exception('No store to publish')
        for store in stores_to_publish:
            shop_product = product.shop_products.filter(store=store).first()
            if shop_product.product_id:
                raise Exception('Product may have been publish to store %s %s ' % (store.name, store.id))
            self.publish_product_to_store(product, merchant_id, store)

    def publish_golbal_product(self, product: StoreProductModel, merchant_id, stores_to_publish=[]):
        if not (product.product_status == 'EDIT' or product.product_status == 'PUBLISH_READY'):
            raise Exception('product may have been publish %s  %s' % (product.id, product.status))
        main_product_info = ProductHelper.wrap_main_product_info(product, merchant_id)
        logger.info('publish global product ', main_product_info)
        (tier_variation, global_models) = ProductHelper.wrap_product_spec(product, merchant_id)
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
                model_tier_index = ','.join([str(index) for index in global_model['tier_index']])
                local_model = product.product_variant.filter(option_item_index=model_tier_index).first()
                if not local_model:
                    raise Exception('Local model has publish, but not found in published global model')
                local_model.model_id = global_model_id
                local_model.save()
            if len(stores_to_publish) > 0:
                for store in stores_to_publish:
                    self.publish_product_to_store(product, merchant_id, store)

    def publish_product_to_store(self, product: StoreProductModel, merchant_id, store):
        publish_info = ProductHelper.wrap_product_price_info(product, store)
        logger.info('publish product to store , publish info %s', publish_info)
        task_id = ProductService.get_instance().create_publish_task(merchant_id, publish_info)
        shop_product = product.shop_products.filter(store=store).first()
        publish_task = ShopeeStorePublishTask(shop_product, merchant_id, task_id)
        AsyncSchedulerExecutor.get_instance().register(publish_task)

    def pubish_shopee_discount(self, shop_product: StoreProductModel):
        discount_id, discount_model_list = ProductHelper.wrap_product_discount_info(shop_product)
        if len(discount_model_list) > 0:
            discount_item_list = [
                {'item_id':  shop_product.product_id, 'purchase_limit': 0, 'model_list': discount_model_list}]
            logger.info('update model discount %s %s %s ',  shop_product.product_id, discount_id, discount_model_list)
            ProductService.get_instance().add_discount_item(shop_product.store.uid, discount_id, discount_item_list)
        else:
            logger.info('product %s has no model discount to publish to shop %s', shop_product.product_sku, shop_product.store.name)

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
