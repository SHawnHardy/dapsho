"""
@Author     : Hengyu Shang
@License    : MIT License
"""

from copy import copy

import pytest

from dapsho.util.container import StrictNestedDict


class TestStrictNestedDict:

    def test_init(self):
        StrictNestedDict()
        StrictNestedDict({})
        StrictNestedDict({"data": "data"})
        StrictNestedDict(data="data")
        StrictNestedDict(StrictNestedDict(data="data"))

    def test_update(self):
        a = StrictNestedDict({"a": {"b": 1}})
        b = StrictNestedDict({"a": {"c": 2}})
        a.update(b)
        assert a["a.b"] == 1
        assert a["a.c"] == 2

    def test_dump(self):
        assert StrictNestedDict().dump_yaml() == "{}\n"
        assert StrictNestedDict({}).dump_yaml() == "{}\n"
        assert (
            StrictNestedDict(data="data").dump_yaml()
            == StrictNestedDict({"data": "data"}).dump_yaml()
            == StrictNestedDict(StrictNestedDict(data="data")).dump_yaml()
            == "data: data\n"
        )

    def test_load(self):
        assert (
            StrictNestedDict.load_yaml(StrictNestedDict().dump_yaml())
            == StrictNestedDict()
        )
        assert StrictNestedDict.load_yaml(
            StrictNestedDict(data="data").dump_yaml()
        ) == StrictNestedDict({"data": "data"})
        assert StrictNestedDict.load_yaml("""---""") == StrictNestedDict()

    def test_copy(self):
        with pytest.raises(
            NotImplementedError,
            match="shallow copy is not allowed for the StrictNestedDict object,"
            + " please use deepcopy instead",
        ):
            copy(StrictNestedDict())

    def test_convert_type(self):
        t = StrictNestedDict()
        t.setdefault("a", (1, 2))
        # pylint: disable=unidiomatic-typecheck
        assert type(t["a"]) is list

    def test_str(self):
        assert str(StrictNestedDict()) == "{}\n"

    def test_repr(self):
        # pylint: disable=eval-used
        assert eval(repr(StrictNestedDict({"a": 1}))) == StrictNestedDict({"a": 1})
