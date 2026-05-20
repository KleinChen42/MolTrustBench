"""Collect per-run metrics into slice tables."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from moltrustbench.evaluation.adjusted_scores import add_exposure_delta
from moltrustbench.io import write_dataframe


def collect_metric_jsons(metrics_dir: str | Path = "results/metrics") -> pd.DataFrame:
    rows = []
    for path in sorted(Path(metrics_dir).glob("*.json")):
        rows.append(json.loads(path.read_text(encoding="utf-8")))
    return pd.DataFrame.from_records(rows)


def write_slice_metrics(metrics_dir: str | Path = "results/metrics", output_path: str | Path = "results/tables/slice_metrics.csv") -> pd.DataFrame:
    metrics = collect_metric_jsons(metrics_dir)
    if metrics.empty:
        write_dataframe(metrics, output_path)
        return metrics
    score_col = "auroc" if "auroc" in metrics.columns else "rmse"
    if score_col == "rmse":
        metrics["primary_score"] = -metrics[score_col]
    else:
        metrics["primary_score"] = metrics[score_col]
    metrics = add_exposure_delta(metrics, score_col="primary_score")
    write_dataframe(metrics, output_path)
    return metrics
