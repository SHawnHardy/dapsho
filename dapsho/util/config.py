"""
@Author     : Hengyu Shang
@License    : MIT License
"""

import logging
import os
import re
from contextlib import contextmanager
from copy import deepcopy
from functools import reduce
from importlib.resources import files
from pathlib import Path
from typing import Literal, Optional, Tuple

from .. import PKG_NAME
from .container import (
    StrictNestedDict,
    StrictNestedDictAcceptValueType,
    StrictNestedDictLikeType,
    StrictNestedDictValueType,
)

logger = logging.getLogger(__name__)


def load_config_from_files(
    project_config_path: Optional[os.PathLike] = None,
) -> None:
    """
    Load configuration from multiple files and merge them into a single dictionary.

    The function attempts to load configuration files from three predefined paths:
    - Package default configuration path
    - Home directory configuration path (default: ~/.config/dapsho.yaml)
    - Project directory configuration path (default: ./dapsho.yaml)

    The home and project configuration files can be ignored if the corresponding
    environment variables are set to "TRUE":
    - {PKG_NAME}_IGNORE_HOME_CONFIG
    - {PKG_NAME}_IGNORE_PROJECT_CONFIG

    !!! NOTICE: Setting "ignore_home_config" or "ignore_project_config" to "true" in the
    !!!         configuration files will not take effect.

    The configuration files are expected to be in YAML format and are loaded into
    `StrictNestedDict` objects. The configurations are then merged, with later
    configurations overriding earlier ones.

    ATTENTION: If any of the configuration files are not found, a warning
    is logged, but the function continues to process the remaining files.

    Returns:
        StrictNestedDict: A dictionary containing the merged configuration from all
        the loaded files.
    """
    cfgs = []
    for k, p in {
        "pkg default": PKG_CONFIG_PATH,
        "home": HOME_CONFIG_PATH,
        "project": (
            DEFAULT_PROJECT_CONFIG_PATH
            if project_config_path is None
            else project_config_path
        ),
    }.items():
        if (k in ("home", "project")) and (
            os.environ.get(
                f"{PKG_NAME.upper()}_IGNORE_{k.upper()}_CONFIG", "false"
            ).upper()
            == "TRUE"
        ):
            logger.debug('skip loading the %s config file from the "%s"', k, p)
            continue

        try:
            with open(p, "r", encoding="utf-8") as fp:
                logger.debug('load the %s config file from the "%s"', k, p)
                cfg = StrictNestedDict.load_yaml(fp)
                logger.debug("%s config:\n%s", k, cfg)
            cfgs.append(cfg)
        except FileNotFoundError:
            logger.warning('%s config file was not found at "%s"', k, p)

    return reduce(lambda x, y: x | y, cfgs, StrictNestedDict())


PKG_CONFIG_PATH = os.path.abspath(files("dapsho") / "config.yaml")
HOME_CONFIG_PATH = os.path.abspath(Path.home() / ".config/dapsho.yaml")
DEFAULT_PROJECT_CONFIG_PATH = os.path.abspath(Path("./dapsho.yaml"))


class DapshoConfig:
    default_config = load_config_from_files()
    explicit_config = StrictNestedDict()


def _parse_value_string(
    value: str,
    *,
    key: Optional[str] = None,
    tp_str: Optional[
        Literal[
            "bool",
            "boolean",
            "b",
            "int",
            "integer",
            "d",
            "float",
            "f",
            "str",
            "string",
            "s",
        ]
    ] = None,
    guess_type_by_key: bool = False,
    guess_type_by_content: bool = False,
) -> Tuple[str, bool | int | float | str]:
    type_symbols = (
        "bool",
        "boolean",
        "b",
        "int",
        "integer",
        "d",
        "float",
        "f",
        "str",
        "string",
        "s",
    )
    if not isinstance(value, str):
        raise TypeError(f"the value must be a string, but got {type(value)}")
    if tp_str is not None:
        match tp_str:
            case "bool" | "boolean" | "b":
                value = value.lower() == "true"
            case "int" | "integer" | "d":
                value = int(value, 0)
            case "float" | "f":
                value = float(value)
            case "str" | "string" | "s":
                value = str(value)
            case _:
                raise ValueError(f"unsupported type: {tp_str}")
        return key, value

    # by key, {name}__{symbol}
    if guess_type_by_key:

        re_match = re.match(
            r"^(?:.+?)(?:__(" + "|".join(type_symbols) + r"))?$",
            key.lower(),
        )

        if re_match is not None:
            tp_str = re_match.group(1)
            if tp_str is not None:
                return _parse_value_string(
                    value,
                    key=key[: (-(len(tp_str) + 2))],
                    tp_str=tp_str,
                )

    # by content
    if guess_type_by_content:
        if value.lower() in ("true", "false"):
            value = value.lower() == "true"
        else:
            for func in ((lambda x: int(x, 0)), float):
                try:
                    value = func(value)
                    break
                except ValueError:
                    pass
        return key, value

    return key, str(value)


def load_config_from_env(prefix: Optional[str] = None) -> StrictNestedDict:
    if prefix is None:
        prefix = PKG_NAME.lower()

    result = {}
    for k, v in os.environ.items():
        k = k.lower()
        if not k.startswith(f"{prefix}_"):
            continue
        k = k[len(prefix) + 1 :]
        k, v = _parse_value_string(
            v,
            key=k,
            tp_str=(
                None
                if (k not in DapshoConfig.default_config)
                else (type(DapshoConfig.default_config[k]).__name__)
            ),
            guess_type_by_key=True,
            guess_type_by_content=True,
        )
        result[k] = v

    return result


@staticmethod
def get_config(
    key: Optional[str] = None,
    *,
    from_explicit=True,
    from_env=True,
    from_default=True,
) -> StrictNestedDictValueType | StrictNestedDict:
    """
    Retrieve configuration value based on the provided key.

    This function first checks if the key exists in the explicit configuration
    dictionary (`DapshoConfig.explicit_config`).

    If not found, it then attempts to retrieve the value from the environment variables.
    It constructs an environment variable name by prefixing the key with
    the package name "DAPSHO_" and replacing dots with underscores.

    If the key is not found in the environment variables, it returns the value
    from the default configuration(`DapshoConfig.DEFAULT_CONFIG`).

    If no key is provided, it returns a merged dictionary of default configuration,
    environment variables, and explicit configuration.

    Args:
        key (Optional[str]): The configuration key to retrieve. If None,
        returns the entire configuration.

    Returns:
        Union[StrictNestedDict, StrictNestedDictValueType]: The configuration value
        associated with the key, or the entire configuration dictionary if no key is provided.

    Raises:
        KeyError: If the key is not found in the default configuration or environment variables.
    """
    if key is None:
        result = (
            deepcopy(DapshoConfig.default_config)
            if from_default
            else StrictNestedDict()
        )
        if from_env:
            result |= load_config_from_env()
        if from_explicit:
            result |= DapshoConfig.explicit_config
        return result

    if from_explicit:
        try:
            return DapshoConfig.explicit_config[key]
        except KeyError:
            pass
    if from_env:
        env_vars = load_config_from_env()
        try:
            return env_vars[key]
        except KeyError:
            pass
    if from_default:
        try:
            return DapshoConfig.default_config[key]
        except KeyError:
            pass
    raise KeyError(f"config key '{key}' not found")


def set_config(
    arg: Optional[StrictNestedDictLikeType] = None,
    /,
    **kwargs: StrictNestedDictAcceptValueType,
) -> None:
    DapshoConfig.explicit_config |= StrictNestedDict(arg, **kwargs)


def reset_config(reset_default: bool = False) -> None:
    DapshoConfig.explicit_config = StrictNestedDict()
    if reset_default:
        DapshoConfig.default_config = load_config_from_files()


@contextmanager
def config_context(
    arg: Optional[StrictNestedDictLikeType] = None,
    /,
    **kwargs: StrictNestedDictAcceptValueType,
):
    _config_bak = deepcopy(DapshoConfig.explicit_config)
    try:
        update = StrictNestedDict(arg, **kwargs)
        DapshoConfig.explicit_config.update(update)
        yield DapshoConfig.explicit_config
    finally:
        DapshoConfig.explicit_config = deepcopy(_config_bak)
