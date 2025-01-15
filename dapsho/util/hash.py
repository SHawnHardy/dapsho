"""
@Author     : Hengyu Shang
@License    : MIT License
"""

__all__ = ["reg_hash", "myhash"]

import hashlib
import importlib
import logging
from collections.abc import Buffer
from functools import wraps
from io import IOBase
from typing import Literal, Optional

from .register import Register

logger = logging.getLogger(__name__)

reg_hash = Register("hash")


def _dcrt_read_iobase_before_hash(func):
    @wraps(func)
    def wrapper(data: IOBase):
        if isinstance(data, IOBase):
            if not data.readable():
                raise TypeError("input data must be readable")
            data = data.read()
        return func(data=data)

    return wrapper


def _dcrt_encode_str_before_hash(func):
    @wraps(func)
    def wrapper(data: str | Buffer):
        if isinstance(data, str):
            data = data.encode()
        return func(data=data)

    return wrapper


@reg_hash
@_dcrt_read_iobase_before_hash
@_dcrt_encode_str_before_hash
def md5(data) -> str:
    return hashlib.md5(data).hexdigest()


@reg_hash
@_dcrt_read_iobase_before_hash
@_dcrt_encode_str_before_hash
def sha1(data) -> str:
    return hashlib.sha1(data).hexdigest()


@reg_hash
@_dcrt_read_iobase_before_hash
@_dcrt_encode_str_before_hash
def sha256(data) -> str:
    return hashlib.sha256(data).hexdigest()


def myhash(
    data: str | Buffer, method: Optional[Literal["md5", "sha1", "sha256"]] = None
) -> str:
    """
    Generate a hash for the given data using the specified method.

    Args:
        data (str | Buffer): The data to be hashed.
        method (Optional[Literal["md5", "sha1", "sha256"]]): The hashing method to use.
            If not provided, the default method from the configuration will be used.

    Returns:
        str: The resulting hash as a hexadecimal string.

    Raises:
        KeyError: If the specified method is not supported.
    """
    if method is None:
        method = importlib.import_module(".config", __package__).get_config(
            "hash_method"
        )

    return reg_hash[method](data)
