from abc import ABC, abstractmethod

from django.db import models
from order.models import ShopeeOrderDetailModel, ShopeeOrderModifyModel, ShopeeOrderPackageModel
from stock.services.stockprovider import StockBean
from stock.models import ProductGoodsRelations, StockRecord


class AbstractStockBeanFactory(ABC):

    @abstractmethod
    def create(self, *args, **kwargs) -> StockBean:
        pass


class AbstractModelStockBean(AbstractStockBeanFactory):

    @property
    @abstractmethod
    def stock_id(self) -> int:
        pass

    @property
    @abstractmethod
    def goods_code(self):
        pass

    @property
    @abstractmethod
    def goods_image(self):
        pass

    @property
    @abstractmethod
    def goods_id(self):
        pass


class OrderDetailStockBeanFactory(AbstractModelStockBean, AbstractStockBeanFactory):

    def __init__(self, order: ShopeeOrderDetailModel):
        self.order = order

    def create(self):
        return StockBean(
            stock_id=self.stock_id,
            goods_id=self.goods_id,
            goods_code=self.goods_code,
            goods_image=self.goods_image
        )

    @property
    def goods_code(self):
        return self.order.model_sku

    @property
    def goods_id(self):
        if self.order.stock:
            return self.order.stock.goods_id
        model_id = self.order.model_id
        goods_relation = ProductGoodsRelations.objects.filter(publish_id=model_id).first()
        return goods_relation.goods_id if goods_relation else None

    @property
    def goods_image(self):
        if self.order.stock:
            return self.order.stock.goods_image
        return self.order.image_url

    @property
    def stock_id(self):
        if self.order.stock:
            return self.order.stock.stock_id
        return None


class OrderModifyStockBeanFactory(AbstractModelStockBean, AbstractStockBeanFactory):

    def __init__(self, modify: ShopeeOrderModifyModel):
        self.modify = modify

    def create(self):
        return StockBean(
            stock_id=self.stock_id,
            goods_id=self.goods_id,
            goods_code=self.goods_code,
            goods_image=self.goods_image
        )

    @property
    def goods_code(self):
        if self.modify:
            return self.modify.global_sku
        return None

    @property
    def goods_id(self):
        stock = self.modify.stock
        if stock:
            return stock.goods_id
        return None

    @property
    def goods_image(self):
        if self.modify.stock:
            return self.modify.stock.goods_image
        return self.modify.image_url

    @property
    def stock_id(self):
        if self.modify.stock:
            return self.modify.stock.stock_id
        return None


class OrderPackageStockBeanFactory(AbstractModelStockBean, AbstractStockBeanFactory):
    def __init__(self, package: ShopeeOrderPackageModel):
        self.package = package

    def create(self):
        return StockBean(
            stock_id=self.stock_id,
            goods_id=self.goods_id,
            goods_code=self.goods_code,
            goods_image=self.goods_image
        )

    @property
    def goods_code(self):
        return self.package.sku

    @property
    def goods_id(self):
        if self.package.stock:
            return self.package.stock.goods_id
        return None

    @property
    def goods_image(self):
        if self.package.stock:
            return self.package.stock.goods_image
        return None

    @property
    def stock_id(self):
        if self.package.stock:
            return self.package.stock.stock_id
        return None
