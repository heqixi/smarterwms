
from stock.models import StockListModel
from stock.gRpc.servers.protos.stock import stock_pb2


def status_to_proto(status: int):
    if status == StockListModel.Constants.STATUS_DAMAGE:
        return stock_pb2.StockStatus.DAMAGE
    elif status == StockListModel.Constants.STATUS_PURCHASED:
        return stock_pb2.StockStatus.PURCHASED
    elif status == StockListModel.Constants.STATUS_SORTED:
        return stock_pb2.StockStatus.SORTED
    elif status == StockListModel.Constants.STATUS_ONHAND:
        return stock_pb2.StockStatus.ONHAND
    elif status == StockListModel.Constants.STATUS_RESERVE:
        return stock_pb2.StockStatus.RESERVE
    elif status == StockListModel.Constants.STATUS_SHIP:
        return stock_pb2.StockStatus.SHIP
    elif status == StockListModel.Constants.STATUS_BACK_ORDER:
        return stock_pb2.StockStatus.BACK_ORDER
    else:
        raise Exception('Unknow model stock status %s'%status)


def status_from_proto(status: stock_pb2.StockStatus):
    if status == stock_pb2.StockStatus.DAMAGE:
        return status == StockListModel.Constants.STATUS_DAMAGE
    elif status == stock_pb2.StockStatus.PURCHASED:
        return StockListModel.Constants.STATUS_PURCHASED
    elif status == stock_pb2.StockStatus.SORTED:
        return StockListModel.Constants.STATUS_SORTED
    elif status == stock_pb2.StockStatus.ONHAND:
        return StockListModel.Constants.STATUS_ONHAND
    elif status == stock_pb2.StockStatus.RESERVE:
        return StockListModel.Constants.STATUS_RESERVE
    elif status == stock_pb2.StockStatus.SHIP:
        return StockListModel.Constants.STATUS_SHIP
    elif stock_pb2.StockStatus.BACK_ORDER:
        return StockListModel.Constants.STATUS_BACK_ORDER
    else:
        raise Exception('Fail to parse proto stock stauts %s' % status)


def stock_model_to_message(stock: StockListModel):
    goods = stock.goods
    return stock_pb2.Stock(
        id=stock.id,
        goods=stock.goods.id,
        stock_qty=stock.stock_qty,
        stock_status=status_to_proto(stock.stock_status),
        goods_code=goods.goods_code,
        goods_image=goods.goods_image
    ) if stock and goods else None