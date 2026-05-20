"""Nearest-neighbor public-exposure utilities."""

from __future__ import annotations

import pandas as pd

from moltrustbench.chem import fingerprint_bits, tanimoto_from_bits


def max_similarity_to_public_index(
    smiles: str,
    public_index: pd.DataFrame,
    *,
    allow_fallback: bool = False,
) -> float:
    query_bits = fingerprint_bits(smiles, allow_fallback=allow_fallback)
    best = 0.0
    for public_smiles in public_index["standard_smiles"].dropna().unique().tolist():
        public_bits = fingerprint_bits(public_smiles, allow_fallback=allow_fallback)
        best = max(best, tanimoto_from_bits(query_bits, public_bits))
        if best >= 1.0:
            break
    return round(float(best), 6)


def add_nn_exposure_columns(
    df: pd.DataFrame,
    public_index: pd.DataFrame,
    *,
    thresholds: tuple[float, ...] = (0.6, 0.7, 0.8, 0.9),
    allow_fallback: bool = False,
) -> pd.DataFrame:
    out = df.copy()
    out["max_nn_similarity_before_cutoff"] = [
        max_similarity_to_public_index(smiles, public_index, allow_fallback=allow_fallback)
        for smiles in out["standard_smiles"].tolist()
    ]
    for threshold in thresholds:
        suffix = str(threshold).replace(".", "")
        out[f"nn_exposed_{suffix}"] = out["max_nn_similarity_before_cutoff"] >= threshold
    return out
