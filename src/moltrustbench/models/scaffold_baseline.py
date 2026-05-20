"""Scaffold-majority baseline."""

from __future__ import annotations

import pandas as pd


def scaffold_majority_predict(train_df: pd.DataFrame, test_df: pd.DataFrame) -> pd.Series:
    global_mean = float(train_df["label"].mean())
    by_scaffold = train_df.groupby("murcko_scaffold_smiles")["label"].mean().to_dict()
    return test_df["murcko_scaffold_smiles"].map(by_scaffold).fillna(global_mean)
