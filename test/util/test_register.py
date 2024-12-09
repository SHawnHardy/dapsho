"""
@Author     : Hengyu Shang
@License    : MIT License
"""

import logging

import pytest

from dapsho.util.register import Register


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

    @register_test("tbar")
    def tbar2():
        return "bar_overwritten"

    assert register_test["tbar"]() == "bar_overwritten"


def test_register_non_string_key():
    register_test = Register("test")
    with pytest.raises(TypeError):
        register_test.register(123)(lambda: "foo")


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
