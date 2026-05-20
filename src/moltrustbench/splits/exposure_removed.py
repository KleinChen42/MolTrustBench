"""Exposure-removed split construction."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from moltrustbench.io import write_json


def exact_removed_split(df: pd.DataFrame) -> dict[str, list[int]]:
    train = df[df["split"].isin(["train", "valid", "validation"])]["row_id"].astype(int).tolist()
    test = df[(df["split"] == "test") & (~df["exact_exposed"].fillna(False))]["row_id"].astype(int).tolist()
    return {"train": train, "test": test}


def write_exact_removed_split(df: pd.DataFrame, *, output_path: str | Path) -> dict:
    payload = {"split_name": "exact_removed", "indices": exact_removed_split(df)}
    write_json(payload, output_path)
    return payload
