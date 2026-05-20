import pandas as pd

from moltrustbench.evaluation.metrics import compute_metrics


def test_classification_metrics_are_finite_for_two_classes():
    metrics = compute_metrics(pd.Series([0, 1, 0, 1]), pd.Series([0.1, 0.9, 0.2, 0.8]), task_type="classification")
    assert metrics["auroc"] == 1.0
    assert metrics["auprc"] == 1.0
    assert metrics["n"] == 4
