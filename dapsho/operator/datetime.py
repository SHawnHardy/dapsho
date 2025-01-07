"""
@Author     : Hengyu Shang
@License    : MIT License
"""

import re
from datetime import date
from typing import Optional, overload

import pandas as pd

__all__ = [
    "month_add",
    "get_last_month",
    "get_next_month",
    "month_range",
    "convert_timedelta",
    "convert_month_str_to_int",
    "convert_month_int_to_str",
]


def month_add(month, x):
    year, month = month // 100, month % 100
    month += x - 1
    year += month // 12
    month = month % 12
    return year * 100 + month + 1


def get_last_month(month):
    return month_add(month, -1)


def get_next_month(month):
    return month_add(month, 1)


@overload
def month_range(stop: int, /, *, include_stop: bool = False): ...
@overload
def month_range(
    start: int, stop: int, /, step: int = 1, *, include_stop: bool = False
): ...
def month_range(
    start: int,
    stop: Optional[int] = None,
    /,
    step: int = 1,
    *,
    include_stop: bool = False,
):
    if step == 0:
        raise ValueError("step must be non-zero")
    if stop is None:
        today = date.today()
        start, stop = today.year * 100 + today.month, start

    while (step > 0 and start < stop) or (step < 0 and start > stop):
        yield start
        start = month_add(start, step)
    if include_stop and start == stop:
        yield stop


def convert_timedelta(delta: pd.Timedelta, unit: str = "minutes"):
    seconds = delta.days * 24 * 3600 + delta.seconds
    match unit:
        case "days" | "day" | "D":
            return seconds / (3600 * 24)
        case "hours" | "hour" | "hr" | "h":
            return seconds / (3600)
        case "minutes" | "minute" | "m":
            return seconds / (60)
        case "seconds" | "second" | "sec":
            return seconds


def convert_month_str_to_int(month_str):
    year, month = tuple(map(int, re.match(r"(\d{4})-(\d{2})", month_str).groups()))
    return year * 100 + month


def convert_month_int_to_str(month):
    year, month = month // 100, month % 100
    return f"{year:04}-{month:02}"
