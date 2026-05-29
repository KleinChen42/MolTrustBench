"""Benchmark trust card generation."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from moltrustbench.io import write_json


def make_exposure_card(annotated: pd.DataFrame, *, cutoff_release: str) -> dict:
    total = int(len(annotated))
    task = str(annotated["task_name"].iloc[0]) if total and "task_name" in annotated else ""
    source = str(annotated["source_name"].iloc[0]) if total and "source_name" in annotated else ""

    def rate(column: str) -> float:
        if total == 0 or column not in annotated:
            return 0.0
        return round(float(annotated[column].fillna(False).mean()), 6)

    clean = int((~annotated.get("exact_exposed", pd.Series([False] * total)).fillna(False)).sum()) if total else 0
    risk = "low"
    if rate("exact_exposed") >= 0.5 or rate("nn_exposed_08") >= 0.7:
        risk = "high"
    elif rate("exact_exposed") >= 0.2 or rate("nn_exposed_08") >= 0.4:
        risk = "medium"

    return {
        "source_name": source,
        "task_name": task,
        "cutoff_release": cutoff_release,
        "n_molecules": total,
        "exact_public_exposure_rate": rate("exact_exposed"),
        "scaffold_public_exposure_rate": rate("scaffold_exposed"),
        "nn_exposure_rate_06": rate("nn_exposed_06"),
        "nn_exposure_rate_07": rate("nn_exposed_07"),
        "nn_exposure_rate_08": rate("nn_exposed_08"),
        "nn_exposure_rate_09": rate("nn_exposed_09"),
        "exact_unobserved_n": clean,
        "exposure_removed_test_n": clean,
        "exact_clean_molecules": clean,
        "risk_level": risk,
        "interpretation": "Observable public-exposure lower bound; not evidence of model-specific training exposure.",
    }


def write_exposure_card(annotated: pd.DataFrame, *, cutoff_release: str, output_path: str | Path) -> dict:
    card = make_exposure_card(annotated, cutoff_release=cutoff_release)
    write_json(card, output_path)
    return card
