# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: shopee.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0cshopee.proto\x12\x06shopee\x1a\x1bgoogle/protobuf/empty.proto\"N\n\x07Product\x12\n\n\x02id\x18\x01 \x01(\x05\x12\r\n\x05store\x18\x02 \x01(\x05\x12\x12\n\nproduct_id\x18\x03 \x01(\x05\x12\x14\n\x0cproduct_name\x18\x04 \x01(\t\"\x14\n\x12ProductListRequest\"\x18\n\x16ProductRetrieveRequest\"\"\n\x0cQueryRequest\x12\x12\n\nproduct_id\x18\x01 \x01(\x05\x32\xd1\x02\n\x18ProductServiceController\x12\x37\n\x04List\x12\x1a.shopee.ProductListRequest\x1a\x0f.shopee.Product\"\x00\x30\x01\x12,\n\x06\x43reate\x12\x0f.shopee.Product\x1a\x0f.shopee.Product\"\x00\x12=\n\x08Retrieve\x12\x1e.shopee.ProductRetrieveRequest\x1a\x0f.shopee.Product\"\x00\x12,\n\x06Update\x12\x0f.shopee.Product\x1a\x0f.shopee.Product\"\x00\x12-\n\x07\x44\x65story\x12\x0f.shopee.Product\x1a\x0f.shopee.Product\"\x00\x12\x32\n\x05Query\x12\x14.shopee.QueryRequest\x1a\x0f.shopee.Product\"\x00\x30\x01\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'shopee_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _PRODUCT._serialized_start=53
  _PRODUCT._serialized_end=131
  _PRODUCTLISTREQUEST._serialized_start=133
  _PRODUCTLISTREQUEST._serialized_end=153
  _PRODUCTRETRIEVEREQUEST._serialized_start=155
  _PRODUCTRETRIEVEREQUEST._serialized_end=179
  _QUERYREQUEST._serialized_start=181
  _QUERYREQUEST._serialized_end=215
  _PRODUCTSERVICECONTROLLER._serialized_start=218
  _PRODUCTSERVICECONTROLLER._serialized_end=555
# @@protoc_insertion_point(module_scope)