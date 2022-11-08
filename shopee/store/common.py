# 店铺类型
class StoreType:
    MERCHANT = 1
    SHOP = 2


# 平台类型
class PlatformType:
    SHOPEE = 1


# Store status
class StoreStatus:
    DELETE = 0
    NORMAL = 1


# 店铺产品类型
class StoreProductType:
    # 主产品
    MAIN = 1
    # 变体
    VARIANTS = 2


# 店铺产品状态
class StoreProductStatus:
    # 正常
    NORMAL = 'NORMAL'
    # 删除
    DELETED = 'DELETED'
    # 审批中
    UNLIST = 'UNLIST'
    # 禁止/审批中
    BANNED = 'BANNED'


class MediaType:
    """
    媒体类型
    """
    VIDEO = 1
    IMAGE = 2
    THUMBNAIL = 3


class PackageProductType:
    # 店铺主产品
    STORE_MAIN = 1
    # 店铺变体
    STORE_VARIANTS = 2
    # 货物
    GOODS = 3
