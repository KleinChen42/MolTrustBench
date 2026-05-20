"""Metric computation for classification and regression."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    roc_auc_score,
)


def compute_metrics(y_true: pd.Series, y_pred: pd.Series, *, task_type: str) -> dict[str, float | int | str]:
    y_true = pd.Series(y_true).astype(float)
    y_pred = pd.Series(y_pred).astype(float)
    metrics: dict[str, float | int | str] = {"n": int(len(y_true)), "task_type": task_type}
    if len(y_true) == 0:
        metrics["status"] = "empty"
        return metrics
    if task_type == "classification":
        labels = sorted(y_true.dropna().unique().tolist())
        hard = (y_pred >= 0.5).astype(int)
        metrics["accuracy"] = float(accuracy_score(y_true, hard))
        metrics["balanced_accuracy"] = float(balanced_accuracy_score(y_true, hard)) if len(labels) > 1 else float("nan")
        metrics["auprc"] = float(average_precision_score(y_true, y_pred)) if len(labels) > 1 else float("nan")
        metrics["auroc"] = float(roc_auc_score(y_true, y_pred)) if len(labels) > 1 else float("nan")
    else:
        metrics["mae"] = float(mean_absolute_error(y_true, y_pred))
        metrics["rmse"] = float(math.sqrt(mean_squared_error(y_true, y_pred)))
        metrics["r2"] = float(r2_score(y_true, y_pred)) if len(y_true) > 1 else float("nan")
    return metrics


def finite_metric_values(metrics: dict) -> bool:
    for value in metrics.values():
        if isinstance(value, float) and not np.isfinite(value):
            return False
    return True
