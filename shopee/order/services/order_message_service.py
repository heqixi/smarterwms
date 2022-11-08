import threading


class OrderMessageService(object):
    """
    订单消息服务，对外开放订单消息，方便及时了解订单信息
    """
    __create_key = object()
    lock = threading.RLock()
    service = None

    def __init__(self, create_key):
        assert (create_key == OrderMessageService.__create_key), \
            "StoreService objects must be created using StoreService.get_instance"

    @classmethod
    def get_instance(cls):
        if cls.service is None:
            cls.lock.acquire()
            if cls.service is None:
                cls.service = cls(OrderMessageService.__create_key)
            cls.lock.release()
            return cls.service
        return cls.service


