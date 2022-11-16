from rest_framework import serializers
from .models import ListModel, Media
from utils import datasolve


class Validator():
    def mediaTypeValidator(data):
        print("goods media type validating ", data)
        return data


class GoodsMediaGetSerializer(serializers.ModelSerializer):
    url = serializers.CharField(read_only=True, required=False)
    media_type = serializers.CharField(read_only=True, required=False)
    media_tag = serializers.CharField(read_only=True, required=False)
    media_desc = serializers.CharField(read_only=True, required=False)
    relative_goods_id = serializers.PrimaryKeyRelatedField(read_only=True)
    create_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
    update_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
    class Meta:
        model = ListModel
        exclude = ['openid']
        read_only_fields = ['id']


class GoodsMediaPostSerializer(serializers.ModelSerializer):
    media = serializers.FileField(max_length=1024, allow_empty_file=False)
    media_type = serializers.CharField(read_only=False, required=True, validators=[datasolve.data_validate, Validator.mediaTypeValidator])
    media_tag = serializers.CharField(read_only=False, required=False)
    openid = serializers.CharField(read_only=False, required=False, validators=[datasolve.openid_validate])
    class Meta:
        model = ListModel
        fields  = ['media', 'media_type', 'media_tag', 'openid']
        read_only_fields = ['id', 'create_time', 'update_time', ]


class GoodsMediaUpdateSerializer(serializers.ModelSerializer):
    parents_class_id = serializers.CharField(read_only=False, required=False, validators=[datasolve.data_validate])
    goods_class = serializers.CharField(read_only=False, required=True, validators=[datasolve.data_validate])
    creater = serializers.CharField(read_only=False, required=True, validators=[datasolve.data_validate])

    class Meta:
        model = ListModel
        exclude = ['openid', 'is_delete', ]
        read_only_fields = ['id', 'create_time', 'update_time', ]


class GoodsMediaPartialUpdateSerializer(serializers.ModelSerializer):
    parents_class_id = serializers.CharField(read_only=False, required=False, validators=[datasolve.data_validate])
    goods_class = serializers.CharField(read_only=False, required=False, validators=[datasolve.data_validate])
    creater = serializers.CharField(read_only=False, required=False, validators=[datasolve.data_validate])
    class Meta:
        model = ListModel
        exclude = ['openid', 'is_delete', ]
        read_only_fields = ['id', 'create_time', 'update_time', ]


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



