import base64

from django.db import transaction
from django.db.models import Q

from category.serializers import ProductAttributePostSerializer
from publish.gRpc.client.types.global_product import GlobalProduct

from store.models import StoreProductModel, StoreProductOptionModel, StoreProductMedia, StoreProductVariantModel, \
    StoreProductVariantStock, StoreProductPriceInfoModel, StoreProductOptionItemModel, StoreModel, ProductSupplierInfo

from category.models import ShopeeAttributeValue

from .shopeehelper import ShopeeHelper

import logging

from ..models import ProductCategory, ProductCategoryBrand, ProductCategoryAttribute

logger = logging.getLogger()


class ProductHelper:

    @classmethod
    def wrap_product_spec(cls, product: StoreProductModel, merchant_id):
        tier_variation = []
        product_specifications = getattr(product, StoreProductModel.RelativeFields.PRODUCT_OPTION).order_by(
            'index').all()
        for spec_index, specification in enumerate(product_specifications):
            option_list = []
            specification_options = getattr(specification,
                                            StoreProductOptionModel.RelativeFields.OPTION_ITEM).order_by(
                'index').all()
            for option in specification_options:
                option_dict = {
                    'option': option.name,
                }
                if spec_index == 0:
                    # 第一个规格的选项要带图片
                    option_image_id = option.image_id
                    if not option_image_id:
                        raise Exception('Option %s missing image id' % option.name)
                    option_dict['image'] = {'image_id': option_image_id}
                option_list.append(option_dict)
            tier_variation.append({
                'name': specification.name,
                'option_list': option_list
            })
        global_models = []
        for variant in product.product_variant.all():
            original_price = variant.variant_price.first().original_price
            stock = variant.variant_stock.first().current_stock
            global_model = {
                'original_price': original_price,
                'normal_stock': min(stock, 1000),
                'global_model_sku': variant.model_sku,
                'tier_index': [int(index) for index in variant.option_item_index.split(',')]
            }
            global_models.append(global_model)
        return tier_variation, global_models

    @classmethod
    def wrap_main_product_info(cls, product: StoreProductModel, merchant_id):
        if not product:
            raise Exception('Must provide product to publish')
        publish_info = {}
        # base info
        publish_info['global_item_name'] = product.product_name
        desc = product.description.replace('</div>', '\n').replace('<div>', ' ').replace('<br>', '\n').replace('</br>', '\n')
        publish_info['description'] = desc
        publish_info['global_item_sku'] = product.product_sku
        publish_info['weight'] = product.weight
        if product.length and product.width and product.height:
            publish_info['dimension'] = {
                'package_length': product.length,
                'package_width': product.width,
                'package_height': product.height
            }
        publish_info['pre_order'] = {'days_to_ship': product.days_to_ship}
        publish_info['condition'] = 'NEW'

        # images
        image_id_list = ShopeeHelper.get_product_image_ids(product)
        publish_info['image'] = {'image_id_list': image_id_list}

        # model (option) stock and price info
        variants_stock = [variant.variant_stock.first().current_stock if variant.variant_stock.first() else 0 for variant in product.product_variant.all()]
        min_stock = min([stock for stock in variants_stock])
        variants_price = [variant.variant_price.first().original_price if variant.variant_price.first() else 0 for variant in product.product_variant.all()]
        max_price = max([price for price in variants_price])
        if max_price <= 0:
            raise Exception('Max price must be positive')
        publish_info['original_price'] = max_price
        publish_info['normal_stock'] = min_stock

        # category
        category = getattr(product, StoreProductModel.RelativeFields.PRODUCT_CATEGORY).filter(
            merchant_id=merchant_id).first()
        publish_info['category_id'] = category.category_id
        brand = category.brand
        if not brand:
            publish_info['brand'] = {'brand_id': 0}
        else:
            publish_info['brand'] = {'brand_id': brand.brand_id}
        attributes = getattr(category, ProductCategory.RelativeFields.ATTRIBUTES).all()
        attribute_key_value = {}
        attribute_list = []
        for attribute in attributes:
            attribute_values = attribute_key_value.get(attribute.attribute_id, [])
            value_id = attribute.value_id if attribute.value_id > 0 else 0
            if value_id > 0:
                attribute_value = {
                    'value_id': value_id
                }
                value_instance = ShopeeAttributeValue.objects.filter(value_id=value_id, openid=attribute.openid).first()
                if value_instance.value_unit:
                    attribute_value['value_unit'] = value_instance.value_unit
            else:
                attribute_value = {
                    'original_value_name': attribute.display_value_name
                }
            attribute_values.append(attribute_value)
            attribute_key_value[attribute.attribute_id] = attribute_values
        for attribute_id, attribute_values in attribute_key_value.items():
            attribute_list.append({
                'attribute_id': int(attribute_id),
                'attribute_value_list': attribute_values
            })
        publish_info['attribute_list'] = attribute_list
        logger.info('publish main prouct %s' % publish_info)
        return publish_info

    @classmethod
    def wrap_product_price_info(cls, product: StoreProductModel, store):
        price_info = {"global_item_id": int(product.product_id), "shop_id": int(store.uid),
                      "shop_region": store.area}
        model_price_list = []
        shop_product = product.shop_products.filter(store=store).first()
        if not shop_product:
            raise Exception('Shop product of store %s not found ' % store.name)
        for variant in shop_product.product_variant.all():
            variant_price_info = variant.variant_price.first()
            model_price_list.append({
                "tier_index": [int(index) for index in variant.option_item_index.split(',')],
                "original_price": variant_price_info.original_price
            })
        price_info["item"] = {"model": model_price_list}
        return price_info

    @classmethod
    def wrap_product_discount_info(cls, shop_product: StoreProductModel):
        discount_model_list = []
        discount_id = None
        promotion_ids = [variant.promotion_id for variant in shop_product.product_variant.all() if variant.promotion_id]
        if len(promotion_ids) <= 0:
            raise Exception('Wrap product discount info missing promotion id')
        promotion_id = promotion_ids[0] # all variants' promotions id should be same
        for variant in shop_product.product_variant.all():
            price_info = variant.variant_price.first()
            if price_info.current_price > 0:
                discount_id = promotion_id
                discount_model_list.append({
                    'model_id': variant.model_id,
                    'model_promotion_price': price_info.current_price
                })
            else:
                logger.error('Current price must not 0 !!!')
        return discount_id, discount_model_list

    @classmethod
    def clone_product_logistic(cls, product_clone: StoreProductModel, origin: GlobalProduct):
        logistic = getattr(origin, StoreProductModel.RelativeFields.PRODUCT_LOGISTIC).first()
        if not logistic:
            return
        logistic_clone = logistic
        logistic_clone.pk = None
        logistic_clone.product = product_clone
        logistic_clone.save()

    @classmethod
    def clone_product_category(cls, prdoct_clone: StoreProductModel, origin: GlobalProduct):
        category = getattr(origin, StoreProductModel.RelativeFields.PRODUCT_CATEGORY).first()
        if not category:
            return
        category_id = category.id
        category_clone = category
        category_clone.pk = None
        category_clone.product = prdoct_clone
        category_clone.save()
        category = ProductCategory.objects.get(id=category_id)
        for attribute in getattr(category, ProductCategory.RelativeFields.ATTRIBUTES).all():
            attribute_clone = attribute
            attribute_clone.pk = None
            attribute_clone.category = category_clone
            attribute_clone.save()

    @classmethod
    def spec_info_to_str(cls, spec_infos):
        info_str = []
        for spec_info in spec_infos:
            options_str = []
            for option in spec_info.options:
                options_str.append({
                    'id': option.get('id', None),
                    'image': option.get('image', None),
                    'order': option.get('order', None),
                    'is_delete': option.get('is_delete', None)
                })
            spec_str = {
                'id': spec_info.id,
                'name': spec_info.id,
                'is_delete': spec_info.is_delete,
                'order': spec_info.order
            }

    @classmethod
    def create_or_update_images(cls, product, images_infos):
        for image_info in images_infos:
            image_info['creater'] = product.creater
            image_info['openid'] = product.openid
            image_info['product'] = product.id
            image_index = image_info.get('index', None)
            url = image_info.get('url', None)
            if image_index is not None and url:
                image_instance = StoreProductMedia.objects.filter(store_product=product, index=image_index, type=2).first()
                if image_instance:
                    image_instance.url = url
                    image_instance.save()
                else:
                    image_instance = StoreProductMedia.objects.create(
                        openid=product.openid,
                        creater=product.creater,
                        store_product=product,
                        type=2,
                        url=url,
                        index=image_index
                    )
        return images_infos

    @classmethod
    def create_or_update_models(cls, product, models_info):
        models = list(StoreProductVariantModel.objects.filter(store_product=product, is_delete=False).all())
        for data in models_info:
            options_index = data.get('options_index', None)
            if not options_index:
                raise Exception('Create/update model missing options index %s' % data.get('sku', None))
            model_match = [m for m in models if m.option_item_index == options_index]
            model_instance = model_match[0] if model_match else None
            if not model_instance:
                model_instance = StoreProductVariantModel.objects.create(
                    openid=product.openid,
                    creater=product.creater,
                    store_product=product,
                    model_sku=data.get('sku', None),
                    option_item_index=options_index
                )
            else:
                model_instance.model_sku = data.get('sku', model_instance.model_sku)
                model_instance.save()
            if not data.get('stock', None):
                continue
            stock = data.get('stock')
            if stock.get('stock_qty', None):
                stock_info = StoreProductVariantStock.objects.filter(variant=model_instance,
                                                                     is_delete=False).first()
                if not stock_info:
                    stock_info = StoreProductVariantStock.objects.create(
                        openid=product.openid,
                        creater=product.creater,
                        variant=model_instance,
                        current_stock=stock.get('stock_qty')
                    )
                else:
                    stock_info.current_stock = data.get('stock').get('stock_qty', stock_info.current_stock)
                    stock_info.save()
            if stock.get('price', None):
                price_info = StoreProductPriceInfoModel.objects.filter(variant=model_instance, is_delete=False).first()
                if not price_info:
                    price_info = StoreProductPriceInfoModel.objects.create(
                        openid=product.openid,
                        creater=product.creater,
                        variant=model_instance,
                        store_product=product,
                        original_price=stock.get('price')
                    )
                else:
                    price_info.original_price = stock.get('price')
                    price_info.save()

    @classmethod
    def create_or_update_spec(cls, product, spec_info):
        for data in spec_info:
            index = data.get('index', None)
            name = data.get('name', None)
            if index is None:
                logger.error('can not create spec, missing index %s', name)
                raise Exception('Create spec missing index %s ' % name)
            if not name:
                logger.error('can not create spec, missing name %s', index)
                raise Exception('Create spec missing name %s ' % index)
            spec = StoreProductOptionModel.objects.filter(index=index, store_product=product).first()
            if not spec:
                spec = StoreProductOptionModel.objects.create(
                    openid=product.openid,
                    creater=product.creater,
                    store_product=product,
                    name=name,
                    index=index
                )
            else:
                spec.name = name
                spec.save()
            options = data.get('options', [])
            for option in options:
                cls._create_or_update_option(product, spec, option)
        return spec_info

    @classmethod
    def _create_or_update_option(cls, product, spec, data):
        index = data.get('index', None)
        name = data.get('name', None)
        image_url = data.get('iamge', None)
        if index is None:
            logger.error('can not create option, missing index %s %s', spec.name, name)
            raise Exception('Create option missing indexndex %s %s' % (spec.name, name))
        if not name:
            logger.error('can not create option, missing name %s', spec.name, index)
            raise Exception('Create option missing name %s %s ' % (spec.name, index))
        option = StoreProductOptionItemModel.objects.filter(store_product=product, store_product_option=spec, index=index).first()
        if not option:
            option = StoreProductOptionItemModel.objects.create(
                openid=product.openid,
                creater=product.creater,
                store_product=product,
                store_product_option=spec,
                name=name,
                image_url=image_url,
                index=index
            )
        else:
            option.name = name
            option.image_url = image_url if image_url else option.image_url
            option.save()
        return option

    @classmethod
    def create_or_update_category(cls, product, category_info):
        print('create category ,', product.id, category_info.get('category_id', None))
        category_id = category_info.get('category_id', None)
        if not category_id:
            logger.warning('create or update category no category id')
            return
        category_instance = ProductCategory.objects.filter(product=product, is_delete=False).first()
        brand_info = category_info.get('brand', None)
        brand_instance = category_instance.brand if category_instance else None
        if not brand_instance:
            brand_id = brand_info.get('brand_id', 0) if brand_info else 0
            display_brand_name = brand_info.get('display_brand_name', 'NoBrand') if brand_info else 'NoBrand'
            brand_instance = ProductCategoryBrand.objects.create(
                openid=product.openid,
                creater=product.creater,
                brand_id=brand_id,
                display_brand_name=display_brand_name
            )
        if not category_instance:
            category_instance = ProductCategory.objects.create(
                openid=product.openid,
                creater=product.creater,
                merchant_id=product.store.uid,
                category_id=category_id,
                brand=brand_instance,
                product=product
            )
        else:
            category_instance.category_id = category_id
            category_instance.brand = brand_instance
            category_instance.save()

        ProductCategoryAttribute.objects.filter(Q(category_id=category_instance.id)).delete()
        attribute_values_info = category_info.get('attribute_values', None)
        if attribute_values_info:
            cls._create_category_attribute(category_instance, attribute_values_info)

    @classmethod
    def _create_category_attribute(cls, category, attribute_values_info):
        logger.info('_create_or_update_category_attribute %s', attribute_values_info)
        for attribute_value in attribute_values_info:
            if not attribute_value.get('attribute_id', None):
                raise Exception(
                    'Missing attribute id for attribute value %s' % attribute_value.get('display_value_name', None))
            if not attribute_value.get('value_id', None):
                raise Exception(
                    'Missing valid id for attribute value %s' % attribute_value.get('display_value_name', None))
            if not attribute_value.get('display_value_name', None):
                raise Exception(
                    'Missing valid id for attribute display name %s' % attribute_value.get('attribute_id', None))
            attribute_value['category'] = category.id
            attribute_value['openid'] = category.openid
            attribute_value['creater'] = category.creater
            serializer = ProductAttributePostSerializer(data=attribute_value)
            if not serializer.is_valid():
                logger.error('Fail to save category attribute %s', serializer.errors)
                raise Exception('Fail to save category attribute')
            serializer.save()

    @classmethod
    def create_or_update_supplier_info(cls, global_product: StoreProductModel, supplier_info:dict):
        product_logistics = global_product.supplier_info.first()
        if not product_logistics:
            product_logistics = ProductSupplierInfo.objects.create(
                openid=global_product.openid,
                creater=global_product.creater,
                product=global_product,
                url=supplier_info.get('url', None),
                logistics_costs=supplier_info.get('logistics_costs', 0),
                min_purchase_num=supplier_info.get('min_purchase_num', 1),
                supplier_name=supplier_info.get('supplier_name', None)
            )
        else:
            product_logistics.url = supplier_info.get('url', product_logistics.url)
            product_logistics.logistics_costs = supplier_info.get('logistics_costs', product_logistics.logistics_costs)
            product_logistics.min_purchase_num = supplier_info.get('min_purchase_num', product_logistics.min_purchase_num)
            product_logistics.supplier_name = supplier_info.get('supplier_name', product_logistics.supplier_name)
            product_logistics.save()
        return product_logistics

    @classmethod
    @transaction.atomic
    def global_product_to_shop_product(cls, global_product: StoreProductModel, store: StoreModel):
        product_id = global_product.id
        product_clone = global_product
        product_clone.pk = None
        product_clone.name = ''
        product_clone.product_id = None
        product_clone.store = store
        product_clone.save()
        origin_product = StoreProductModel.objects.get(id=product_id)
        origin_product.shop_products.add(product_clone)
        origin_product.save()
        for option in origin_product.product_option.all():
            cls._clone_product_option(option, product_clone)

        cls._clone_product_media_info(origin_product, product_clone)
        cls._clone_product_variant(origin_product, product_clone)

    @classmethod
    def _clone_product_option(cls, option: StoreProductModel, product: StoreProductModel):
        option_id = option.id
        option_clone = option
        option_clone.pk = None
        option_clone.store_product = product
        option_clone.save()
        origin_option = StoreProductOptionModel.objects.get(id=option_id)
        for option_item in origin_option.option_item.all():
            option_item_clone = option_item
            option_item_clone.pk = None
            option_item_clone.store_product = product
            option_item_clone.store_product_option = origin_option
        return option_clone

    @classmethod
    def _clone_product_variant(cls, from_product: StoreProductModel, to_product: StoreProductModel):
        for variant in from_product.product_variant.all():
            variant_id = variant.id
            variant_clone = variant
            variant_clone.model_id = None
            variant_clone.pk = None
            variant_clone.store_product = to_product
            variant_clone.save()
            origin_variant = StoreProductVariantModel.objects.get(id=variant_id)
            cls._clone_variant_price_info(origin_variant, to_product, variant_clone)
            cls._clone_variant_stock_info(origin_variant, variant_clone)

    @classmethod
    def _clone_product_media_info(cls, from_product: StoreProductModel, to_product: StoreProductModel):
        for product_media in from_product.product_media.all():
            product_media_clone = product_media
            product_media_clone.pk = None
            product_media_clone.store_product = to_product
            product_media_clone.save()

    @classmethod
    def _clone_variant_price_info(cls, from_variant: StoreProductVariantModel,
                                  to_product: StoreProductModel, to_variant: StoreProductVariantModel):
        for price_info in from_variant.variant_price.all():
            price_info_clone = price_info
            price_info_clone.pk = None
            price_info_clone.variant = to_variant
            price_info_clone.store_product = to_product

    @classmethod
    def _clone_variant_stock_info(cls, from_varaint: StoreProductVariantModel, to_variant: StoreProductVariantModel):
        for stock_info in from_varaint.variant_stock.all():
            stock_info_clone = stock_info
            stock_info_clone.pk = None
            stock_info_clone.variant = to_variant
            stock_info_clone.save()

    @classmethod
    def upload_product_image(cls, media: dict):
        media_id = media.get('id', None)
        file = media.get('file', None)
        if not (media_id and file):
            raise Exception('Missing media id')
        media_instance = StoreProductMedia.objects.get(id=media_id)
        if media_instance.image_id:
            logger.warning('product media %s already has media id' % media_id)
            return
        store = media_instance.store_product.store
        image_id = ShopeeHelper.publish_shopee_image(base64.b64decode(file), store)
        media_instance.image_id = image_id
        media_instance.save()

    @classmethod
    def upload_option_image(cls, option_item):
        option_item_id = option_item.get('id', None)
        option_item_file = option_item.get('file', None)
        if not (option_item_id and option_item_file):
            raise Exception('Missing option item id or file')
        option_item_instance = StoreProductOptionItemModel.objects.get(id=option_item_id)
        if option_item_instance.image_id:
            logger.warning('option item %s already has media id' % option_item_id)
            return
        store = option_item_instance.store_product.store
        image_id = ShopeeHelper.publish_shopee_image(base64.b64decode(option_item_file), store)
        option_item_instance.image_id = image_id
        option_item_instance.save()

