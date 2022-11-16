
from google.protobuf import empty_pb2

from stock.models import StockListModel
from goods.models import ListModel as Goods
from django_grpc_framework import generics
from stock.gRpc.servers.serializers.StockSerializer import StockSerializer
from stock.services.stockprovider import StockService as StockProvider
from stock.gRpc.servers.utils.Utils import status_from_proto, stock_model_to_message
from stock.gRpc.servers.types.response import Success, StockNotFoundError,\
    GoodsNotFoundError, UnknowError, IllegalParametersError, MissingParametersError, IllegelStockStatusError, NotEnoughStockError


class StockService(generics.ModelService):
    """
    gRPC service that allows users to be retrieved or updated.
    """
    print('StockBinService in ')
    queryset = StockListModel.objects.all().order_by('-id')
    serializer_class = StockSerializer

    def Create(self, request, context):
        print('create stock ', request)
        openid = 'd8ee5135188748805e32f3db8e64fbdf'
        creater = 'admin'
        goods_id = request.goods
        stock_qty = request.stock_qty
        if stock_qty is None:
            return MissingParametersError('Missing parameter stock').to_proto()
        if stock_qty <= 0:
            return IllegalParametersError('Illegal parameter stock_qty %s' % stock_qty).to_proto()
        stock_status = request.stock_status
        if stock_status is None:
            return MissingParametersError('Missing parameter stock_status').to_proto()

        # find or create goods: we retrieve goods by goods_id or goods_code.
        # If not found, create a new goods by given goods_code and goods_image
        if not goods_id:
            if not (request.goods_code and request.goods_image):
                return MissingParametersError('Missing parameter goods').to_proto()
            goods = Goods.objects.filter(goods_code=request.goods_code).first()
            if not goods:
                goods = Goods.objects.create(
                    openid=openid,
                    creater=creater,
                    goods_code=request.goods_code,
                    goods_image=request.goods_image
                )
        else:
            goods = Goods.objects.filter(id=goods_id).first()
        if not goods:
            return GoodsNotFoundError('Goods of id not found %s ' % goods_id).to_proto()
        stock_status = status_from_proto(stock_status)
        if stock_status in [StockListModel.Constants.STATUS_ONHAND, StockListModel.Constants.STATUS_DAMAGE]:
            stock = self._create_or_add_stock(stock_qty, goods, stock_status)
        else:
            stock = StockListModel(
                openid='d8ee5135188748805e32f3db8e64fbdf',
                creater='admin',
                goods=goods,
                stock_status=stock_status,
                stock_qty=stock_qty
            )
        stock.save()
        return Success(stock).to_proto()

    def Update(self, request, context):
        stock_id = request.id
        if not stock_id:
            return MissingParametersError('Missing stock id').to_proto()
        stock_obj = StockListModel.objects.filter(id=stock_id, is_delete=False).first()
        if not stock_obj:
            return StockNotFoundError('Stock of id %s not found' % stock_id).to_proto()
        data = {}
        if request.goods:
            goods = Goods.objects.filter(id=request.goods).first()
            if not goods:
                return GoodsNotFoundError('Fail to update stock, goods of id %s not found' % request.goods)
            data['goods'] = goods
        if request.stock_qty:
            data['stock_qty'] = request.stock_qty
        if request.stock_status:
            data['stock_status'] = status_from_proto(request.stock_status)
        if len(data) == 0:
            return MissingParametersError('Empty stock data').to_proto()
        try:
            print('goods of stock ', stock_obj.goods.goods_code)
            stock_obj.goods = data.get('goods', stock_obj.goods)
            stock_obj.stock_qty = data.get('stock_qty', stock_obj.stock_qty)
            stock_obj.stock_status = data.get('stock_status', stock_obj.stock_status)
            stock_obj.save()
            print('goods of stock ', stock_obj.goods, stock_obj.goods.goods_code)
        except Exception as e:
            return UnknowError(str(e)).to_proto()
        else:
            return Success(stock_obj).to_proto()

    def Reserve(self, request, context):
        print('reserve stock')
        stock_qty = request.stock_qty
        if stock_qty is None or stock_qty <= 0:
            print('Fail to reserve stock, qty must positive')
            return IllegalParametersError('Illegal stock qty %s' % stock_qty)
        goods_id = request.goods
        if not goods_id:
            return MissingParametersError('Missing param goods').to_proto()
        goods = Goods.objects.filter(id=goods_id).first()
        if not goods:
            return GoodsNotFoundError('Goods of id %s not found' % goods_id).to_proto()
        try:
            stock = StockProvider.get_instance().reserve_goods_stock(stock_qty, goods)
        except Exception as e:
            return UnknowError(str(e)).to_proto()
        else:
            return Success(stock).to_proto()

    def Back(self, request, context):
        instance = self.get_object()
        if not instance:
            return StockNotFoundError('Stock not found!')

        to_reserve_qty = request.to_reserve_qty
        to_onhand_qty = request.to_onhand_qty
        print('Back stock to onhand ', to_onhand_qty)
        is_delete = request.is_delete
        try:
            StockProvider.get_instance().back_stock(instance, to_reserve_qty, to_onhand_qty, is_delete)
        except Exception as e:
            return UnknowError(str(e))
        else:
            return Success(instance).to_proto()

    def Ship(self, request, context):
        instance = self.get_object()
        if not instance:
            return StockNotFoundError().to_proto()
        if instance.stock_status == StockListModel.Constants.STATUS_SHIP:
            return Success(instance).to_proto()
        if instance.stock_status != StockListModel.Constants.STATUS_RESERVE:
            return IllegelStockStatusError('Only stock of status reserve can be ship').to_proto()
        stock_on_hand = StockListModel.objects.filter(goods=instance.goods,
                                                      stock_status=StockListModel.Constants.STATUS_ONHAND).first()
        if not stock_on_hand or stock_on_hand.stock_qty < instance.stock_qty:
            return NotEnoughStockError('Not enough stock to ship').to_proto()
        stock_on_hand.stock_qty -= instance.stock_qty
        stock_on_hand.save()
        instance.stock_status = StockListModel.Constants.STATUS_SHIP
        instance.save()
        return Success(instance).to_proto()

    def Destroy(self, request, context):
        stock_id = request.id
        if stock_id is None:
            return MissingParametersError('Missing stock id').to_proto()
        stock_obj = StockListModel.objects.filter(id=stock_id).first()
        if not stock_obj:
            return StockNotFoundError('Stock of id %s no found' % stock_id)
        try:
            stock_obj.delete()
        except Exception as exec:
            return UnknowError('Delete stock fail, msg: %s' % str(exec))
        return Success(stock_obj).to_proto()

    def Retrieve(self, request, context):
        stock_id = request.id
        if not stock_id:
            return MissingParametersError('Missing stock id')
        stock_obj = StockListModel.objects.filter(id=stock_id).first()
        if not stock_obj:
            return StockNotFoundError('Stock of id %s not found' % stock_id)
        return Success(stock_obj).to_proto()

    def Query(self, request, context):
        queryset = StockListModel.objects.none()
        if request.id:
            queryset |= StockListModel.objects.filter(id__in=request.id)
        goods_id = []
        if request.goods_code:
            goods_id += Goods.objects.filter(goods_code__in=request.goods_code)
        if request.goods_id:
            goods_id += request.goods_id
        if goods_id:
            queryset |= StockListModel.objects.filter(goods_id__in=goods_id)
        if request.stock_status:
            queryset = queryset.filter(stock_status__in=request.stock_status)
        if not queryset.exists():
            return empty_pb2.Empty()
        for stock in queryset.all():
            yield stock_model_to_message(stock)

    def _create_or_add_stock(self, stock_qty, goods, stock_status):
        stock = StockListModel.objects.filter(goods=goods, stock_status=stock_status).first()
        if not stock:
            stock = StockListModel(
                openid='c240c14ea66ef48bc3c5645735a715af',
                creater='admin',
                goods=goods,
                stock_status=StockListModel.Constants.STATUS_ONHAND,
                stock_qty=stock_qty
            )
        else:
            stock.stock_qty += stock_qty
        return stock

