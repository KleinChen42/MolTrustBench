"""GPU Morgan-MLP exposure-sliced baseline for overnight controls."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from time import time

import numpy as np
import pandas as pd

from moltrustbench.evaluation.metrics import compute_metrics
from moltrustbench.io import ensure_dir, read_dataframe, stable_hash_text, write_dataframe, write_json
from moltrustbench.models.classical import featurize, infer_task_type
from moltrustbench.training.train import split_train_test


def _load_torch():
    try:
        import torch
        from torch import nn
        from torch.utils.data import DataLoader, TensorDataset
    except Exception as exc:  # pragma: no cover - depends on optional GPU env
        raise RuntimeError("PyTorch is required for the GPU MLP baseline") from exc
    return torch, nn, DataLoader, TensorDataset


def _device(torch):
    if os.environ.get("CUDA_VISIBLE_DEVICES") not in {"0", "GPU-0"}:
        raise RuntimeError("GPU MLP must run with CUDA_VISIBLE_DEVICES=0")
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is unavailable; refusing to run GPU MLP on CPU")
    return torch.device("cuda:0")


def _make_model(nn, n_features: int, *, hidden_dim: int, dropout: float):
    return nn.Sequential(
        nn.Linear(n_features, hidden_dim),
        nn.ReLU(),
        nn.Dropout(dropout),
        nn.Linear(hidden_dim, hidden_dim // 2),
        nn.ReLU(),
        nn.Dropout(dropout),
        nn.Linear(hidden_dim // 2, 1),
    )


def _batch_loader(torch, TensorDataset, x: np.ndarray, y: np.ndarray, *, batch_size: int, seed: int, device):
    gen = torch.Generator(device="cpu")
    gen.manual_seed(seed)
    dataset = TensorDataset(
        torch.as_tensor(x, dtype=torch.float32, device=device),
        torch.as_tensor(y.reshape(-1, 1), dtype=torch.float32, device=device),
    )
    return DataLoader(dataset, batch_size=batch_size, shuffle=True, generator=gen)


def train_gpu_mlp(
    annotated_df: pd.DataFrame,
    *,
    split_name: str,
    seed: int,
    hidden_dim: int,
    dropout: float,
    epochs: int,
    batch_size: int,
    learning_rate: float,
) -> tuple[pd.DataFrame, dict]:
    torch, nn, DataLoader, TensorDataset = _load_torch()
    device = _device(torch)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

    train_df, test_df = split_train_test(annotated_df, split_name=split_name)
    task_type = infer_task_type(train_df["label"])
    x_train = featurize(train_df["standard_smiles"].tolist(), allow_fallback=False)
    y_train = train_df["label"].astype(float).to_numpy()
    x_test = featurize(test_df["standard_smiles"].tolist(), allow_fallback=False)
    y_test = test_df["label"].astype(float).to_numpy()

    model = _make_model(nn, x_train.shape[1], hidden_dim=hidden_dim, dropout=dropout).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=1e-4)
    if task_type == "classification":
        pos = max(float((y_train == 1).sum()), 1.0)
        neg = max(float((y_train == 0).sum()), 1.0)
        loss_fn = nn.BCEWithLogitsLoss(pos_weight=torch.tensor([neg / pos], device=device))
    else:
        loss_fn = nn.MSELoss()

    loader = _batch_loader(torch, TensorDataset, x_train, y_train, batch_size=batch_size, seed=seed, device=device)
    start = time()
    model.train()
    last_loss = float("nan")
    for _ in range(epochs):
        for xb, yb in loader:
            optimizer.zero_grad(set_to_none=True)
            logits = model(xb)
            loss = loss_fn(logits, yb)
            loss.backward()
            optimizer.step()
            last_loss = float(loss.detach().cpu())

    model.eval()
    with torch.no_grad():
        xt = torch.as_tensor(x_test, dtype=torch.float32, device=device)
        raw = model(xt).detach().cpu().numpy().reshape(-1)
    if task_type == "classification":
        pred = 1.0 / (1.0 + np.exp(-raw))
    else:
        pred = raw

    predictions = test_df[
        [
            "source_name",
            "task_name",
            "row_id",
            "split",
            "label",
            "standard_smiles",
            "exact_exposed",
            "scaffold_exposed",
            "max_nn_similarity_before_cutoff",
        ]
    ].copy()
    source = str(annotated_df["source_name"].iloc[0])
    task = str(annotated_df["task_name"].iloc[0])
    run_id = stable_hash_text(
        f"{source}|{task}|morgan_mlp_gpu|{split_name}|{seed}|{hidden_dim}|{dropout}|{epochs}",
        prefix="gpu-mlp-",
    )
    predictions["prediction"] = pred
    predictions["model_id"] = "morgan_mlp_gpu"
    predictions["model_backend"] = "torch_cuda_mlp"
    predictions["task_type"] = task_type
    predictions["split_name"] = split_name
    predictions["run_id"] = run_id

    metrics = compute_metrics(predictions["label"], predictions["prediction"], task_type=task_type)
    metrics.update(
        {
            "run_id": run_id,
            "source_name": source,
            "task_name": task,
            "model_id": "morgan_mlp_gpu",
            "model_backend": "torch_cuda_mlp",
            "split_name": split_name,
            "seed": seed,
            "hidden_dim": hidden_dim,
            "dropout": dropout,
            "epochs": epochs,
            "batch_size": batch_size,
            "learning_rate": learning_rate,
            "train_n": int(len(train_df)),
            "test_n": int(len(test_df)),
            "exact_exposed_test_n": int(test_df["exact_exposed"].fillna(False).sum()),
            "clean_test_n": int((~test_df["exact_exposed"].fillna(False)).sum()),
            "last_train_loss": last_loss,
            "runtime_sec": round(time() - start, 3),
            "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES", ""),
            "torch_device": str(device),
        }
    )
    return predictions, metrics


def run_gpu_mlp_matrix(
    annotation_paths: list[str | Path],
    *,
    splits: tuple[str, ...],
    seeds: tuple[int, ...],
    hidden_dims: tuple[int, ...],
    epochs: int,
    batch_size: int,
    learning_rate: float,
    dropout: float,
    output_dir: str | Path = "results",
) -> pd.DataFrame:
    metrics_records: list[dict] = []
    pred_dir = ensure_dir(Path(output_dir) / "predictions")
    metric_dir = ensure_dir(Path(output_dir) / "metrics")
    for annotation_path in annotation_paths:
        frame = read_dataframe(annotation_path)
        for hidden_dim in hidden_dims:
            for seed in seeds:
                for split_name in splits:
                    try:
                        predictions, metrics = train_gpu_mlp(
                            frame,
                            split_name=split_name,
                            seed=seed,
                            hidden_dim=hidden_dim,
                            dropout=dropout,
                            epochs=epochs,
                            batch_size=batch_size,
                            learning_rate=learning_rate,
                        )
                    except ValueError as exc:
                        metrics = {
                            "run_id": stable_hash_text(f"{annotation_path}|skip|{split_name}|{seed}|{hidden_dim}", prefix="gpu-mlp-"),
                            "source_name": Path(annotation_path).stem,
                            "task_name": Path(annotation_path).stem,
                            "model_id": "morgan_mlp_gpu",
                            "model_backend": "torch_cuda_mlp",
                            "split_name": split_name,
                            "seed": seed,
                            "hidden_dim": hidden_dim,
                            "status": "skipped",
                            "skip_reason": str(exc),
                        }
                    else:
                        write_dataframe(predictions, pred_dir / f"{metrics['run_id']}.parquet")
                        write_json(metrics, metric_dir / f"{metrics['run_id']}.json")
                    metrics_records.append(metrics)
    metrics_df = pd.DataFrame.from_records(metrics_records)
    if not metrics_df.empty:
        score_col = "auroc" if "auroc" in metrics_df.columns else "rmse"
        if score_col in metrics_df:
            metrics_df["primary_score"] = -metrics_df[score_col] if score_col == "rmse" else metrics_df[score_col]
            key_cols = ["source_name", "task_name", "model_id", "seed", "hidden_dim"]
            standard = (
                metrics_df[metrics_df["split_name"] == "standard"][key_cols + ["primary_score"]]
                .rename(columns={"primary_score": "standard_score"})
            )
            clean = (
                metrics_df[metrics_df["split_name"] == "exact_removed"][key_cols + ["primary_score"]]
                .rename(columns={"primary_score": "clean_subset_score"})
            )
            metrics_df = metrics_df.merge(standard, on=key_cols, how="left").merge(clean, on=key_cols, how="left")
            metrics_df["exposure_delta"] = metrics_df["standard_score"] - metrics_df["clean_subset_score"]
    write_dataframe(metrics_df, Path(output_dir) / "tables" / "gpu_mlp_slice_metrics.csv")
    return metrics_df


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotations", action="append", default=None)
    parser.add_argument("--annotations-glob", default="results/benchmark_annotations/*_exposure.parquet")
    parser.add_argument("--split", action="append", default=None)
    parser.add_argument("--seed", action="append", type=int, default=None)
    parser.add_argument("--hidden-dim", action="append", type=int, default=None)
    parser.add_argument("--epochs", type=int, default=800)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--dropout", type=float, default=0.15)
    parser.add_argument("--output-dir", default="results")
    args = parser.parse_args(argv)

    paths = [Path(p) for p in (args.annotations or [])]
    if not paths:
        paths = sorted(Path(".").glob(args.annotations_glob))
    if not paths:
        raise SystemExit(f"No annotation files found for {args.annotations_glob}")
    metrics = run_gpu_mlp_matrix(
        paths,
        splits=tuple(args.split or ["standard", "exact_removed", "density_matched_clean"]),
        seeds=tuple(args.seed or [0, 1, 2]),
        hidden_dims=tuple(args.hidden_dim or [256, 512]),
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        dropout=args.dropout,
        output_dir=args.output_dir,
    )
    print(json.dumps({"metrics_rows": int(len(metrics)), "output": str(Path(args.output_dir) / "tables" / "gpu_mlp_slice_metrics.csv")}, indent=2))


if __name__ == "__main__":
    main()
