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
            image_id_list.append(image.image_id)
        return image_id_list

    @classmethod
    def _publish_shopee_image(cls, image_url, file_stream, merchant_id, openid, creater):
        image_stream = [('image', ('image', file_stream, 'application/octet-stream'))]
        publish_image_info = ProductService.get_instance().upload_image(image_stream, openid)
        product_media_publish = ProductMediaPublish(
            merchant_id=merchant_id,
            publish_id=publish_image_info['image_id'],
            publish_url='',
            source_url=image_url,
            openid=openid,
            creater=creater
        )
        product_media_publish.save()
        return publish_image_info['image_id']


