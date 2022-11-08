from rest_framework import serializers
from .models import ProductMedia, Media


class Validator():
    def mediaTypeValidator(data):
        print("product media type validating ", data)
        return data


class MediaGetSerializer(serializers.ModelSerializer):

    create_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
    update_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = Media
        exclude = ['openid']
        read_only_fields = ['id']


class MediaPostSerializer(serializers.ModelSerializer):

    create_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
    update_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = Media
        exclude = []
        read_only_fields = ['id', 'create_time', 'update_time']


class ProductMediaGetSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField('get_url')

    def get_url(self, instance):
        request = self.context.get('request')
        if instance.url:
            return instance.url
        if not instance.media or not instance.media.file:
            return None
        return request.build_absolute_uri(instance.media.file.url)

    class Meta:
        model = ProductMedia
        exclude = ['openid', 'create_time', 'update_time', 'is_delete']
        read_only_fields = ['id']


class ProductMediaPostSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductMedia
        exclude = []
        read_only_fields = ['id', 'create_time', 'update_time', ]




