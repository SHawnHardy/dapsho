"""
@Author     : Hengyu Shang
@License    : MIT License
"""

import logging
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)


def flatten_index(index: pd.Index, separator: Optional[str] = "_") -> pd.Index:
    """
    Flatten a MultiIndex into a single-level Index.

    Parameters
    ----------
    index : pd.Index
        The MultiIndex object to flatten.
    separator : str or None, default '_'
        The separator to use between levels. If None, only the last level will be keeped.

    Returns
    -------
    pd.Index
        The flattened Index object.
    """
    if separator is None:
        return pd.Index([x[-1] for x in index])
    return pd.Index([separator.join([str(y) for y in x]) for x in index])
