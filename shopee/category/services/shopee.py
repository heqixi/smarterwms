import logging
import threading

from rest_framework.exceptions import APIException

from category.models import ShopeeAttribute, ShopeeAttributeValue, ShopeeCategory, ShopeeCategoryBrand, \
    ShopeeCategoryTemplate, ShopeeCategoryTemplateAttribute
from category.serializers import ShopeeAttributePostSerializer, ShopeeAttributeValuePostSerializer, \
    ShopeeAttributeGetSerializer, ShopeeCategoryGetSerializer, ShopeeBrandPostSerializer, ShopeeBrandGetSerializer, \
    ShopeeCategoryTemplateAttributeGetSerializer
from store.models import StoreModel

logger = logging.getLogger()


class CategoryService(object):
    __create_key = object()
    lock = threading.RLock()
    service = None

    def __init__(self, create_key):
        assert (
                create_key == CategoryService.__create_key), "Global Product Service is single instance, please use GlobalProductService.get_instance()"

    @classmethod
    def get_instance(cls):
        if cls.service is None:
            cls.lock.acquire()
            if cls.service is None:
                cls.service = cls(CategoryService.__create_key)
            cls.lock.release()
            return cls.service
        return cls.service

    def get_category_attribute(self, openid, merchant_id, category_id):
        attributes = ShopeeAttribute.objects.filter(openid=openid, category_id=category_id).all()
        if attributes.count() <= 0:
            CategoryService.get_instance().refresh_shopee_attribute(openid, merchant_id, category_id)
        attributes = ShopeeAttribute.objects.filter(category_id=category_id).all()
        serializer = ShopeeAttributeGetSerializer(attributes, many=True)
        return serializer.data

    def get_category_brand(self, openid, merchant_id, category_id):
        brands = ShopeeCategoryBrand.objects.filter(openid=openid, category_id=category_id, merchant_id=merchant_id).all()
        if brands.count() <= 0:
            self.refresh_shopee_brand(openid, merchant_id, category_id)
        brands = ShopeeCategoryBrand.objects.filter(openid=openid, category_id=category_id,
                                                    merchant_id=merchant_id).all()
        serializer = ShopeeBrandGetSerializer(brands, many=True)
        return serializer.data

    def refresh_shopee_attribute(self, openid, merchant_id, category_id):
        from store.services.global_service import GlobalService
        if not merchant_id or not category_id:
            raise APIException('Can not refresh shopee attribute, missing merchant id / category id')
        attribute_list = GlobalService.get_instance().get_global_attributes(merchant_id, category_id)
        for attribute in ShopeeAttribute.objects.filter(openid=openid, category_id=category_id).all():
            ShopeeAttributeValue.object.filter(openid=openid, attribute_id=attribute.id).delete()
            attribute.delete()
        for attribute in attribute_list:
            attribute['category_id'] = category_id
            attribute['openid'] = openid
            attribute['creater'] = 'unknow'
            serializer = ShopeeAttributePostSerializer(data=attribute)
            if not serializer.is_valid():
                logger.error('Shopee attribute info is invalid %s' % serializer.errors)
                raise APIException('Can not save shopee cateory attribute, data is in value ')
            attribute_instance = serializer.save()
            for attribute_value in attribute['attribute_value_list']:
                attribute_value['attribute'] = attribute_instance.id
                attribute_value['openid'] = attribute_instance.openid
                attribute_value['creater'] = attribute_instance.creater

                serializer = ShopeeAttributeValuePostSerializer(data=attribute_value)
                if not serializer.is_valid():
                    logger.error('Can not save attribute value %s' % serializer.errors)
                    raise APIException('Can not save attribute value')
                serializer.save()

    def refresh_shopee_brand(self, openid, merchant_id, category_id):
        logger.info('refresh_shopee_brand %s ' % category_id)
        from store.services.global_service import GlobalService
        brand_list = GlobalService.get_instance().get_global_brands(merchant_id, category_id)
        ShopeeCategoryBrand.objects.filter(openid=openid, merchant_id=merchant_id, category_id=category_id).delete()
        saved_data = []
        for brand in brand_list:
            brand['openid'] = openid
            brand['merchant_id'] = merchant_id
            brand['category_id'] = category_id
            brand['creater'] = 'unknow'
            serializer = ShopeeBrandPostSerializer(data=brand)
            if not serializer.is_valid():
                logger.info('Can not save brand, invalid brand info %s %s %s' % (serializer.errors, category_id, brand['brand_id']))
                raise APIException('Invalid brand info')
            serializer.save()
            saved_data.append(serializer.data)
        return saved_data

    def refresh_shopee_cateogry(self, merchant_id, openid, creater):
        from store.services.product_service import ProductService
        category_list = ProductService.get_instance().get_category(merchant_id)
        logger.info('refresh shopee category ', category_list)

        # 先删除原有数据
        ShopeeCategory.objects.filter(merchant_id=merchant_id).delete()
        category_instance_list = []
        for category in category_list:
            category_instance = ShopeeCategory(
                merchant_id=merchant_id,
                category_id=category['category_id'],
                original_category_name=category['original_category_name'],
                display_category_name=category['display_category_name'],
                has_children=category['has_children'],
                openid=openid,
                creater=creater
            )
            category_instance.save()
            if category['parent_category_id'] > 0:
                category_parent = ShopeeCategory.objects.filter(category_id=category['parent_category_id'], merchant_id=merchant_id).first()
                category_instance.parent = category_parent
                category_instance.save()
            category_instance_list.append(category_instance)
        serializer = ShopeeCategoryGetSerializer(category_instance_list, many=True)
        return serializer.data

    def get_category_template(self, openid, merchant_id):
        templates = ShopeeCategoryTemplate.objects.filter(openid=openid, merchant_id=merchant_id).all()
        result = []
        for instance in templates:
            root_category = self.serialize_category_template(instance)
            result.append(root_category)
        return result

    def serialize_category_template(self, instance: ShopeeCategoryTemplate):
        root_category = {}
        shopee_category = ShopeeCategory.objects.filter(category_id=instance.category_id,
                                                        merchant_id=instance.merchant_id).first()
        if not shopee_category:
            return None
        attributes = CategoryService.get_instance().get_category_attribute(instance.openid, instance.merchant_id,
                                                                           instance.category_id)

        attribute_values = ShopeeCategoryTemplateAttribute.objects.filter(openid=instance.openid,
                                                                          category_id=instance.id).all()
        attribute_values_data = ShopeeCategoryTemplateAttributeGetSerializer(attribute_values, many=True).data
        brand_info = {}
        if instance.brand_id >= 0:
            brand_info['brand'] = {'brand_id': instance.brand_id, 'display_brand_name': instance.display_brand_name}
        merchant = StoreModel.objects.filter(uid=instance.merchant_id).first()
        category_tree = [shopee_category]
        while shopee_category.parent:
            shopee_category = shopee_category.parent
            category_tree.append(shopee_category)
        category_tree.reverse()
        current_category = None
        for index, category in enumerate(category_tree):
            if index == 0:
                root_category['template_name'] = instance.template_name
                root_category['id'] = instance.id
                root_category['category_id'] = category.category_id
                root_category['merchant'] = {'uid': category.merchant_id, 'name': merchant.name}
                root_category['original_category_name'] = category.original_category_name
                root_category['display_category_name'] = category.display_category_name
                root_category['attributes'] = attributes
                root_category['brand_info'] = brand_info
                root_category['attribute_values'] = attribute_values_data
                current_category = root_category
            else:
                current_category['sub_category'] = {
                    'category_id': category.category_id,
                    'original_category_name': category.original_category_name,
                    'display_category_name': category.display_category_name
                }
                current_category = current_category['sub_category']
        return root_category

