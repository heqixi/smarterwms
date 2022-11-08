# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: stock.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0bstock.proto\x12\x05stock\"\x88\x01\n\x05Stock\x12\n\n\x02id\x18\x01 \x01(\x05\x12\r\n\x05goods\x18\x02 \x01(\x05\x12\x11\n\tstock_qty\x18\x03 \x01(\x05\x12(\n\x0cstock_status\x18\x04 \x01(\x0e\x32\x12.stock.StockStatus\x12\x12\n\ngoods_code\x18\x05 \x01(\t\x12\x13\n\x0bgoods_image\x18\x06 \x01(\t\"}\n\x12StockUpdateRequest\x12\n\n\x02id\x18\x01 \x01(\x05\x12\r\n\x05goods\x18\x02 \x01(\x05\x12\x11\n\tstock_qty\x18\x03 \x01(\x05\x12(\n\x0cstock_status\x18\x04 \x01(\x0e\x32\x12.stock.StockStatus\x12\x0f\n\x07partial\x18\x05 \x01(\x08\"\x12\n\x10StockListRequest\"t\n\x12StockCreateRequest\x12\r\n\x05goods\x18\x01 \x01(\x05\x12\x12\n\nproduct_id\x18\x02 \x01(\x05\x12\x11\n\tstock_qty\x18\x03 \x01(\x05\x12(\n\x0cstock_status\x18\x04 \x01(\x0e\x32\x12.stock.StockStatus\"\"\n\x14StockRetrieveRequest\x12\n\n\x02id\x18\x01 \x01(\x05\"j\n\x0cQueryRequest\x12\n\n\x02id\x18\x01 \x03(\x05\x12\x10\n\x08goods_id\x18\x02 \x03(\x05\x12\x12\n\ngoods_code\x18\x03 \x03(\t\x12(\n\x0cstock_status\x18\x04 \x03(\x0e\x32\x12.stock.StockStatus\"7\n\x13StockReserveRequest\x12\x11\n\tstock_qty\x18\x01 \x01(\x05\x12\r\n\x05goods\x18\x02 \x01(\x05\"\\\n\x10StockBackRequest\x12\n\n\x02id\x18\x01 \x01(\x05\x12\x16\n\x0eto_reserve_qty\x18\x02 \x01(\x05\x12\x11\n\tto_onhand\x18\x03 \x01(\x08\x12\x11\n\tis_delete\x18\x04 \x01(\x08\"\x1e\n\x10StockShipRequest\x12\n\n\x02id\x18\x01 \x01(\x05\"\xe1\x02\n\x13StockCommonResponse\x12\x1b\n\x05stock\x18\x01 \x01(\x0b\x32\x0c.stock.Stock\x12\x31\n\x06status\x18\x02 \x01(\x0e\x32!.stock.StockCommonResponse.Status\x12-\n\x04\x63ode\x18\x03 \x01(\x0e\x32\x1f.stock.StockCommonResponse.Code\x12\x0b\n\x03msg\x18\x04 \x01(\t\"\x1f\n\x06Status\x12\x0b\n\x07SUCCESS\x10\x00\x12\x08\n\x04\x46\x41IL\x10\x01\"\x9c\x01\n\x04\x43ode\x12\n\n\x06UNKNOW\x10\x00\x12\x13\n\x0fSTOCK_NOT_FOUND\x10\x01\x12\x13\n\x0fGOODS_NOT_FOUND\x10\x02\x12\x16\n\x12ILLEGAL_PARAMETERS\x10\x03\x12\x16\n\x12MISSING_PARAMETERS\x10\x04\x12\x18\n\x14ILLEGAL_STOCK_STATUS\x10\x05\x12\x14\n\x10NOT_ENOUGH_STOCK\x10\x06*g\n\x0bStockStatus\x12\n\n\x06\x44\x41MAGE\x10\x00\x12\r\n\tPURCHASED\x10\x01\x12\n\n\x06SORTED\x10\x02\x12\n\n\x06ONHAND\x10\x03\x12\x0b\n\x07RESERVE\x10\x0b\x12\x08\n\x04SHIP\x10\x0c\x12\x0e\n\nBACK_ORDER\x10\r2\xa1\x04\n\x0fStockController\x12\x31\n\x04List\x12\x17.stock.StockListRequest\x1a\x0c.stock.Stock\"\x00\x30\x01\x12\x34\n\x06\x43reate\x12\x0c.stock.Stock\x1a\x1a.stock.StockCommonResponse\"\x00\x12\x45\n\x08Retrieve\x12\x1b.stock.StockRetrieveRequest\x1a\x1a.stock.StockCommonResponse\"\x00\x12\x34\n\x06Update\x12\x0c.stock.Stock\x1a\x1a.stock.StockCommonResponse\"\x00\x12\x35\n\x07\x44\x65stroy\x12\x0c.stock.Stock\x1a\x1a.stock.StockCommonResponse\"\x00\x12\x43\n\x07Reserve\x12\x1a.stock.StockReserveRequest\x1a\x1a.stock.StockCommonResponse\"\x00\x12=\n\x04\x42\x61\x63k\x12\x17.stock.StockBackRequest\x1a\x1a.stock.StockCommonResponse\"\x00\x12=\n\x04Ship\x12\x17.stock.StockShipRequest\x1a\x1a.stock.StockCommonResponse\"\x00\x12.\n\x05Query\x12\x13.stock.QueryRequest\x1a\x0c.stock.Stock\"\x00\x30\x01\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'stock_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _STOCKSTATUS._serialized_start=1109
  _STOCKSTATUS._serialized_end=1212
  _STOCK._serialized_start=23
  _STOCK._serialized_end=159
  _STOCKUPDATEREQUEST._serialized_start=161
  _STOCKUPDATEREQUEST._serialized_end=286
  _STOCKLISTREQUEST._serialized_start=288
  _STOCKLISTREQUEST._serialized_end=306
  _STOCKCREATEREQUEST._serialized_start=308
  _STOCKCREATEREQUEST._serialized_end=424
  _STOCKRETRIEVEREQUEST._serialized_start=426
  _STOCKRETRIEVEREQUEST._serialized_end=460
  _QUERYREQUEST._serialized_start=462
  _QUERYREQUEST._serialized_end=568
  _STOCKRESERVEREQUEST._serialized_start=570
  _STOCKRESERVEREQUEST._serialized_end=625
  _STOCKBACKREQUEST._serialized_start=627
  _STOCKBACKREQUEST._serialized_end=719
  _STOCKSHIPREQUEST._serialized_start=721
  _STOCKSHIPREQUEST._serialized_end=751
  _STOCKCOMMONRESPONSE._serialized_start=754
  _STOCKCOMMONRESPONSE._serialized_end=1107
  _STOCKCOMMONRESPONSE_STATUS._serialized_start=917
  _STOCKCOMMONRESPONSE_STATUS._serialized_end=948
  _STOCKCOMMONRESPONSE_CODE._serialized_start=951
  _STOCKCOMMONRESPONSE_CODE._serialized_end=1107
  _STOCKCONTROLLER._serialized_start=1215
  _STOCKCONTROLLER._serialized_end=1760
# @@protoc_insertion_point(module_scope)
