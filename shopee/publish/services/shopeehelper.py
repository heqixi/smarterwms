import logging

from publish.models import ProductMediaPublish
from store.models import StoreProductModel
from store.services.product_service import ProductService

logger = logging.getLogger()


class ShopeeHelper:

    @classmethod
    def get_product_image_ids(cls, store_product: StoreProductModel):
        product_images = getattr(store_product, StoreProductModel.RelativeFields.PRODUCT_MEDIA).order_by('index').all()
        image_id_list = []
        for image in product_images:
            if image.image_id:
                image_id_list.append(image.image_id)
        return image_id_list

    @classmethod
    def publish_shopee_image(cls, file_stream, store):
        image_stream = [('image', ('image', file_stream, 'application/octet-stream'))]
        publish_image_info = ProductService.get_instance().upload_image(image_stream, store)
        return publish_image_info['image_id']


