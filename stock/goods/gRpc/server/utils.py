from goods.gRpc.server.protos import goods_pb2
from goods.models import GoodsGroup


def goods_group_to_message(group: GoodsGroup):
    goods_list = [
        goods_pb2.Goods(id=goods.id) for goods in group.goods.all()
    ]
    return goods_pb2.GoodsGroup(
        id=group.id,
        group_name=group.name,
        goods=goods_list
    )
