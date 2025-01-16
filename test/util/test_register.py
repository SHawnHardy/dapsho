"""
@Author     : Hengyu Shang
@License    : MIT License
"""

import logging

import pytest
from semver import Version

from dapsho.util.register import Register, check_version_compatibility, parse_version


def test_parse_version():
    assert parse_version("1.0.0") == Version(1, 0, 0)
    assert parse_version([1, 0, 0]) == Version(1, 0, 0)
    assert parse_version({"major": 1, "minor": 0, "patch": 0}) == Version(1, 0, 0)
    assert parse_version(Version(1, 0, 0)) == Version(1, 0, 0)
    with pytest.raises(TypeError):
        parse_version(123)


def test_check_version_compatibility():
    assert check_version_compatibility("1.0.0", "1.0.0")
    assert check_version_compatibility("1.0.0", "1.1.0")
    assert not check_version_compatibility("1.0.0", "2.0.0")
    assert not check_version_compatibility("1.0.0-alpha", "1.0.0")
    assert check_version_compatibility("1.0.0", "1.0.1")
    assert not check_version_compatibility("0.1.0", "0.2.0")


def test_parse_version_invalid_type():
    with pytest.raises(TypeError):
        parse_version(123)


def test_register():
    register_test = Register("test")

    @register_test
    def tfoo():
        return "foo"

    @register_test
    def tbar():
        return "bar"

    assert register_test["tfoo"]() == "foo"
    assert register_test["tbar"]() == "bar"

    @register_test("tbar", version="1.0.0")
    def tbar2():
        return "bar_v2"

    assert register_test[("tbar", Version(1, 0, 0))]() == "bar_v2"

    with pytest.raises(KeyError):
        id(register_test["baz"])


def test_register_non_string_key():
    register_test = Register("test")
    with pytest.raises(TypeError):
        register_test.register(123)(lambda: "foo")


def test_register_override():
    register_test = Register("test")

    @register_test
    def tfoo():
        return "foo"

    @register_test("tfoo")
    def tfoo2():
        return "foo_override"

    assert register_test["tfoo"]() == "foo_override"


def test_register_override_warning(caplog):
    register_test = Register("test")

    @register_test
    def tfoo():
        return "foo"

    with caplog.at_level(logging.WARNING):

        @register_test("tfoo")
        def tfoo2():
            return "foo_overwritten"

    assert "will be overridden" in caplog.text


def test_get_latest():
    register_test = Register("test")

    @register_test("foo", version="1.0.0")
    def foo_v1():
        return "foo_v1"

    @register_test("foo", version="1.1.0")
    def foo_v1_1():
        return "foo_v1_1"

    @register_test("foo", version="2.0.1")
    def foo_v2():
        return "foo_v2"

    assert register_test.get_latest("foo")() == "foo_v2"
    assert register_test.get_latest("foo", compatible_with="1.0.0")() == "foo_v1_1"
    assert register_test.get_latest("foo", compatible_with="1.1.0")() == "foo_v1_1"
    with pytest.raises(KeyError):
        register_test.get_latest("foo", compatible_with="1.2.0")()
    with pytest.raises(KeyError):
        register_test.get_latest("foo", compatible_with="3.0.0")()
    with pytest.raises(KeyError):
        register_test.get_latest("foo", compatible_with="2.1.0")()
    assert register_test.get_latest("foo", compatible_with="2.0.0")() == "foo_v2"
    assert register_test.get_latest("foo", compatible_with="2.0.0")() == "foo_v2"

    with pytest.raises(KeyError):
        register_test.get_latest("bar")
