"""
@Author     : Hengyu Shang
@License    : MIT License
"""

import re
from collections.abc import Iterable, Mapping, MutableMapping, Sequence
from copy import deepcopy
from datetime import date, datetime
from itertools import repeat
from typing import (
    Iterator,
    Optional,
    Protocol,
    Self,
    TypeVar,
    Union,
    overload,
    override,
    runtime_checkable,
)

import yaml

try:
    from yaml import CSafeDumper as SafeDumper
    from yaml import CSafeLoader as SafeLoader
except ImportError:
    from yaml import SafeDumper, SafeLoader

from .hash import myhash

_KtT = TypeVar("_KtT")
_VtT_co = TypeVar("_VtT_co", covariant=True)


@runtime_checkable
class SupportsKeysAndGetItem(Protocol[_KtT, _VtT_co]):
    def keys(self) -> Iterable[_KtT]: ...
    def __getitem__(self, key: _KtT, /) -> _VtT_co: ...


StrictNestedDictAcceptValueType = Union[
    str, bool, int, float, date, datetime, Sequence, Mapping
]
StrictNestedDictValueType = Union[
    str, bool, int, float, date, datetime, list, "StrictNestedDict"
]
StrictNestedDictLikeType = Union[
    SupportsKeysAndGetItem[str, StrictNestedDictAcceptValueType],
    Iterable[tuple[str, StrictNestedDictAcceptValueType]],
    "StrictNestedDict",
    None,
]


class StrictNestedDict(MutableMapping):
    """
    StrictNestedDict is a custom dictionary-like class that enforces strict key and value types,
    supports nested keys, and provides additional functionalities such as YAML serialization.

    Attributes:
        __NESTED_KEY_PATTERN (str): A regex pattern for validating nested keys.

    Methods:
        __init__(*args, **kwargs):
            Initializes the StrictNestedDict with optional initial data.

        assert_key_is_valid(key: str) -> str:
            Validates that the key is a string matching the required pattern.

        convert_type(x: StrictNestedDictAcceptValueType) -> StrictNestedDictValueType:
            Converts the input value to an acceptable type for the dictionary.

        fromkeys(iterable: Iterable[str], value: Optional[StrictNestedDictAcceptValueType] = None)
                -> Self:
            Creates a new StrictNestedDict with keys from the given iterable and a common value.

        to_dict() -> dict[str, StrictNestedDictValueType]:
            Converts the StrictNestedDict to a regular dictionary.

        __delitem__(key: str) -> None:
            Deletes the item with the specified key.

        __getitem__(key: str) -> StrictNestedDictValueType:
            Retrieves the value associated with the specified key, supporting nested keys.

        __iter__() -> Iterator[str]:
            Returns an iterator over the keys of the dictionary.

        __len__() -> int:
            Returns the number of items in the dictionary.

        __setitem__(key: str, value: StrictNestedDictAcceptValueType) -> None:
            Sets the value for the specified key, converting the value to an acceptable type.

        __eq__(other: StrictNestedDictLikeType) -> bool:
            Checks equality with another StrictNestedDict-like object.

        update(other: Optional[StrictNestedDictLikeType] = None,
                **kwargs: StrictNestedDictAcceptValueType) -> None:
            Updates the dictionary with the key-value pairs from another dictionary or iterable.

        __or__(value: StrictNestedDictLikeType) -> Self:
            Returns a new StrictNestedDict that is the union of the current dictionary and another.

        __ior__(value: StrictNestedDictLikeType) -> Self:
            Updates the current dictionary with the union of itself and another.

        __copy__():
            Raises NotImplementedError as shallow copy is not allowed.

        dump_yaml(stream=None, **kwargs) -> bytes | str | None:
            Serializes the dictionary to a YAML formatted string or stream.

        load_yaml(stream) -> Self:
            Deserializes a YAML formatted string or stream to a StrictNestedDict.

        __str__() -> str:
            Returns a YAML formatted string representation of the dictionary.

        __repr__() -> str:
            Returns a string representation of the dictionary for debugging.

        # Methods inherited from MutableMapping and Mapping
        clear() -> None:
            Removes all items from the dictionary.

        get(key: str, default: Optional[StrictNestedDictValueType] = None)
                -> StrictNestedDictValueType:
            Returns the value for the specified key if key is in the dictionary, else default.

        items() -> Iterable[tuple[str, StrictNestedDictValueType]]:
            Returns a set-like object providing a view on the dictionary's items.

        keys() -> Iterable[str]:
            Returns a set-like object providing a view on the dictionary's keys.

        pop(key: str, default: Optional[StrictNestedDictValueType] = None)
                -> StrictNestedDictValueType:
            Removes the specified key and returns the corresponding value.
            If key is not found, default is returned if given, otherwise KeyError is raised.

        popitem() -> tuple[str, StrictNestedDictValueType]:
            Removes and returns a (key, value) pair from the dictionary.
            Pairs are returned in LIFO (last-in, first-out) order.

        setdefault(key: str, default: Optional[StrictNestedDictValueType] = None)
                -> StrictNestedDictValueType:
            Inserts key with a value of default if key is not in the dictionary.
            Returns the value for key if key is in the dictionary, else default.

        values() -> Iterable[StrictNestedDictValueType]:
            Returns an object providing a view on the dictionary's values.
    """

    __NESTED_KEY_PATTERN = (
        r"([a-zA-Z_][a-zA-Z0-9_]*)(?:\[(\d+)\])?(?:\.([a-zA-Z_][a-zA-Z0-9_\[\]\.]*))?$"
    )

    @overload
    def __init__(self) -> None: ...
    @overload
    def __init__(self, **kwargs: StrictNestedDictAcceptValueType) -> None: ...
    @overload
    def __init__(
        self,
        map_: SupportsKeysAndGetItem[str, StrictNestedDictAcceptValueType],
        /,
        **kwargs: StrictNestedDictAcceptValueType,
    ) -> None: ...
    @overload
    def __init__(
        self,
        iterable: Iterable[tuple[str, StrictNestedDictAcceptValueType]],
        /,
        **kwargs: StrictNestedDictAcceptValueType,
    ) -> None: ...
    def __init__(self, arg=None, /, **kwargs) -> None:
        if arg is None:
            arg = ()
        self.__data = {
            self.assert_key_is_valid(k): self.convert_type(v)
            for k, v in dict(arg, **kwargs).items()
        }

    @classmethod
    def assert_key_is_valid(cls, key: str) -> str:
        if type(key) is not str:  # pylint: disable=unidiomatic-typecheck
            raise TypeError(
                f'StrictNestedDict key must be str, but "{repr(key)}" was received'
            )
        if not re.match(r"[a-zA-Z_][a-zA-Z0-9_]*", key):
            raise ValueError(
                "StrictNestedDict key must be [a-zA-Z_][a-zA-Z0-9_]+, "
                + f'but "{repr(key)}" was received'
            )
        return key

    @classmethod
    def convert_type(
        cls, x: StrictNestedDictAcceptValueType
    ) -> StrictNestedDictValueType:
        if x is None:
            return x
        if type(x) in (str, bool, int, float):
            return x
        if type(x) in (date, datetime):
            return deepcopy(x)
        if isinstance(x, Sequence):
            return [cls.convert_type(y) for y in x]
        if isinstance(x, Mapping):
            return cls(
                {cls.assert_key_is_valid(k): cls.convert_type(v) for k, v in x.items()}
            )
        raise TypeError(
            "StrictDict value must be one of the following types: (str, bool, int, float, None, "
            + "datetime.date, datetime.datetime, Sequence, Mapping), but "
            f'"{x.__repr__}" was received'
        )

    @classmethod
    def fromkeys(
        cls,
        iterable: Iterable[str],
        value: Optional[StrictNestedDictAcceptValueType] = None,
    ) -> Self:
        return cls(zip(iterable, repeat(value)))

    def to_dict(self) -> dict[str, StrictNestedDictValueType]:
        return {
            k: (v.to_dict() if isinstance(v, self.__class__) else v)
            for k, v in self.items()
        }

    @override
    def __delitem__(self, key: str) -> None:
        return self.__data.__delitem__(key)

    @override
    def __getitem__(self, key: str) -> StrictNestedDictValueType:
        direct_key, seq_idx, left = re.match(self.__NESTED_KEY_PATTERN, key).groups()
        result = self.__data.__getitem__(direct_key)
        if seq_idx is not None:
            result = result[int(seq_idx)]
        if left is not None:
            return result.__getitem__(left)
        return result

    @override
    def __iter__(self) -> Iterator[str]:
        return self.__data.__iter__()

    @override
    def __len__(self) -> int:
        return self.__data.__len__()

    @override
    def __setitem__(self, key: str, value: StrictNestedDictAcceptValueType) -> None:
        return self.__data.__setitem__(
            self.assert_key_is_valid(key), self.convert_type(value)
        )

    @override
    def __eq__(self, other: StrictNestedDictLikeType) -> bool:
        return super().__eq__(self.__class__(other))

    def update(
        self,
        other: Optional[StrictNestedDictLikeType] = None,
        /,
        **kwargs: StrictNestedDictAcceptValueType,
    ) -> None:
        if other is None:
            other = ()
        if not isinstance(other, self.__class__):
            other = self.__class__(other, **kwargs)
        for k, v in other.items():
            if (k in self) and (
                isinstance(v, self.__class__) and isinstance(self[k], self.__class__)
            ):
                self[k].update(v)
            else:
                self[k] = v

    def __or__(self, value: StrictNestedDictLikeType, /) -> Self:
        tmp = deepcopy(self)
        tmp.update(value)
        return tmp

    def __ior__(
        self,
        value: StrictNestedDictLikeType,
        /,
    ) -> Self:
        self.update(value)
        return self

    def __copy__(self):
        raise NotImplementedError(
            "shallow copy is not allowed for the StrictNestedDict object,"
            + " please use deepcopy instead"
        )

    def dump_yaml(self, stream=None, **kwargs) -> bytes | str | None:
        return yaml.dump(self.to_dict(), stream=stream, Dumper=SafeDumper, **kwargs)

    @classmethod
    def load_yaml(cls, stream) -> Self:
        return cls(yaml.load(stream, SafeLoader))

    def __str__(self) -> str:
        return self.dump_yaml()

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__
        return f"{cls_name}({cls_name}.load_yaml('''{self.dump_yaml()}'''))"

    def get_hash(self):
        return myhash(self.dump_yaml())
