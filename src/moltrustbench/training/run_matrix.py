"""Run a small endpoint x model x split matrix."""

from __future__ import annotations

from pathlib import Path

from moltrustbench.io import read_dataframe
from moltrustbench.training.train import train_and_evaluate, write_run_outputs


def run_matrix(
    annotation_paths: list[str | Path],
    *,
    models: tuple[str, ...] = ("morgan_logreg", "morgan_xgb"),
    splits: tuple[str, ...] = ("standard", "exact_removed"),
    allow_fallback: bool = False,
) -> list[dict]:
    results = []
    for path in annotation_paths:
        frame = read_dataframe(path)
        for model_id in models:
            for split_name in splits:
                predictions, metrics = train_and_evaluate(frame, model_id=model_id, split_name=split_name, allow_fallback=allow_fallback)
                write_run_outputs(predictions, metrics)
                results.append(metrics)
    return results
