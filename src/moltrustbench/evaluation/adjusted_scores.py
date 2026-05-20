"""Exposure-adjusted score helpers."""

from __future__ import annotations

import pandas as pd


def exposure_delta(standard_score: float | None, clean_score: float | None) -> float | None:
    if standard_score is None or clean_score is None:
        return None
    return float(standard_score) - float(clean_score)


def add_exposure_delta(metrics_df: pd.DataFrame, *, score_col: str = "primary_score") -> pd.DataFrame:
    out = metrics_df.copy()
    key_cols = ["source_name", "task_name", "model_id"]
    standard = out[out["split_name"] == "standard"][key_cols + [score_col]].rename(columns={score_col: "standard_score"})
    clean = out[out["split_name"] == "exact_removed"][key_cols + [score_col]].rename(columns={score_col: "clean_subset_score"})
    merged = out.merge(standard, on=key_cols, how="left").merge(clean, on=key_cols, how="left")
    merged["exposure_delta"] = merged["standard_score"] - merged["clean_subset_score"]
    return merged
