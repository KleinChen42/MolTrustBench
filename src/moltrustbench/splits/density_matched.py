"""Density-matched split placeholder with deterministic nearest-neighbor bins."""

from __future__ import annotations

import pandas as pd


def density_bins(df: pd.DataFrame, *, column: str = "max_nn_similarity_before_cutoff", bins: int = 5) -> pd.Series:
    values = df[column].fillna(0.0)
    if values.nunique() <= 1:
        return pd.Series([0] * len(values), index=df.index)
    return pd.qcut(values.rank(method="first"), q=bins, labels=False, duplicates="drop")
