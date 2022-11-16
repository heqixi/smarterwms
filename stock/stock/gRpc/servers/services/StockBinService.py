from stock.models import StockBinModel
from django_grpc_framework import generics
from stock.gRpc.servers.serializers.StockBinSerializer import StockBinSerializer


class StockBinService(generics.ModelService):
    """
    gRPC service that allows users to be retrieved or updated.
    """
    print('StockBinService in')
    queryset = StockBinModel.objects.all().order_by('-id')
    serializer_class = StockBinSerializer


