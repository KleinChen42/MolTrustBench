"""Temporal split interface."""

from __future__ import annotations

import pandas as pd


def temporal_future_split(df: pd.DataFrame, *, train_max_release_order: int, test_min_release_order: int) -> dict[str, list[int]]:
    train = df[df["earliest_exact_order"].fillna(10**9) <= train_max_release_order]["row_id"].astype(int).tolist()
    test = df[df["earliest_exact_order"].fillna(-1) >= test_min_release_order]["row_id"].astype(int).tolist()
    return {"train": train, "test": test}
