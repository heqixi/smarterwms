from abc import abstractmethod


class ProtoType(object):

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @abstractmethod
    def to_message(self):
        pass

    @abstractmethod
    def is_valid(self):
        raise NotImplementedError('Has not Implement')

    def is_not_negetive(self, *args, nullable=False):
        for field in args:
            if field is None and not nullable:
                return False
            if field and field < 0:
                return False
        return True

    def is_not_empty(self, *args, nullable=False):
        for field in args:
            if field is None and not nullable:
                return False
            if field and len(field) == 0:
                return False
        return True

