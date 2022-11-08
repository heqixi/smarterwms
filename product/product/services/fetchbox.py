import functools

from product.models import GlobalProduct, ProductSupplier, ProductSpecification, ProductOption, ProductModelStock
from productmedia.models import Constants, ProductMedia, ProductOptionMedia


class FetchBoxHelper:

    @classmethod
    def _create_product_media(cls, product, medias):
        def media_compare(media_1, media_2):
            return media_2.get('is_main', 0) - media_1.get('is_main', 0)
        sorted(medias, key=functools.cmp_to_key(media_compare))
        for index, media in enumerate(medias):
            product_media = ProductMedia(
                product=product,
                url=media.get('url', ''),
                media_type=Constants.MEDIA_TYPE_VIDEO if media.get('type', None) == 1 else Constants.MEDIA_TYPE_IMAGE,
                media_tag=Constants.MEDIA_TAG_MAIN_IMAGE if media.get('is_main') else Constants.MEDIA_TAG_DESC_IMAGE,
                index=index,
                openid=product.openid,
                creater=product.creater
            )
            if media.get('is_main') and media.get('type', None) == 2:
                product.image = media.get('url', '')
                product.save()
            product_media.save()

    @classmethod
    def _create_product_specification_from_fetchbox(cls, product, specfications, options):
        global_product_specs = getattr(product, GlobalProduct.RelativeFields.PRODUCT_SPECIFICATION).all()
        for spec in specfications:
            spec_index = spec.get('index', None)
            if spec_index is None:
                raise Exception('Missing spec index %s ' % spec)
            spec_instance = global_product_specs.filter(index=spec_index).first()
            if not spec_instance:
                spec_instance = ProductSpecification(
                    product=product,
                    name=spec.get('name', ''),
                    index=spec_index,
                    openid=product.openid,
                    creater=product.creater)
            else:
                spec_instance.name = spec.get('name', '')
            spec_instance.save()
            spec_options = getattr(spec_instance, ProductSpecification.RelativeFields.SPECIFICATION_OPTION)
            for option in options:
                if option.get('option', -1) == spec['id']:
                    option_instance = spec_options.filter(index=option.get('index')).first()
                    if not option_instance:
                        option_instance = ProductOption(
                            specification=spec_instance,
                            name=option.get('name'),
                            image=option.get('image'),
                            index=option.get('index'),
                            openid=product.openid,
                            creater=product.creater)
                    else:
                        option_instance.name = option.get('name')
                        option_instance.image = option.get('image')
                        option_instance.index = option.get('index')
                    option_instance.save()
                    option_media = getattr(option_instance, ProductOption.RelativeFields.OPTION_MEDIA).first()
                    if not option_media:
                        option_media = ProductOptionMedia(
                            media=None,
                            option=option_instance,
                            url=option_instance.image,
                            openid=option_instance.openid,
                            creater=option_instance.creater
                        )
                        option_media.save()

    @classmethod
    def _attach_model_to_option(cls, product, model_instance, option_indexes):
        full_option_name = []
        for spec_index, option_index in enumerate(option_indexes):
            spec_instance = getattr(product, GlobalProduct.RelativeFields.PRODUCT_SPECIFICATION) \
                .filter(index=spec_index).first()
            if not spec_instance:
                raise Exception('Fail to find spec %s %s' % (spec_index, option_index))
            option_instance = getattr(spec_instance,
                                      ProductSpecification.RelativeFields.SPECIFICATION_OPTION).filter(
                index=option_index).first()
            if not option_instance:
                raise Exception('Fail to find option %s %s' % (spec_index, option_index))
            if spec_index == 0:
                # 去第一个规格的图片作为变体的图片
                model_instance.image = option_instance.image
                model_instance.save()
            full_option_name.append(option_instance.name)
            if not option_instance.models.filter(id=model_instance.id).first():
                option_instance.models.add(model_instance)
            option_instance.save()
        if not model_instance.sku or not model_instance.name or len(model_instance.name) <= 0:
            model_instance.name = '-'.join(full_option_name)
            model_instance.sku = product.sku + '-' + '-'.join(full_option_name)
            model_instance.save()

    @classmethod
    def _create_product_models(cls, product: GlobalProduct, models_info):
        for model_info in models_info:
            model_instance = GlobalProduct(
                name=model_info.get('name'),
                sku=model_info.get('name'),
                status=GlobalProduct.EDIT,
                type=GlobalProduct.TYPE_MODEL,
                second_hand=False,
                openid=product.openid,
                creater=product.creater
            )
            model_instance.save()
            product.models.add(model_instance)
            product.save()
            model_stock = ProductModelStock(
                model=model_instance,
                stock_qty=model_info.get('stock_qty', 0),
                price=model_info.get('price', 0),
                creater=model_instance.creater,
                openid=model_instance.openid
            )
            model_stock.save()
            cls._attach_model_to_option(product, model_instance, model_info['item_index'].split(','))

    @classmethod
    def create_product(cls, product_info, openid, creater):
        product = GlobalProduct(
            name=product_info.get('name', ''),
            status=GlobalProduct.EDIT,
            desc=product_info.get('description', ''),
            second_hand=False,
            type=GlobalProduct.TYPE_MAIN,
            openid=openid,
            creater=creater
        )
        product.save()
        supplier = ProductSupplier(
            product=product,
            logistics_costs=product_info.get('logistics_costs', ''),
            min_purchase_num=product_info.get('mix_purchase_qty', 2),
            supplier_city=product_info.get('logistics_city', ''),
            supplier_name=product_info.get('company', ''),
            url=product_info.get('url', ''),
            openid=product.openid,
            creater=product.creater
        )
        supplier.save()
        cls._create_product_media(product, product_info.get('medias', []))
        cls._create_product_specification_from_fetchbox(product, product_info['options'], product_info['option_items'])
        cls._create_product_models(product, product_info['variants'])
        return product
