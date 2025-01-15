"""
@Author     : Hengyu Shang
@License    : MIT License
"""

import pandas as pd

__all__ = [
    "norm_df_dtypes",
]


def norm_df_dtypes(
    df: pd.DataFrame,
    *,
    pd_convert_dtypes: bool = True,
    obj_to_str: bool = True,
) -> pd.DataFrame:
    """
    Normalize the data types of a pandas DataFrame.

    Parameters:
    df (pd.DataFrame): The DataFrame to normalize.
    pd_convert_dtypes (bool, default=True): If True, use pandas' convert_dtypes method
        to infer better dtypes.
    obj_to_str (bool, default=True): If True, convert columns with
        dtype 'object' to 'string'.

    Returns:
    pd.DataFrame: Copy of DataFrame with normalized data types.
    """
    df = df.copy()
    if pd_convert_dtypes:
        df = df.convert_dtypes()
    if obj_to_str:
        df = df.astype(
            {k: "string" for k, v in df.dtypes.to_dict().items() if v == "object"}
        )
    return df
