"""
@Author     : Hengyu Shang
@License    : MIT License
"""

from datetime import datetime

import pandas as pd

from dapsho.operator.dtype import norm_df_dtypes


def test_norm_df_dtypes_default():
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"], "c": [1.1, 2.2, 3.3]})
    result = norm_df_dtypes(df)
    assert result["a"].dtype == "Int64"
    assert result["b"].dtype == "string"
    assert result["c"].dtype == "Float64"

    now = datetime.now()
    df = pd.DataFrame({"a": [1, 2, 3], "b": [now, "y", "z"], "c": [1.1, 2.2, 3.3]})
    result = norm_df_dtypes(df)
    assert result["a"].dtype == "Int64"
    assert result["b"].dtype == "string"
    assert result.loc[0, "b"] == str(now)
    assert result["c"].dtype == "Float64"


def test_norm_df_dtypes_no_convert_dtypes():
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"], "c": [1.1, 2.2, 3.3]})
    result = norm_df_dtypes(df, pd_convert_dtypes=False)
    assert result["a"].dtype == "int64"
    assert result["b"].dtype == "string"
    assert result["c"].dtype == "float64"


def test_norm_df_dtypes_no_obj_to_str():
    df = pd.DataFrame(
        {"a": [1, 2, 3], "b": [datetime.today(), "y", "z"], "c": [1.1, 2.2, 3.3]}
    )
    result = norm_df_dtypes(df, obj_to_str=False)
    assert result["a"].dtype == "Int64"
    assert result["b"].dtype == "object"
    assert result["c"].dtype == "Float64"


def test_norm_df_dtypes_no_convert_dtypes_no_obj_to_str():
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"], "c": [1.1, 2.2, 3.3]})
    result = norm_df_dtypes(df, pd_convert_dtypes=False, obj_to_str=False)
    assert result["a"].dtype == "int64"
    assert result["b"].dtype == "object"
    assert result["c"].dtype == "float64"
