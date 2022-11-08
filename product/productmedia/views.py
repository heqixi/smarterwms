import os
from rest_framework import viewsets
from .models import Media

from rest_framework.response import Response

from rest_framework.exceptions import APIException

from .models import ProductMedia
from productmedia import serializers


class MediaView(viewsets.ModelViewSet):
    ordering_fields = ['id', "create_time", "update_time", ]

    def get_project(self):
        try:
            id = self.kwargs.get('pk')
            return id
        except:
            return None

    def get_queryset(self):
        print("product media get queryset")
        id = self.get_project()
        if self.request.user:
            if id is None:
                return Media.objects.filter(openid=self.request.auth.openid)
            else:
                return Media.objects.filter(openid=self.request.auth.openid, id=id)
        else:
            return Media.objects.none()

    def get_serializer_class(self):
        if self.action in ['list', 'restrieve', 'destroy']:
            return serializers.MediaGetSerializer
        elif self.action in ['create', 'receivedFile']:
            return serializers.MediaPostSerializer
        elif self.action in ['update']:
            return serializers.MediaPostSerializer
        elif self.action in ['partial_update']:
            return serializers.MediaPostSerializer
        else:
            return self.http_method_not_allowed(request=self.request)

    def create(self, request, *args, **kwargs):
        openid = request.META.get('HTTP_TOKEN')
        data = self.request.data
        if data is None or len(data) == 0:
            raise APIException({"detail": 'empty data'})
        save_data = []
        for (key, value) in data.lists():
            media_byte = value[1]
            image = Media(
                file=media_byte,
                openid=openid,
                creater='admin')
            image.save()
            save_data.append({'name':key, "url": self.request.build_absolute_uri(image.file.url), 'id': image.id})
        headers = self.get_success_headers("success")
        return Response(save_data, status=200, headers=headers)

    def update(self, request, pk):
        pass

    def partial_update(self, request, pk):
        pass

    def destroy(self, request, pk):
        print("destory object ", request, ", pk", pk)
        qs = self.get_object()
        if qs.openid != self.request.auth.openid:
            raise APIException({"detail": "Cannot delete data which is not yours "})
        else:
            if qs.media and os.path.isfile(qs.media.path):
                os.remove(qs.media.path)
            deleteModel = qs.delete()
            return Response(deleteModel, status=200)

    def receivedFile(self, request, *args, **kwargs):
        raise Exception('Improper Denpendency') # TODO
        # data = self.request.data
        # if data is None or len(data) == 0:
        #     raise APIException({"detail": 'empty data'})
        # responseData = []
        # for fileName, entry in data.lists():
        #     mediaModel = GoodsMedia(
        #         media=entry[1],
        #         media_tag=entry[0],
        #         openid=self.request.auth.openid,
        #         media_type='V' if 'video' in fileName > 0 else 'M')
        #     mediaModel.save()
        #     responseData.append({'name':fileName, "url": mediaModel.media.url, 'id': mediaModel.id})
        # headers = self.get_success_headers(data=responseData)
        # return Response(responseData, status=200, headers=headers)


class APIViewSet(viewsets.ModelViewSet):
    ordering_fields = ['id', "create_time", "update_time", ]

    def get_project(self):
        try:
            id = self.kwargs.get('pk')
            return id
        except:
            return None

    def get_queryset(self):
        raise Exception('Improper Denpendency') # TODO
        print("product media get queryset")
        # id = self.get_project()
        # if self.request.user:
        #     if id is None:
        #         return GoodsMedia.objects.filter(openid=self.request.auth.openid)
        #     else:
        #         return GoodsMedia.objects.filter(openid=self.request.auth.openid, id=id)
        # else:
        #     return GoodsMedia.objects.none()

    def get_serializer_class(self):
        raise Exception('Improper Denpendency')  # TODO
        # if self.action in ['list', 'restrieve', 'destroy']:
        #     return GoodsMediaGetSerializer
        # elif self.action in ['create', 'receivedFile']:
        #     return serializers.GoodsMediaPostSerializer
        # elif self.action in ['update']:
        #     return serializers.GoodsMediaUpdateSerializer
        # elif self.action in ['partial_update']:
        #     return serializers.GoodsMediaPartialUpdateSerializer
        # else:
        #     return self.http_method_not_allowed(request=self.request)

    def create(self, request, *args, **kwargs):
        raise Exception('Improper Denpendency') # TODO
        # data = self.request.data
        # if data is None or len(data) == 0:
        #     raise APIException({"detail": 'empty data'})
        # for (key, value) in data.lists():
        #     mediaTag = value[0]
        #     mediaByte = value[1]
        #     media = GoodsMedia(
        #         media=mediaByte,
        #         media_tag=mediaTag,
        #         openid=self.request.auth.openid,
        #         media_type='V')
        #     media.save()
        #     headers = self.get_success_headers("success")
        #     return Response("success", status=200, headers=headers)

    def update(self, request, pk):
        pass

    def partial_update(self, request, pk):
        pass

    def destroy(self, request, pk):
        print("destory object ", request, ", pk", pk)
        qs = self.get_object()
        if qs.openid != self.request.auth.openid:
            raise APIException({"detail": "Cannot delete data which is not yours "})
        else:
            if qs.media and os.path.isfile(qs.media.path):
                os.remove(qs.media.path)
            deleteModel = qs.delete()
            return Response(deleteModel, status=200)

    def receivedFile(self, request, *args, **kwargs):
        raise Exception('Improper Denpendency') # TODO
        # data = self.request.data
        # if data is None or len(data) == 0:
        #     raise APIException({"detail": 'empty data'})
        # responseData = []
        # for fileName, entry in data.lists():
        #     mediaModel = GoodsMedia(
        #         media=entry[1],
        #         media_tag=entry[0],
        #         openid=self.request.auth.openid,
        #         media_type='V' if 'video' in fileName > 0 else 'M')
        #     mediaModel.save()
        #     responseData.append({'name':fileName, "url": mediaModel.media.url, 'id': mediaModel.id})
        # headers = self.get_success_headers(data=responseData)
        # return Response(responseData, status=200, headers=headers)


class ProductMediaView(viewsets.ModelViewSet):
    ordering_fields = ['id', "create_time", "update_time", ]

    def get_project(self):
        try:
            id = self.kwargs.get('pk')
            return id
        except:
            return None

    def get_queryset(self):
        print("product media get queryset")
        id = self.get_project()
        if self.request.user:
            if id is None:
                return ProductMedia.objects.filter(openid=self.request.auth.openid)
            else:
                return ProductMedia.objects.filter(openid=self.request.auth.openid, id=id)
        else:
            return ProductMedia.objects.none()

    def get_serializer_class(self):
        if self.action in ['list', 'restrieve', 'destroy']:
            return serializers.ProductMediaGetSerializer
        elif self.action in ['create', 'receivedFile']:
            return serializers.ProductMediaPostSerializer
        elif self.action in ['update']:
            return serializers.ProductMediaPostSerializer
        elif self.action in ['partial_update']:
            return serializers.ProductMediaPostSerializer
        else:
            return self.http_method_not_allowed(request=self.request)

    def create(self, request, *args, **kwargs):
        raise Exception('Improper Denpendency') # TODO
        # data = self.request.data
        # if data is None or len(data) == 0:
        #     raise APIException({"detail": 'empty data'})
        # for (key, value) in data.lists():
        #     mediaTag = value[0]
        #     mediaByte = value[1]
        #     media = GoodsMedia(
        #         media=mediaByte,
        #         media_tag=mediaTag,
        #         openid=self.request.auth.openid,
        #         media_type='V')
        #     media.save()
        #     headers = self.get_success_headers("success")
        #     return Response("success", status=200, headers=headers)

    def update(self, request, pk):
        pass

    def partial_update(self, request, pk):
        pass

    def destroy(self, request, pk):
        print("destory object ", request, ", pk", pk)
        qs = self.get_object()
        if qs.openid != self.request.auth.openid:
            raise APIException({"detail": "Cannot delete data which is not yours "})
        else:
            if qs.media and os.path.isfile(qs.media.path):
                os.remove(qs.media.path)
            deleteModel = qs.delete()
            return Response(deleteModel, status=200)

    def receivedFile(self, request, *args, **kwargs):
        data = self.request.data
        if data is None or len(data) == 0:
            raise APIException({"detail": 'empty data'})
        responseData = []
        for fileName, entry in data.lists():
            mediaModel = Media(file=entry[1])
            mediaModel.save()
            responseData.append({'name': fileName, "url": mediaModel.file.url, 'id': mediaModel.id})
        headers = self.get_success_headers(data=responseData)
        return Response(responseData, status=200, headers=headers)


