import datetime

from django.db import transaction

from asn.models import AsnListModel, AsnDetailModel, AsnOrder


class AsnHelper:

    @classmethod
    def amend_asn(cls, asn: AsnListModel, details):
        asn_id = asn.id
        asn_clode = asn
        asn_clode.pk = None
        asn_clode.asn_status = 1
        asn_clode.total_cost = 0
        asn.amend = True
        asn_clode.save()
        asn_origin = AsnListModel.objects.get(id=asn_id)
        asn_order = getattr(asn_origin, AsnListModel.Relative_Fields.ASN_ORDER).first()
        if asn_order:
            asn_order_clonde = asn_order
            asn_order_clonde.pk = None
            asn_order_clonde.asn = asn_clode
            asn_order.delivery_date = None
            asn_order.trans_name = ''
            asn_order.trans_url = ''
            asn_order.trans_phone = ''
            asn_order.status = 0
            asn_order.item_cost = 0
            asn_order.trans_fee = 0
            asn_order.discount = 0
            asn_order.save()
        totaol_qty = 0
        for detail_to_amend in details:
            details_origin = AsnDetailModel.objects.filter(asn_id=asn_id, id=detail_to_amend['id']).first()
            if not details_origin:
                raise Exception('Fail to clone amend asn, missing detail of id %'%detail_to_amend)
            detail_clone = details_origin
            detail_clone.pk = None
            detail_clone.asn = asn_clode
            detail_clone.goods_qty = detail_to_amend['goods_qty']
            detail_clone.goods_actual_qty = detail_to_amend['goods_qty']
            detail_clone.goods_shortage_qty = 0
            detail_clone.goods_more_qty = 0
            detail_clone.goods_damage_qty = 0
            detail_clone.goods_cost = 0
            detail_clone.sorted = False
            detail_clone.stock = None
            totaol_qty += detail_clone.goods_qty
            detail_clone.save()
        asn_clode.total_qty = totaol_qty
        asn_clode.save()
        return asn_clode