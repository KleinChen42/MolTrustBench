"""Benchmark exposure risk scoring."""

from __future__ import annotations

import pandas as pd


def exposure_risk_score(row: pd.Series) -> float:
    score = 0.0
    if bool(row.get("exact_exposed", False)):
        score = max(score, 1.0)
    if bool(row.get("scaffold_exposed", False)):
        score = max(score, 0.75)
    nn = float(row.get("max_nn_similarity_before_cutoff", 0.0) or 0.0)
    if nn >= 0.9:
        score = max(score, 0.65)
    elif nn >= 0.8:
        score = max(score, 0.55)
    elif nn >= 0.7:
        score = max(score, 0.4)
    elif nn >= 0.6:
        score = max(score, 0.25)
    return round(float(score), 4)


def exposure_category(row: pd.Series) -> str:
    if bool(row.get("exact_exposed", False)):
        return "exact_public_exposure"
    if bool(row.get("scaffold_exposed", False)):
        return "scaffold_public_exposure"
    if bool(row.get("nn_exposed_08", False)):
        return "nearest_neighbor_public_exposure"
    if bool(row.get("nn_exposed_06", False)):
        return "weak_neighbor_public_exposure"
    return "no_observed_public_exposure"
