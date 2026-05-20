"""Result sanity checks for MolTrustBench."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from moltrustbench.io import read_dataframe, write_dataframe


REQUIRED_ARTIFACTS = [
    "paper/claims.md",
    "paper/auto_report.md",
    "results/release_index/compound_release_index.parquet",
    "results/release_index/scaffold_release_index.parquet",
    "results/tables/chembl_release_counts.csv",
    "results/tables/exposure_summary.csv",
    "results/tables/slice_metrics.csv",
    "results/figures/release_histogram.pdf",
    "results/figures/exposure_heatmap.pdf",
    "results/figures/performance_drop.pdf",
]


def _row(check: str, severity: str, status: str, detail: str) -> dict:
    return {"check": check, "severity": severity, "status": status, "detail": detail}


def run_sanity_checks(root: str | Path = ".", *, require_real_data: bool = False) -> pd.DataFrame:
    base = Path(root)
    rows: list[dict] = []
    for artifact in REQUIRED_ARTIFACTS:
        path = base / artifact
        rows.append(_row(f"artifact_exists:{artifact}", "critical", "pass" if path.exists() else "fail", str(path)))

    exposure_path = base / "results/tables/exposure_summary.csv"
    if exposure_path.exists():
        exposure = pd.read_csv(exposure_path)
        rows.append(_row("exposure_summary_nonempty", "critical", "pass" if len(exposure) >= 2 else "fail", f"rows={len(exposure)}"))
        for column in ["exact_exposure_rate", "scaffold_exposure_rate", "nn_exposure_rate_08"]:
            if column in exposure:
                ok = exposure[column].between(0, 1).all()
                rows.append(_row(f"exposure_rate_bounds:{column}", "critical", "pass" if ok else "fail", column))

    slice_path = base / "results/tables/slice_metrics.csv"
    if slice_path.exists():
        metrics = pd.read_csv(slice_path)
        rows.append(_row("slice_metrics_nonempty", "critical", "pass" if len(metrics) >= 4 else "fail", f"rows={len(metrics)}"))
        numeric = metrics.select_dtypes(include=[np.number])
        finite = bool(np.isfinite(numeric.to_numpy()).all()) if not numeric.empty else True
        rows.append(_row("slice_metrics_finite", "critical", "pass" if finite else "fail", "numeric metrics finite"))
        if "split_name" in metrics:
            has_standard = "standard" in set(metrics["split_name"])
            has_clean = "exact_removed" in set(metrics["split_name"])
            rows.append(_row("required_splits_present", "critical", "pass" if has_standard and has_clean else "fail", "standard and exact_removed"))

    for path in sorted((base / "results/benchmark_annotations").glob("*_exposure.parquet")):
        frame = read_dataframe(path)
        if "exact_exposed" in frame and "split" in frame:
            clean_test = frame[(frame["split"] == "test") & (~frame["exact_exposed"].fillna(False))]
            status = "pass" if len(clean_test) > 0 else "fail"
            rows.append(_row(f"clean_test_nonempty:{path.name}", "critical", status, f"clean_test={len(clean_test)}"))

    standardization_path = base / "data/processed/standardization_report.json"
    if standardization_path.exists():
        report = json.loads(standardization_path.read_text(encoding="utf-8"))
        mode = report.get("mode", "")
        backends = set(report.get("standardization_backends", []))
        if require_real_data:
            rows.append(_row("real_data_mode", "critical", "pass" if mode == "real_data_audit" else "fail", str(mode)))
        if mode == "real_data_audit" or require_real_data:
            no_fallback = "fallback-fixture-only" not in backends
            rows.append(_row("no_fixture_fallback_backend", "critical", "pass" if no_fallback else "fail", ",".join(sorted(backends))))

    return pd.DataFrame.from_records(rows)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--output", default="results/tables/sanity_report.csv")
    parser.add_argument("--fail-on-critical", action="store_true")
    parser.add_argument("--require-real-data", action="store_true")
    args = parser.parse_args(argv)
    report = run_sanity_checks(args.root, require_real_data=args.require_real_data)
    write_dataframe(report, args.output)
    failed = report[(report["severity"] == "critical") & (report["status"] == "fail")]
    print(report.to_string(index=False))
    if args.fail_on_critical and not failed.empty:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
