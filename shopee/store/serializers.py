
from rest_framework import serializers

from category.models import ShopeeCategory
from category.serializers import ProductAttributeGetSerializer, ProductCategoryBrandGetSerializer
from category.services.shopee import CategoryService
from publish.models import ProductCategoryAttribute, ProductCategory, ProductCategoryBrand
from store.common import StoreProductType, PackageProductType
from store.models import StoreModel, StoreProductModel, StoreProductVariantModel, StoreProductOptionItemModel, \
    StoreProductPackageModel, ShopeeRegionSettingsModel, ShopeeStoreRegionSetting
from utils import spg


class StoreListGetSerializer(serializers.ModelSerializer):

    name = serializers.CharField(read_only=True, required=False)
    uid = serializers.CharField(read_only=True, required=False)
    type = serializers.IntegerField(read_only=True, required=False)
    creater = serializers.CharField(read_only=True, required=False)
    create_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
    update_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
    merchant = serializers.SerializerMethodField()

    def get_merchant(self, obj):
        return spg.django_model_to_dict(obj)

    class Meta:
        model = StoreModel
        exclude = []
        read_only_fields = ['id']


class StoreProductListGetSerializer(serializers.ModelSerializer):

    create_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
    update_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
    global_item_id = serializers.SerializerMethodField()

    def get_global_item_id(self, obj):
        return obj.global_product.first().product_id if obj.global_product.first() else ''

    def get_fields(self):
        fields = super().get_fields()
        store_details = self.context['request'].query_params.get('shopee_store', None)
        if store_details:
            store = StoreListGetSerializer()
            fields['store'] = store
        return fields

    class Meta:
        model = StoreProductModel
        exclude = ['creater', 'openid']
        read_only_fields = ['id']


class StoreGlobalProductListGetSerializer(serializers.ModelSerializer):
    create_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
    update_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')

    def get_fields(self):
        fields = super().get_fields()
        is_shopee_store_products = self.context['request'].query_params.get('store_products', None)
        if is_shopee_store_products:
            shopee_store_products = StoreProductListGetSerializer(many=True)
            fields['store_products'] = shopee_store_products
        return fields

    class Meta:
        model = StoreProductModel
        exclude = ['creater']
        read_only_fields = ['id']


class StoreProductVariantListGetSerializer(serializers.ModelSerializer):
    product_id = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()
    product_sku = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        index = obj.option_item_index.split(',')[0]
        first_option_item = StoreProductOptionItemModel.objects.filter(
            store_product=obj.store_product, index=index).first()
        return first_option_item.image_url if first_option_item else None

    def get_product_id(self, obj):
        return obj.store_product.product_id

    def get_product_name(self, obj):
        return obj.store_product.product_name

    def get_product_sku(self, obj):
        return obj.store_product.product_sku

    class Meta:
        model = StoreProductVariantModel
        exclude = ['creater', 'openid']
        read_only_fields = ['id']


class StoreShopProductVariantSerializer(serializers.ModelSerializer):

    price_info = serializers.SerializerMethodField()
    stock_info = serializers.SerializerMethodField()

    def get_price_info(self, obj):
        price = obj.variant_price.first()
        return spg.django_model_to_dict(model=price) if price else None

    def get_stock_info(self, obj):
        stock_info = {'current_stock': 0, 'reserved_stock': 0}
        for stock in obj.variant_stock.all():
            stock_info['current_stock'] += stock.current_stock
            stock_info['reserved_stock'] += stock.reserved_stock
        return stock_info

    class Meta:
        model = StoreProductVariantModel
        exclude = ['creater', 'openid']
        read_only_fields = ['id']


class StoreShopProductDetailSerializer(serializers.ModelSerializer):
    store = serializers.SerializerMethodField()
    options = serializers.SerializerMethodField()
    option_items = serializers.SerializerMethodField()
    variants = serializers.SerializerMethodField()
    medias = serializers.SerializerMethodField()
    price_info = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    def get_store(self, obj):
        return spg.django_model_to_dict(model=obj.store)

    def get_price_info(self, obj):
        price = obj.product_price_info.filter(type=StoreProductType.MAIN).first()
        return spg.django_model_to_dict(model=price) if price else None

    def get_options(self, obj):
        return spg.django_model_to_dict(model_list=obj.product_option.all())

    def get_option_items(self, obj):
        return spg.django_model_to_dict(model_list=obj.product_option_item.all())

    def get_variants(self, obj):
        product_variant_list = []
        for product_variant in obj.product_variant.all():
            product_variant_list.append(StoreShopProductVariantSerializer(product_variant).data)
        return product_variant_list

    def get_medias(self, obj):
        return spg.django_model_to_dict(model_list=obj.product_media.all())

    def get_category(self, product: StoreProductModel):
        instance = getattr(product, StoreProductModel.RelativeFields.PRODUCT_CATEGORY).first()
        if not instance:
            brand = ProductCategoryBrand.objects.filter(brand_id=product.brand_id).first()
            if product.category_id:
                instance = ProductCategory.objects.create(
                    openid=product.openid,
                    creater=product.creater,
                    product=product,
                    merchant_id=product.store.uid,
                    category_id=product.category_id,
                    brand=brand
                )
        if not instance:
            return None
        root_category = {}
        shopee_category = ShopeeCategory.objects.filter(category_id=instance.category_id,
                                                        merchant_id=instance.merchant_id).first()
        merchant = StoreModel.objects.filter(uid=instance.merchant_id).first()
        if not shopee_category:
            return None
        attributes = CategoryService.get_instance().get_category_attribute(instance.openid, instance.merchant_id,
                                                                           instance.category_id)
        attribute_values = ProductCategoryAttribute.objects.filter(openid=instance.openid,
                                                                   category_id=instance.id).all()
        attribute_values_data = ProductAttributeGetSerializer(attribute_values, many=True).data
        brand_info = {"brand": {
            "brand_id": 0,
            "display_brand_name": 'NoBrand',
            "original_brand_name": 'NoBrand'
        }}
        if instance.brand:
            brand = ProductCategoryBrandGetSerializer(instance.brand).data
            brand_info['brand'] = brand
            brand_info['id'] = instance.brand.id

        category_tree = [shopee_category]
        while shopee_category.parent:
            shopee_category = shopee_category.parent
            category_tree.append(shopee_category)
        category_tree.reverse()
        current_category = None
        for index, category in enumerate(category_tree):
            if index == 0:
                root_category['id'] = instance.id
                root_category['category_id'] = category.category_id
                root_category['merchant'] = {'uid': category.merchant_id, 'name': merchant.name, 'id': merchant.id}
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

    class Meta:
        model = StoreProductModel
        exclude = ['creater', 'openid']
        read_only_fields = ['id']


class StoreGlobalProductEmitDataSerializer(StoreShopProductDetailSerializer):
    """
    通知草稿箱产品序列化数据
    """
    shop_products = serializers.SerializerMethodField()

    def get_shop_products(self, obj):
        products = []
        for shop_product in obj.shop_products.all():
            products.append(StoreShopProductDetailSerializer(shop_product).data)
        return products

    class Meta:
        model = StoreProductModel
        exclude = []
        read_only_fields = ['id']


class StoreProductPackageGetListSerializer(serializers.ModelSerializer):

    image = serializers.SerializerMethodField()
    create_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
    update_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
    package_item = serializers.SerializerMethodField()

    def get_package_item(self, obj):
        return spg.django_model_to_dict(model_list=obj.package_item.all())

    def get_image(self, obj):
        if obj.product_type == PackageProductType.STORE_MAIN:
            product = StoreProductModel.objects.get(openid=obj.openid, product_id=obj.uid)
            return product.image_url
        if obj.product_type == PackageProductType.STORE_VARIANTS:
            variant = StoreProductVariantModel.objects.get(openid=obj.openid, model_id=obj.uid)
            index = variant.option_item_index.split(',')[0]
            first_option_item = StoreProductOptionItemModel.objects.filter(
                store_product=variant.store_product, index=index).first()
            return first_option_item.image_url if first_option_item else None
        return None

    class Meta:
        model = StoreProductPackageModel
        exclude = []
        read_only_fields = ['id']


class ShopeeRegionSettingsGetSerializer(serializers.ModelSerializer):

    logistics_calc_list = serializers.SerializerMethodField()
    stores = serializers.SerializerMethodField()

    def get_logistics_calc_list(self, obj):
        return spg.django_model_to_dict(model_list=obj.region_logistics_calc.all())

    def get_stores(self, obj):
        store_uids = []
        for store_setting in getattr(obj, ShopeeStoreRegionSetting.RelativeFields.SETTING_STORES).all():
            store_uids.append(store_setting.store_uid)
        return store_uids

    class Meta:
        model = ShopeeRegionSettingsModel
        exclude = ['openid', 'is_delete', 'create_time', 'creater']
        read_only_fields = ['id']

