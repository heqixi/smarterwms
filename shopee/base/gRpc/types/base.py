from abc import abstractmethod
from abc import ABC
import functools


class MessageEncoder(object):

    @abstractmethod
    def to_message(self):
        pass


class MessageDecoder(object):

    @abstractmethod
    def from_message(self, *args):
        pass


class Verifiable(object):
    msg: str

    @abstractmethod
    def is_valid(self, raise_exception=False):
        pass

    def not_empty(self, *args, nullable=False):
        for field in args:
            if field is None:
                if not nullable:
                    return False
            elif len(field) == 0:
                return False
        return True

    def not_negative(self, *args, nullable=False):
        for field in args:
            if field is None and not nullable:
                return False
            if field is not None and field < 0:
                return False
        return True


def non_empty(name, nullable=False):
    def inner(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            val = func(*args, **kwargs)
            if not nullable and val is None:
                raise Exception('%s must be not be none' % name)
            if val is not None and len(val) <= 0:
                raise Exception('%s must be not empty %s' % (name, val))
            return val
        return wrapper
    return inner


def non_negative(name, nullable=False):
    def inner(func):
        @functools.wraps(func)
        def getter(*args, **kwargs):
            val = func(*args, **kwargs)
            if not nullable and val is None:
                raise Exception('%s must be not be none' % name)
            if val is not None and val < 0:
                raise Exception('%s must be not negative %s' % (name, val))
            return val
        return getter
    return inner


class ResponseResolver(object):

    @abstractmethod
    def success(self):
        pass

    @abstractmethod
    def code(self):
        pass

    @abstractmethod
    def msg(self):
        pass


def not_empty(*args, nullable=False):
    for field in args:
        if field is None and not nullable:
            return False, field
        if field and len(field) == 0:
            return False, field
    return True, None


def not_negetive(*args, nullable=False):
    for field in args:
        if field is None and not nullable:
            return False, field
        if field is not None and field < 0:
            return False, field
    return True, None


def all_empty(*args):
    for field in args:
        if field and len(field) > 0:
            return False
    return True


class ProtoType(MessageEncoder, ABC):

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @abstractmethod
    def is_valid(self):
        raise NotImplementedError('Has not Implement')

    @abstractmethod
    def from_message(self, *args):
        raise NotImplementedError('Not Implement')

    def is_not_negetive(self, *args, nullable=False):
        for field in args:
            if field is None and not nullable:
                return False
            if field is not None and field < 0:
                return False
        return True

    def is_not_empty(self, *args, nullable=False):
        for field in args:
            if field is None and not nullable:
                return False
            if field and len(field) == 0:
                return False
        return True

    def is_not_all_empty(self, *args):
        for field in args:
            if field and len(field) > 0:
                return True
        return False

