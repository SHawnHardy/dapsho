"""
@Author     : Hengyu Shang
@License    : MIT License
"""

from datetime import date

import pytest

from dapsho.operator.datetime import month_add, month_range


def test_month_range_forward():
    assert list(month_range(202301, 202305)) == [202301, 202302, 202303, 202304]
    assert list(month_range(202311, 202403)) == [202311, 202312, 202401, 202402]


def test_month_range_backward():
    result = list(month_range(202305, 202301, step=-1))
    expected = [202305, 202304, 202303, 202302]
    assert result == expected
    result = list(month_range(202305, 202301, -1))
    expected = [202305, 202304, 202303, 202302]
    assert result == expected
    result = list(month_range(202301, 202211, -1))
    expected = [202301, 202212]
    assert result == expected
    result = list(month_range(202501, 202001, -12))
    expected = [202501, 202401, 202301, 202201, 202101]
    assert result == expected


def test_month_range_include_stop():
    result = list(month_range(202301, 202305, include_stop=True))
    expected = [202301, 202302, 202303, 202304, 202305]
    assert result == expected

    result = list(month_range(202301, 202305, step=3, include_stop=True))
    expected = [202301, 202304]
    assert result == expected


def test_month_range_step():
    result = list(month_range(202301, 202305, step=2))
    expected = [202301, 202303]
    assert result == expected
    result = list(month_range(202301, 202305, 2))
    expected = [202301, 202303]
    assert result == expected


def test_month_range_backward_include_stop():
    result = list(month_range(202305, 202301, step=-1, include_stop=True))
    expected = [202305, 202304, 202303, 202302, 202301]
    assert result == expected


def test_month_range_no_output_for_invalid_conditions():
    assert not list(month_range(202301, 202301))
    assert not list(month_range(202301, 202401, -1))
    assert not list(month_range(202401, 202301, 1))


def test_month_range_zero_step():
    with pytest.raises(ValueError):
        list(month_range(202301, 202305, step=0))


def test_month_range_default_stop():
    today = date.today()
    current_month = today.year * 100 + today.month
    result = list(month_range(month_add(current_month, 3)))
    expected = list(month_range(current_month, month_add(current_month, 3)))
    assert result == expected
