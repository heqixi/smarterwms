# from collections.abc import Sequence
#
# import logging
#
# from rest_framework.response import Response
# from rest_framework import viewsets
# from rest_framework.exceptions import APIException
#
# from .models import ProductEditPrice
#
# logger = logging.getLogger()


# class EditPriceView(viewsets.ModelViewSet):
#     ordering_fields = ['id', "create_time", "update_time", ]
#
#     def get_project(self):
#         try:
#             id = self.kwargs.get('pk')
#             return id
#         except:
#             return None
#
#     def get_queryset(self):
#         print("goods media get queryset")
#         id = self.get_project()
#         if self.request.user:
#             if id is None:
#                 return ProductEditPrice.objects.filter(openid=self.request.auth.openid)
#             else:
#                 return ProductEditPrice.objects.filter(openid=self.request.auth.openid, id=id)
#         else:
#             return ProductEditPrice.objects.none()
#
#     def get_serializer_class(self):
#         if self.action in ['list', 'restrieve', 'destroy']:
#             return EditPriceGetSerializer
#         elif self.action in ['create', 'update', 'create_or_update_price']:
#             return EditPricePostSerializer
#         else:
#             return self.http_method_not_allowed(request=self.request)
#
#     def create(self, request, *args, **kwargs):
#         data = self.request.data
#         if not isinstance(data, Sequence):
#             data = [data]
#         if len(data) == 0:
#             raise APIException({"detail": 'empty data'})
#         save_data = []
#         for edit_price in data:
#             serializer = EditPricePostSerializer(data=data)
#             if not serializer.is_valid():
#                 raise APIException('Illegal edit price data %s %s' % (serializer.errors, edit_price))
#             serializer.save()
#             save_data.append(serializer.data)
#         headers = self.get_success_headers("success")
#         return Response(save_data, status=200, headers=headers)
#
#     def create_or_update_price(self, request, *args, **kwargs):
#         data = self.request.data
#         logger.info('create or update price %s' % data)
#         if not isinstance(data, Sequence):
#             data = [data]
#         if len(data) == 0:
#             raise APIException({"detail": 'empty data'})
#         save_data = []
#         for edit_price in data:
#             instance_id = edit_price.get('id', None)
#             if instance_id:
#                 price_instance = ProductEditPrice.objects.get(id=instance_id)
#                 serializer = EditPricePostSerializer(price_instance, data=edit_price, partial=True)
#             else:
#                 edit_price['openid'] = self.request.auth.openid
#                 edit_price['creater'] = self.request.META.get('HTTP_OPERATOR')
#                 serializer = EditPricePostSerializer(data=edit_price)
#             if not serializer.is_valid():
#                 raise APIException('Illegal edit price data %s %s' % (serializer.errors, edit_price))
#             serializer.save()
#             save_data.append(serializer.data)
#         headers = self.get_success_headers("success")
#         return Response(save_data, status=200, headers=headers)
#
#     def update(self, request, pk):
#         pass
#
#     def partial_update(self, request, pk):
#         pass
#
#     def destroy(self, request, pk):
#         pass
