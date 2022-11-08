
from functools import cmp_to_key

from django.db import transaction

from base.gRpc.types.base import RequestVerifier, MessageDecoder, MessageEncoder
from product.gRpc.server.protos import product_pb2
from base.gRpc.types.base import Verifiable
from product.gRpc.server.utils import product_to_message, specification_to_message, option_to_message, \
    not_all_empty, models_to_message, product_media_to_message

from product.models import GlobalProduct, ProductSpecification, ProductOption as ProductOptionModel
from productmedia.models import ProductMedia


class ProductStatus(object):
    EDIT = 0
    PUBLISH_READY = 1
    PUBLISH = 2


def encode_status(status: ProductStatus):
    if status == ProductStatus.EDIT:
        return 0
    elif status == ProductStatus.PUBLISH_READY:
        return 1
    elif status == ProductStatus.PUBLISH:
        return 2
    else:
        raise Exception('Unknow status %s' % status)


def decode_status(status: ProductStatus):
    if status == ProductStatus.EDIT:
        return GlobalProduct.EDIT
    elif status == ProductStatus.PUBLISH:
        return GlobalProduct.PUBLISH
    elif status == ProductStatus.PUBLISH_READY:
        return GlobalProduct.PUBLISH_READY
    else:
        raise Exception('Unknow status %s to decode' % status)


class Specification(MessageDecoder, Verifiable):

    id: int
    product_id: int
    name: str
    index: int

    def __init__(self, id=None, product_id=None, name=None, index=None):
        self.id = id
        self.product_id = product_id
        self.name = name
        self.index = index

    def is_valid(self, raise_exception=False):
        is_valid = False
        if self.id is not None:
            is_valid = self.id >= 0
        if self.id is None:
            is_valid = self.not_empty(self.name) and self.not_negative(self.product_id, self.index)
        if not is_valid and raise_exception:
            raise Exception('Illegal specification')
        return is_valid

    def save(self, *args):
        raise NotImplementedError('Not Implement')


class ProductOption(MessageDecoder, Verifiable):

    def __init__(self, id=None, specification=None, name=None, index=None):
        self.id = id
        self.specification = specification
        self.name = name
        self.index = index

    def is_valid(self, raise_exception=False):
        if self.id is not None:
            is_valid = self.id >= 0
        else:
            # TODO
            is_valid = self.specification and self.specification.is_valid(raise_exception) and self.not_empty(self.name) and self.not_negative(self.index)
        if not is_valid and raise_exception:
            raise Exception('Illegal product option')
        return is_valid

    def to_message(self):
        return product_pb2.ProductOption(
            id=self.id,
            specification=self.specification.to_message() if self.specification else None,
            name=self.name,
            index=self.index
        )

    def save(self, *args):
        raise NotImplementedError('Not Implement')


class Product(MessageDecoder, MessageEncoder, Verifiable):

    def encode(self, *args):
        raise NotImplementedError

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
            is_valid = self.not_empty(self.sku, self.image) and isinstance(self.status, ProductStatus)
        if not is_valid and raise_exception:
            raise Exception('Illegal product')
        return is_valid

    def to_message(self):
        return product_pb2.Product(
            id=self.id,
            sku=self.sku,
            status=encode_status(self.status) if self.status else None,
            image=self.image,
            name=self.name,
            desc=self.desc,
            second_hand=self.second_hand,
            models=self.models
        )

    @staticmethod
    def save(*args):
        raise NotImplementedError('Not Implement')


class ProductExtra(MessageDecoder, MessageEncoder, Verifiable):
    def encode(self, *args):
        raise NotImplementedError

    def __init__(self, specifications=None, options=None, publish_id=None, models=None):
        self.specifications = specifications
        self.options = options
        self.publish_id = publish_id
        self.models = models

    def is_valid(self, raise_exception=False):
        if not (self.specifications or self.options or self.publish_id or self.models):
            if raise_exception:
                raise Exception('Empty product extra')
            else:
                return False
        if self.specifications:
            if len(self.specifications) > 2:
                if raise_exception:
                    raise Exception('No more product specifications than 2, found %s ' % len(self.specifications))
            for spec in self.specifications:
                if not spec.is_valid(raise_exception):
                    break
        if self.options:
            for option in self.options:
                if not option.is_valid(raise_exception):
                    break
        if self.models:
            for model in self.models:
                if not model.is_valid(raise_exception):
                    return False
        return True

    def to_message(self):
        message_spec = None if not self.specifications else [spec.to_message() for spec in self.specifications]
        message_options = None if not self.options else [opt.to_message() for opt in self.options]
        message_publish_id = self.publish_id if self.publish_id else None
        message_models = None if not self.models else [model.to_message() for model in self.models]
        return product_pb2.ProductExtra(
            specifications=message_spec,
            options=message_options,
            publish_id=message_publish_id,
            models=message_models
        )

    def save(self, *args):
        raise NotImplementedError('Not Implement')


class ProductDetails(MessageEncoder, Verifiable):

    def encode(self, *args):
        raise NotImplementedError

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

    # ------------------------------------------
    # Request Relative Class
    # ------------------------------------------


class ProductCreateSerializer(MessageDecoder, MessageEncoder, RequestVerifier):

    def __init__(self, messge: product_pb2.ProductDetails):
        self.message = messge
        self.product = None
        self.first_spec = None
        self.second_spec = None
        self.options = []
        self.meida = []
        self.models = []
        self.code = None
        self.msg = None

    @transaction.atomic
    def save(self, *args):
        openid = 'd8ee5135188748805e32f3db8e64fbdf'
        creater = 'admin'
        if not self.is_valid():
            self.code, self.msg = product_pb2.ActionCode.MISSING_PARAMETERS, 'Fail to create product，empty product info'
            return False
        _product = self.message.product
        if _product.id:
            self.product = GlobalProduct.objects.filter(id=_product.id).first()
            if not self.product:
                self.code, self.msg = product_pb2.ActionCode.PRODUCT_NOT_FOUND, 'Product of id %s not found' % _product.id
                return False
        if not self.product:
            self.product = GlobalProduct(
                openid=openid,
                creater=creater,
                sku=_product.sku,
                status=decode_status(_product.status),
                mode=GlobalProduct.MODE_MULTIPLE,
                image=_product.image,
                name=_product.name,
                desc=_product.desc,
                second_hand=_product.second_hand,
                type=GlobalProduct.TYPE_MAIN
            )
        else:
            self.product.sku = _product.sku
            self.product.status = decode_status(_product.status)
            self.product.image = _product.image
            self.product.name = _product.name
            self.product.desc = _product.desc
        try:
            self.product.save()
        except Exception as e:
            self.code, self.msg = product_pb2.ActionCode.STORAGE_EXCEPTION, 'Fail to save product %s' % str(e)
            return False
        _extra = self.message.extra
        if not _extra:
            return True
        _media_list = _extra.media
        if _media_list:
            for _media in _media_list:
                media = self._create_product_media(self.product, _media)
                if not media:
                    return False
                self.meida.append(media)
        _first_spec = _extra.firstSpec
        if _first_spec:
            _first_spec.index = 0
            spec_model = self._create_product_specification(self.product, _first_spec)
            if not spec_model:
                return False
            self.first_spec = spec_model
        _second_spec = _extra.secondSpec
        if _second_spec:
            _second_spec.index = 1
            spec_model = self._create_product_specification(self.product, _second_spec)
            if not spec_model:
                return False
            self.second_spec = spec_model
        _models = _extra.models
        if _models:
            for _model in _models:
                model = self._create_product_model(self.product, _model)
                if not model:
                    return False
                self.models.append(model)
        return True

    def encode(self):
        if not isinstance(self.product, GlobalProduct):
            raise Exception('Fail to encode, product is empty')
        _product = product_to_message(self.product)
        _first_spec = specification_to_message(self.first_spec, True) if self.first_spec else None
        _second_spec = specification_to_message(self.second_spec, True) if self.second_spec else None
        _media = []
        for media in self.meida:
            _media.append(product_media_to_message(media))
        _models = []
        for model in self.models:
            _models.append(models_to_message(model))
        _extra = product_pb2.ProductExtra(firstSpec=_first_spec, secondSpec=_second_spec, media=_media, models=_models)
        return product_pb2.ProductDetails(product=_product, extra=_extra)

    def _create_product_media(self, product: GlobalProduct, media):
        if media.index is None:
            self.code, self.msg = product_pb2.ActionCode.MISSING_PARAMETERS, 'Product media missing index'
            return None
        media_obj = ProductMedia.objects.filter(product=product, index=media.index).first()
        if not media_obj:
            media_obj = ProductMedia.objects.create(
                openid=product.openid,
                creater=product.creater,
                product=product,
                media_type='image' if media.type == 2 else 'video',
                url=media.url,
                index=media.index
            )
        else:
            media_obj.url = media.url
            media_obj.is_delete = False
            media_obj.save()
        return media_obj

    def _create_product_specification(self, product: GlobalProduct, specification):
        spec_model = ProductSpecification.objects.filter(product=product, index=specification.index).first()
        if not spec_model:
            spec_model = ProductSpecification(
                openid=product,
                creater=product,
                product=self.product,
                name=specification.name,
                index=specification.index
            )
        else:
            spec_model.name = specification.name
            spec_model.is_delete = False
        try:
            spec_model.save()
        except Exception as exec:
            self.code, self.msg = product_pb2.ActionCode.STORAGE_EXCEPTION, 'Fail to save product spec %s' % str(
                exec)
            return None
        for opt in specification.options:
            opt_model = ProductOptionModel.objects.filter(specification=spec_model, index=opt.index).first()
            if not opt_model:
                opt_model = ProductOptionModel(
                    openid=product.openid,
                    creater=product.creater,
                    specification=spec_model,
                    name=opt.name,
                    index=opt.index,
                    image=opt.image
                )
            else:
                opt_model.name = opt.name
                opt_model.image = opt.image
                opt_model.is_delete = False
            try:
                opt_model.save()
            except Exception as exec:
                self.code, self.msg = product_pb2.ActionCode.STORAGE_EXCEPTION, 'Fail to save product option %s' % exec
                return None
        return spec_model

    def _create_product_model(self, product: GlobalProduct, model):
        if not model.sku:
            self.code, self.msg = product_pb2.ActionCode.MISSING_PARAMETERS, 'Model missing sku'
            return False
        if not model.options_index:
            self.code, self.msg = product_pb2.ActionCode.MISSING_PARAMETERS, 'Model missing options index'
            return False
        options_index = model.options_index.split(',')
        product_specifications = ProductSpecification.objects.filter(product=product, is_delete=False)
        global_model = product.models.filter(sku=model.sku, is_delete=False).first()
        try:
            if not global_model:
                global_model = GlobalProduct.objects.create(
                    sku=model.sku,
                    status=product.status,
                    mode=product.mode,
                    name=model.name,
                    second_hand=product.second_hand,
                    type=GlobalProduct.TYPE_MODEL,
                    openid=product.openid,
                    creater=product.creater
                )
                product.models.add(global_model)
                product.save()
            else:
                global_model.sku = model.sku
                global_model.status = product.status
                global_model.name = model.name
                global_model.save()
        except Exception as e:
            self.code, self.msg = product_pb2.ActionCode.STORAGE_EXCEPTION, 'Fail to save model(%s) %s' % (model.sku, exec)
            return False
        for index, option_index in enumerate(options_index):
            spec = product_specifications.filter(index=index).first()
            if not spec:
                self.code, self.msg = product_pb2.ActionCode.MISSING_PARAMETERS, 'model of sku: %s, spec at index %s not found' % (
                    model.sku, index)
                return False
            spec_option_of_index = getattr(spec, ProductSpecification.RelativeFields.SPECIFICATION_OPTION).filter(index=option_index).first()
            if not spec_option_of_index:
                self.code, self.msg = product_pb2.ActionCode.MISSING_PARAMETERS, 'model of sku: %s, optin(index %s) of spec(index %s) not found' % (
                    model.sku, option_index, index)
                return False
            spec_option_of_index.models.add(global_model)
            spec_option_of_index.save()
        return global_model

    def is_valid(self):
        if not self.message:
            self.code, self.msg = product_pb2.ActionCode.MISSING_PARAMETERS, 'Can not create product from, empty product info'
            return False
        print('message ....', self.message)
        if not self.message.HasField('product'):
            self.code, self.msg = product_pb2.ActionCode.MISSING_PARAMETERS, 'Missing product base info must'
            return False
        product = self.message.product
        if not product.sku:
            self.code = product_pb2.ActionCode.MISSING_PARAMETERS, 'Missing product sku'
            return False
        if product.status is None:
            self.code, self.msg = product_pb2.ActionCode.MISSING_PARAMETERS, 'Missing product status'
            return False
        if not product.image:
            self.code, self.msg = product_pb2.ActionCode.MISSING_PARAMETERS, 'Missing product image'
            return False
        extra = self.message.extra
        if not extra:
            return True
        if extra.HasField('firstSpec'):
            _first_spec = extra.firstSpec
            if not _first_spec.name:
                self.code, self.msg = product_pb2.ActionCode.MISSING_PARAMETERS, 'Missing name for 1st specification'
                return False
            if not _first_spec.options:
                self.code, self.msg = product_pb2.ActionCode.MISSING_PARAMETERS, 'Missing option for 1st specification'
            sorted(_first_spec.options, key=cmp_to_key(lambda x, y: x.index < y.index))
            for idx, opt in enumerate(_first_spec.options):
                if not opt.name or not opt.image:
                    self.code, self.msg = product_pb2.ActionCode.ILLEGAL_PARAMETERS, 'Illegal option name or image at index %s' % opt.index
                if opt.index is None or idx != opt.index:
                    self.code, self.msg = product_pb2.ActionCode.ILLEGAL_PARAMETERS, 'Illegal option index of name %s' % opt.name
        if extra.HasField('secondSpec'):
            _second_spec = extra.secondSpec
            if not _second_spec.name:
                self.code, self.msg = product_pb2.ActionCode.MISSING_PARAMETERS, 'Missing name for 2nd specification'
                return False
            if not _second_spec.options:
                self.code, self.msg = product_pb2.ActionCode.MISSING_PARAMETERS, 'Missing option for 2nd specification'
            sorted(_second_spec.options, key=cmp_to_key(lambda x, y: x.index < y.index))
            for idx, opt in enumerate(_second_spec.options):
                if not opt.name:
                    self.code, self.msg = product_pb2.ActionCode.ILLEGAL_PARAMETERS, 'Illegal option name at index %s' % opt.index
                if opt.index is None or idx != opt.index:
                    self.code, self.msg = product_pb2.ActionCode.ILLEGAL_PARAMETERS, 'Illegal option index of name %s' % opt.name
        return True

    def code(self):
        return self.code

    def msg(self):
        return self.msg


class ProductRetrieveSerializer(RequestVerifier, MessageEncoder, MessageDecoder):

    def __init__(self, message: product_pb2.RetrieveRequest):
        self.message = message
        self.product = None
        self.extra = None
        self.code = None
        self.msg = ''

    def is_valid(self):
        if not self.message:
            self.code, self.msg = product_pb2.ActionCode.MISSING_PARAMETERS, 'Empty retrieve request'
            return False
        if not self.message.id:
            self.code, self.msg = product_pb2.ActionCode.MISSING_PARAMETERS, 'Missing product id'
            return False
        return True

    def code(self):
        return self.code

    def msg(self):
        return self.msg

    def encode(self, *args):
        if not self.product:
            raise Exception('product is none')
        _product = product_to_message(self.product)
        # determine if need extra info
        _extra = None
        if self.message.HasField('selector'):
            selector = self.message.selector
            is_specification = selector.specification
            is_option = selector.option
            _first_spec = None
            _second_spec = None
            if is_specification:
                first_spec = ProductSpecification.objects.filter(product_id=self.product.id, index=0).first()
                if first_spec:
                    _first_spec = specification_to_message(first_spec, is_option)
                second_spec = ProductSpecification.objects.filter(product_id=self.product.id, index=1).first()
                if second_spec:
                    _second_spec = specification_to_message(second_spec, is_option)
            _models = []
            if selector.models:
                for model in self.product.models.all():
                    print(models_to_message(model))
                    _models.append(models_to_message(model))
            _product_media = []
            if selector.media:
                for media in getattr(self.product, GlobalProduct.RelativeFields.PRODUCT_MEDIA).all():
                    _product_media.append(product_media_to_message(media))
            _extra = product_pb2.ProductExtra(firstSpec=_first_spec, secondSpec=_second_spec, models=_models, media=_product_media)
        return product_pb2.ProductResponse(code=0, product=_product, extra=_extra)

    def save(self, *args):
        if not self.is_valid():
            raise Exception('Invalid requet')
        product = GlobalProduct.objects.filter(id=self.message.id, is_delete=False).first()
        if not product:
            self.code, self.msg = product_pb2.ActionCode.PRODUCT_NOT_FOUND, 'Product of id %s not found' % self.message.id
            return False
        self.product = product
        return True


class QueryRequest(RequestVerifier, MessageEncoder, MessageDecoder):

    def __init__(self, **kwargs):
        self.sku = None
        self.publish_id = None
        self.code = None
        self.msg = None

    def encode(self, *args):
        return product_pb2.ProductQueryRequest(sku=self.sku, publish_id=self.publish_id)

    def save(self, product: product_pb2.Product):
        product_id = product.id

        product = GlobalProduct.objects.filter(id=product_id, is_delete=False).first()
        if not product:
            return None

        return Product(id=product.id,
                       sku=product.sku,
                       status=product.status,
                       image=product.image,
                       name=product.name,
                       desc=product.desc,
                       second_hand=product.second_hand,
                       models=product.models
                       )

    def is_valid(self):
        return not_all_empty(self.sku, self.publish_id)

    def code(self):
        pass

    def msg(self):
        pass


# class ProductResponse(MessageDecoder, RequestVerifier):
#
#     def is_valid(self):
#         pass
#
#     def save(self, *args):
#         pass
#
#     def __init__(self, product=None, extra=None):
#         self.code = response.code
#         self.msg = response.msg
#         self.product = Product.to_message(product_pb2.product)
#         self.extra = ProductExtra.decode(product_pb2.extra)
#
#
#     def code(self):
#         return self.code
#
#     def msg(self):
#         pass
#
#     @property
#     def product(self):
#         return self.product
#
#     @property
#     def extra(self):
#         return self.extra
#
#     def decode(self, response: product_pb2.ProductResponse):
#         self.code = response.code
#         self.msg = response.msg
#         self.product = Product.decode(product_pb2.product)
#         self.extra = ProductExtra.decode(product_pb2.extra)





