from product.models import GlobalProduct, ProductSpecification, ProductOption

import logging
logger = logging.getLogger()


class ProductHelper:

    @classmethod
    def get_shopee_global_publish_id(cls, global_product: GlobalProduct, merchant_id):
        global_publish = getattr(global_product, GlobalProduct.RelativeFields.SHOPEE_GLOBAL_PUBLISH) \
            .filter(merchant_id=merchant_id).first()
        if not global_publish:
            return None
        return global_publish.publish_id

    @classmethod
    def get_shopee_store_publish_id(cls, global_product: GlobalProduct, shop_uid):
        store_publish = getattr(global_product, GlobalProduct.RelativeFields.PUBLISH_PUBLISH) \
            .filter(shop_id=shop_uid).first()
        if not store_publish:
            return None
        return store_publish.publish_id

    @classmethod
    def wrap_product_discount_info(cls, product: GlobalProduct, store_uid):
        discount_model_list = []
        discount_id = None
        for model in product.models.all():
            model_price = getattr(model, GlobalProduct.RelativeFields.PRICE_INFO).filter(store_id=store_uid).first()
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
            model_store_publish = getattr(model, GlobalProduct.RelativeFields.PUBLISH_PUBLISH) \
                .filter(shop_id=store_uid).first()
            if not model_store_publish:
                logger.warning('store product publish info of model are not found %s ' % model.id)
                continue
            publish_id = model_store_publish.publish_id
            discount_model_list.append({
                'model_id': publish_id,
                'model_promotion_price': model_price.current_price
            })
        return discount_id, discount_model_list

    @classmethod
    def clone_product_model_and_spec(cls, product_clone:GlobalProduct, origin: GlobalProduct):
        model_map = {}
        for model in origin.models.all():
            model_id = model.id
            model_clone = model
            model_clone.pk = None
            model_clone.save()
            model = GlobalProduct.objects.get(id=model_id)

            model_stock = getattr(model, GlobalProduct.RelativeFields.MODEL_STOCKS).first()
            if model_stock:
                model_stock_clone = model_stock
                model_stock_clone.pk = None
                model_stock_clone.model = model_clone
                model_stock_clone.save()

            model_relation = getattr(model, GlobalProduct.RelativeFields.GOODS_RELATION).first()
            if model_relation:
                model_relation_clone = model_relation
                model_relation_clone.pk = None
                model_relation.product = model_clone
                model_relation_clone.save()

            product_clone.models.add(model_clone)
            model_map[model_id] = model_clone

        product_clone.save()

        for spec in getattr(origin, GlobalProduct.RelativeFields.PRODUCT_SPECIFICATION).all():
            spec_id = spec.id
            spec_clone = spec
            spec_clone.pk = None
            spec_clone.product = product_clone
            spec_clone.save()
            spec = ProductSpecification.objects.get(id=spec_id) # 还原
            for option in getattr(spec, ProductSpecification.RelativeFields.SPECIFICATION_OPTION).all():
                option_id = option.id
                option_clone = option
                option_clone.pk = None
                option_clone.specification = spec_clone
                option_clone.save()
                option = ProductOption.objects.get(id=option_id)
                for option_media in getattr(option, ProductOption.RelativeFields.OPTION_MEDIA).all():
                    option_media_clone = option_media
                    option_media_clone.pk = None
                    option_media_clone.option = option_clone
                    option_media_clone.media = None
                    option_media_clone.save()
                for model in option.models.all():
                    model_clone = model_map.get(model.id, None)
                    if model_clone:
                        option_clone.models.add(model_clone)
                option_clone.save()

    @classmethod
    def clone_product_supplier(cls, product_clone: GlobalProduct, origin: GlobalProduct):
        supplier = getattr(origin, GlobalProduct.RelativeFields.PRODUCT_SUPPLIER).first()
        if supplier:
            supplier_clone = supplier
            supplier_clone.pk = None
            supplier_clone.product = product_clone
            supplier_clone.save()

    @classmethod
    def clone_product_logistic(cls, product_clone: GlobalProduct, origin: GlobalProduct):
        logistic = getattr(origin, GlobalProduct.RelativeFields.PRODUCT_LOGISTIC).first()
        if not logistic:
            return
        logistic_clone = logistic
        logistic_clone.pk = None
        logistic_clone.product = product_clone
        logistic_clone.save()

    @classmethod
    def clone_product_media(cls, product_clone: GlobalProduct, origin: GlobalProduct):
        for media in getattr(origin, GlobalProduct.RelativeFields.PRODUCT_MEDIA).all():
            media_clone = media
            media_clone.pk = None
            media_clone.product = product_clone
            media_clone.media = None
            media_clone.save()

    @classmethod
    def clone_product_category(cls, prdoct_clone: GlobalProduct, origin: GlobalProduct):
        category = getattr(origin, GlobalProduct.RelativeFields.PRODUCT_CATEGORY).first()
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



