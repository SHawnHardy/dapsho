"""
@Author     : Hengyu Shang
@License    : MIT License
"""

import logging
from collections.abc import Mapping, Sequence
from typing import Callable, Optional, override

from semver import Version

logger = logging.getLogger(__name__)

VersionLike = str | Sequence[int | str] | Mapping[str, int | str] | Version


def parse_version(version: VersionLike) -> Version:
    """
    Parse a semver string/sequence/mapping into a Version object.

    Args:
        version (Union[str, Sequence[Union[int, str]], Mapping[str, Union[int, str]]]):
            The version to parse.

    Returns:
        Version: The parsed version object.
    """
    if isinstance(version, Version):
        return version
    if isinstance(version, str):
        version = Version.parse(version, optional_minor_and_patch=True)
    elif isinstance(version, Sequence):
        version = Version(*version)
    elif isinstance(version, Mapping):
        version = Version(**version)
    else:
        raise TypeError("a valid semver must be string | tuple | list | dict")
    return version


def check_version_compatibility(need: VersionLike, have: VersionLike) -> bool:
    """
    Check if a version is compatible with another version.

    Args:
        need (Union[str, Sequence[Union[int, str]], Mapping[str, Union[int, str]]]):
            The version to check compatibility with.
        have (Union[str, Sequence[Union[int, str]], Mapping[str, Union[int, str]]]):
            The version to check compatibility against.

    Returns:
        bool: True if the versions are compatible, False otherwise.
    """
    need = parse_version(need)
    have = parse_version(have)
    if need == have:
        return True
    if (need.major == 0) or (need.major != have.major):
        return False
    if need.prerelease is not None:
        return False
    return need < have


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

    def register(self, target: Callable | str, *, version: Optional[str] = None):

        def _add_register_item(key, value, *, version):
            if not isinstance(key, str):
                raise TypeError("the key for the register must be a string")
            if not callable(value):
                raise TypeError(f"{repr(value)} is not callable!")
            if version is None:
                version = "default"
            else:
                try:
                    version = parse_version(version)
                except ValueError as e:
                    raise ValueError(
                        "the version for the registered callable object must be a valid semver"
                    ) from e

            # pylint: disable=super-with-arguments
            if key in self and version in super(Register, self).__getitem__(key):
                logger.warning("register %s: '%s' will be overridden!", self.name, key)
            self.setdefault(key, {})[version] = value
            logger.debug(
                "register %s: '%s' ver.%s has been registered", self.name, key, version
            )
            return value

        if callable(target):
            return _add_register_item(target.__name__, target, version=version)
        return lambda x: _add_register_item(target, x, version=version)

    @override
    def __getitem__(self, key):
        if isinstance(key, str):
            version = "default"
        else:
            key, version = key[0], key[1]
        if key not in self:
            raise KeyError(f"register {self.name}: '{key}' not found")
        return super().__getitem__(key)[version]

    def get_latest(
        self, key: str, *, compatible_with: Optional[VersionLike] = None
    ) -> Callable:
        """
        Get the latest registered callable for a given key,
            optionally compatible with a specific version.

        Args:
            key (str): The key for the registered callable.
            compatible_with (Optional[VersionLike]): The version to check compatibility with.

        Returns:
            Callable: The latest registered callable that is compatible with the specified version.

        Raises:
            KeyError: If the key is not found in the register.
        """
        if key not in self:
            raise KeyError(f"register {self.name}: '{key}' not found")

        versions = super().__getitem__(key).keys()

        if compatible_with is not None:
            compatible_with = parse_version(compatible_with)
            versions = filter(
                lambda x: isinstance(x, Version)
                and check_version_compatibility(compatible_with, x),
                versions,
            )
            try:
                return super().__getitem__(key)[max(versions)]
            except ValueError as e:
                raise KeyError(
                    f"register {self.name}: '{key}' ver.{compatible_with} has no compatible version"
                ) from e

        if len(versions) == 1:
            return next(iter(super().__getitem__(key).values()))

        try:
            return super().__getitem__(key)[
                max(filter(lambda x: isinstance(x, Version), versions))
            ]
        except ValueError as e:
            raise KeyError(
                f"register {self.name}: '{key}' has no registered version"
            ) from e

    def __call__(self, target: Callable | str, *, version: Optional[str] = None):
        return self.register(target, version=version)
