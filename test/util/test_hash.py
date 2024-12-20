"""
@Author     : Hengyu Shang
@License    : MIT License
"""

from dapsho.util import StrictNestedDict, myhash, reg_hash


def test_md5():
    assert (
        reg_hash["md5"](str(StrictNestedDict()))
        == reg_hash["md5"](StrictNestedDict().dump_yaml().encode("utf-8"))
        == "8a80554c91d9fca8acb82f023de02f11"
        != reg_hash["md5"](str(StrictNestedDict(a=1)))
    )


def test_hash():
    assert reg_hash["sha256"](StrictNestedDict().dump_yaml().encode("utf-8")) == myhash(
        StrictNestedDict().dump_yaml().encode("utf-8")
    )
