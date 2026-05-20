"""Run the real-data Milestone 1 public-exposure audit."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from typing import Callable

import pandas as pd

from moltrustbench.audit.exact_exposure import annotate_exposure, exposure_summary, write_exposure_outputs
from moltrustbench.chem import rdkit_available
from moltrustbench.constants import CHEMBL_RELEASES
from moltrustbench.data.benchmark_loader import normalize_benchmark, write_benchmark_outputs
from moltrustbench.data.build_release_index import build_release_indexes, read_chembl_sqlite, write_release_outputs
from moltrustbench.data.download_benchmarks import load_moleculenet_task, load_tdc_hERG
from moltrustbench.data.download_chembl import download_chembl_release
from moltrustbench.evaluation.adjusted_scores import add_exposure_delta
from moltrustbench.evaluation.sanity_checks import run_sanity_checks
from moltrustbench.io import ensure_dir, write_dataframe, write_json
from moltrustbench.reporting.make_manuscript_report import generate_auto_report
from moltrustbench.splits.exposure_removed import write_exact_removed_split
from moltrustbench.splits.standard import write_standard_split
from moltrustbench.training.run_matrix import run_matrix
from moltrustbench.visualization.plot_exposure_heatmap import plot_exposure_heatmap
from moltrustbench.visualization.plot_performance_drop import plot_performance_drop
from moltrustbench.visualization.plot_release_histogram import plot_release_histogram


DEFAULT_RELEASES = ("CHEMBL24", "CHEMBL27", "CHEMBL30", "CHEMBL33", "CHEMBL36")


class RunLedger:
    def __init__(self, run_dir: str | Path = "results/logs/real_audit_gpu0") -> None:
        self.run_dir = ensure_dir(run_dir)
        self.status_path = self.run_dir / "status.tsv"
        self.manifest_path = self.run_dir / "job_manifest.jsonl"
        self.summary_path = self.run_dir / "summary.json"
        if not self.status_path.exists() or self.status_path.stat().st_size == 0:
            self.status_path.write_text("timestamp\tstage\tstatus\tdetail\n", encoding="utf-8")

    def record(self, stage: str, status: str, detail: str = "") -> None:
        stamp = datetime.now(timezone.utc).isoformat()
        safe_detail = str(detail).replace("\t", " ").replace("\n", " ")
        with self.status_path.open("a", encoding="utf-8") as handle:
            handle.write(f"{stamp}\t{stage}\t{status}\t{safe_detail}\n")
        with self.manifest_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"timestamp": stamp, "stage": stage, "status": status, "detail": safe_detail}) + "\n")

    def stage(self, name: str, fn: Callable[[], object]) -> object:
        self.record(name, "started")
        try:
            result = fn()
        except Exception as exc:
            self.record(name, "failed", repr(exc))
            self.write_summary({"status": "failed", "failed_stage": name, "error": repr(exc)})
            raise
        self.record(name, "completed")
        return result

    def write_summary(self, payload: dict) -> None:
        write_json(payload, self.summary_path)


def _check_gpu0() -> dict:
    env_visible = os.environ.get("CUDA_VISIBLE_DEVICES", "")
    info = {"CUDA_VISIBLE_DEVICES": env_visible}
    try:
        proc = subprocess.run(
            ["nvidia-smi", "--query-gpu=index,memory.used,utilization.gpu", "--format=csv,noheader,nounits"],
            check=False,
            capture_output=True,
            text=True,
            timeout=20,
        )
        info["nvidia_smi_returncode"] = proc.returncode
        info["nvidia_smi"] = proc.stdout.strip().splitlines()
    except Exception as exc:
        info["nvidia_smi_error"] = repr(exc)
    return info


def _preflight(releases: tuple[str, ...]) -> dict:
    if os.environ.get("CUDA_VISIBLE_DEVICES") not in {"0", "GPU-0"}:
        raise RuntimeError("Real audit must run with CUDA_VISIBLE_DEVICES=0.")
    if not rdkit_available():
        raise RuntimeError("RDKit is required for real-data ChEMBL indexing.")
    usage = shutil.disk_usage(Path.cwd())
    missing = [release for release in releases if release not in CHEMBL_RELEASES]
    if missing:
        raise RuntimeError(f"Unknown ChEMBL releases: {missing}")
    return {
        "python": sys.version,
        "cwd": str(Path.cwd()),
        "disk_free_gb": round(usage.free / (1024**3), 3),
        "gpu": _check_gpu0(),
        "rdkit_available": True,
    }


def _download_releases(releases: tuple[str, ...], *, raw_dir: str | Path) -> list[dict]:
    return [download_chembl_release(release, output_dir=raw_dir, skip_existing=True) for release in releases]


def _build_release_index(manifests: list[dict]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    frames = {manifest["release_id"]: read_chembl_sqlite(manifest["sqlite_path"]) for manifest in manifests}
    compound_index, scaffold_index, counts, rejected = build_release_indexes(frames, allow_fallback=False)
    write_release_outputs(compound_index, scaffold_index, counts, rejected)
    return compound_index, scaffold_index, counts


def _load_real_benchmarks(*, allow_tdc_failure: bool, moleculenet_fallback: str) -> list[Path]:
    outputs: list[Path] = []
    try:
        tdc = load_tdc_hERG()
        standardized, rejected, manifest = normalize_benchmark(tdc, source_name="tdc_admet", task_name="hERG", allow_fallback=False)
        outputs.append(write_benchmark_outputs(standardized, rejected, manifest))
    except Exception:
        if not allow_tdc_failure:
            raise

    try:
        bbbp = load_moleculenet_task("BBBP")
        standardized, rejected, manifest = normalize_benchmark(bbbp, source_name="moleculenet", task_name="BBBP", allow_fallback=False)
        outputs.append(write_benchmark_outputs(standardized, rejected, manifest))
    except Exception:
        fallback = load_moleculenet_task(moleculenet_fallback)
        standardized, rejected, manifest = normalize_benchmark(
            fallback,
            source_name="moleculenet",
            task_name=moleculenet_fallback,
            allow_fallback=False,
        )
        outputs.append(write_benchmark_outputs(standardized, rejected, manifest))
    if len(outputs) < 2:
        raise RuntimeError(f"Expected at least two real benchmark tasks, got {len(outputs)}")
    return outputs


def _annotate_benchmarks(
    benchmark_paths: list[Path],
    compound_index: pd.DataFrame,
    scaffold_index: pd.DataFrame,
    *,
    cutoff_release: str,
) -> list[Path]:
    annotated_frames = []
    annotation_paths = []
    for path in benchmark_paths:
        benchmark = pd.read_parquet(path)
        annotated = annotate_exposure(
            benchmark,
            compound_index,
            scaffold_index,
            cutoff_release=cutoff_release,
            allow_fallback=False,
        )
        annotation_path, _ = write_exposure_outputs(annotated)
        annotation_paths.append(annotation_path)
        annotated_frames.append(annotated)
        split_dir = Path("data/splits") / f"{annotated['source_name'].iloc[0]}_{annotated['task_name'].iloc[0]}"
        split_dir.mkdir(parents=True, exist_ok=True)
        write_standard_split(annotated, output_path=split_dir / "standard.json")
        write_exact_removed_split(annotated, output_path=split_dir / "exact_removed.json")
    summary = exposure_summary(annotated_frames)
    summary["data_mode"] = "real_chembl_release_index"
    write_dataframe(summary, "results/tables/exposure_summary.csv")
    return annotation_paths


def _run_baselines(annotation_paths: list[Path]) -> pd.DataFrame:
    metrics = run_matrix(annotation_paths, allow_fallback=False)
    metrics_df = pd.DataFrame.from_records(metrics)
    score_col = "auroc" if "auroc" in metrics_df.columns else "rmse"
    metrics_df["primary_score"] = -metrics_df[score_col] if score_col == "rmse" else metrics_df[score_col]
    metrics_df = add_exposure_delta(metrics_df, score_col="primary_score")
    metrics_df["data_mode"] = "real_chembl_release_index"
    write_dataframe(metrics_df, "results/tables/slice_metrics.csv")
    return metrics_df


def _write_required_controls() -> None:
    controls = pd.DataFrame(
        [
            {"risk": "R1", "required_control": "Conservative public-exposure terminology", "status": "supported"},
            {"risk": "R2", "required_control": "Density-matched clean split", "status": "missing"},
            {"risk": "R3", "required_control": "Novelty boundary against ADMET/OOD benchmarks", "status": "preliminary"},
            {"risk": "R4", "required_control": "Cutoff release reported as observability date", "status": "supported"},
            {"risk": "R5", "required_control": "Model pretraining registry", "status": "missing"},
            {"risk": "R6", "required_control": "Exposure-adjusted scores and trust cards", "status": "supported"},
            {"risk": "R7", "required_control": "Foundation model wrappers scoped as case studies", "status": "missing"},
            {"risk": "R8", "required_control": "Clean subset size sanity checks", "status": "supported"},
            {"risk": "R9", "required_control": "Standardization report and rejected molecules", "status": "supported"},
            {"risk": "R10", "required_control": "Assay-provenance conflict scoring", "status": "missing"},
        ]
    )
    write_dataframe(controls, "results/tables/required_controls.csv")


def _update_standardization_report(compound_index: pd.DataFrame, benchmark_paths: list[Path]) -> None:
    write_json(
        {
            "mode": "real_data_audit",
            "standardization_backends": sorted(compound_index["standardization_backend"].dropna().unique().tolist()),
            "compound_index_rows": int(len(compound_index)),
            "benchmark_tasks": int(len(benchmark_paths)),
            "note": "Real ChEMBL release-index run; fallback fixture identifiers are not used.",
        },
        "data/processed/standardization_report.json",
    )


def _update_paper_status_after_real_run() -> None:
    claims = Path("paper/claims.md")
    if claims.exists():
        text = claims.read_text(encoding="utf-8")
        text = text.replace(
            "| C1 | Molecular AI benchmarks contain measurable public-exposure risk at the molecule, scaffold, and nearest-neighbor levels. | preliminary |",
            "| C1 | Molecular AI benchmarks contain measurable public-exposure risk at the molecule, scaffold, and nearest-neighbor levels. | supported |",
        )
        text = text.replace(
            "| C2 | Exact molecule exposure is only the easiest case; scaffold and chemical-neighbor exposure reveal broader benchmark time-travel risk. | preliminary |",
            "| C2 | Exact molecule exposure is only the easiest case; scaffold and chemical-neighbor exposure reveal broader benchmark time-travel risk. | supported |",
        )
        text = text.replace(
            "full support depends on real ChEMBL release index outputs",
            "real ChEMBL release index outputs have been generated and passed sanity checks",
        )
        claims.write_text(text, encoding="utf-8")
    evidence = Path("paper/evidence_matrix.md")
    if evidence.exists():
        text = evidence.read_text(encoding="utf-8")
        text = text.replace("| C1 | `src/moltrustbench/data/build_release_index.py`, `src/moltrustbench/audit/exact_exposure.py` |", "| C1 | `src/moltrustbench/data/build_release_index.py`, `src/moltrustbench/audit/exact_exposure.py`, `src/moltrustbench/real_audit.py` |")
        text += "\n\nReal-data provenance: `results/logs/real_audit_gpu0/summary.json` records the GPU0-only ChEMBL release-index run. Fixture smoke artifacts are pipeline checks, not paper evidence.\n"
        evidence.write_text(text, encoding="utf-8")


def run_real_audit(
    *,
    releases: tuple[str, ...] = DEFAULT_RELEASES,
    cutoff_release: str = "CHEMBL30",
    raw_chembl_dir: str | Path = "data/raw/chembl",
    allow_tdc_failure: bool = False,
    moleculenet_fallback: str = "ClinTox",
) -> dict:
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"
    ledger = RunLedger()
    preflight = ledger.stage("preflight", lambda: _preflight(releases))
    manifests = ledger.stage("download_chembl_releases", lambda: _download_releases(releases, raw_dir=raw_chembl_dir))
    compound_index, scaffold_index, counts = ledger.stage("build_release_index", lambda: _build_release_index(manifests))
    benchmark_paths = ledger.stage("load_real_benchmarks", lambda: _load_real_benchmarks(allow_tdc_failure=allow_tdc_failure, moleculenet_fallback=moleculenet_fallback))
    annotation_paths = ledger.stage("annotate_exposure", lambda: _annotate_benchmarks(benchmark_paths, compound_index, scaffold_index, cutoff_release=cutoff_release))
    metrics = ledger.stage("run_baselines", lambda: _run_baselines(annotation_paths))
    ledger.stage("make_figures", lambda: (
        plot_release_histogram(counts),
        plot_exposure_heatmap(pd.read_csv("results/tables/exposure_summary.csv")),
        plot_performance_drop(metrics),
    ))
    _write_required_controls()
    _update_standardization_report(compound_index, benchmark_paths)
    sanity = ledger.stage("sanity_checks", lambda: run_sanity_checks(".", require_real_data=True))
    write_dataframe(sanity, "results/tables/sanity_report.csv")
    failed = sanity[(sanity["severity"] == "critical") & (sanity["status"] == "fail")]
    if failed.empty:
        _update_paper_status_after_real_run()
    ledger.stage("make_auto_report", generate_auto_report)
    summary = {
        "status": "completed" if failed.empty else "completed_with_sanity_failures",
        "data_mode": "real_chembl_release_index",
        "cutoff_release": cutoff_release,
        "releases": list(releases),
        "preflight": preflight,
        "compound_index_rows": int(len(compound_index)),
        "scaffold_index_rows": int(len(scaffold_index)),
        "benchmark_tasks": [str(path) for path in benchmark_paths],
        "annotation_paths": [str(path) for path in annotation_paths],
        "metrics_rows": int(len(metrics)),
        "failed_critical_checks": int(len(failed)),
    }
    ledger.write_summary(summary)
    if not failed.empty:
        raise RuntimeError("Real audit completed but sanity checks failed; see results/tables/sanity_report.csv")
    return summary


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release", action="append", default=None, choices=sorted(CHEMBL_RELEASES))
    parser.add_argument("--cutoff-release", default="CHEMBL30", choices=sorted(CHEMBL_RELEASES))
    parser.add_argument("--raw-chembl-dir", default="data/raw/chembl")
    parser.add_argument("--allow-tdc-failure", action="store_true")
    parser.add_argument("--moleculenet-fallback", default="ClinTox")
    args = parser.parse_args(argv)

    summary = run_real_audit(
        releases=tuple(args.release or DEFAULT_RELEASES),
        cutoff_release=args.cutoff_release,
        raw_chembl_dir=args.raw_chembl_dir,
        allow_tdc_failure=args.allow_tdc_failure,
        moleculenet_fallback=args.moleculenet_fallback,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
