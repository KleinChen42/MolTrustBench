"""Deterministic Milestone 1 smoke pipeline."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import pandas as pd

from moltrustbench.audit.exact_exposure import annotate_exposure, exposure_summary, write_exposure_outputs
from moltrustbench.data.benchmark_loader import load_fixture_benchmarks
from moltrustbench.data.build_release_index import build_fixture_release_index, write_release_outputs
from moltrustbench.evaluation.sanity_checks import run_sanity_checks
from moltrustbench.evaluation.slice_metrics import write_slice_metrics
from moltrustbench.io import ensure_dir, read_dataframe, write_dataframe
from moltrustbench.io import write_json
from moltrustbench.reporting.make_manuscript_report import generate_auto_report
from moltrustbench.splits.exposure_removed import write_exact_removed_split
from moltrustbench.splits.standard import write_standard_split
from moltrustbench.training.run_matrix import run_matrix
from moltrustbench.visualization.plot_exposure_heatmap import plot_exposure_heatmap
from moltrustbench.visualization.plot_performance_drop import plot_performance_drop
from moltrustbench.visualization.plot_release_histogram import plot_release_histogram


GENERATED_DIRS = [
    "data/processed/benchmarks",
    "data/manifests",
    "data/splits",
    "results/release_index",
    "results/benchmark_annotations",
    "results/report_cards",
    "results/predictions",
    "results/metrics",
    "results/figures",
    "results/tables",
    "results/logs",
]


def clean_generated() -> None:
    for directory in GENERATED_DIRS:
        path = Path(directory)
        if path.exists():
            shutil.rmtree(path)


def run_smoke(*, allow_fallback: bool = True) -> dict[str, object]:
    for directory in GENERATED_DIRS:
        ensure_dir(directory)

    compound_index, scaffold_index, counts, rejected = build_fixture_release_index(allow_fallback=allow_fallback)
    write_release_outputs(compound_index, scaffold_index, counts, rejected)

    benchmark_paths = load_fixture_benchmarks(allow_fallback=allow_fallback)
    annotated_frames = []
    annotation_paths = []
    for path in benchmark_paths:
        benchmark = read_dataframe(path)
        annotated = annotate_exposure(
            benchmark,
            compound_index,
            scaffold_index,
            cutoff_release="CHEMBL30",
            allow_fallback=allow_fallback,
        )
        annotation_path, _ = write_exposure_outputs(annotated)
        annotation_paths.append(annotation_path)
        annotated_frames.append(annotated)
        split_dir = Path("data/splits") / f"{annotated['source_name'].iloc[0]}_{annotated['task_name'].iloc[0]}"
        split_dir.mkdir(parents=True, exist_ok=True)
        write_standard_split(annotated, output_path=split_dir / "standard.json")
        write_exact_removed_split(annotated, output_path=split_dir / "exact_removed.json")

    summary = exposure_summary(annotated_frames)
    write_dataframe(summary, "results/tables/exposure_summary.csv")
    required_controls = pd.DataFrame(
        [
            {"risk": "R1", "required_control": "Conservative public-exposure terminology", "status": "preliminary"},
            {"risk": "R2", "required_control": "Density-matched clean split", "status": "missing"},
            {"risk": "R3", "required_control": "Novelty boundary against ADMET/OOD benchmarks", "status": "preliminary"},
            {"risk": "R4", "required_control": "Cutoff release reported as observability date", "status": "preliminary"},
            {"risk": "R5", "required_control": "Model pretraining registry", "status": "missing"},
            {"risk": "R6", "required_control": "Exposure-adjusted scores and trust cards", "status": "preliminary"},
            {"risk": "R7", "required_control": "Foundation model wrappers scoped as case studies", "status": "missing"},
            {"risk": "R8", "required_control": "Clean subset size sanity checks", "status": "preliminary"},
            {"risk": "R9", "required_control": "Standardization report and rejected molecules", "status": "preliminary"},
            {"risk": "R10", "required_control": "Assay-provenance conflict scoring", "status": "missing"},
        ]
    )
    write_dataframe(required_controls, "results/tables/required_controls.csv")

    run_matrix(annotation_paths, allow_fallback=allow_fallback)
    metrics = write_slice_metrics()

    plot_release_histogram(counts)
    plot_exposure_heatmap(summary)
    plot_performance_drop(metrics)

    sanity = run_sanity_checks(".")
    write_dataframe(sanity, "results/tables/sanity_report.csv")
    write_json(
        {
            "mode": "fixture_smoke",
            "standardization_backends": sorted(compound_index["standardization_backend"].dropna().unique().tolist()),
            "compound_index_rows": int(len(compound_index)),
            "benchmark_tasks": int(len(benchmark_paths)),
            "note": "Fallback identifiers are fixture-only and must not be used as chemical InChIKeys in paper claims.",
        },
        "data/processed/standardization_report.json",
    )
    generate_auto_report()

    failed = sanity[(sanity["severity"] == "critical") & (sanity["status"] == "fail")]
    return {
        "compound_index_rows": int(len(compound_index)),
        "scaffold_index_rows": int(len(scaffold_index)),
        "benchmark_tasks": int(len(benchmark_paths)),
        "annotation_paths": [str(path) for path in annotation_paths],
        "failed_critical_checks": int(len(failed)),
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-fallback-standardizer", action="store_true")
    parser.add_argument("--clean", action="store_true")
    parser.add_argument("--fail-on-critical", action="store_true")
    args = parser.parse_args(argv)

    if args.clean:
        clean_generated()
        return
    result = run_smoke(allow_fallback=args.allow_fallback_standardizer)
    print(result)
    if args.fail_on_critical and result["failed_critical_checks"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
