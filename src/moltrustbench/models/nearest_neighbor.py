"""Nearest-neighbor baseline."""

from __future__ import annotations

import pandas as pd

from moltrustbench.chem import fingerprint_bits, tanimoto_from_bits


def nearest_neighbor_predict(train_df: pd.DataFrame, test_df: pd.DataFrame, *, allow_fallback: bool = False) -> pd.Series:
    train_bits = [(fingerprint_bits(row.standard_smiles, allow_fallback=allow_fallback), float(row.label)) for row in train_df.itertuples()]
    preds = []
    for row in test_df.itertuples():
        bits = fingerprint_bits(row.standard_smiles, allow_fallback=allow_fallback)
        best_sim = -1.0
        best_label = 0.0
        for candidate_bits, label in train_bits:
            sim = tanimoto_from_bits(bits, candidate_bits)
            if sim > best_sim:
                best_sim = sim
                best_label = label
        preds.append(best_label)
    return pd.Series(preds, index=test_df.index)
