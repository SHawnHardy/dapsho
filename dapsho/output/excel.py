"""
@Author     : Hengyu Shang
@License    : MIT License
"""

import os
from collections.abc import Mapping, Sequence
from copy import deepcopy
from typing import Optional, overload

import pandas as pd

from ..util.config import get_config


class XlsxWriter:
    def __init__(
        self,
        path: os.PathLike,
        *,
        df: Optional[
            pd.DataFrame | list[pd.DataFrame] | dict[str, pd.DataFrame]
        ] = None,
        pandas_kwargs: Optional[dict] = None,
        default_config: Optional[dict] = None,
        special_config: Optional[dict] = None,
    ) -> None:

        self.pandas_kwargs = (
            deepcopy(pandas_kwargs) if (pandas_kwargs is not None) else {}
        )

        self.default_config = get_config("output.excel")
        if default_config is not None:
            self.default_config |= default_config
        self.special_config = (
            deepcopy(special_config) if (special_config is not None) else {}
        )

        self.writer = pd.ExcelWriter(path, engine="xlsxwriter")

        self.cell_format = {}
        self._preset_cell_format()

        self.dfs = {}
        if df is not None:
            self.load_df(df)

    def _preset_cell_format(self):
        self.cell_format["default"] = self.writer.book.add_format({"border": 1})
        self.cell_format["percent"] = self.writer.book.add_format(
            {"num_format": "0.0%", "border": 1}
        )
        self.cell_format["percent-1"] = self.writer.book.add_format(
            {"num_format": "0.0%", "border": 1}
        )
        self.cell_format["percent-2"] = self.writer.book.add_format(
            {"num_format": "0.00%", "border": 1}
        )
        self.cell_format["int"] = self.writer.book.add_format(
            {"num_format": "0", "border": 1}
        )
        self.cell_format["float"] = self.writer.book.add_format(
            {"num_format": "0.00", "border": 1}
        )
        self.cell_format["float-1"] = self.writer.book.add_format(
            {"num_format": "0.0", "border": 1}
        )
        self.cell_format["float-2"] = self.writer.book.add_format(
            {"num_format": "0.00", "border": 1}
        )

    @overload
    def load_df(self, df: pd.DataFrame): ...
    @overload
    def load_df(self, df: Sequence[pd.DataFrame] | Mapping[pd.DataFrame]): ...
    def load_df(
        self,
        df: pd.DataFrame | Sequence[pd.DataFrame] | Mapping[str, pd.DataFrame],
    ):
        if isinstance(df, pd.DataFrame):
            self.dfs = {"Sheet1": df.copy(deep=True)}
        elif isinstance(df, Sequence):
            self.dfs = {f"Sheet{i}": df[i].copy(deep=True) for i in range(len(df))}
        elif isinstance(df, dict):
            self.dfs = deepcopy(df)
        else:
            raise TypeError()

    def write(self):
        for sheet_name, df in self.dfs.items():
            df = df.copy()
            cfg = self.default_config | self.special_config.get(sheet_name, {})
            if cfg.get("reset_index", False):
                df.reset_index(inplace=True)
            if cfg.get("rename_columns"):
                df.rename(columns=cfg["rename_columns"], inplace=True)
            df.to_excel(
                self.writer,
                sheet_name=str(sheet_name),
                index=cfg.get("index", True),
                **self.pandas_kwargs,
            )
            sheet_table = self.writer.sheets[str(sheet_name)]

            for col_num, col in enumerate(df):
                if col in cfg.get("col_format", {}):
                    sheet_table.set_column(
                        col_num,
                        col_num,
                        width=cfg.get("col_width", {}).get(col, 12),
                        cell_format=self.cell_format[cfg.get("col_format", {})[col]],
                    )
                else:
                    sheet_table.set_column(
                        col_num,
                        col_num,
                        width=cfg.get("col_width", {}).get(col, 12),
                        cell_format=self.cell_format["default"],
                    )
            sheet_table.autofit()

            if cfg["autofilter"]:
                sheet_table.autofilter(0, 0, len(df.columns), len(df))

    def close(self):
        self.writer.book.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.writer.book.close()


def simple_write_xlsx(
    df: pd.DataFrame | Sequence[pd.DataFrame] | Mapping[str, pd.DataFrame],
    path: os.PathLike,
    *,
    pandas_kwargs: dict | None = None,
    default_config: dict | None = None,
    special_config: dict | None = None,
):
    with XlsxWriter(
        path=path,
        pandas_kwargs=pandas_kwargs,
        default_config=default_config,
        special_config=special_config,
    ) as writer:
        writer.load_df(df)
        writer.write()
    return path
