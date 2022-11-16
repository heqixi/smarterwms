from django.db.models import Prefetch

from base.profiler import profile


class GoodsHelper:

    # @classmethod
    # @profile("GoodsHelper:get_goods_models")
    # def get_goods_models(cls, queryset, data, openid):
    #     prefetch_models_of_goods = Prefetch(
    #         'product_relation',
    #         queryset=GlobalProductGoodsRelation.objects.filter(openid=openid, is_delete=False).prefetch_related(
    #             Prefetch(
    #                 'product',
    #                 queryset=GlobalProduct.objects.filter(openid=openid, is_delete=False).prefetch_related(
    #                     Prefetch(
    #                         'parient_products',
    #                         queryset=GlobalProduct.objects.filter(openid=openid, is_delete=False).prefetch_related(
    #                             Prefetch(
    #                                 'models',
    #                                 queryset=GlobalProduct.objects.filter(openid=openid, is_delete=False).prefetch_related(
    #                                     Prefetch(
    #                                         'goods_relation',
    #                                         queryset=GlobalProductGoodsRelation.objects.filter(openid=openid, is_delete=False).select_related('goods'),
    #                                         to_attr='relative_goods')),
    #                                 to_attr='product_models')),
    #                         to_attr='parents')),
    #                 to_attr='relative_product')),
    #         to_attr='product_relations')
    #     queryset = queryset.prefetch_related(prefetch_models_of_goods)
    #     goods_with_products = dict([(goods.id, goods) for goods in queryset.all()])
    #     for goods_dict in data:
    #         goods = goods_with_products.get(goods_dict['id'], None)
    #         if not goods:
    #             goods_dict['products'] = []
    #             continue
    #         goods_dict['products'] = cls._get_goods_product(goods)

    @classmethod
    @profile("GoodsHelper:get_goods_purchase")
    def get_goods_purchase(cls, queryset, data, request):
        raise Exception("Improper dependencies")
        # openid = request.auth.openid
        # purchase_id_filter = request.query_params.get('purchase_filter', None)
        #
        # if purchase_id_filter:
        #     prefetch_purchase_settings = PurchasePlanGoodsSetting.objects.filter(openid=openid,
        #                                                                          plan_id=purchase_id_filter)
        # else:
        #     prefetch_purchase_settings = PurchasePlanGoodsSetting.objects.filter(openid=openid,
        #                                                                          is_delete=False).order_by('level')
        # prefetch_purchase = Prefetch(
        #     'goods_purchases_settings',
        #     queryset=prefetch_purchase_settings.prefetch_related(
        #         Prefetch(
        #             'plan',
        #             queryset=PurchasePlan.objects.filter(openid=openid, is_delete=False).select_related('supplier') \
        #                 .prefetch_related(Prefetch('goods', to_attr='goods_list')),
        #             to_attr='purchase'
        #         )
        #     ),
        #     to_attr='purchase_settings'
        # )
        # queryset = queryset.prefetch_related(prefetch_purchase)
        # goods_with_products = dict([(goods.id, goods) for goods in queryset.all()])
        # for goods_dict in data:
        #     goods = goods_with_products.get(goods_dict['id'], None)
        #     if not goods or not goods.purchase_settings:
        #         goods_dict['purchases'] = []
        #         continue
        #     purchases = []
        #     purchase_settings = goods.purchase_settings
        #     for setting in purchase_settings:
        #         if not setting.purchase:
        #             continue
        #         purchase = setting.purchase
        #         purchases.append({
        #             'id': purchase.id,
        #             'goods': [goods.id for goods in purchase.goods_list],
        #             'image_url': purchase.image_url,
        #             'supplier': {
        #                 'id': purchase.supplier.id,
        #                 'supplier_name': purchase.supplier.supplier_name
        #             } if purchase.supplier else None,
        #             'price': purchase.price,
        #             'tag': purchase.tag,
        #             'level': setting.level
        #         })
        #     goods_dict['purchases'] = purchases

    @classmethod
    @profile('GoodsHelper:_get_goods_product')
    def _get_goods_product(cls, goods):
        product_relations = goods.product_relations
        if len(product_relations) <= 0:
            return []
        products = []
        for product_relation in product_relations:
            if not product_relation.relative_product:
                continue
            if not product_relation.relative_product.parents:
                continue
            main_product = product_relation.relative_product.parents[0]
            product_info = {
                'id': main_product.id,
                'sku': main_product.sku,
                'image': main_product.image,
                'goods': []
            }
            for model in main_product.product_models:
                relative_goods = model.relative_goods[0]
                goods_of_model = relative_goods.goods
                product_info['goods'].append({
                    'id': goods_of_model.id,
                    'goods_image': goods_of_model.goods_image,
                    'goods_code': goods_of_model.goods_code
                })
            products.append(product_info)
        return products
