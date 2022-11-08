# import threading
# import logging
#
# from product.models import GlobalProduct
# from productpublish.serializers import EditPricePostSerializer
#
# logger = logging.getLogger()
#
#
# class ProductPriceService(object):
#     __create_key = object()
#     lock = threading.RLock()
#     service = None
#
#     def __init__(self, create_key):
#         assert (
#                 create_key == ProductPriceService.__create_key), "Global Product Price Service is single instance, please use GlobalProductService.get_instance()"
#
#     @classmethod
#     def get_instance(cls):
#         if cls.service is None:
#             cls.lock.acquire()
#             if cls.service is None:
#                 cls.service = cls(ProductPriceService.__create_key)
#             cls.lock.release()
#             return cls.service
#         return cls.service
#
#     # def create_or_udpate_price(self, model: GlobalProduct, price_infos):
#     #     for price_info in price_infos:
#     #         price = getattr(model, GlobalProduct.RelativeFields.PRICE_INFO)\
#     #             .filter(store_id=price_info['store_id']).first()
#     #         if not price:
#     #             price_info['product'] = model.id
#     #             price_info['creater'] = model.creater
#     #             price_info['openid'] = model.openid
#     #             serializer = EditPricePostSerializer(data=price_info)
#     #         else:
#     #             serializer = EditPricePostSerializer(price, data=price_info, partial=True)
#     #         if not serializer.is_valid():
#     #             logger.error('Fail to save / update price %s ' % serializer.errors)
#     #             raise Exception('Fail to save update price ')
#     #         serializer.save()
#
#
