from abc import abstractmethod, ABC


class RequestVerifier(object):

    @abstractmethod
    def is_valid(self):
        pass

    @abstractmethod
    def code(self):
        pass

    @abstractmethod
    def msg(self):
        pass


class MessageDecoder(object):

    @abstractmethod
    def save(self, *args):
        pass


class MessageEncoder(object):

    @abstractmethod
    def encode(self, *args):
        pass


class Verifiable(object):

    @abstractmethod
    def is_valid(self, raise_exception=False):
        pass

    def not_empty(self, *args, nullable=False):
        for field in args:
            if field is None and not nullable:
                return False
            if field and len(field) == 0:
                return False, field
        return True

    def not_negative(self, *args, nullable=False):
        for field in args:
            if field is None and not nullable:
                return False
            if field is not None and field < 0:
                return False
        return True


class ProtoType(object):

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @abstractmethod
    def is_valid(self):
        raise NotImplementedError('Has not Implement')


    @abstractmethod
    def to_proto_obj(self):
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

