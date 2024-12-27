"""
@Author     : Hengyu Shang
@License    : MIT License
"""

import threading
from abc import ABCMeta


class SingletonMeta(type):
    """
    SingletonMeta is a metaclass that ensures a class has only one instance.
    Thread-safe.

    Methods:
        __new__(mcs, name, bases, namespace):
            Initializes the singleton instance and lock in the class namespace.

        __call__(cls, *args, **kwargs):
            Returns the singleton instance, creating it if it does not already exist.
    """

    def __new__(mcs, name, bases, namespace):
        namespace["_singleton_instance"] = None
        namespace["_singleton_lock"] = threading.Lock()
        return super().__new__(mcs, name, bases, namespace)

    def __call__(cls, *args, **kwargs):
        with cls._singleton_lock:
            if cls._singleton_instance is None:
                cls._singleton_instance = super().__call__(*args, **kwargs)
        return cls._singleton_instance


class SingletonABCMeta(ABCMeta, SingletonMeta):
    """
    SingletonABCMeta is a metaclass that combines the functionality of ABCMeta and SingletonMeta.
    """
