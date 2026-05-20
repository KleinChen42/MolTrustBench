"""Normalize benchmark files into MolTrustBench benchmark parquet files."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from moltrustbench import __version__
from moltrustbench.data.download_benchmarks import fixture_benchmarks
from moltrustbench.data.standardize import standardize_dataframe
from moltrustbench.io import dataframe_manifest_id, read_dataframe, write_dataframe, write_json


def normalize_benchmark(
    df: pd.DataFrame,
    *,
    source_name: str,
    task_name: str,
    allow_fallback: bool = False,
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    required = {"smiles", "label", "split"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Benchmark is missing columns: {sorted(missing)}")
    standardized, rejected, report = standardize_dataframe(
        df,
        smiles_col="smiles",
        source_name=source_name,
        task_name=task_name,
        allow_fallback=allow_fallback,
    )
    standardized["source_name"] = source_name
    standardized["task_name"] = task_name
    standardized["benchmark_name"] = f"{source_name}_{task_name}"
    standardized["input_manifest_id"] = dataframe_manifest_id(df, prefix=f"{source_name}-{task_name}-")
    standardized["row_count"] = int(len(standardized))
    standardized["cutoff_release"] = ""
    standardized["moltrustbench_version"] = __version__
    manifest = {
        "source_name": source_name,
        "task_name": task_name,
        "rows": int(len(df)),
        "standardized_rows": int(len(standardized)),
        "rejected_rows": int(len(rejected)),
        "input_manifest_id": standardized["input_manifest_id"].iloc[0] if not standardized.empty else "",
        "splits": sorted(standardized["split"].dropna().unique().tolist()) if not standardized.empty else [],
    }
    report.update(manifest)
    return standardized, rejected, report


def write_benchmark_outputs(
    standardized: pd.DataFrame,
    rejected: pd.DataFrame,
    manifest: dict,
    *,
    output_dir: str | Path = "data/processed/benchmarks",
) -> Path:
    source = manifest["source_name"]
    task = manifest["task_name"]
    out = Path(output_dir) / f"{source}_{task}.parquet"
    write_dataframe(standardized, out)
    write_json(manifest, Path("data/manifests") / f"benchmark_{source}_{task}.json")
    if not rejected.empty:
        write_dataframe(rejected, Path("data/processed") / f"rejected_{source}_{task}.csv")
    return out


def load_fixture_benchmarks(*, allow_fallback: bool = True) -> list[Path]:
    paths: list[Path] = []
    for (source, task), frame in fixture_benchmarks().items():
        standardized, rejected, manifest = normalize_benchmark(
            frame,
            source_name=source,
            task_name=task,
            allow_fallback=allow_fallback,
        )
        paths.append(write_benchmark_outputs(standardized, rejected, manifest))
    return paths


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input")
    parser.add_argument("--source-name")
    parser.add_argument("--task-name")
    parser.add_argument("--fixture", action="store_true")
    parser.add_argument("--allow-fallback-standardizer", action="store_true")
    parser.add_argument("--output-dir", default="data/processed/benchmarks")
    args = parser.parse_args(argv)

    if args.fixture:
        paths = load_fixture_benchmarks(allow_fallback=args.allow_fallback_standardizer)
        for path in paths:
            print(path)
        return
    if not args.input or not args.source_name or not args.task_name:
        raise SystemExit("--input, --source-name, and --task-name are required unless --fixture is used")
    frame = read_dataframe(args.input)
    standardized, rejected, manifest = normalize_benchmark(
        frame,
        source_name=args.source_name,
        task_name=args.task_name,
        allow_fallback=args.allow_fallback_standardizer,
    )
    print(write_benchmark_outputs(standardized, rejected, manifest, output_dir=args.output_dir))


if __name__ == "__main__":
    main()
