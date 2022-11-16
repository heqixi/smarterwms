import datetime
import logging
import os
import threading
import time
import traceback
from hashlib import md5

from PyPDF2 import PdfMerger
from django.conf import settings
from django.db import transaction
from django.db.models import Sum

from goods.gRpc.client.goods_service_stub import GoodsServiceClient
from goods.gRpc.client.types.goods import CreateGroupRequest
from goods.models import GoodsGroupRecord
from order.common import OrderMsgType, OrderMsgMark, OrderStatus, OrderModifyType, OrderHandleStatus, OrderRecordType, \
    OrderPackageType
from order.models import ShopeeOrderModel, ShopeeOrderDetailModel, ShopeeOrderMessageModel, ShopeeOrderModifyModel, \
    ShopeeOrderPackageModel
from order.services.order_record_service import OrderRecordService
from order.utils import OrderDetailStockBeanFactory, OrderModifyStockBeanFactory, OrderPackageStockBeanFactory
from stock.models import StockRecord
from stock.services.stockprovider import StockService
from store.common import StoreType, PackageProductType
from store.models import StoreModel, StoreProductVariantModel, StoreProductPackageModel
from store.services.product_service import ProductService
from store.services.global_service import GlobalService
from utils import shopee, spg

logger = logging.getLogger()


class OrderService(object):
    """
    订单服务，对外提供订单相关操作功能
    """
    __create_key = object()
    lock = threading.RLock()
    service = None
    product_service = ProductService.get_instance()
    global_service = GlobalService.get_instance()
    stock_service = StockService.get_instance()

    def __init__(self, create_key):
        assert (create_key == OrderService.__create_key), \
            "StoreService objects must be created using StoreService.get_instance"

    @classmethod
    def get_instance(cls):
        if cls.service is None:
            cls.lock.acquire()
            if cls.service is None:
                cls.service = cls(OrderService.__create_key)
            cls.lock.release()
            return cls.service
        return cls.service

    def change_goods(self, openid, detail_id, goods_id, goods_code):
        from store.services.global_service import GlobalService
        detail = ShopeeOrderDetailModel.objects.get(openid=openid, pk=detail_id)
        if not detail.model_id:
            raise ValueError('Order detail error: model is None')
        merchant = detail.shopee_order.store.merchant
        variant = StoreProductVariantModel.objects.get(model_id=detail.model_id)
        store_product = variant.store_product
        if not store_product.global_product.first():
            # 重新同步全球产品
            self.product_service.refresh_product(detail.shopee_order.store.uid, [store_product.product_id])
        global_product = store_product.global_product.first()
        g_variant = global_product.product_variant.get(option_item_index=variant.option_item_index)
        GlobalService.get_instance().update_model_sku(merchant.uid, [
            {
                'openid': openid,
                'product_id': global_product.product_id,
                'model_id': g_variant.model_id,
                'model_sku': goods_code
            }
        ])
        # 本地修改Global/Shop Product 更新
        variant.model_sku = goods_code
        variant.save()
        g_variant.model_sku = goods_code
        g_variant.save()
        res = self.stock_service.update_stock_goods(detail.stock, goods_id, openid)
        if not res.success:
            logger.error('change_goods update stock goods fail, %s %s %s !', detail_id, goods_id, goods_code)

    def order_remark(self, openid, order_id, note):
        order = ShopeeOrderModel.objects.get(openid=openid, pk=order_id)
        shopee.request(url_key='order.set_note', method='POST', shop_id=order.store.uid, params={
            'order_sn': order.order_sn,
            'note': note
        })
        if ShopeeOrderMessageModel.objects.filter(
                shopee_order=order,
                type=OrderMsgType.SELLER_NOTES
        ).exists():
            ShopeeOrderMessageModel.objects.filter(
                shopee_order=order,
                type=OrderMsgType.SELLER_NOTES).update(
                message=note
            )
        else:
            order_message = ShopeeOrderMessageModel(
                shopee_order=order,
                type=OrderMsgType.SELLER_NOTES,
                mark=OrderMsgMark.FINISHED,
                message=note
            )
            order_message.save()

    @transaction.atomic
    def freed_stock(self, openid, order_id_list, last=False):
        """
        释放订单库存
        """
        if openid is None:
            raise ValueError('openid can not be none')
        if order_id_list is not None and len(order_id_list) > 0:
            logger.info('order freed stock: %s', order_id_list)
            for order_id in order_id_list:
                order = ShopeeOrderModel.objects.get(pk=order_id)
                # 检查订单是否都已经锁定
                for detail in ShopeeOrderDetailModel.objects.filter(shopee_order=order):
                    self.__freed_detail_stock(detail, order.handle_status)
                for modify in ShopeeOrderModifyModel.objects.filter(shopee_order=order):
                    self.__freed_modify_stock(modify, order.handle_status)
                for package in ShopeeOrderPackageModel.objects.filter(shopee_order=order):
                    self.__freed_package_stock(package, order.handle_status)
                if last:
                    order.handle_status = OrderHandleStatus.AT_LAST
                order.save()

    def __freed_package_stock(self, package: ShopeeOrderPackageModel, handle_status: int):
        stock = package.stock
        if stock:
            if handle_status == OrderHandleStatus.FORCED_SHIPMENT:
                self.stock_service.back_stock(stock, to_reserve_qty=package.quantity, to_onhand_qty=0)
            elif handle_status == OrderHandleStatus.PARTIALLY_SHIPMENT:
                self.stock_service.back_stock(stock)
                if stock.stock_qty == 0:
                    self.stock_service.update_stock_qty(stock, package.quantity) #需要回退部分库存
            else:
                self.stock_service.back_stock(stock)

    def __freed_modify_stock(self, modify: ShopeeOrderModifyModel, handle_status: int):
        stock = modify.stock
        if stock:
            if handle_status == OrderHandleStatus.FORCED_SHIPMENT:
                self.stock_service.back_stock(stock, to_reserve_qty=modify.quantity, to_onhand_qty=0)
            elif handle_status == OrderHandleStatus.PARTIALLY_SHIPMENT:
                self.stock_service.back_stock(stock)
                if stock.stock_qty == 0:
                    self.stock_service.update_stock_qty(stock, modify.quantity)
            else:
                self.stock_service.back_stock(stock)

    def __freed_detail_stock(self, detail: ShopeeOrderDetailModel, handle_status: int):
        stock = detail.stock
        if stock:
            if handle_status == OrderHandleStatus.FORCED_SHIPMENT:
                replace_count = ShopeeOrderModifyModel.objects.filter(
                    shopee_order=detail.shopee_order, replaced_id=detail.model_id, modify_type=OrderModifyType.REPLACE
                ).aggregate(sum=Sum('quantity')).get('sum')
                replace_count = replace_count if replace_count else 0
                qyt = detail.model_quantity_purchased - replace_count
                self.stock_service.back_stock(stock, to_reserve_qty=qyt, to_onhand_qty=0)
            elif handle_status == OrderHandleStatus.PARTIALLY_SHIPMENT:
                self.stock_service.back_stock(stock)
                if stock.stock_qty == 0:
                    replace_count = ShopeeOrderModifyModel.objects.filter(
                        shopee_order=detail.shopee_order, replaced_id=detail.model_id, modify_type=OrderModifyType.REPLACE
                    ).aggregate(sum=Sum('quantity')).get('sum')
                    replace_count = replace_count if replace_count else 0
                    qyt = detail.model_quantity_purchased - replace_count
                    self.stock_service.update_stock_qty(stock, qyt)
            else:
                self.stock_service.back_stock(stock)

    @transaction.atomic
    def partially_shipment(self, openid, order_id_list):
        """
        部分出货，用于特殊情况缺货，导致只能部分出货
        """
        if openid is None:
            raise ValueError('openid can not be none')
        if order_id_list is not None and len(order_id_list) > 0:
            logger.info('order partially shipment: %s', order_id_list)
            # 已出货的忽略
            order_list = ShopeeOrderModel.objects.filter(
                openid=openid, id__in=order_id_list, handle_status__in=[
                    OrderHandleStatus.LACK, OrderHandleStatus.UNPROCESSED, OrderHandleStatus.AT_LAST
                ])
            for order in order_list:
                # 状态修改为12，不缺货的直接发出，缺货的库存设置为0
                for detail in ShopeeOrderDetailModel.objects.filter(openid=openid, shopee_order=order):
                    self.__partially_stock_shipment(detail.stock)
                for modify in ShopeeOrderModifyModel.objects.filter(openid=openid, shopee_order=order):
                    self.__partially_stock_shipment(modify.stock)
                for package in ShopeeOrderPackageModel.objects.filter(openid=openid, shopee_order=order):
                    self.__partially_stock_shipment(package.stock)
                order.handle_status = OrderHandleStatus.PARTIALLY_SHIPMENT
                order.save()

    def __partially_stock_shipment(self, stock):
        if stock:
            if not self.stock_service.ship_reserve_stock(stock.id):
                self.stock_service.update_stock_qty(stock, 0)
                if not self.stock_service.ship_reserve_stock(stock):
                    raise ValueError('Partially shipment error: update qty 0 and reserve error')

    @transaction.atomic
    def forced_shipment(self, openid, order_id_list):
        """
        强制出货
        """
        if openid is None:
            raise ValueError('openid can not be none')
        if order_id_list is not None and len(order_id_list) > 0:
            logger.info('order forced shipment: %s', order_id_list)
            # 已出货的忽略
            order_list = ShopeeOrderModel.objects.filter(
                openid=openid, id__in=order_id_list, handle_status__in=[
                    OrderHandleStatus.LACK, OrderHandleStatus.UNPROCESSED, OrderHandleStatus.AT_LAST
                ])
            for order in order_list:
                # 状态修改为12，释放已经锁定的库存
                for detail in ShopeeOrderDetailModel.objects.filter(openid=openid, shopee_order=order):
                    if detail.stock:
                        qty = detail.stock.qty
                        self.stock_service.back_stock(detail.stock, is_delete=True)  # 强制出货, 无须预留库存
                        stock_bean = OrderDetailStockBeanFactory(detail).create().set_stock_qty(qty)
                        detail.stock = self.stock_service.add_shipping_stock(stock_bean)
                for modify in ShopeeOrderModifyModel.objects.filter(openid=openid, shopee_order=order):
                    if modify.stock:
                        qty = modify.stock.qty
                        self.stock_service.back_stock(modify.stock, is_delete=True)  # 强制出货, 无须预留库存
                        stock_bean = OrderModifyStockBeanFactory(modify).create().set_stock_qty(qty)
                        modify.stock = self.stock_service.add_shipping_stock(stock_bean)
                for package in ShopeeOrderPackageModel.objects.filter(openid=openid, shopee_order=order):
                    if package.stock:
                        qty = package.stock.qty
                        self.stock_service.back_stock(package.stock, is_delete=True)  # 强制出货, 无须预留库存
                        stock_bean = OrderPackageStockBeanFactory(package).create().set_stock_qty(qty)
                        package.stock = self.stock_service.add_shipping_stock(stock_bean)
                order.handle_status = OrderHandleStatus.FORCED_SHIPMENT
                order.save()

    @transaction.atomic
    def shipment(self, openid, order_id_list):
        if openid is None:
            raise ValueError('openid can not be none')
        if order_id_list is not None and len(order_id_list) > 0:
            logger.info('order shipment: %s', order_id_list)
            for order_id in order_id_list:
                # 检查订单是否都已经锁定
                for detail in ShopeeOrderDetailModel.objects.filter(shopee_order=order_id):
                    if detail.stock and detail.stock.stock_status != StockRecord.SHIP_STOCK:
                        logger.error('order shipment error: %s, stock_status not yet reserve', order_id)
                        raise ValueError('order shipment error: %s, stock_status not yet reserve' % order_id)
                for modify in ShopeeOrderModifyModel.objects.filter(shopee_order=order_id):
                    if modify.stock.stock_status != StockRecord.SHIP_STOCK:
                        raise ValueError('order shipment error: %s, stock_status not yet reserve' % order_id)
                for package in ShopeeOrderPackageModel.objects.filter(shopee_order=order_id):
                    if package.stock.stock_status != StockRecord.SHIP_STOCK:
                        raise ValueError('order shipment error: %s, stock_status not yet reserve' % order_id)

            ShopeeOrderModel.objects.filter(
                openid=openid, id__in=order_id_list, handle_status=OrderHandleStatus.UNPROCESSED
            ).update(handle_status=OrderHandleStatus.SHIPPED)
        else:
            raise ValueError('order_id_list must be > 0')

    def stock_matching_by_order(self, openid, order_id):
        order = ShopeeOrderModel.objects.get(pk=order_id)
        if order:
            if order.order_status in [OrderStatus.PROCESSED, OrderStatus.READY_TO_SHIP, OrderStatus.SHIPPED] and \
                    order.handle_status in [OrderHandleStatus.UNPROCESSED, OrderHandleStatus.LACK, OrderHandleStatus.AT_LAST]:
                available = True
                modify_list = ShopeeOrderModifyModel.objects.filter(openid=openid, shopee_order=order)
                for modify in modify_list:
                    reserve = False
                    if modify.stock:
                        reserve = self.stock_service.ship_reserve_stock(modify.stock)
                    available = available and reserve
                detail_no_variant_map = {}
                for detail in ShopeeOrderDetailModel.objects.filter(openid=openid, shopee_order=order):
                    reserve = False
                    if detail.stock:
                        reserve = self.stock_service.ship_reserve_stock(detail.stock)
                    elif detail.model_id == '0':
                        item_qty = detail_no_variant_map.get(detail.item_id)
                        item_qty = item_qty if item_qty else 0
                        item_qty += detail.model_quantity_purchased
                        detail_no_variant_map[detail.item_id] = item_qty
                        reserve = True
                    available = available and reserve
                for package in ShopeeOrderPackageModel.objects.filter(openid=openid, shopee_order=order):
                    reserve = False
                    if package.stock:
                        reserve = self.stock_service.ship_reserve_stock(package.stock)
                    available = available and reserve
                for item_id in detail_no_variant_map:
                    replaced_sum = modify_list.filter(
                        modify_type=OrderModifyType.REPLACE_NO_VARIANTS, replaced_id=item_id
                    ).aggregate(sum=Sum('quantity')).get('sum')
                    if replaced_sum != detail_no_variant_map.get(item_id):
                        available = False
                logger.info('order: %s, available: %s', order.order_sn, available)
                if available:
                    order.handle_status = OrderHandleStatus.UNPROCESSED
                    order.save()
                return available
            else:
                raise ValueError('Incorrect order status')
        else:
            raise ValueError('Order not found')

    @transaction.atomic
    def stock_matching(self, openid):
        # 订单匹配库存
        orders = ShopeeOrderModel.objects.filter(
            openid=openid,
            order_status__in=[OrderStatus.PROCESSED, OrderStatus.READY_TO_SHIP, OrderStatus.SHIPPED],
            handle_status__in=[
                OrderHandleStatus.UNPROCESSED, OrderHandleStatus.LACK, OrderHandleStatus.AT_LAST
            ]).order_by('-handle_status', 'ship_by_date')
        for order in orders:
            self.stock_matching_by_order(openid, order.id)

    @transaction.atomic
    def delete_order_modify(self, openid, modify_id):
        modify = ShopeeOrderModifyModel.objects.get(id=modify_id)
        if modify.openid == openid:
            self.cancel_package(openid, modify_id, OrderPackageType.MODIFY)
            if modify.modify_type == OrderModifyType.REPLACE or modify.modify_type == OrderModifyType.REPLACE_NO_VARIANTS:
                if modify.modify_type == OrderModifyType.REPLACE:
                    details = ShopeeOrderDetailModel.objects.filter(model_id=modify.replaced_id)
                else:
                    details = ShopeeOrderDetailModel.objects.filter(item_id=modify.replaced_id)
                leave_qty = modify.stock.stock_qty
                for detail in details:
                    if leave_qty != 0:
                        cur_stock_qty = detail.stock.stock_qty
                        max_stock_qty = detail.model_quantity_purchased
                        if max_stock_qty > cur_stock_qty:
                            if leave_qty > (max_stock_qty - cur_stock_qty):
                                new_stock_qty = max_stock_qty
                                leave_qty -= (max_stock_qty - cur_stock_qty)
                            else:
                                new_stock_qty = cur_stock_qty + leave_qty
                                leave_qty -= leave_qty
                            self.stock_service.back_stock(detail.stock, to_reserve_qty=new_stock_qty)
                if leave_qty != 0:
                    raise ValueError('Delete Modify Error: leave_qty != 0')
            modify.delete()
            if modify.stock:
                self.stock_service.delete_stock(modify.stock)
        else:
            logger.error('Openid:%s Auth Error, order modify id: %s', openid, modify_id)
            raise ValueError('Openid Auth Error')

    def freed_model_stock(self, openid, is_modify, pk):
        if is_modify:
            modify = ShopeeOrderModifyModel.objects.get(openid=openid, pk=pk)
            order = modify.shopee_order
            stock = modify.stock
            package_type = OrderPackageType.MODIFY
            uid = modify.id
        else:
            detail = ShopeeOrderDetailModel.objects.get(openid=openid, pk=pk)
            order = detail.shopee_order
            stock = detail.stock
            package_type = OrderPackageType.DETAIL
            uid = detail.id
        if order.handle_status > 0:
            raise ValueError('The order has been shipped and the inventory information cannot be changed')

        self.stock_service.back_stock(stock)
        for package in ShopeeOrderPackageModel.objects.filter(openid=openid, type=package_type, uid=uid):
            self.stock_service.back_stock(package.stock)
        order.handle_status = OrderHandleStatus.LACK
        order.save()

    def model_stock_matching(self, openid, is_modify, pk):
        if is_modify:
            modify = ShopeeOrderModifyModel.objects.get(openid=openid, pk=pk)
            stock = modify.stock
            uid = modify.id
            package_type = OrderPackageType.MODIFY
        else:
            detail = ShopeeOrderDetailModel.objects.get(openid=openid, pk=pk)
            stock = detail.stock
            uid = detail.id
            package_type = OrderPackageType.DETAIL
        self.stock_service.ship_reserve_stock(stock)
        for package in ShopeeOrderPackageModel.objects.filter(openid=openid, type=package_type, uid=uid):
            self.stock_service.ship_reserve_stock(package.stock)

    @transaction.atomic
    def order_modify(self, params):
        order_id = params.get('orderId')
        modify_type = params.get('modifyType')
        model_list = params.get('modelList')
        replaced_sku = params.get('replacedSku')
        replaced_id = params.get('replacedId')
        if modify_type is None:
            raise ValueError('Missing param modifyType')
        if model_list is None or len(model_list) == 0:
            raise ValueError('Missing param modelList')
        if (modify_type == OrderModifyType.REPLACE or modify_type == OrderModifyType.REPLACE_NO_VARIANTS) \
                and replaced_sku is None:
            raise ValueError('Missing param replacedSku')
        order = ShopeeOrderModel.objects.get(pk=order_id)
        modify_list = []
        check_sku = {}
        if order.handle_status != OrderHandleStatus.SHIPPED:
            self.freed_stock(order.openid, [order.id])
        for model in model_list:
            quantity = model.get('quantity')
            global_sku = model.get('globalSku')
            image_url = model.get('imageUrl')
            goods_id = model.get('goodsId')
            if model.get('quantity') is None or int(quantity) <= 0:
                continue
            if image_url is None or global_sku is None:
                raise ValueError('Missing model imageUrl or globalSku')
            modify = ShopeeOrderModifyModel(
                creater=order.creater, openid=order.openid,
                shopee_order=order, global_sku=global_sku,
                modify_type=modify_type, quantity=quantity,
                image_url=image_url
            )
            if modify_type == OrderModifyType.REPLACE or modify_type == OrderModifyType.REPLACE_NO_VARIANTS:
                modify.replaced_id = replaced_id
                modify.replaced_sku = replaced_sku
                sku_quantity = check_sku.get(replaced_sku) if check_sku.get(replaced_sku) is not None else 0
                check_sku[replaced_sku] = sku_quantity + int(quantity)
            stock_bean = OrderModifyStockBeanFactory(modify).create().set_stock_qty(int(modify.quantity))
            modify.stock = self.stock_service.reserve_stock(stock_bean)
            modify_list.append(modify)

        if modify_type == OrderModifyType.REPLACE:
            detail = ShopeeOrderDetailModel.objects.get(pk=params.get('id'))
            for replaced_sku in check_sku:
                qty = self.__check_replaced_sku_quantity(order, modify_type, replaced_id, check_sku.get(replaced_sku))
                self.stock_service.update_stock_qty(detail.stock, qty)

        if modify_type == OrderModifyType.REPLACE_NO_VARIANTS:
            detail = ShopeeOrderDetailModel.objects.get(pk=params.get('id'))
            for replaced_sku in check_sku:
                qty = self.__check_replaced_sku_quantity(order, modify_type, replaced_id, check_sku.get(replaced_sku))
                if detail.stock:
                    self.stock_service.update_stock_qty(detail.stock, qty)
        for modify in modify_list:
            modify.save()

    @transaction.atomic
    def toggle_package(self, openid, uid, order_package_type):
        from goods.gRpc.client.goods_service_stub import GoodsServiceClient as GoodsClient
        if order_package_type == OrderPackageType.DETAIL:
            order_detail = ShopeeOrderDetailModel.objects.get(openid=openid, id=uid)
            order = order_detail.shopee_order
            sku = order_detail.model_sku
            stock = order_detail.stock
            quantity = order_detail.model_quantity_purchased
        elif order_package_type == OrderPackageType.MODIFY:
            order_modify = ShopeeOrderModifyModel.objects.get(openid=openid, id=uid)
            order = order_modify.shopee_order
            sku = order_modify.global_sku
            stock = order_modify.stock
            quantity = order_modify.quantity
        else:
            logger.error('Error Order Package Type')
            raise ValueError('Error Order Package Type')
        if order.handle_status > 0:
            logger.error('Order shipped %s', order.handle_status)
            raise Exception('Order shipped')
        package = ShopeeOrderPackageModel.objects.filter(type=order_package_type, uid=uid)
        if package.exists():
            logger.error('Package already exists, type:%s, uid:%s', order_package_type, uid)
            raise ValueError('Package already exists')
        else:
            package = StoreProductPackageModel.objects.filter(
                sku=sku, product_type=PackageProductType.STORE_VARIANTS).first()
            if not package:
                raise ValueError('Package undefined')
            self.stock_service.back_stock(stock)
            for item in package.package_item.all():
                stock = self.stock_service.reserve_stock(
                    int(quantity), item.uid, order.openid, order.creater)
                order_package = ShopeeOrderPackageModel(
                    openid=openid, creater=order.creater,
                    shopee_order=order, type=order_package_type,
                    sku=item.sku, uid=uid, quantity=quantity, image_url=stock.goods_image,
                    stock=stock
                )
                order_package.save()
            self.stock_service.update_stock_qty(stock, 0)
            order.handle_status = OrderHandleStatus.LACK
            order.save()

    @transaction.atomic
    def cancel_package(self, openid, uid, order_package_type):
        if order_package_type == OrderPackageType.DETAIL:
            order_detail = ShopeeOrderDetailModel.objects.get(openid=openid, id=uid)
            order = order_detail.shopee_order
            stock = order_detail.stock
        elif order_package_type == OrderPackageType.MODIFY:
            order_modify = ShopeeOrderModifyModel.objects.get(openid=openid, id=uid)
            order = order_modify.shopee_order
            stock = order_modify.stock
        else:
            logger.error('Error Order Package Type')
            raise ValueError('Error Order Package Type')
        if order.handle_status > 0:
            logger.error('Order shipped %s', order.handle_status)
            raise Exception('Order shipped')
        self.stock_service.back_stock(stock)
        count = 0
        package_stock_sum = 0
        packages = ShopeeOrderPackageModel.objects.filter(openid=openid, type=order_package_type, uid=uid)
        if packages.exists():
            for package in packages:
                count += 1
                package_stock_sum += package.quantity
                if package.stock:
                    self.stock_service.back_stock(package.stock)
                    self.stock_service.delete_stock(package.stock)
                package.delete()
            quantity = package_stock_sum / count
            self.stock_service.update_stock_qty(stock, quantity)
            order.handle_status = OrderHandleStatus.LACK
            order.save()

    def __check_replaced_sku_quantity(self, order, replaced_type, replaced_id, sku_quantity):
        if replaced_type == OrderModifyType.REPLACE:
            sku_ori_quantity = ShopeeOrderDetailModel.objects.filter(
                shopee_order=order, model_id=replaced_id
            ).aggregate(sum=Sum('model_quantity_purchased')).get('sum')
        elif replaced_type == OrderModifyType.REPLACE_NO_VARIANTS:
            sku_ori_quantity = ShopeeOrderDetailModel.objects.filter(
                shopee_order=order, item_id=replaced_id
            ).aggregate(sum=Sum('model_quantity_purchased')).get('sum')
        else:
            raise ValueError('Replaced Type: %s Not Exists' % replaced_type)
        if sku_ori_quantity is None:
            raise ValueError('Replaced Id: %s Error' % replaced_id)

        replaced_sku_quantity = ShopeeOrderModifyModel.objects.filter(
            shopee_order=order, replaced_id=replaced_id
        ).aggregate(sum=Sum('quantity')).get('sum')
        replaced_sku_quantity = 0 if replaced_sku_quantity is None else replaced_sku_quantity
        if (sku_ori_quantity - replaced_sku_quantity) < sku_quantity:
            raise ValueError('Already beyond the replacement quantity')
        else:
            return sku_ori_quantity - replaced_sku_quantity - sku_quantity
            # return sku_quantity

    def update_openid(self, store: StoreModel):
        ShopeeOrderModel.objects.filter(store=store).update(openid=store.openid, creater=store.creater)
        ShopeeOrderDetailModel.objects.filter(shopee_order__store=store) \
            .update(openid=store.openid, creater=store.creater)
        ShopeeOrderMessageModel.objects.filter(shopee_order__store=store) \
            .update(openid=store.openid, creater=store.creater)

    def sync_shipment_list(self, shop_id):
        """
        同步待发货订单
        """
        cursor = ''
        flag = True
        # 最大100限制
        page_size = 100
        order_sn_list = []
        while flag:
            ret = shopee.request(url_key='order.get_shipment_list', method='GET', shop_id=shop_id, params={
                'cursor': cursor,
                'page_size': page_size
            })
            if ret.get('response') is None:
                flag = False
                cursor = ''
            else:
                resp = ret.get('response')
                for order in resp.get('order_list'):
                    order_sn_list.append(order.get('order_sn'))
                flag = resp.get('more')
                cursor = resp.get('next_cursor') if flag else ''
        self.refresh_order_detail(shop_id, order_sn_list)

    def get_order_list(self, shop_id, order_status):
        """
        查询本地订单数据
        shop_id: Shopee 店铺ID
        order_status: 订单状态或状态列表, 如OrderStatus.READY_TO_SHIP
        """
        if order_status is None or shop_id is None:
            raise ValueError('Params Error')
        if isinstance(order_status, list):
            return ShopeeOrderModel.objects.filter(
                store__type=StoreType.SHOP,
                store__uid=shop_id,
                order_status__in=order_status)
        else:
            return ShopeeOrderModel.objects.filter(
                store__type=StoreType.SHOP,
                store__uid=shop_id,
                order_status=order_status)

    def get_order_logistics_file(self, openid, order_sn_strs):
        """
        获取订单物流面单文件
        shop_id: Shopee店铺ID
        order_sn_strs: 订单列表，”,“分割的字符串
        """
        if openid is None:
            raise ValueError('openid can not be none')
        if order_sn_strs is not None and len(order_sn_strs) > 0:
            order_sn_list = order_sn_strs.split(',')
            if len(order_sn_list) == 1:
                return ShopeeOrderModel.objects.get(order_sn=order_sn_list[0]).waybill_path
            else:
                shipping_doc_path = settings.SHOPEE.get('shipping_doc_path')
                base_path = shipping_doc_path + "/" + datetime.datetime.now().strftime('%Y%m%d')
                md5hash = md5(order_sn_strs.encode('utf-8')).hexdigest()
                merger_pdf_path = base_path + "/" + openid + md5hash + '.pdf'
                if os.path.isfile(merger_pdf_path):
                    return merger_pdf_path
                merger = PdfMerger()
                try:
                    for order in ShopeeOrderModel.objects.filter(
                            openid=openid,
                            store__type=StoreType.SHOP,
                            order_sn__in=order_sn_list
                    ).values('waybill_path'):
                        waybill_path = order.get('waybill_path')
                        if waybill_path is not None and len(waybill_path) > 0:
                            merger.append(waybill_path)
                        else:
                            raise ValueError('Order Logistics pdf not exist')
                    if not os.path.exists(base_path):
                        os.makedirs(base_path)
                    merger.write(merger_pdf_path)
                    return merger_pdf_path
                finally:
                    merger.close()
        else:
            raise ValueError('order_sn_list must > 0')

    def multi_shop_apply_logistics(self, openid, order_sn_list):
        if not order_sn_list or len(order_sn_list) == 0:
            raise ValueError('Order List must > 0')
        order_list = ShopeeOrderModel.objects.filter(openid=openid, order_sn__in=order_sn_list)
        if len(order_list) == len(order_sn_list):
            shop_map = {}
            for order in order_list:
                shop_id = order.store.uid
                shop_order_list = shop_map.get(shop_id)
                if not shop_order_list:
                    shop_map[shop_id] = []
                    shop_map[shop_id].append(order.order_sn)
                else:
                    shop_order_list.append(order.order_sn)
            for shop_id in shop_map:
                self.apply_logistics(shop_id, shop_map.get(shop_id))
        else:
            raise ValueError('Auth Error: No permission to operate')

    # 申请并下载Shopee面单
    def apply_logistics(self, shop_id, order_sn_list):
        if not shop_id:
            raise ValueError('Shop ID can not be None')
        if not order_sn_list or len(order_sn_list) == 0:
            raise ValueError('Order List must > 0')
        # 同步订单，获取最新状态或信息
        self.sync_order_by_order_sn(shop_id, order_sn_list)
        # 待出货
        ready_list = []
        # 已处理
        processed_list = []
        for order in ShopeeOrderModel.objects.filter(order_sn__in=order_sn_list):
            if order.order_status == 'READY_TO_SHIP':
                ready_list.append({'order_sn': order.order_sn})
            if order.order_status == 'PROCESSED':
                # 判断是否已经存在该物流面单
                if order.waybill_path is not None and os.path.isfile(order.waybill_path):
                    continue
                bill_path = spg.search_order_bill(order.order_sn)
                if bill_path:
                    order.waybill_path = bill_path
                    order.save()
                else:
                    processed_list.append({'order_sn': order.order_sn})

        if len(ready_list) > 0:
            # 申请面单
            for order in ready_list:
                order_sn = order.get('order_sn')
                self.__shipping_order(shop_id, order_sn)
                # order['tracking_number'] = self.__get_tracking_number(shop_id, order_sn)
            success_list = self.__create_shipping_document(shop_id, ready_list)
            processed_list.extend(success_list)
            OrderRecordService.get_instance().record_order(success_list, OrderRecordType.CREATE_SHIPPING_DOCUMENT)

        if len(processed_list) > 0:
            # 下载面单到本地
            for order in processed_list:
                self.__download_shipping_document(shop_id, order)

    def __download_shipping_document(self, shop_id, order, request_num=0):
        shipping_doc_path = settings.SHOPEE.get('shipping_doc_path')
        if not os.path.isdir(shipping_doc_path):
            raise NotADirectoryError('"shipping_doc_path" directory not exists, '
                                     'please setting shipping_doc_path in "settings.py" file')
        base_path = shipping_doc_path + "/" + datetime.datetime.now().strftime('%Y%m%d')
        if not os.path.exists(base_path):
            os.makedirs(base_path)
        try:
            ret = shopee.request(
                url_key='logistics.download_shipping_document',
                shop_id=shop_id,
                method='POST',
                params={
                    'order_list': [order]
                }
            )
            file_path = base_path + "/" + order.get('order_sn') + ".pdf"
            # 如果文件存在删除原文件
            if os.path.isfile(file_path):
                os.remove(file_path)
            with open(file_path, "wb") as code:
                code.write(ret)
            ShopeeOrderModel.objects.filter(order_sn=order.get('order_sn')).update(
                waybill_path=file_path,
                order_status=OrderStatus.PROCESSED,
            )
        except Exception as e:
            if request_num < 2:
                time.sleep(1)
                logger.warning('logistics.download_shipping_document error: %s', e)
                request_num += 1
                return self.__download_shipping_document(shop_id, order, request_num)
            else:
                logger.error('logistics.download_shipping_document error: %s', e)
                raise e

    def get_order_details(self, order_id):
        """
        通过OrderID 查询订单下的所有规格详情
        """
        data = {
            'order_id': order_id,
            'order_detail_list': [],
            'reissue_list': []
        }
        order_detail_map = {}
        order_detail_list = ShopeeOrderDetailModel.objects.filter(shopee_order=order_id)
        for order_detail in order_detail_list:
            detail = order_detail_map.get(order_detail.model_id)
            if detail:
                detail.model_quantity_purchased += order_detail.model_quantity_purchased
                if order_detail.stock:
                    detail.stock.stock_qty += order_detail.stock.stock_qty
            else:
                order_detail_map[order_detail.model_id] = order_detail

        for key in order_detail_map:
            order_detail = order_detail_map.get(key)
            logger.info('goods_code stock %s', order_detail.stock)

            goods_code = order_detail.stock.goods_code if order_detail.stock else order_detail.model_sku
            logger.info('goods_code %s', goods_code)
            dict_order_detail = spg.django_model_to_dict(model=order_detail)
            dict_order_detail['has_package'] = StoreProductPackageModel.objects.filter(
                openid=order_detail.openid, sku=order_detail.model_sku).exists()
            packages = ShopeeOrderPackageModel.objects.filter(
                shopee_order=order_id, type=OrderPackageType.DETAIL, uid=order_detail.id)
            if packages.exists():
                dict_order_detail['packages'] = []
                for package in packages:
                    _package = spg.django_model_to_dict(model=package)
                    _package['stock'] = spg.django_model_to_dict(model=package.stock)
                    _package['stock']['goods'] = {'goods_code': package.stock.goods_code,
                                                  'goods_image': package.stock.goods_image}
                    dict_order_detail['packages'].append(_package)
            dict_order_detail['replace_list'] = self.get_order_replace_list(order_id, order_detail)
            if order_detail.stock:
                dict_order_detail['stock'] = spg.django_model_to_dict(order_detail.stock)
                dict_order_detail['stock']['goods'] = {'goods_code': order_detail.stock.goods_code,
                                                       'goods_image': order_detail.stock.goods_image}

            # dict_order_detail['stock'] = StockListGetSerializer(order_detail.stock).data
            dict_order_detail['goods_code'] = goods_code
            data['order_detail_list'].append(dict_order_detail)
        data['reissue_list'].extend(
            self.get_order_reissue_list(order_id)
        )
        data['messages'] = spg.django_model_to_dict(
            model_list=ShopeeOrderMessageModel.objects.filter(shopee_order=order_id))
        return data

    def get_order_reissue_list(self, order_id):
        reissue_list = []
        reissues = ShopeeOrderModifyModel.objects.filter(
            shopee_order=order_id, modify_type=OrderModifyType.REISSUE
        )
        for reissue in reissues:
            _reissue = spg.django_model_to_dict(model=reissue)
            _reissue['stock'] = spg.django_model_to_dict(model=reissue.stock)
            _reissue['stock']['goods'] = {'goods_code': reissue.stock.goods_code,
                                          'goods_image': reissue.stock.goods_image}
            _reissue['has_package'] = StoreProductPackageModel.objects.filter(
                openid=reissue.openid, sku=reissue.global_sku).exists()
            packages = ShopeeOrderPackageModel.objects.filter(
                shopee_order=order_id, type=OrderPackageType.MODIFY, uid=reissue.id)
            if packages.exists():
                _reissue['packages'] = []
                for package in packages:
                    _package = spg.django_model_to_dict(model=package)
                    _package['stock'] = spg.django_model_to_dict(model=package.stock)
                    _package['stock']['goods'] = {'goods_code': package.stock.goods_code,
                                                  'goods_image': package.stock.goods_image}
                    _reissue['packages'].append(_package)
            reissue_list.append(_reissue)
        return reissue_list

    def get_order_replace_list(self, order_id, detail):
        replace_list = []
        if detail.model_sku:
            replaces = ShopeeOrderModifyModel.objects.filter(
                shopee_order=order_id,
                replaced_id=detail.model_id,
                modify_type=OrderModifyType.REPLACE
            )
        else:
            replaces = ShopeeOrderModifyModel.objects.filter(
                shopee_order=order_id,
                replaced_id=detail.item_id,
                modify_type=OrderModifyType.REPLACE_NO_VARIANTS
            )
        for replace in replaces:
            _replace = spg.django_model_to_dict(model=replace)
            _replace['stock'] = spg.django_model_to_dict(model=replace.stock)
            _replace['stock']['goods'] = {'goods_code': replace.stock.goods_code,
                                          'goods_image': replace.stock.goods_image}
            _replace['has_package'] = StoreProductPackageModel.objects.filter(
                openid=replace.openid, sku=replace.global_sku).exists()
            packages = ShopeeOrderPackageModel.objects.filter(
                shopee_order=order_id, type=OrderPackageType.MODIFY, uid=replace.id)
            if packages.exists():
                _replace['packages'] = []
                for package in packages:
                    _package = spg.django_model_to_dict(model=package)
                    _package['stock'] = spg.django_model_to_dict(model=package.stock)
                    _package['stock']['goods'] = {'goods_code': package.stock.goods_code,
                                                  'goods_image': package.stock.goods_image}
                    _replace['packages'].append(_package)
            replace_list.append(_replace)
        return replace_list

    def sync_order_by_order_sn_and_openid(self, openid, order_sn):
        order = ShopeeOrderModel.objects.get(openid=openid, order_sn=order_sn)
        self.sync_order_by_order_sn(order.store.uid, order_sn)

    def sync_order_by_order_sn(self, shop_id, order_sn):
        """
        同步指定订单号的订单信息
        """
        order_sn_list = []
        if order_sn is None:
            raise ValueError('order_sn can not be None')
        elif isinstance(order_sn, list):
            order_sn_list.extend(order_sn)
        else:
            order_sn_list.append(order_sn)
        self.refresh_order_detail(shop_id, order_sn_list)

    def sync_batch_order(self, shop_id, time_from, time_to, order_status=None):
        """
        根据指定的店铺、时间、状态，同步所有订单
        """
        if shop_id is None:
            raise ValueError('Missing shop_id')
        start_time = int(time.time())
        logger.info('Sync Shop: %s Order Start...', shop_id)

        order_sn_list = []

        logger.info('Sync all order in the shop %s, from: %s ~ to: %s',
                    shop_id,
                    datetime.datetime.fromtimestamp(time_from).strftime('%Y-%m-%d'),
                    datetime.datetime.fromtimestamp(time_to).strftime('%Y-%m-%d')
                    )
        # Shopee 查询日期的限制
        days_limit = 15
        for sub_time in self.__split_datetime_list(time_from, time_to, days_limit):
            cursor = ''
            flag = True
            while flag:
                # Shopee Order List Max Page Size
                page_size = 100
                params = {
                    'cursor': cursor,
                    'page_size': page_size,
                    'time_range_field': 'create_time',
                    'time_from': sub_time.get('time_from'),
                    'time_to': sub_time.get('time_to'),
                    'response_optional_fields': 'order_status'
                }
                if order_status is not None:
                    params['order_status'] = order_status
                ret = shopee.request(url_key='order.get_order_list', shop_id=shop_id, method='GET', params=params)
                if ret.get('response') is None:
                    flag = False
                    cursor = ''
                else:
                    response = ret.get('response')
                    logger.info('response: %s', response)
                    for order in response.get('order_list'):
                        order_sn = order.get('order_sn')
                        order_sn_list.append(order_sn)
                    flag = response.get('more')
                    cursor = response.get('next_cursor') if flag else ''

        self.refresh_order_detail(shop_id, order_sn_list)
        end_time = int(time.time())
        logger.info('Sync Order: %s completion, Take %s s', shop_id, (end_time - start_time))

    def refresh_order_detail(self, shop_id, order_sn_list):
        """
        刷新订单详情信息
        """
        store = StoreModel.objects.get(uid=shop_id, type=StoreType.SHOP)
        if len(order_sn_list) > 0:
            # Shopee最大限制为50
            max_len = 50
            for sub_list in self.__split_list(order_sn_list, max_len):
                for order_info in self.__request_order_detail(shop_id, sub_list):
                    try:
                        order = ShopeeOrderModel.objects.filter(
                            store__uid=shop_id, order_sn=order_info.get('order_sn')).first()
                        if order:
                            order.openid = store.openid
                            order.creater = store.creater
                        else:
                            order = ShopeeOrderModel(
                                store=store, openid=store.openid, creater=store.creater,
                                handle_status=OrderHandleStatus.LACK)
                        new_order = self.save_order(order, order_info)
                        self.save_order_detail(new_order, order_info.get('item_list'))
                        self.save_order_message(new_order, order_info)
                    except Exception as e:
                        logger.error('Refresh Order Detail error: %s\n%s', e, traceback.format_exc())

    # 获取列印出货单的参数
    def __create_shipping_document(self, shop_id, order_sn_list, request_num=0):
        # logistics.get_shipping_document_parameter
        ret = shopee.request(
            url_key='logistics.get_shipping_document_parameter', shop_id=shop_id, method='POST', params={
                'order_list': order_sn_list
            })
        logger.info('get_shipping_document_parameter res: %s', ret)
        result_list = ret.get('response').get('result_list')
        if len(result_list) != len(order_sn_list):
            raise ValueError('logistics.get_shipping_document_parameter error: result_list != order_list')
        csd_order_list = []
        for result in result_list:
            csd = {
                'order_sn': result.get('order_sn'),
                'package_number': result.get('package_number'),
                'shipping_document_type': result.get('suggest_shipping_document_type')
            }
            ret = shopee.request(
                url_key='logistics.get_tracking_number', shop_id=shop_id,
                method='GET', params={
                    'order_sn': csd.get('order_sn'),
                    'package_number': csd.get('package_number')
                })
            tracking_number = ret.get('response').get('tracking_number')
            csd['tracking_number'] = tracking_number
            csd_order_list.append(csd)
        try:
            ret = shopee.request(url_key='logistics.create_shipping_document', shop_id=shop_id,
                                 method='POST', params={'order_list': csd_order_list})
            logger.info('create_shipping_document res: %s', ret)
            processed_list = []
            resp = ret.get('response')
            if len(resp.get('result_list')) == len(csd_order_list):
                for order in resp.get('result_list'):
                    processed_list.append({'order_sn': order.get('order_sn')})
            else:
                logger.warning('logistics.create_shipping_document warning：%s', resp.get('warning'))
            return processed_list
        except Exception as e:
            if request_num < 2:
                logger.warning('logistics.create_shipping_document error: %s', e)
                request_num += 1
                return self.__create_shipping_document(shop_id, order_sn_list, request_num)
            else:
                logger.error('logistics.create_shipping_document error: %s', e)
                raise e

    def __get_tracking_number(self, shop_id, order_sn):
        ret = shopee.request(url_key='logistics.get_tracking_number', shop_id=shop_id, method='GET', params={
            'order_sn': order_sn
        })
        return ret.get('response').get('tracking_number')

    def __shipping_order(self, shop_id, order_sn):
        # 获取申请面单的参数
        ret = shopee.request(url_key='logistics.get_shipping_parameter', shop_id=shop_id, method='GET', params={
            'order_sn': order_sn
        })
        params = {}
        res = ret.get('response')
        info_needed = res.get('info_needed')
        for attr in info_needed:
            params[attr] = {}
            attr_value = res.get(attr)
            for param_key in info_needed.get(attr):
                params[attr][param_key] = attr_value[param_key]
        params['order_sn'] = order_sn
        shopee.request(url_key='logistics.ship_order', shop_id=shop_id, method='POST', params=params)

    # 通过Shopee API 获取指定订单列表的订单详情信息
    def __request_order_detail(self, shop_id, order_sn_list):
        r_list = []
        ret = shopee.request(url_key='order.get_order_detail', shop_id=shop_id, method='GET', params={
            'order_sn_list': [','.join(order_sn_list)],
            'response_optional_fields': self.__order_detail_field
        })
        response = ret.get('response')
        order_list = response.get('order_list')
        if len(order_list) == len(order_sn_list):
            r_list.extend(order_list)
        else:
            r_list.extend(order_list)
            for order in order_list:
                order_sn_list.remove(order.get('order_sn'))
            r_list.extend(self.__request_order_detail(shop_id, order_sn_list))
        return r_list

    def save_order_message(self, order, order_info):
        """
        保存订单消息
        """
        order_message_list = []
        if order_info.get('cancel_reason') is not None and len(order_info.get('cancel_reason')) > 0:
            if not ShopeeOrderMessageModel.objects.filter(
                    shopee_order=order,
                    type=OrderMsgType.CANCEL
            ).exists():
                order_message = ShopeeOrderMessageModel(
                    shopee_order=order,
                    type=OrderMsgType.CANCEL,
                    mark=OrderMsgMark.PENDING,
                    message="%s:%s" % (order_info.get('cancel_by'), order_info.get('cancel_reason'))
                )
                order_message_list.append(order_message)
        if order_info.get('note') is not None and len(order_info.get('note')) > 0:
            if not ShopeeOrderMessageModel.objects.filter(
                    shopee_order=order,
                    type=OrderMsgType.SELLER_NOTES
            ).exists():
                order_message = ShopeeOrderMessageModel(
                    shopee_order=order,
                    type=OrderMsgType.SELLER_NOTES,
                    mark=OrderMsgMark.FINISHED,
                    message=order_info.get('note')
                )
                order_message_list.append(order_message)
            else:
                ShopeeOrderMessageModel.objects.filter(
                    shopee_order=order,
                    type=OrderMsgType.SELLER_NOTES).update(
                    message=order_info.get('note'),
                    update_time=datetime.datetime.fromtimestamp(order_info.get('note_update_time'))
                )
        if order_info.get('message_to_seller') is not None and len(order_info.get('message_to_seller')) > 0:
            if not ShopeeOrderMessageModel.objects.filter(
                    shopee_order=order,
                    type=OrderMsgType.MESSAGE_TO_SELLER
            ).exists():
                order_message = ShopeeOrderMessageModel(
                    shopee_order=order,
                    type=OrderMsgType.MESSAGE_TO_SELLER,
                    mark=OrderMsgMark.FINISHED,
                    message=order_info.get('message_to_seller')
                )
                order_message_list.append(order_message)
        # 保存订单消息
        if len(order_message_list) > 0:
            ShopeeOrderMessageModel.objects.bulk_create(order_message_list)

    def save_order_detail(self, order: ShopeeOrderModel, item_list):
        """
        保存订单详情
        """
        tmp_map = {}
        if item_list is not None and len(item_list) > 0:
            try:
                self.product_service.sync_global_product_by_item(order.store, item_list)
            except Exception as e:
                logger.warning('Order Sync Global Product Failed: %s\n%s', e, traceback.format_exc())
            for item in item_list:
                model_id = item.get('model_id')
                if not tmp_map.get(model_id):
                    tmp_map[model_id] = []
                exclude = tmp_map.get(model_id) if tmp_map.get(model_id) else []
                details = ShopeeOrderDetailModel.objects.exclude(id__in=exclude).filter(
                    shopee_order=order, model_id=item.get('model_id')
                )
                if details.exists():
                    order_detail = details.first()
                else:
                    order_detail = ShopeeOrderDetailModel(
                        shopee_order=order, openid=order.openid, creater=order.creater)
                order_detail.item_id = item.get('item_id')
                order_detail.item_name = item.get('item_name')
                order_detail.item_sku = item.get('item_sku')
                order_detail.model_id = item.get('model_id')
                order_detail.model_name = item.get('model_name')
                order_detail.model_sku = item.get('model_sku')
                order_detail.model_quantity_purchased = item.get('model_quantity_purchased')
                order_detail.model_original_price = item.get('model_original_price')
                order_detail.model_discounted_price = item.get('model_discounted_price')
                order_detail.image_url = item.get('image_info').get('image_url')
                order_detail.save()
                if order.order_status == OrderStatus.PROCESSED or order.order_status == OrderStatus.READY_TO_SHIP:
                    if not order_detail.stock and item.get('model_id') != 0:
                        package = StoreProductPackageModel.objects.filter(
                            sku=order_detail.model_sku, product_type=PackageProductType.STORE_VARIANTS).first()
                        detail_stock_qty = 0
                        if package:
                            for p_item in package.package_item.all():
                                stock_bean = OrderDetailStockBeanFactory(order_detail).create().set_stock_qty(
                                    order_detail.model_quantity_purchased).set_goods_id(p_item.uid)
                                stock = self.stock_service.reserve_stock(stock_bean)
                                order_package = ShopeeOrderPackageModel(
                                    openid=order_detail.openid, creater=order_detail.creater,
                                    shopee_order=order, type=OrderPackageType.DETAIL, sku=p_item.sku,
                                    uid=order_detail.id, quantity=order_detail.model_quantity_purchased,
                                    image_url=stock.goods_image, stock=stock
                                )
                                order_package.save()
                        else:
                            detail_stock_qty = order_detail.model_quantity_purchased
                        stock_bean = OrderDetailStockBeanFactory(order_detail).create().set_stock_qty(detail_stock_qty)
                        stock = self.stock_service.reserve_stock(stock_bean)
                        if not stock:
                            self.product_service.refresh_product(
                                order.store.uid, [order_detail.item_id], self.global_service.emit_goods)
                            stock = self.stock_service.reserve_stock(stock_bean)
                        order_detail.stock = stock if stock else None
                elif order.order_status != OrderStatus.UNPAID and order.order_status != OrderStatus.CANCELLED:
                    if not order_detail.stock_id and item.get('model_id') != 0:
                        stock_bean = OrderDetailStockBeanFactory(order_detail).create().set_stock_qty(
                            order_detail.model_quantity_purchased)
                        stock = self.stock_service.add_shipping_stock(stock_bean)
                        if not stock: # TODO 为何需要调用两次
                            self.product_service.refresh_product(
                                order.store.uid, [order_detail.item_id], self.global_service.emit_goods)
                            stock = self.stock_service.add_shipping_stock(stock_bean)
                        if stock:
                            order_detail.stock = stock
                else:
                    if order_detail.stock:
                        self.stock_service.update_stock_qty(order_detail.stock, 0)
                order_detail.save()
                tmp_map.get(model_id).append(order_detail.id)

    def _sync_goods_(self, store_model_ids):
        # store_product_model -> stor_product -> global_product -> global_product_model
        global_product_dict = {}
        for model_id in store_model_ids:
            store_model = StoreProductVariantModel.objects.filter(model_id=model_id).first()
            if not store_model:
                continue
            store_product = store_model.store_product
            if not store_product:
                continue
            global_product = store_product.global_product
            if not global_product_dict.get(global_product.product_id, None):
                global_product_dict[global_product.product_id] = global_product
        for product_id, global_product in global_product_dict.items():
            if not GoodsGroupRecord.objects.filter(product_id=product_id).exists():
                pass # TODO
                # goods =
                # req = CreateGroupRequest(name=global_product.product_sku)
                # GoodsServiceClient.get_instance().create_group()

    # 保存或更新ShopeeOrder
    def save_order(self, order, data):
        order.order_sn = data.get('order_sn')
        order.order_status = data.get('order_status')
        order.total_amount = data.get('total_amount')
        order.actual_shipping_fee = data.get('actual_shipping_fee')
        if data.get('pay_time') is not None:
            order.pay_time = datetime.datetime.fromtimestamp(data.get('pay_time'))
        order.ship_by_date = data.get('ship_by_date')
        order.buyer_user_id = data.get('buyer_user_id')
        order.buyer_username = data.get('buyer_username')
        order.days_to_ship = data.get('days_to_ship')
        # 当订单为第一次同步时，或者之前为未支付时候忽略的状态时，需要设置handle_status
        if not order.id or order.handle_status == OrderHandleStatus.IGNORE:
            if order.order_status == OrderStatus.READY_TO_SHIP \
                    or order.order_status == OrderStatus.PROCESSED:
                order.handle_status = OrderHandleStatus.LACK
            elif order.order_status == OrderStatus.UNPAID or order.order_status == OrderStatus.CANCELLED:
                order.handle_status = OrderHandleStatus.IGNORE
            else:
                order.handle_status = OrderHandleStatus.FORCED_SHIPMENT
        else:
            if order.order_status == OrderStatus.CANCELLED:
                order.handle_status = OrderHandleStatus.IGNORE
                for modify in ShopeeOrderModifyModel.objects.filter(shopee_order=order):
                    self.stock_service.update_stock_qty(modify.stock, 0)
        order.ship_by_date = datetime.datetime.fromtimestamp(data.get('ship_by_date'))
        if data.get('update_time') is not None:
            order.update_time = datetime.datetime.fromtimestamp(data.get('update_time'))
        if data.get('create_time') is not None:
            order.create_time = datetime.datetime.fromtimestamp(data.get('create_time'))
        order.save()
        return order

    # 将时间按指定天数区间划分列表
    def __split_datetime_list(self, start, end, days: int):
        if end < start:
            raise ValueError('Must be End time > Start time')
        if days is None or days <= 0:
            raise ValueError('Days must be > 0')
        start_time = datetime.datetime.fromtimestamp(start)
        end_time = datetime.datetime.fromtimestamp(end)
        num = (end_time - start_time).days
        while num > 0:
            if num > days:
                end = start_time + datetime.timedelta(days=days)
                yield {'time_from': int(start_time.timestamp()), 'time_to': int(end.timestamp())}
                start_time = end
                num = (end_time - start_time).days
            else:
                yield {'time_from': int(start_time.timestamp()), 'time_to': int(end_time.timestamp())}
                num = 0

    # 按照指定数量, 分割list
    def __split_list(self, iterable, n=1):
        itl = len(iterable)
        for ndx in range(0, itl, n):
            it = iterable[ndx:min(ndx + n, itl)]
            yield it

    __order_detail_field = [
        'buyer_user_id,'
        'buyer_username,'
        'estimated_shipping_fee,'
        # 'recipient_address,'
        'actual_shipping_fee,'
        'goods_to_declare,'
        'note,'
        'note_update_time,'
        'item_list,'
        'pay_time,'
        'dropshipper,'
        'dropshipper_phone,'
        'split_up,'
        'buyer_cancel_reason,'
        'cancel_by,'
        'cancel_reason,'
        'actual_shipping_fee_confirmed,'
        'buyer_cpf_id,'
        'fulfillment_flag,'
        'pickup_done_time,'
        # 'package_list,'
        'shipping_carrier,'
        # 'payment_method,'
        'total_amount,'
        'buyer_username,'
        # 'invoice_data,'
        # 'checkout_shipping_carrier,'
        # 'reverse_shipping_fee,'
        # 'order_chargeable_weight_gram'
    ]
