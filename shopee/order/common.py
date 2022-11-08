# 订单消息类型
class OrderMsgType:
    # 1: Cancel Message 取消通知
    CANCEL = 1
    # 2: Saller Remark 卖家备注 / Seller Notes 卖家笔记
    SELLER_NOTES = 2
    # 3: Shipping Forecast 发货预报
    FORECAST = 3
    # 4: Message to seller 买家备注
    MESSAGE_TO_SELLER = 4


# 订单消息标识
class OrderMsgMark:
    # 已完成
    FINISHED = 1
    # 待处理
    PENDING = 0


# 订单详情类型
class OrderModifyType:
    # 补发类型
    REISSUE = 1
    # 替换类型
    REPLACE = 2
    # 替换无变体产品类型
    REPLACE_NO_VARIANTS = 3


# 订单组合装替换类型
class OrderPackageType:
    DETAIL = 1
    MODIFY = 2


# 订单状态
class OrderStatus:
    # 已处理
    PROCESSED = 'PROCESSED'
    # 待发货
    READY_TO_SHIP = 'READY_TO_SHIP'
    # 运送中
    SHIPPED = 'SHIPPED'
    # 取消
    CANCELLED = 'CANCELLED'
    # 未支付
    UNPAID = 'UNPAID'
    # 已送达
    TO_CONFIRM_RECEIVE = 'TO_CONFIRM_RECEIVE'
    # 已完成
    COMPLETED = 'COMPLETED'
    # 申请退款/退货
    TO_RETURN = 'TO_RETURN'


# 订单处理状态
class OrderHandleStatus:
    # 忽略，用于临时状态，如在订单未支付时
    IGNORE = -3
    # 最后处理
    AT_LAST = -2
    # 缺少库存
    LACK = -1
    # 未处理
    UNPROCESSED = 0
    # 已出货
    SHIPPED = 1
    # 强制出货
    FORCED_SHIPMENT = 2
    # 部分发货
    PARTIALLY_SHIPMENT = 3


# 订单记录类型
class OrderRecordType:
    # 创建物流面单
    CREATE_SHIPPING_DOCUMENT = 1


# 产品组合状态
class PackageStatus:
    # 停止
    STOP = 0
    # 启动
    START_UP = 1
