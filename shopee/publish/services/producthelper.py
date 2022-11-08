
from publish.gRpc.client.types.global_product import GlobalProduct

from store.models import StoreProductModel, StoreProductOptionModel

from category.models import ShopeeAttributeValue

from .shopeehelper import ShopeeHelper

import logging

from ..models import ProductCategory

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
        publish_model_list = []
        for variant in product.product_variant.all():
            original_price = variant.variant_price.first().original_price
            stock = variant.variant_stock.first().current_stock
            tier_index = variant.option_item_index
            global_model = {
                'original_price': original_price,
                'normal_stock': min(stock, 1000),
                'global_model_sku': variant.model_sku,
                'tier_index': variant.option_item_index
            }
            publish_model_list.append(variant)
            global_models.append(global_model)
        return tier_variation, global_models, publish_model_list

    @classmethod
    def wrap_main_product_info(cls, product: StoreProductModel, merchant_id):
        if not product:
            raise Exception('Must provide product to publish')
        publish_info = {}

        # category
        category = getattr(product, StoreProductModel.RelativeFields.PRODUCT_CATEGORY).filter(
            merchant_id=merchant_id).first()
        publish_info['category_id'] = category.category_id

        # base info
        publish_info['global_item_name'] = product.product_name
        desc = product.description.replace('</div>', '\n').replace('<div>', ' ').replace('<br>', '\n').replace('</br>', '\n')
        publish_info['description'] = desc
        publish_info['global_item_sku'] = product.product_sku

        # images
        image_id_list = ShopeeHelper.get_product_image_ids(product)
        publish_info['image'] = {'image_id_list': image_id_list}

        # model (option) stock and price info
        model_stocks = getattr(product, StoreProductModel.RelativeFields.MODEL_STOCKS).all()
        min_stock = min([stock.stock_qty for stock in model_stocks])
        max_price = max([stock.price for stock in model_stocks])
        publish_info['original_price'] = max_price
        publish_info['normal_stock'] = min_stock

        logistic_info = getattr(product, StoreProductModel.RelativeFields.PRODUCT_LOGISTIC).first()
        publish_info['weight'] = logistic_info.weight
        if logistic_info.product_d and logistic_info.product_w and logistic_info.product_h and (
                logistic_info.product_d * logistic_info.product_w * logistic_info.product_h) > 0:
            publish_info['dimension'] = {
                'package_length': logistic_info.product_d,
                'package_width': logistic_info.product_w,
                'package_height': logistic_info.product_h
            }

        brand = category.brand
        if not brand:
            publish_info['brand'] = {'brand_id': 0}
        else:
            publish_info['brand'] = {'brand_id': brand.brand_id}
        publish_info['pre_order'] = {'days_to_ship': logistic_info.days_deliver}
        publish_info['condition'] = 'NEW'

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
    def wrap_product_price_info(cls, product: StoreProductModel, shopee_global_models, store):
        price_info = {"global_item_id": int(product.product_id), "shop_id": int(store['uid']),
                      "shop_region": store['area']}
        model_price_list = []
        for variant in product.product_variant.all():
            model_id = variant.model_id
            edit_price = variant.edit_price.first()
            found = False
            for global_model in shopee_global_models:
                if not edit_price:
                    raise Exception('Model edit product not found %s' % variant.model_sku)
                if str(global_model['global_model_id']) == str(model_id):
                    model_price_list.append({
                        "tier_index": global_model['tier_index'],
                        "original_price": edit_price.original_price
                    })
                found = True
            if not found:
                raise Exception('Can not found local variant for global model %s ' % variant.model_sku)
        price_info["item"] = {"model": model_price_list}
        return price_info

    @classmethod
    def wrap_product_discount_info(cls, product: StoreProductModel, shop_product: StoreProductModel):
        discount_model_list = []
        discount_id = None
        for model in product.product_variant.all():
            model_price = model.edit_price.first()
            if not model_price or model_price.discount_id <= 0 or model_price.current_price <= 0:
                logger.warning('discount of  model %s is illegal %s ', model.id, model_price)
                continue
            if model_price.published:
                logger.warning('discount of  model %s has publish %s ', model.id, model_price.id)
                continue
            if not model_price.publish_ready:
                logger.warning('discount of  model %s has not ready to publish %s ', model.id, model_price.id)
                continue
            discount_id = model_price.discount_id

            # match shop product variant and global product variant by option_item_index
            shop_product_model = shop_product.product_variant.filter(option_item_index=model.option_item_index)
            if not shop_product_model:
                logger.warning('shop product variant of model %s are not found %s ' % model.option_item_index)
                continue
            discount_model_list.append({
                'model_id': shop_product_model.model_id,
                'model_promotion_price': model_price.current_price
            })
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


