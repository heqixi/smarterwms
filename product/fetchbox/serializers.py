
from rest_framework import serializers

from fetchbox.common import MediaType
from fetchbox.models import FetchProductModel, FetchMediaModel, FetchOptionModel, FetchOptionItemModel, \
    FetchVariantModel, ShopeeRegionSettingsModel, ShopeeStoreRegionSetting
from utils import spg


class FetchProductGetSerializer(serializers.ModelSerializer):

    size = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        media = FetchMediaModel.objects.filter(product=obj, is_main=1, type=MediaType.IMAGE).first()
        if media:
            return media.url
        return None

    def get_size(self, obj):
        if obj.length and obj.width and obj.height:
            return "%s * %s * %s" % (obj.length, obj.width, obj.height)
        return None

    class Meta:
        model = FetchProductModel
        exclude = ['openid', 'is_delete', 'create_time', 'creater']
        read_only_fields = ['id']


class FetchProductDetailsSerializer(serializers.ModelSerializer):
    """
    采集产品的所有详细信息
    """
    medias = serializers.SerializerMethodField()
    options = serializers.SerializerMethodField()
    option_items = serializers.SerializerMethodField()
    variants = serializers.SerializerMethodField()

    def get_variants(self, obj):
        return spg.django_model_to_dict(model_list=obj.fetch_product_variants.all())

    def get_option_items(self, obj):
        return spg.django_model_to_dict(model_list=obj.fetch_product_option_items.all())

    def get_options(self, obj):
        return spg.django_model_to_dict(model_list=obj.fetch_product_options.all())

    def get_medias(self, obj):
        return spg.django_model_to_dict(model_list=obj.fetch_product_medias.all())

    class Meta:
        model = FetchProductModel
        exclude = ['openid', 'is_delete', 'create_time', 'creater']
        read_only_fields = ['id']