import base64
import io

from django.core.files.images import ImageFile
from django.db import transaction
from rest_framework import viewsets


from productmedia.models import ProductMedia, Media, ProductOptionMedia
from productmedia.serializers import ProductMediaPostSerializer


from .models import GlobalProduct, ProductSupplier, ProductSpecification, ProductOption, \
    ProductLogistic, ProductModelStock, GlobalProductGoodsRelation
from . import serializers
from .page import GlobalProductLimitPagination
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .filter import GlobalProductFilter
from rest_framework.exceptions import APIException
from .serializers import ProductSupplierSerializers, ProductLogisticPostSerializers, \
    ProductOptionPostSerializers, ProductSpecificationPostSerializers, GlobalProductSerializers, \
    ProductModelStockPostSerializer, GlobalProductGetSerializers
from rest_framework.response import Response
from base.bustools import GLOBAL_BUS as bus, FETCH_PRODUCT_RECEIVE_EVENT
from django.db.models import Q

import logging

from .services.product_service import GlobalProductService

logger = logging.getLogger()


class GlobalProductView(viewsets.ModelViewSet):
    pagination_class = GlobalProductLimitPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter, ]
    ordering_fields = ['id', "create_time", "update_time", ]
    filter_class = GlobalProductFilter

    def get_project(self):
        try:
            id = self.kwargs.get('pk')
            return id
        except:
            return None

    def get_queryset(self):
        id = self.get_project()
        search_params = self.request.query_params.getlist('search', None)
        openid = self.request.META.get('HTTP_TOKEN')
        if not openid:
            raise APIException('Please offer your openid')
            # return GlobalProduct.objects.filter().none()
        queryset = GlobalProduct.objects.all().filter(openid=openid, type=GlobalProduct.TYPE_MAIN, is_delete=False)
        if id is None:
            queryset = queryset.filter(openid=openid, is_delete=False)
        else:
            queryset = queryset.filter(openid=openid, id=id, is_delete=False)
        if search_params:
            search_term = search_params[0]  # 暂时只支持一个搜素条件
            print('search params', search_term, ', before search apply', queryset.count())
            queryset = queryset.filter(
                Q(sku__contains=search_term) | Q(name__contains=search_term)).distinct()
        print('query product set count ', queryset.count())
        return queryset

    def unbind_goods(self, request, *args, **kwargs):
        openid = request.META.get('HTTP_TOKEN')
        if not openid:
            raise APIException('Please offer your open id')
        data = self.request.data
        product_id = data.get('product', None)
        if product_id is None:
            raise APIException('Fail to unbind product of product, null arguments')
        goods_relation = GlobalProductGoodsRelation.objects.filter(product_id=product_id, openid=openid).first()
        if not goods_relation:
            raise APIException('Fail to unbind product of product, relation not found')
        goods_relation.delete()
        return Response('success', status=200)

    def bind_goods(self, request, *args, **kwargs):
        data = self.request.data
        logger.info('bind product ', data)
        product_id = data.get('product', None)
        goods_id = data.get('goods_id', None)
        openid = request.META.get('HTTP_TOKEN')
        if product_id is None or goods_id is None:
            raise APIException('Fail to bind product to product, null arguments')
        goods_relation = GlobalProductGoodsRelation.objects.filter(product_id=product_id).first()
        product = GlobalProduct.objects.get(id=product_id)
        if not goods_relation:
            goods_relation = GlobalProductGoodsRelation(
                product=product,
                goods_id=goods_id,
                creater=self.request.META.get('HTTP_OPERATOR'),
                openid=openid,
                confirm=True
            )
            goods_relation.save()
        elif goods_relation.goods_id != goods_id:
            goods_relation.goods_id = goods_id
            goods_relation.confirm = True
            goods_relation.save()
        else:
            logger.warning('no need to rebind ')
        return Response('success', status=200)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return serializers.GlobalProductGetSerializers
        if self.action in ['create', 'update', 'partial_update']:
            return serializers.GlobalProductSerializers
        else:
            return self.http_method_not_allowed(request=self.request)

    def create(self, request, *args, **kwargs):
        data = self.request.data
        logger.info("create global products ", data)
        data['openid'] = request.META.get('HTTP_TOKEN')
        sku = data.get('sku', None)
        if not sku:
            raise APIException('Must specify product sku to create / update product')
        serializer = self.get_serializer(data=data)
        if not serializer.is_valid():
            logger.info('Create product invalid data')
            raise APIException('Can not create product, data is invalid')
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        self._create_or_update_product_detail(instance, data)
        return Response(serializer.data, status=200, headers=self.get_success_headers(serializer.data))

    def update(self, request, *args, **kwargs):
        qs = self.get_object()
        openid = request.META.get('HTTP_TOKEN')
        if qs.openid != openid:
            raise APIException(
                {"detail": "Cannot update asn order which not yours"})
        data = self.request.data
        serializer = self.get_serializer(qs, data=data, partial=data.get('partial', False))
        self._create_or_update_product_detail(qs, data)
        if not serializer.is_valid():
            print(serializer.errors)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=200, headers=self.get_success_headers(serializer.data))

    def clone_product(self, request, *args, **kwargs):
        product_id_to_clone = self.request.data
        logger.info('clone products %s', product_id_to_clone)
        open_id = request.META.get('HTTP_TOKEN')
        clone_products = []
        for product_id in product_id_to_clone:
            product = GlobalProduct.objects.filter(id=product_id, openid=open_id).first()
            if not product:
                raise APIException('Fail to clone product, Product of id %s not found')
            product_clone = GlobalProductService.get_instance().clone_product(product)
            clone_products.append(GlobalProductGetSerializers(product_clone, context={'request': self.request}).data)
        return Response(clone_products, status=200)

    @transaction.atomic
    def _create_or_update_product_detail(self, product, data):
        supplier_info = data.get('supplier', None)
        if supplier_info:
            self._create_or_update_supplier(product, supplier_info)
        images_infos = data.get('images', None)
        if images_infos:
            self._create_or_update_images(product, images_infos)
        spec_info = data.get('specifications', None)
        if spec_info:
            self._create_or_update_spec(product, spec_info)
        models_info = data.get('models_info', None)
        if models_info:
            self._create_or_update_models(product, models_info)
        logistic_info = data.get('logistic', None)
        if logistic_info:
            self._create_or_update_logistic(product, logistic_info)

    def _create_or_update_images(self, product, images_infos):
        for image_info in images_infos:
            image_info['creater'] = product.creater
            image_info['openid'] = product.openid
            image_info['product'] = product.id
            image_id = image_info.get('id', None)
            image_instance = None
            if image_id:
                image_instance = ProductMedia.objects.get(id=image_id)
            if image_info.get('is_delete', False):
                image_instance.delete()
                continue
            if not image_info.get('media', None):
                media = self._create_product_media(product, image_info)
                image_info['media'] = media.id

            if image_instance:
                serializer = ProductMediaPostSerializer(image_instance, data=image_info, partial=image_info.get('partial', True))
            else:
                serializer = ProductMediaPostSerializer(data=image_info)
            if not serializer.is_valid():
                raise APIException('Product image info is invalid %s', serializer.errors)
            image_instance = serializer.save()
            image_info['id'] = image_instance.id
        return images_infos

    def _create_or_update_models(self, product, models_info):
        print('create or update model ', models_info)
        for data in models_info:
            data['creater'] = product.creater
            data['openid'] = product.openid
            data['type'] = GlobalProduct.TYPE_MODEL
            data['status'] = product.status
            model_id = data.get('id', None)
            model_instance = None
            if model_id:
                model_instance = GlobalProduct.objects.get(id=model_id)
            if data.get('is_delete', False):
                if not model_instance:
                    raise APIException('Can not delete model, instanct not found')
                if product.models.filter(id=model_instance.id).count() > 0:
                    product.models.remove(model_instance)
                    product.save()
                if getattr(model_instance, GlobalProduct.RelativeFields.PARIENT_PRODUCTS).count() == 0:  # 编辑状态的变体也删除掉
                    product_media = getattr(model_instance, GlobalProduct.RelativeFields.PRODUCT_MEDIA).all()
                    for media in product_media:
                        media.delete()
                    model_instance.delete()
                continue

            options = data.get('options', [])
            if model_id:
                serializer = GlobalProductSerializers(model_instance, data=data, partial=data.get('partial', False))
                if not serializer.is_valid():
                    raise APIException('Can not create / update model %s' % serializer.errors)
                serializer.save()
                options = data.get('options', [])
            else:
                # 创建变体前先检查并创建规格和选项
                if product.mode == GlobalProduct.MODE_MULTIPLE and len(options) <= 0:
                    raise APIException('Can not create model without option on multiple model product')
                serializer = GlobalProductSerializers(data=data)
                if not serializer.is_valid():
                    logger.info('Can not create / update model ', serializer.errors)
                    raise APIException('Can not create / update model ', serializer.errors)
                model_instance = serializer.save()
                product.models.add(model_instance)
                product.save()

            # 关联变体和规格选项
            for option in options:
                option_instance = self._get_product_option(product, option)
                if not option_instance:
                    logger.warning('missing option instance for model %s , ', data)
                    continue
                if not option_instance.models.filter(id=model_instance.id).exists():
                    option_instance.models.add(model_instance)
                    option_instance.save()

            stock_info = data.get('stock', None)
            if stock_info:
                stock_id = stock_info.get('id', None)
                if stock_id:
                    stock_instance = ProductModelStock.objects.get(id=stock_id)
                    serializer = ProductModelStockPostSerializer(stock_instance, data=stock_info, partial=True)
                else:
                    stock_info['model'] = model_instance.id
                    stock_info['creater'] = model_instance.creater
                    stock_info['openid'] = model_instance.openid
                    serializer = ProductModelStockPostSerializer( data=stock_info)
                if not serializer.is_valid():
                    logger.error('Can not save model stock %s ' % serializer.errors)
                    raise APIException('Save model stock fail')
                serializer.save()
            price_info = data.get('price_info', None)
            # if price_info:
            #     ProductPriceService.get_instance().create_or_udpate_price(model_instance, price_info)

    def _get_product_option(self, product, model_option):
        option_id = model_option.get('id', None)
        if option_id:
            option = ProductOption.objects.filter(id=option_id).first()
            if option:
                return option
        option_name = model_option.get('name', None)
        if not option_name:
            raise APIException('Illegal option data, missing option name')
        spec_of_option = model_option.get('specification', None)
        if not spec_of_option:
            raise APIException('Can not find spec, missing specification')
        spec_name = spec_of_option.get('name', None)
        spec_instance_of_option = getattr(product, GlobalProduct.RelativeFields.PRODUCT_SPECIFICATION)\
            .filter(name=spec_name).first()
        if not spec_instance_of_option:
            raise APIException("Can not found Specficiation for model")
        option = getattr(spec_instance_of_option, ProductSpecification.RelativeFields.SPECIFICATION_OPTION).all()\
            .filter(name=option_name).first()
        return option

    def _create_or_update_spec(self, product, spec_info):
        print('create or update spec ', spec_info)
        for data in spec_info:
            if data.get('is_delete', False):
                self._delete_spec(data)
                continue
            id = data.get('id', None)
            if id:
                spec = ProductSpecification.objects.get(id=id)
                serializer = ProductSpecificationPostSerializers(spec, data=data, partial=True)
            else:
                data['creater'] = product.creater
                data['openid'] = product.openid
                data['product'] = product.id
                serializer = ProductSpecificationPostSerializers(data=data)
            if not serializer.is_valid():
                logger.info('Fail to create / update product spec, data is invalid %s', serializer.errors)
                raise APIException(serializer.errors)
            spec_instance = serializer.save()
            options = data.get('options', [])
            for option in options:
                self._create_or_update_option(product, spec_instance, option)
        return spec_info

    def _create_product_media(self, product, image_info):
        file_string = image_info.get('file', None)
        if not file_string:
            raise APIException("Can not create product meida ,file bytes string is None")
        file_name = image_info.get('filename')
        file_bytes = base64.b64decode(file_string)
        if not file_string:
            raise APIException("Must provide media file while media id is None")
        media = Media(
            file=ImageFile(io.BytesIO(file_bytes), name=file_name),
            openid=product.openid,
            creater=product.creater
        )
        media.save()
        return media

    def _delete_spec(self, data):
        id = data.get('id', None)
        if not id:
            raise APIException('Cant not delete specification , missing id')
        spec = ProductSpecification.objects.get(id=id)
        for option in getattr(spec, ProductSpecification.RelativeFields.SPECIFICATION_OPTION).all():
            option.models.clear()
            option.delete()
        return spec.delete()

    def _create_or_update_option(self, product, spec, data):
        # print('get or update option ', data)
        id = data.get('id', None)
        if id:
            option = ProductOption.objects.filter(id=id).first()
            if not option:
                logger.error('fail to update option, id not found %s', id)
                return
            if data.get('is_delete', False):
                for model in option.models.all():
                    if product.models.filter(id=model.id).count() > 0:
                        product.models.remove(model)
                product.save()
                option.models.clear()
                option_medias = getattr(option, ProductOption.RelativeFields.OPTION_MEDIA).all()
                for option_media in option_medias:
                    option_media_publish = getattr(option_media, ProductOptionMedia.RelativeFields.MEDIA_PUBLISH)
                    for media_publish in option_media_publish.all():
                        media_publish.delete() #TODO
                    option_media.delete()
                return option.delete()
            serializer = ProductOptionPostSerializers(option, data=data, partial=True)
            if not serializer.is_valid():
                logger.info('Fail to create / update product spec, data is invalid %s', serializer.errors)
                raise APIException(serializer.errors)
            option = serializer.save()
        else:
            data['creater'] = spec.creater
            data['openid'] = spec.openid
            data['specification'] = spec.id
            serializer = ProductOptionPostSerializers(data=data)
            if not serializer.is_valid():
                logger.info('Fail to create / update product spec, data is invalid %s', serializer.errors)
                raise APIException(serializer.errors)
            option = serializer.save()
        media_info = data.get('option_media', None)
        if media_info and spec.order == 0:
            option_media = getattr(option, ProductOption.RelativeFields.OPTION_MEDIA).first()
            media_storage_id = media_info.get('media', None)
            if media_storage_id:
                media_storage = Media.objects.get(id=media_storage_id)
            else:
                file = media_info.get('file', None)
                if not file:
                    raise Exception('Must provide media id or file for option_meida')
                # 创建规格图片
                media_storage = self._create_product_media(product, media_info)
            if not option_media:
                option_media = ProductOptionMedia(
                    media=media_storage,
                    option=option,
                    url=option.image,
                    openid=option.openid,
                    creater=option.creater,
                )
            else:
                option_media.media = media_storage
            option_media.save()
        return option

    def _create_or_update_supplier(self, product, data):
        print('get or update supplier ', data)
        id = data.get('id', None)
        if id:
            supplier_instance = ProductSupplier.objects.get(id=id)
        else:
            supplier_instance = getattr(product, GlobalProduct.RelativeFields.PRODUCT_SUPPLIER).first()
        if supplier_instance:
            serializer = ProductSupplierSerializers(supplier_instance, data=data, partial=True)
            if not serializer.is_valid():
                print('Can not create product supplier ', serializer.errors)
        else:
            data['product'] = product.id
            data['creater'] = product.creater
            data['openid'] = product.openid
            serializer = ProductSupplierSerializers(data=data)
            if not serializer.is_valid():
                print('Can not create product supplier ', serializer.errors)
            serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data

    def _create_or_update_logistic(self, product, data):
        print('get or update supplier ', data)
        id = data.get('id', None)
        if id:
            logistic_instance = ProductLogistic.objects.get(id=id)
            if data.get('is_delete', False):
                return logistic_instance.delete()
            serializer = ProductLogisticPostSerializers(logistic_instance, data=data, partial=data.get('partial', True))
        else:
            data['product'] = product.id
            data['creater'] = product.creater
            data['openid'] = product.openid
            serializer = ProductLogisticPostSerializers(data=data)
        if not serializer.is_valid():
            logger.error('Invalid logistic data %s', serializer.errors)
            raise APIException('Can not create product logistic, data is invalid')
        serializer.save()
        return serializer.data

    def destroy(self, request, pk):
        qs = self.get_object()
        logger.info('delete purchase id ', qs.id)
        if qs.openid != request.META.get('HTTP_TOKEN'):
            raise APIException(
                {"detail": "Cannot delete data which not yours"})
        else:
            qs.is_delete = True
            qs.save()
            serializer = serializers.GlobalProductSerializers(qs)
            return Response({"status": 200, "data": serializer.data}, status=200, headers=self.get_success_headers(""))

    def delete_batch(self, request):
        data = self.request.data
        logger.info('delete product batch %s' % data)
        openid = request.META.get('HTTP_TOKEN')
        for product_id in data:
            target_product = GlobalProduct.objects.filter(openid=openid, id=product_id).first()
            if target_product:
                target_product.is_delete = True
                target_product.save()
        return Response('success', status=200, headers=self.get_success_headers(""))

    @bus.on(FETCH_PRODUCT_RECEIVE_EVENT)
    def on_product_received(product_info, openid, creater):
        logger.info('on fetch product receive ', product_info)
        GlobalProductService.get_instance().create_product(product_info, openid, creater)
