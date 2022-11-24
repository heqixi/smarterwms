
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
        models = self.context['request'].query_params.get('models', None)
        if store_details:
            store = StoreListGetSerializer()
            fields['store'] = store
        if models:
            models = StoreProductVariantListGetSerializer(many=True, source='product_variant')
            fields['models'] = models
        return fields

    class Meta:
        model = StoreProductModel
        exclude = ['creater', 'openid']
        read_only_fields = ['id']


class StoreGlobalProductListGetSerializer(serializers.ModelSerializer):
    create_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
    update_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')

    def get_fields(self):
        print('get store global fields')
        fields = super().get_fields()
        store_detail = self.context['request'].query_params.get('store_detail', None)
        is_models = self.context['request'].query_params.get('models', None)
        supplier_info = self.context['request'].query_params.get('supplier_info', None)
        product_medias = self.context['request'].query_params.get('product_medias', None)
        option = self.context['request'].query_params.get('options', None)
        store_prices = self.context['request'].query_params.get('store_prices', None)
        if store_detail:
            store = StoreListGetSerializer()
            fields['store'] = store
        if is_models:
            variants = StoreProductVariantListGetSerializer(many=True, source='product_variant')
            fields['variants'] = variants
        if supplier_info:
            supplier_info = serializers.SerializerMethodField('get_supplier_info')
            fields['supplier_info'] = supplier_info
        if product_medias:
            medias = serializers.SerializerMethodField('get_product_medias')
            fields['medias'] = medias
        if option:
            options = serializers.SerializerMethodField('get_options')
            option_items = serializers.SerializerMethodField('get_option_items')
            fields['options'] = options
            fields['option_items'] = option_items
        if store_prices:
            print('get store global store_prices')
            fields['store_prices'] = serializers.SerializerMethodField('get_store_prices')
        return fields

    def get_store_prices(self, product: StoreProductModel):
        store_prices = []
        for store_product in product.shop_products.all():
            variant_prices = [(variant_price.original_price, variant_price.current_price) for variant_price in
                              store_product.product_price_info.all()]
            if not variant_prices:
                continue
            min_original_price = min([original_price for original_price, _ in variant_prices if original_price])
            max_original_price = max([original_price for original_price, _ in variant_prices if original_price])
            min_current_price = min([current_price for _, current_price in variant_prices if current_price])
            max_current_price = max([current_price for _, current_price in variant_prices if current_price])
            if variant_prices:
                store_prices.append(
                    {
                        'store': {
                            'id': store_product.store.id,
                            'name': store_product.store.name
                        },
                        'original_price': {'min': min_original_price, 'max': max_original_price},
                        'current_price': {'min': min_current_price, 'max': max_current_price}
                    }
                )
        return store_prices

    def get_supplier_info(self, obj):
        suppler_info = obj.supplier_info.first()
        if not suppler_info:
            return None
        return spg.django_model_to_dict(model=suppler_info)

    def get_product_medias(self, obj: StoreProductModel):
        media_list = obj.product_media.all()
        return spg.django_model_to_dict(model_list=media_list)

    def get_option_items(self, obj: StoreProductModel):
        option_items = obj.product_option_item.all()
        return spg.django_model_to_dict(model_list=option_items)

    def get_options(self, obj: StoreProductModel):
        options = obj.product_option.all()
        return spg.django_model_to_dict(model_list=options)

    class Meta:
        model = StoreProductModel
        exclude = ['creater']
        read_only_fields = ['id']


class StoreProductVariantListGetSerializer(serializers.ModelSerializer):
    product_id = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()
    product_sku = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    price_info = serializers.SerializerMethodField()

    def get_image(self, obj):
        index = obj.option_item_index.split(',')[0]
        option = obj.store_product.product_option.filter(index=0).first()
        first_option_item = StoreProductOptionItemModel.objects.filter(
            store_product=obj.store_product, index=index, store_product_option=option).first()
        return first_option_item.image_url if first_option_item else None

    def get_product_id(self, obj):
        return obj.store_product.product_id

    def get_product_name(self, obj):
        return obj.store_product.product_name

    def get_product_sku(self, obj):
        return obj.store_product.product_sku

    def get_price_info(self, obj: StoreProductVariantModel):
        price_info_model = obj.variant_price.first()
        if not price_info_model:
            return {}
        return {
            'original_price': price_info_model.original_price,
            'current_price': price_info_model.current_price,
            'currency': price_info_model.currency
        }

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
    supplier_info = serializers.SerializerMethodField()

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

    def get_supplier_info(self, obj):
        suppler_info = obj.supplier_info.first()
        if suppler_info:
            return spg.django_model_to_dict(model=suppler_info)
        return {}

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

