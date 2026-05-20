"""Standard split serialization."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from moltrustbench.io import write_json


def split_indices(df: pd.DataFrame, *, split_col: str = "split") -> dict[str, list[int]]:
    return {
        name: [int(value) for value in group["row_id"].tolist()]
        for name, group in df.groupby(split_col)
    }


def write_standard_split(df: pd.DataFrame, *, output_path: str | Path) -> dict:
    payload = {"split_name": "standard", "indices": split_indices(df)}
    write_json(payload, output_path)
    return payload
