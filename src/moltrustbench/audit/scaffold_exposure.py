"""Scaffold public-exposure utilities."""

from __future__ import annotations

import pandas as pd


def add_scaffold_exposure_columns(
    benchmark_df: pd.DataFrame,
    scaffold_index: pd.DataFrame,
    *,
    cutoff_order: int,
) -> pd.DataFrame:
    scaffold_cols = [
        "murcko_scaffold_smiles",
        "first_seen_release",
        "first_seen_date",
        "first_seen_order",
    ]
    merged = benchmark_df.merge(
        scaffold_index[scaffold_cols].drop_duplicates("murcko_scaffold_smiles").rename(
            columns={
                "first_seen_release": "earliest_scaffold_release",
                "first_seen_date": "earliest_scaffold_date",
                "first_seen_order": "earliest_scaffold_order",
            }
        ),
        on="murcko_scaffold_smiles",
        how="left",
    )
    merged["scaffold_exposed"] = merged["earliest_scaffold_order"].fillna(10**9) <= cutoff_order
    return merged
