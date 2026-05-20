"""Bootstrap confidence intervals."""

from __future__ import annotations

import numpy as np
import pandas as pd

from moltrustbench.evaluation.metrics import compute_metrics


def bootstrap_metric(
    predictions: pd.DataFrame,
    *,
    task_type: str,
    metric_name: str,
    n_bootstrap: int = 200,
    seed: int = 0,
) -> dict[str, float]:
    if predictions.empty:
        return {"low": float("nan"), "high": float("nan")}
    rng = np.random.default_rng(seed)
    values = []
    for _ in range(n_bootstrap):
        sample_idx = rng.integers(0, len(predictions), len(predictions))
        sample = predictions.iloc[sample_idx]
        metric = compute_metrics(sample["label"], sample["prediction"], task_type=task_type).get(metric_name)
        if isinstance(metric, float) and np.isfinite(metric):
            values.append(metric)
    if not values:
        return {"low": float("nan"), "high": float("nan")}
    return {"low": float(np.quantile(values, 0.025)), "high": float(np.quantile(values, 0.975))}
