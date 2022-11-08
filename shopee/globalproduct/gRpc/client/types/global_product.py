from abc import ABC
from enum import Enum

from base.gRpc.types.base import ProtoType, ResponseResolver
from globalproduct.gRpc.client.protos import product_pb2
from base.gRpc.types.base import Verifiable, MessageEncoder, MessageDecoder


class ProductStatus(Enum):
    EDIT = 0
    PUBLISH_READY = 1
    PUBLISH = 2


def status_to_int(status: ProductStatus):
    if status == ProductStatus.EDIT:
        return 0
    elif status == ProductStatus.PUBLISH_READY:
        return 1
    elif status == ProductStatus.PUBLISH:
        return 2
    else:
        raise Exception('Unknow status %s'%status)


def int_to_status(status: int):
    if status == 0:
        return ProductStatus.EDIT
    elif status == 1:
        return ProductStatus.PUBLISH_READY
    elif status == 2:
        return ProductStatus.PUBLISH
    else:
        raise Exception('int_to_status unknow status %s ' %status)

class ProductOption(MessageDecoder, MessageEncoder, Verifiable):

    def __init__(self, id=None, spec_index=None, name=None, index=None, image=None):
        self.id = id
        self.spec_index = spec_index
        self.name = name
        self.index = index
        self.image = image

    def is_valid(self, raise_exception=False):
        if self.id is not None:
            is_valid = self.id >= 0
        else:
            image_valid = self.spec_index > 0 or self.not_empty(self.image)
            is_valid = self.not_empty(self.name) and self.not_negative(self.index, self.spec_index) and image_valid
        if not is_valid and raise_exception:
            raise Exception('Illegal product option')
        return is_valid

    def to_message(self):
        if self.is_valid(raise_exception=True):
            return product_pb2.ProductOption(
                id=self.id,
                spec_index=self.spec_index,
                name=self.name,
                index=self.index,
                image=self.image
            )

    @classmethod
    def from_dict(cls, options_dict: dict):
        option = ProductOption(
            name=options_dict.get('name', None),
            index=options_dict.get('index', None),
            image=options_dict.get('image_url', None),
            spec_index=options_dict.get('spec_index', None)
        )
        return option

    def from_message(self, *args):
        raise NotImplementedError('Not Implement')


class Specification(MessageDecoder, MessageEncoder, Verifiable):

    id: int
    product_id: int
    name: str
    index: int
    options: list

    def __init__(self, id=None, product_id=None, name=None, index=None, options=None):
        self.id = id
        self.product_id = product_id
        self.name = name
        self.index = index
        self.options = options

    def is_valid(self, raise_exception=False):
        is_valid = False
        if self.id is not None:
            is_valid = self.id >= 0
        if self.id is None:
            is_valid = self.not_empty(self.name) and self.not_negative(self.index) \
                       and all([opt.is_valid(raise_exception) for opt in self.options])
        if not is_valid and raise_exception:
            raise Exception('Illegal specification')
        return is_valid

    def to_message(self):
        return product_pb2.Specification(
            id=self.id,
            product_id=self.product_id,
            name=self.name,
            index=self.index,
            options=[opt.to_message() for opt in self.options]
        )

    def from_message(self, *args):
        raise NotImplementedError('Not Implement')

    @classmethod
    def from_dict(cls, product_spec: dict):
        options_list = product_spec.get('option_items', [])
        for opt in options_list:
            opt['spec_index'] = product_spec['index']
        options = [ProductOption.from_dict(option_dict) for option_dict in options_list]
        return Specification(
            name=product_spec.get('name', None),
            index=product_spec.get('index', None),
            options=options
        )


class Product(MessageDecoder, MessageEncoder, Verifiable):

    def __init__(self, id=None, sku=None, status=None, image=None, name=None, desc=None, second_hand=False, models=None):
        self.id = id
        self.sku = sku
        self.status = status
        self.image = image
        self.name = name
        self.desc = desc
        self.second_hand = second_hand
        self.models = models

    def is_valid(self, raise_exception=False):
        if self.id is not None:
            is_valid = self.id >= 0
        else:
            is_valid = self.not_empty(self.sku) and isinstance(self.status, ProductStatus)
        if not is_valid and raise_exception:
            raise Exception('Illegal product')
        return is_valid

    def to_message(self):
        return product_pb2.Product(
            id=self.id,
            sku=self.sku,
            status=status_to_int(self.status) if self.status else None,
            image=self.image,
            name=self.name,
            desc=self.desc,
            second_hand=self.second_hand,
            models=self.models
        )

    @classmethod
    def _status_from_shopee_product(cls, status:str):
        if status == 'NORMAL':
            return ProductStatus.PUBLISH

    @classmethod
    def from_shopee_product(cls, shopee_product:dict, global_product_id=None):
        product = Product()
        product.id = global_product_id
        product.sku = shopee_product.get('product_sku', None)
        product.status = ProductStatus.PUBLISH
        product.image = shopee_product.get('image_url', None)
        product.name = shopee_product.get('product_name', None)
        product.desc = shopee_product.get('description', None)
        product.second_hand = False
        return product

    @staticmethod
    def from_message(product: product_pb2.Product):
        raise NotImplementedError


class ProductMedia(MessageEncoder, Verifiable):

    def __init__(self, id=None, type=None, index=None, url=None):
        self.id = id
        self.type = type
        self.index = index
        self.url = url

    def to_message(self):
        return product_pb2.ProductMedia(
            id=self.id,
            type=self.type,
            index=self.index,
            url=self.url
        )

    def is_valid(self, raise_exception=False):
        return self.not_negative(self.type, self.index) and self.not_empty(self.url)

    @classmethod
    def from_store_product_media(cls, store_product_media: dict):
        media = ProductMedia()
        media.type = store_product_media.get('type', None)
        media.url = store_product_media.get('url', None)
        media.index = store_product_media.get('index', None)
        return media


class ProductModel(MessageEncoder, Verifiable):

    def __init__(self, sku=None, name=None, stock_qty=None, price=None, options_index=None):
        self.sku = sku
        self.name = name
        self.stock_qty = stock_qty
        self.price = price
        self.options_index = options_index

    def to_message(self):
        return product_pb2.ProductModel(
            sku=self.sku,
            name=self.name,
            stock_qty=self.stock_qty,
            price=self.price,
            options_index=self.options_index
        )

    def is_valid(self, raise_exception=False):
        return self.not_empty(self.sku, self.options_index)

    @classmethod
    def from_shop_model(cls, shopee_model):
        model = ProductModel()
        model.sku = shopee_model.get('model_sku', None)
        model.name = shopee_model.get('model_sku', None)
        model_stock = shopee_model.get('stock_info', None)
        model.stock_qty = model_stock.get('current_stock', None) if model_stock else None
        model_price = shopee_model.get('price_info')
        model.price = model_price.get('original_price', None) if model_price else None
        model.options_index = shopee_model.get('option_item_index')
        return model


class ProductExtra(MessageDecoder, MessageEncoder, Verifiable):
    def __init__(self, first_spec=None, second_spec=None, publish_id=None, models=None, media=None):
        self.firstSpec = first_spec
        self.secondSpec = second_spec
        self.publish_id = publish_id
        self.models = models
        self.media = media

    def is_valid(self, raise_exception=False):
        if not (self.firstSpec or self.secondSpec or self.publish_id or self.models):
            if raise_exception:
                raise Exception('Empty product extra')
            else:
                return False
        if self.firstSpec and not self.firstSpec.is_valid(raise_exception):
            if raise_exception:
                raise Exception('Inval first spec')
        if self.secondSpec:
            if not self.firstSpec:
                if raise_exception:
                    raise Exception('Must config 1st specification when 2nd spec are provided')
                return False
            if not self.secondSpec.is_valid(raise_exception):
                return False
        if self.models:
            for model in self.models:
                if not model.is_valid(raise_exception):
                    return False
        if self.media:
            for _media in self.media:
                if not _media.is_valid(raise_exception):
                    return False
        return True

    def to_message(self):
        message_spec_1st = self.firstSpec.to_message() if self.firstSpec else None
        message_spec_2nd = self.secondSpec.to_message() if self.secondSpec else None
        message_publish_id = self.publish_id if self.publish_id else None
        message_models = None if not self.models else [model.to_message() for model in self.models]
        message_media = None if not self.media else [media.to_message() for media in self.media]
        return product_pb2.ProductExtra(
            firstSpec=message_spec_1st,
            secondSpec=message_spec_2nd,
            publish_id=message_publish_id,
            models=message_models,
            media=message_media
        )

    def from_message(self, *args):
        raise NotImplementedError('Not Implement')


class ProductDetails(MessageEncoder, Verifiable):

    def __init__(self, product=None, extra=None):
        self.product = product
        self.extra = extra

    def is_valid(self, raise_exception=False):
        if not self.product:
            if raise_exception:
                raise Exception('Illegal product details, product is none')
            return False
        if not self.product.is_valid(raise_exception):
            return False
        if self.extra and not self.extra.is_valid(raise_exception):
            return False
        return True

    def to_message(self):
        return product_pb2.ProductDetails(
            product=self.product.to_message(),
            extra=self.extra.to_message() if self.extra else None
        )

    @classmethod
    def from_shopee_product(cls, shopee_global_product: dict, global_product_id=None):
        product = Product.from_shopee_product(shopee_product=shopee_global_product, global_product_id=global_product_id)
        specifications = shopee_global_product.get('options', [])
        _media_list = []
        for product_media in shopee_global_product.get('medias', []):
            _media_list.append(ProductMedia.from_store_product_media(product_media))
        first_spec_list = list(filter(lambda x: x['index'] == 0, specifications))
        _first_spec = None
        if first_spec_list:
            first_spec_dict = first_spec_list[0]
            first_spec_dict['option_items'] = list(filter(lambda x: x['store_product_option'] == first_spec_dict['id'],
                                                          shopee_global_product.get('option_items', [])))
            _first_spec = Specification.from_dict(first_spec_dict)

        second_spec_list = list(filter(lambda x: x['index'] == 1, specifications))
        _second_spec = None
        if second_spec_list:
            second_spec_dict = second_spec_list[0]
            second_spec_dict['option_items'] = list(
                filter(lambda x: x['store_product_option'] == second_spec_dict['id'],
                       shopee_global_product.get('option_items', [])))
            _second_spec = Specification.from_dict(second_spec_dict)
        # encode model of global product
        models_dicts = shopee_global_product.get('variants', [])
        models = []
        for model_dict in models_dicts:
            # Unify the mandatory fields so that we can handle model trans by 'from_shopee_product'
            model = ProductModel.from_shop_model(shopee_model=model_dict)
            models.append(model)
        extra = ProductExtra(first_spec=_first_spec, second_spec=_second_spec, models=models, media=_media_list)
        return ProductDetails(product=product, extra=extra)


class FieldSelector(MessageEncoder):

    def __init__(self, specification=False, option=False, publish_id=False, models=False, media=False):
        self.specification = specification
        self.option = option
        self.publish_id = publish_id
        self.models = models
        self.media = media

    def to_message(self):
        return product_pb2.FieldSelector(
            specification=self.specification,
            option=self.option,
            publish_id=self.publish_id,
            models=self.models,
            media=self.media
        )


class RetrieveRequest(MessageEncoder, Verifiable):

    def __init__(self, id=None, field_selector=None):
        self.id = id
        self.field_selector = field_selector
        self.msg = ''

    def to_message(self):
        return product_pb2.RetrieveRequest(
            id=self.id,
            selector=self.field_selector.to_message())

    def is_valid(self, raise_exception=False):
        is_valid = isinstance(self.id, int) and self.id >= 0
        if not is_valid:
            self.msg = 'Illegal parameter: id %s' % self.id
            if raise_exception:
                raise Exception(self.msg)
        return is_valid


class QueryRequest(ProtoType):

    def __init__(self, **kwargs):
        self.sku = None
        self.publish_id = None
        super().__init__(**kwargs)

    def is_valid(self):
        return super().is_not_all_empty(self.sku, self.publish_id)

    def to_message(self):
        return product_pb2.ProductQueryRequest(sku=self.sku, publish_id=self.publish_id)

    @classmethod
    def from_message(cls, product: product_pb2.Product):
        return Product(id=product.id,
                       sku=product.sku,
                       status=product.status,
                       image=product.image,
                       name=product.name,
                       desc=product.desc,
                       second_hand=product.second_hand,
                       models=product.models
                       )


class ProductResponse(MessageDecoder, ResponseResolver):

    def from_message(self, *args):
        raise NotImplementedError

    @property
    def code(self):
        if not self.response:
            raise Exception('Response is None or not init')
        return self.response.code

    @property
    def msg(self):
        if not self.response:
            raise Exception('Response is None or not init')
        return self.response.msg

    def __init__(self, response: product_pb2.ProductResponse):
        self.response = response

    @property
    def success(self):
        return self.code == product_pb2.ActionCode.SUCCESS

    @property
    def product(self):
        if not self.response:
            raise Exception('Response is None or not init')
        return self.response.product

    @property
    def extra(self):
        if not self.response:
            raise Exception('Response is None or not init')
        return self.response.extra
