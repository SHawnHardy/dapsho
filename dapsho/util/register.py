"""
@Author     : Hengyu Shang
@License    : MIT License
"""

import logging
from typing import Callable

logger = logging.getLogger(__name__)


class Register(dict):
    """
    A dictionary-based registry class that allows for the registration of callable objects.

    Attributes:
        name (str): The name of the register.

    Methods:
        register(target):
            Registers a callable object or returns a decorator for registration.
            Args:
                target (Union[Callable, str]): The callable to register or the key for the callable.
            Returns:
                Callable: The registered callable or a decorator for registration.
            Raises:
                TypeError: If the target is not callable or the key is not a string.

        __call__(target):
            Calls the register method to register the target.
            Args:
                target (Union[Callable, str]): The callable to register or the key for the callable.
            Returns:
                Callable: The registered callable or a decorator for registration.
    """

    def __init__(self, name: str, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name

    def register(self, target: Callable | str):

        def _add_register_item(key, value):
            if not isinstance(key, str):
                raise TypeError("the key for the register must be a string")
            if not callable(value):
                raise TypeError(f"{repr(value)} is not callable!")

            if key in self:
                logger.warning("register %s: '%s' will be overridden!", self.name, key)
            self[key] = value
            logger.debug("register %s: '%s' has been registered", self.name, key)
            return value

        if callable(target):
            return _add_register_item(target.__name__, target)
        return lambda x: _add_register_item(target, x)

    def __call__(self, target: Callable | str):
        return self.register(target)
