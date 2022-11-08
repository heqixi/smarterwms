import logging
import threading
import traceback

from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter

from order.models import ShopeeOrderModel, ShopeeOrderRecordModel, ShopeeOrderDetailModel, ShopeeOrderModifyModel
from order.page import MyPageNumberPagination
from order.serializers import OrderListGetSerializer, ShopeeOrderRecordGetSerializer
from order.services.order_record_service import OrderRecordService
from order.services.order_service import OrderService
from store.common import StoreType
from store.models import StoreModel
from utils import spg

logger = logging.getLogger()


class OrderRecord(viewsets.ModelViewSet):
    pagination_class = MyPageNumberPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['id', "create_time", "update_time"]
    record_service = OrderRecordService.get_instance()
    serializer_class = ShopeeOrderRecordGetSerializer

    def get_queryset(self):
        try:
            params = spg.parse_params(self.request)
            openid = self.request.META.get('HTTP_TOKEN')
            record_type = params.get('type')
            return self.record_service.get_record_batch_info(openid, record_type)
        except Exception as e:
            logger.error("refresh stock error: %s\n%s", e, traceback.format_exc())
            raise e


class Order(viewsets.ModelViewSet):
    pagination_class = MyPageNumberPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['id', "create_time", "update_time"]
    serializer_class = OrderListGetSerializer
    order_service = OrderService.get_instance()

    def get_queryset(self):
        try:
            params = spg.parse_params(self.request)
            openid = self.request.META.get('HTTP_TOKEN')
            ordering = params.get('ordering')
            ordering = ordering if ordering is not None else '-id'
            ordering_arr = []
            kwargs = {'store__type': StoreType.SHOP}
            exclude_kwargs = {}
            shop_id = params.get('shop_id')
            if openid is None:
                logger.error('openid cannot be none')
                raise ValueError('openid cannot be none')
            else:
                kwargs['openid'] = openid
            if shop_id is not None:
                kwargs['store__uid'] = shop_id
            order_sn = params.get('order_sn')
            if order_sn is not None:
                kwargs['order_sn__contains'] = order_sn.upper()
            buyer_user_id = params.get('buyer_user_id')
            if buyer_user_id is not None:
                kwargs['buyer_user_id'] = buyer_user_id
            buyer_username = params.get('buyer_username')
            if buyer_username is not None:
                kwargs['buyer_username'] = buyer_username
            order_status = params.get('order_status')
            if order_status is not None:
                kwargs['order_status'] = order_status.upper()
            if params.get('is_handle'):
                handle_status = params.get('handle_status')
                if handle_status is not None:
                    kwargs['handle_status__in'] = []
                    for hs in handle_status.split(','):
                        kwargs['handle_status__in'].append(int(hs))
                    ordering_arr.append('-handle_status')
                # exclude_kwargs['order_status__in'] = [OrderStatus.UNPAID, OrderStatus.CANCELLED]
            record = params.get('record')
            if record:
                record_arr = record.split(',')
                record_list = ShopeeOrderRecordModel.objects.values('shopee_order').filter(batch_number__in=record_arr)
                order_id_list = []
                for r in record_list:
                    order_id_list.append(r.get('shopee_order'))
                kwargs['id__in'] = order_id_list
            model_sku = params.get('model_sku')
            if model_sku:
                if not kwargs.get('id__in'):
                    kwargs['id__in'] = []
                for r in ShopeeOrderDetailModel.objects.values('shopee_order').filter(
                        stock__goods__goods_code__contains=model_sku).distinct():
                    kwargs.get('id__in').append(r.get('shopee_order'))
                for r in ShopeeOrderModifyModel.objects.values('shopee_order').filter(
                        stock__goods__goods_code__contains=model_sku).distinct():
                    kwargs.get('id__in').append(r.get('shopee_order'))

            ordering_arr.append(ordering)
            return ShopeeOrderModel.objects.exclude(**exclude_kwargs).filter(**kwargs).order_by(*ordering_arr)
        except Exception as e:
            logger.error('Get Order List Error: %s\n%e', e, traceback.format_exc())
            raise e

    def toggle_package(self, request):
        try:
            params = spg.parse_params(request)
            order_package_type = params.get('order_package_type')
            uid = params.get('uid')
            openid = request.META.get('HTTP_TOKEN')
            self.order_service.toggle_package(openid, uid, order_package_type)
            return HttpResponse('order toggle package success', status=200)
        except Exception as e:
            logger.error("order toggle package error: %s\n%s", e, traceback.format_exc())
            return HttpResponse('order toggle package error', content_type='text/html', status=500)

    def cancel_package(self, request):
        try:
            params = spg.parse_params(request)
            order_package_type = params.get('order_package_type')
            uid = params.get('uid')
            openid = request.META.get('HTTP_TOKEN')
            self.order_service.cancel_package(openid, uid, order_package_type)
            return HttpResponse('order cancel package success', status=200)
        except Exception as e:
            logger.error("order cancel package error: %s\n%s", e, traceback.format_exc())
            return HttpResponse('order cancel package error', content_type='text/html', status=500)

    def remark(self, request):
        try:
            params = spg.parse_params(request)
            order_id = params.get('order_id')
            note = params.get('note')
            openid = request.META.get('HTTP_TOKEN')
            self.order_service.order_remark(openid, order_id, note)
            return HttpResponse('order remark success', status=200)
        except Exception as e:
            logger.error("order remark error: %s\n%s", e, traceback.format_exc())
            return HttpResponse('order remark error', content_type='text/html', status=500)

    def model_stock_matching(self, request):
        try:
            params = spg.parse_params(request)
            is_modify = params.get('is_modify')
            pk = params.get('id')
            openid = request.META.get('HTTP_TOKEN')
            self.order_service.model_stock_matching(openid, is_modify, pk)
            return HttpResponse('stock matching success', status=200)
        except Exception as e:
            logger.error("stock matching error: %s\n%s", e, traceback.format_exc())
            return HttpResponse('stock matching error', content_type='text/html', status=500)

    def freed_model_stock(self, request):
        try:
            params = spg.parse_params(request)
            is_modify = params.get('is_modify')
            pk = params.get('id')
            openid = request.META.get('HTTP_TOKEN')
            self.order_service.freed_model_stock(openid, is_modify, pk)
            return HttpResponse('freed stock success', status=200)
        except Exception as e:
            logger.error("freed stock error: %s\n%s", e, traceback.format_exc())
            return HttpResponse('freed stock error', content_type='text/html', status=500)

    def stock_matching(self, request):
        try:
            params = spg.parse_params(request)
            openid = request.META.get('HTTP_TOKEN')
            order_id = params.get('order_id')
            if order_id:
                self.order_service.stock_matching_by_order(openid, order_id)
            else:
                self.order_service.stock_matching(openid)
            return HttpResponse('stock matching success', status=200)
        except Exception as e:
            logger.error("stock matching error: %s\n%s", e, traceback.format_exc())
            return HttpResponse('stock matching error', content_type='text/html', status=500)

    def change_goods(self, request):
        try:
            params = spg.parse_params(request)
            logger.info('params: %s', params)
            detail_id = params.get('detail_id')
            goods_id = params.get('goods_id')
            goods_code = params.get('goods_code')
            openid = request.META.get('HTTP_TOKEN')
            self.order_service.change_goods(openid, detail_id, goods_id, goods_code)
            return HttpResponse('change goods success', status=200)
        except Exception as e:
            logger.error("change goods error: %s\n%s", e, traceback.format_exc())
            return HttpResponse('change goods error', content_type='text/html', status=500)

    def freed_stock(self, request):
        try:
            openid = request.META.get('HTTP_TOKEN')
            params = spg.parse_params(request)
            order_id_list = params.get('order_id_list')
            self.order_service.freed_stock(openid, order_id_list, last=True)
            return HttpResponse('freed stock success', status=200)
        except Exception as e:
            logger.error("freed stock error: %s\n%s", e, traceback.format_exc())
            return HttpResponse('freed stock error', content_type='text/html', status=500)

    def partially_shipment(self, request):
        try:
            openid = request.META.get('HTTP_TOKEN')
            params = spg.parse_params(request)
            order_id_list = params.get('order_id_list')
            self.order_service.partially_shipment(openid, order_id_list)
            return HttpResponse('partially shipment success', status=200)
        except Exception as e:
            logger.error("partially shipment error: %s\n%s", e, traceback.format_exc())
            return HttpResponse('partially shipment error', content_type='text/html', status=500)

    def forced_shipment(self, request):
        try:
            openid = request.META.get('HTTP_TOKEN')
            params = spg.parse_params(request)
            order_id_list = params.get('order_id_list')
            self.order_service.forced_shipment(openid, order_id_list)
            return HttpResponse('forced shipment success', status=200)
        except Exception as e:
            logger.error("forced shipment error: %s\n%s", e, traceback.format_exc())
            return HttpResponse('forced shipment error', content_type='text/html', status=500)

    def shipment(self, request):
        try:
            openid = request.META.get('HTTP_TOKEN')
            params = spg.parse_params(request)
            order_id_list = params.get('order_id_list')
            self.order_service.shipment(openid, order_id_list)
            return HttpResponse('shipment success', status=200)
        except Exception as e:
            logger.error("shipment error: %s\n%s", e, traceback.format_exc())
            return HttpResponse('shipment error', content_type='text/html', status=500)

    def sync_shipment_list(self, request):
        try:
            params = spg.parse_params(request)
            shop_id = params.get('shop_id')
            if shop_id:
                self.order_service.sync_shipment_list(shop_id)
            else:
                openid = request.META.get('HTTP_TOKEN')
                stores = StoreModel.objects.filter(openid=openid, type=StoreType.SHOP)
                for store in stores:
                    self.order_service.sync_shipment_list(store.uid)
            return HttpResponse('sync shipment order list success', status=200)
        except Exception as e:
            logger.error("sync shipment order list error: %s\n%s", e, traceback.format_exc())
            return HttpResponse('sync shipment order list error', content_type='text/html', status=500)

    def delete_order_modify(self, request):
        try:
            params = spg.parse_params(request)
            openid = request.META.get('HTTP_TOKEN')
            modify_id = params.get('modifyId')
            self.order_service.delete_order_modify(openid, modify_id)
            return HttpResponse('Delete order modify success', status=200)
        except Exception as e:
            logger.error("Delete modify error: %s\n%s", e, traceback.format_exc())
            return HttpResponse(e, content_type='text/html', status=500)

    def order_modify(self, request):
        try:
            params = spg.parse_params(request)
            self.order_service.order_modify(params)
            return HttpResponse('Order modify success', status=200)
        except Exception as e:
            logger.error("order_modify error: %s\n%s", e, traceback.format_exc())
            return HttpResponse(e, content_type='text/html', status=500)

    def apply_logistics(self, request):
        try:
            params = spg.parse_params(request)
            order_sn_list = params.get('order_sn_list')
            shop_id = params.get('shop_id')
            store_id = params.get('store_id')
            openid = request.META.get('HTTP_TOKEN')
            if shop_id:
                self.order_service.apply_logistics(shop_id, order_sn_list)
            elif store_id:
                shop_id = StoreModel.objects.get(openid=openid, pk=store_id, type=StoreType.SHOP).uid
                self.order_service.apply_logistics(shop_id, order_sn_list)
            else:
                self.order_service.multi_shop_apply_logistics(openid, order_sn_list)
            return HttpResponse('Apply logistics success', content_type='text/html')
        except Exception as e:
            logger.error("print_logistics error: %s\n%s", e, traceback.format_exc())
            return HttpResponse(e, content_type='text/html', status=500)

    def get_order_details(self, request):
        try:
            params = spg.parse_params(request)
            order_id = params.get('order_id')
            if len(order_id) == 0 and order_id is None:
                raise ValueError('Missing param: order_id')
            return HttpResponse(
                spg.to_json_str(self.order_service.get_order_details(order_id)),
                content_type='application/json'
            )
        except Exception as e:
            logger.error('Get Order Details Error: %s', traceback.format_exc())
            return HttpResponse(e, content_type='text/html', status=500)

    def sync(self, request):
        try:
            params = spg.parse_params(request)
            shop_id = params.get('shop_id')
            openid = request.META.get('HTTP_TOKEN')
            order_sn = params.get('order_sn')
            time_from = params.get('time_from')
            time_to = params.get('time_to')
            if order_sn is not None:
                if shop_id:
                    self.order_service.sync_order_by_order_sn(shop_id, order_sn)
                else:
                    self.order_service.sync_order_by_order_sn_and_openid(openid, order_sn)
            else:
                # 异步同步订单
                threading.Thread(
                    target=self.order_service.sync_batch_order,
                    args=(shop_id, time_from, time_to)
                ).start()
        except Exception as e:
            logger.error('Sync Order Error: %s', traceback.format_exc())
            return HttpResponse(e, content_type='text/html', status=500)
        return HttpResponse('Syncing order success', status=200)

    def get_reserve_order(self, request):
        params = spg.parse_params(request)
        openid = request.META.get('HTTP_TOKEN')
        self.order_service.get_reserve_order(openid)


# @xframe_options_sameorigin
def get_order_logistics_file(request):
    try:
        logger.info('get_order_logistics_file...')
        # params = spg.parse_params(request)
        params = request.GET.dict()
        order_sn_list = params.get('order_sn_list')
        openid = params.get('openid')
        pdf_path = OrderService.get_instance().get_order_logistics_file(openid, order_sn_list)
        with open(pdf_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type="application/pdf", charset="utf-8")
            response['Content-Dispositon'] = 'attachment;filename=order-logistics-file.pdf'
            # response["X-Frame-Options"] = 'ALLOWALL'
            return response
    except Exception as e:
        logger.error("print_logistics error: %s", traceback.format_exc())
        return HttpResponse(e, content_type='text/html', status=500)
