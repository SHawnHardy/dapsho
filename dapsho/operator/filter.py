"""
@Author     : Hengyu Shang
@License    : MIT License
"""

from collections.abc import Hashable, Sequence
from typing import Literal

import pandas as pd

__all__ = [
    "find_duplicates",
]


def find_duplicates(
    df: pd.DataFrame,
    subset: Hashable | Sequence[Hashable] | None = None,
    *,
    keep: Literal["first", "last", False] = False,
    sort_values: bool = True,
    ignore_index: bool = False,
):
    """
    Identify and return duplicate rows in a copyed DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame in which to find duplicates.
    subset : Hashable or Sequence[Hashable] or None, default None
        Columns to consider when identifying duplicates. If None, all columns are used.
    keep : {'first', 'last', False}, default False
        Determines which duplicates (if any) to mark:
        - 'first' : Mark duplicates as True except for the first occurrence.
        - 'last' : Mark duplicates as True except for the last occurrence.
        - False : Mark all duplicates as True.
    sort_values : bool, default True
        If True, sort the resulting DataFrame by the subset columns.
    ignore_index : bool, default False
        If True, the resulting DataFrame will have a new RangeIndex.

    Returns
    -------
    pd.DataFrame
        A DataFrame copy containing the duplicate rows.
    """
    if df.empty:
        return df.copy(deep=None)

    result = df[df.duplicated(subset, keep=keep)].copy()
    if sort_values:
        result.sort_values(
            df.columns.tolist() if subset is None else subset,
            ignore_index=ignore_index,
            inplace=True,
        )
    else:
        if ignore_index:
            result.index = pd.RangeIndex(len(result))
    return result
