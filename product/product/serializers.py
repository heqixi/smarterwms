
from django.forms import model_to_dict
from rest_framework import serializers

from productmedia.models import Constants
from productmedia.serializers import ProductMediaGetSerializer
from .models import GlobalProduct, ProductSupplier, ProductLogistic, ProductSpecification, \
    ProductOption, ProductModelStock


class ProductModelGetSerializer(serializers.ModelSerializer):
    stock = serializers.SerializerMethodField('get_stock')
    price_info = serializers.SerializerMethodField('get_price_info')

    def get_price_info(self, model: GlobalProduct):
        prices_instances = getattr(model, GlobalProduct.RelativeFields.PRICE_INFO).all()
        if not prices_instances:
            return []
        prices = []
        for prices_instance in prices_instances:
            prices.append(model_to_dict(prices_instance))
        return prices

    def get_stock(self, model: GlobalProduct):
        stock = getattr(model, GlobalProduct.RelativeFields.MODEL_STOCKS).first()
        if not stock:
            return {'stock_qty': None, 'price': None}
        return ProductModelStockGetSerializer(stock).data

    def get_fields(self):
        fields = super().get_fields()
        option_params = self.context['request'].query_params.get(GlobalProduct.RelativeFields.MODEL_OPTIONS, None)
        if option_params:
            options = ProductOptionGetSerializers(source=GlobalProduct.RelativeFields.MODEL_OPTIONS, many=True)
            fields['options'] = options
        return fields

    class Meta:
        model = GlobalProduct
        exclude = ['openid', 'create_time', 'update_time', 'models']
        read_only_fields = ['id']


class GlobalProductGetSerializers(serializers.ModelSerializer):
    models = serializers.SerializerMethodField('get_models')
    image = serializers.SerializerMethodField('get_image')
    image_options = serializers.SerializerMethodField('get_image_options')
    images = serializers.SerializerMethodField('get_images')

    class Meta:
        model = GlobalProduct
        exclude = ['openid', 'is_delete']
        read_only_fields = ['id', 'create_time', 'update_time']

    def get_images(self, instance: GlobalProduct):
        images = self.context['request'].query_params.get('images', None)
        if not images:
            return []
        product_images = getattr(instance, GlobalProduct.RelativeFields.PRODUCT_MEDIA).filter(media_type=Constants.MEDIA_TYPE_IMAGE).order_by('index')[:8]
        return ProductMediaGetSerializer(product_images, many=True).data

    def get_image_options(self, instance: GlobalProduct):
        images = self.context['request'].query_params.get('images_options', None)
        if not images:
            return []
        media_list = getattr(instance, GlobalProduct.RelativeFields.PRODUCT_MEDIA).filter(media_type=Constants.MEDIA_TYPE_IMAGE)
        image_options = []
        for media in media_list:
            image_options.append({
                'url': media.url,
                'id': media.id
            })
        return image_options

    def get_image(self, instance):
        if not instance.image:
            media = getattr(instance, GlobalProduct.RelativeFields.PRODUCT_MEDIA).first()
            if media:
                url = media.media.file.url
                return self.context['request'].build_absolute_uri(url)
            return None
        return instance.image

    def get_models(self, obj):
        models = self.context['request'].query_params.get('models', None)
        if not models:
            return []
        else:
            models = obj.models.all()
        return ProductModelGetSerializer(models, many=True, context={'request': self.context['request']}).data

    def get_logistic(self, instance):
        logistic = getattr(instance, GlobalProduct.RelativeFields.PRODUCT_LOGISTIC).all().first()
        if not logistic:
            return None
        return ProductLogisticGetSerializers(logistic, many=False).data

    def get_fields(self):
        fields = super().get_fields()
        spec_params = self.context['request'].query_params.get(GlobalProduct.RelativeFields.PRODUCT_SPECIFICATION, None)
        logistic_params = self.context['request'].query_params.get(GlobalProduct.RelativeFields.PRODUCT_LOGISTIC, None)
        if spec_params:
            specs = ProductSpecificationGetSerializers(source=GlobalProduct.RelativeFields.PRODUCT_SPECIFICATION, many=True)
            fields['specifications'] = specs
        if logistic_params:
            logistic = serializers.SerializerMethodField('get_logistic')
            fields['logistic'] = logistic
        return fields


class GlobalProductSerializers(serializers.ModelSerializer):

    class Meta:
        model = GlobalProduct
        exclude = []
        read_only_fields = ['id', 'create_time', 'update_time']


class ProductSupplierGetSerializers(serializers.ModelSerializer):

    class Meta:
        model = ProductSupplier
        exclude = ['openid']
        read_only_fields = ['id', 'create_time', 'update_time']


class ProductSupplierSerializers(serializers.ModelSerializer):
    class Meta:
        model = ProductSupplier
        exclude = []
        read_only_fields = ['id', 'create_time', 'update_time']


class ProductLogisticGetSerializers(serializers.ModelSerializer):

    class Meta:
        model = ProductLogistic
        exclude = ['openid']
        read_only_fields = ['id', 'create_time', 'update_time']


class ProductLogisticPostSerializers(serializers.ModelSerializer):
    class Meta:
        model = ProductLogistic
        exclude = []
        read_only_fields = ['id', 'create_time', 'update_time']


class ProductSpecificationRetriveSerializers(serializers.ModelSerializer):
    class Meta:
        model = ProductSpecification
        exclude = ['openid', 'create_time', 'update_time']
        read_only_fields = ['id']


class ProductOptionGetSerializers(serializers.ModelSerializer):
    specification = ProductSpecificationRetriveSerializers()
    # option_media = serializers.SerializerMethodField('get_media')

    # def get_media(self, option: ProductOption):
    #     from productmedia.models import ProductOptionMedia
    #     media = getattr(option, ProductOption.RelativeFields.OPTION_MEDIA).first()
    #     if not media:
    #         return None
    #     option_media = {
    #         'id': media.id,
    #         'url': media.url,
    #         'option': option.id,
    #         'media': media.media.id if media.media else None
    #     }
    #     option_media_publishes = getattr(media, ProductOptionMedia.RelativeFields.MEDIA_PUBLISH).all()
    #     media_publish = []
    #     for publish in option_media_publishes:
    #         media_publish.append({
    #             'id': publish.id,
    #             'merchant_id': publish.merchant_id,
    #             'publish_id': publish.publish_id,
    #             'publish_url': publish.publish_url,
    #             'source_url': publish.source_url
    #         })
    #     option_media['publish'] = media_publish
    #     return option_media

    class Meta:
        model = ProductOption
        exclude = ['openid', 'create_time', 'update_time', 'is_delete']
        read_only_fields = ['id']


class ProductOptionPostSerializers(serializers.ModelSerializer):
    class Meta:
        model = ProductOption
        exclude = []
        read_only_fields = ['id', 'create_time', 'update_time']


class ProductSpecificationGetSerializers(serializers.ModelSerializer):
    options = ProductOptionGetSerializers(source=ProductSpecification.RelativeFields.SPECIFICATION_OPTION, many=True)

    class Meta:
        model = ProductSpecification
        exclude = ['openid', 'create_time', 'update_time']
        read_only_fields = ['id']


class ProductSpecificationPostSerializers(serializers.ModelSerializer):
    class Meta:
        model = ProductSpecification
        exclude = []
        read_only_fields = ['id', 'create_time', 'update_time']


class ProductModelStockGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductModelStock
        exclude = ['openid', 'create_time', 'update_time']
        read_only_fields = ['id']


class ProductModelStockPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductModelStock
        exclude = []
        read_only_fields = ['id', 'create_time', 'update_time']