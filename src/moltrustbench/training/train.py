"""Train Milestone 1 baselines and evaluate standard/exposure-removed splits."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from moltrustbench.evaluation.metrics import compute_metrics
from moltrustbench.io import read_dataframe, stable_hash_text, write_dataframe, write_json
from moltrustbench.models.classical import fit_classical_model, predict_model


def split_train_test(df: pd.DataFrame, *, split_name: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    train = df[df["split"].isin(["train", "valid", "validation"])].copy()
    if split_name == "standard":
        test = df[df["split"] == "test"].copy()
    elif split_name == "exact_removed":
        test = df[(df["split"] == "test") & (~df["exact_exposed"].fillna(False))].copy()
    else:
        raise ValueError(f"Unsupported split for Milestone 1: {split_name}")
    if train.empty:
        raise ValueError("Train split is empty")
    if test.empty:
        raise ValueError(f"Test split is empty for split {split_name}")
    return train, test


def train_and_evaluate(
    annotated_df: pd.DataFrame,
    *,
    model_id: str,
    split_name: str,
    allow_fallback: bool = False,
    seed: int = 0,
) -> tuple[pd.DataFrame, dict]:
    train, test = split_train_test(annotated_df, split_name=split_name)
    model = fit_classical_model(train, model_id=model_id, allow_fallback=allow_fallback)
    predictions = predict_model(model, test)
    metrics = compute_metrics(predictions["label"], predictions["prediction"], task_type=model.task_type)
    source = annotated_df["source_name"].iloc[0]
    task = annotated_df["task_name"].iloc[0]
    run_id = stable_hash_text(f"{source}|{task}|{model_id}|{split_name}|{seed}", prefix="run-")
    metrics.update(
        {
            "run_id": run_id,
            "source_name": source,
            "task_name": task,
            "model_id": model_id,
            "model_backend": model.backend,
            "split_name": split_name,
            "seed": seed,
            "train_n": int(len(train)),
            "test_n": int(len(test)),
            "exact_exposed_test_n": int(test["exact_exposed"].fillna(False).sum()) if "exact_exposed" in test else 0,
            "clean_test_n": int((~test["exact_exposed"].fillna(False)).sum()) if "exact_exposed" in test else int(len(test)),
        }
    )
    predictions["run_id"] = run_id
    predictions["split_name"] = split_name
    return predictions, metrics


def write_run_outputs(predictions: pd.DataFrame, metrics: dict) -> tuple[Path, Path, Path]:
    run_id = metrics["run_id"]
    pred_path = Path("results/predictions") / f"{run_id}.parquet"
    metrics_path = Path("results/metrics") / f"{run_id}.json"
    log_path = Path("results/logs") / f"{run_id}.json"
    write_dataframe(predictions, pred_path)
    write_json(metrics, metrics_path)
    write_json({"run_id": run_id, "status": "completed", "metrics_path": str(metrics_path), "prediction_path": str(pred_path)}, log_path)
    return pred_path, metrics_path, log_path


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotations", required=True)
    parser.add_argument("--model-id", required=True, choices=["morgan_logreg", "morgan_ridge", "morgan_xgb"])
    parser.add_argument("--split-name", required=True, choices=["standard", "exact_removed"])
    parser.add_argument("--allow-fallback-standardizer", action="store_true")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args(argv)

    frame = read_dataframe(args.annotations)
    predictions, metrics = train_and_evaluate(
        frame,
        model_id=args.model_id,
        split_name=args.split_name,
        allow_fallback=args.allow_fallback_standardizer,
        seed=args.seed,
    )
    paths = write_run_outputs(predictions, metrics)
    print(json.dumps({"prediction_path": str(paths[0]), "metrics_path": str(paths[1])}, indent=2))


if __name__ == "__main__":
    main()
