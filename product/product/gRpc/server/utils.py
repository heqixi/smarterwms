from functools import cmp_to_key, reduce

from product.models import GlobalProduct, ProductSpecification, ProductOption, ProductSupplier
from product.gRpc.server.protos import product_pb2
from productmedia.models import ProductMedia, Constants


def not_empty(*args, nullable=False):
    for field in args:
        if field is None and not nullable:
            return False
        if field and len(field) == 0:
            return False, field
    return True


def not_all_empty(*args):
    return not all([arg is None or len(arg) == 0 for arg in args])


def not_negative(*args, nullable=False):
    for field in args:
        if field is None and not nullable:
            return False
        if field is not None and field < 0:
            return False
    return True


def product_status_to_message(status: str):
    if status == GlobalProduct.EDIT:
        return product_pb2.ProductStatus.EDIT
    elif status == GlobalProduct.PUBLISH:
        return product_pb2.ProductStatus.PUBLISH
    elif status == GlobalProduct.PUBLISH_READY:
        return product_pb2.ProductStatus.PUBLISH_READY
    else:
        raise Exception('Unknow status %s to decode' % status)


def product_to_message(product: GlobalProduct):
    print(product.id, product.sku, product.status, type(product.image), product.image, product.name, product.desc, product.second_hand)
    return product_pb2.Product(
        id=product.id,
        sku=product.sku,
        status=product_status_to_message(product.status),
        image=product.image,
        name=product.name,
        desc=product.desc,
        second_hand=product.second_hand
    )


def specification_to_message(spec: ProductSpecification, is_option) -> product_pb2.Specification:
    if is_option:
        options = ProductOption.objects.filter(specification_id=spec.id).all()
        options_message = [option_to_message(opt) for opt in options]
    else:
        options_message = None
    return product_pb2.Specification(
        id=spec.id,
        product_id=spec.product_id,
        name=spec.name,
        index=spec.index,
        options=options_message
    )


def option_to_message(option: ProductOption) -> product_pb2.ProductOption:
    return product_pb2.ProductOption(
        id=option.id,
        spec_index=option.specification.id,
        name=option.name,
        image=option.image,
        index=option.index
    )


def models_to_message(model: GlobalProduct) -> product_pb2.ProductModel:
    options = getattr(model, GlobalProduct.RelativeFields.MODEL_OPTIONS).all()
    options = sorted(list(options), key=cmp_to_key(lambda x, y: x.specification.index - y.specification.index))
    options_index = ','.join([str(opt.index) for opt in options])
    model_stock = getattr(model, GlobalProduct.RelativeFields.MODEL_STOCKS).first()
    return product_pb2.ProductModel(
        id=model.id,
        sku=model.sku,
        name=model.name,
        stock_qty=model_stock.stock_qty if model_stock else None,
        price=model_stock.price if model_stock else None,
        options_index=options_index
    )


def product_media_to_message(media: ProductMedia) -> product_pb2.ProductMedia:
    return product_pb2.ProductMedia(
        id=media.id,
        type=1 if media.media_type == Constants.MEDIA_TYPE_VIDEO else 2,
        url=media.url,
        index=media.index
    )


def supplier_info_to_message(supplier_info: ProductSupplier):
    return product_pb2.SupplierInfo(
        id=supplier_info.id,
        url=supplier_info.url,
        logistics_costs=supplier_info.logistics_costs,
        min_purchase_num=supplier_info.min_purchase_num,
        delivery_days=supplier_info.delivery_days,
        supplier_name=supplier_info.supplier_name
    )
