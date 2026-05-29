"""Build a BIB-reviewable supplement table and data-availability package.

The package is intentionally table-first: it copies compact source-data tables
that support the paper claims, records checksums, and leaves large generated
tables in the data-freeze archive instead of duplicating them in the supplement.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pandas as pd
from pandas.errors import EmptyDataError


ROOT = Path(__file__).resolve().parents[1]
SUPP = ROOT / "paper" / "supplement"
TABLES = SUPP / "tables"


@dataclass(frozen=True)
class SupplementTable:
    table_id: str
    title: str
    source: str
    claim: str
    reviewer_role: str
    note: str


TABLE_PLAN = [
    SupplementTable(
        "Table_S1",
        "ChEMBL release-index summary",
        "results/tables/chembl_release_counts.csv",
        "C1/C2",
        "R4/R9",
        "Release dates are public observability dates, not model-training dates.",
    ),
    SupplementTable(
        "Table_S2",
        "Benchmark exposure summary across audited tasks",
        "results/tables/benchmark_coverage_exposure_summary.csv",
        "C1/C2",
        "R1/R2",
        "Exact, scaffold, and NN exposure are reported separately.",
    ),
    SupplementTable(
        "Table_S3",
        "Core BBBP/ClinTox exposure-adjusted baseline metrics",
        "results/tables/slice_metrics.csv",
        "C3",
        "R6/R8",
        "Milestone baseline metrics for standard and exact-removed slices.",
    ),
    SupplementTable(
        "Table_S4",
        "BACE/Tox21 C3 expansion metrics",
        "results/tables/bace_tox21_c3_summary.csv",
        "C3",
        "R6/R8",
        "Additional real benchmark tasks beyond BBBP/ClinTox.",
    ),
    SupplementTable(
        "Table_S5",
        "BACE/Tox21 sequence-family metrics",
        "results/tables/bace_tox21_sequence_summary.csv",
        "C3/C5",
        "R6/R8",
        "SMILES-CNN, SMILES-GRU, and SMILES-Transformer sequence baselines.",
    ),
    SupplementTable(
        "Table_S6",
        "Exposure-adjusted CI summary",
        "results/tables/exposure_delta_ci.csv",
        "C3",
        "R2/R6",
        "Bootstrap/seed-level CI for standard-vs-exposure-aware score deltas.",
    ),
    SupplementTable(
        "Table_S7",
        "Sequence-family CI summary",
        "results/tables/sequence_delta_ci.csv",
        "C3",
        "R2/R6",
        "CI table behind Fig. 5 and supplement sequence-delta claims.",
    ),
    SupplementTable(
        "Table_S8",
        "ESOL/Lipophilicity regression CI summary",
        "results/tables/regression_delta_ci.csv",
        "C3",
        "R8",
        "Regression robustness; Lipophilicity limitations remain explicit.",
    ),
    SupplementTable(
        "Table_S9",
        "Endpoint-native ChEMBL temporal metrics",
        "results/tables/chembl_endpoint_temporal_summary.csv",
        "C3/C4",
        "R4/R8/R10",
        "hERG/CYP temporal-validity sequence metrics with expected limitations.",
    ),
    SupplementTable(
        "Table_S10",
        "Endpoint SMILES-Transformer add-on metrics",
        "results/tables/chembl_endpoint_transformer_summary.csv",
        "C3",
        "R6/R8",
        "Transformer sequence add-on for endpoint-native tasks.",
    ),
    SupplementTable(
        "Table_S11",
        "Train-label-shuffle null-control comparisons",
        "results/tables/label_shuffle_null_control_comparison.csv",
        "C3",
        "R2/R6",
        "Negative control for exposure-adjusted deltas; not causal evidence.",
    ),
    SupplementTable(
        "Table_S12",
        "CYP label-shuffle rescue null summary",
        "results/tables/cyp_extension_label_shuffle_null_summary.csv",
        "C3",
        "R2/R6/R8",
        "CYP2C19 observed-vs-shuffled temporal-delta rescue snapshot.",
    ),
    SupplementTable(
        "Table_S15",
        "Assay-provenance task summary with DILI/hepatotoxicity",
        "results/tables/assay_provenance_task_summary_with_dili.csv",
        "C4",
        "R10",
        "Compact source table for assay conflict map.",
    ),
    SupplementTable(
        "Table_S16",
        "CYP1A2/CYP2C19 assay-provenance summary",
        "results/tables/cyp_endpoint_extension_assay_provenance_summary.csv",
        "C4",
        "R10",
        "Endpoint-native CYP provenance evidence.",
    ),
    SupplementTable(
        "Table_S17",
        "DILI/hepatotoxicity split and provenance boundary",
        "results/tables/dili_hepatotoxicity_split_summary.csv",
        "C4",
        "R8/R10",
        "Shows evaluable standard/scaffold splits and one-class exposure-removed slice limits.",
    ),
    SupplementTable(
        "Table_S18",
        "DILI/hepatotoxicity sequence summary",
        "results/tables/dili_hepatotoxicity_sequence_summary.csv",
        "C3/C4",
        "R8/R10",
        "Sequence baseline summary for the DILI/hepatotoxicity extension.",
    ),
    SupplementTable(
        "Table_S19",
        "Model pretraining registry",
        "results/tables/model_pretraining_registry.csv",
        "C5",
        "R5",
        "Separates model-corpus metadata from observable public exposure.",
    ),
    SupplementTable(
        "Table_S21",
        "Trust-card example source data",
        "results/tables/trust_card_examples.csv",
        "C5",
        "R6",
        "Source table for trust-card examples.",
    ),
    SupplementTable(
        "Table_S22",
        "Workflow artifact map",
        "results/tables/workflow_artifact_map.csv",
        "C5",
        "R6",
        "Links workflow stages to auditable outputs.",
    ),
]


EXPECTED_LIMITATION_FILES = [
    ("regression", "results/tables/regression_sequence_expected_limitations.csv", "results/tables/regression_sequence_critical_failures.csv"),
    ("endpoint_temporal", "results/tables/chembl_endpoint_temporal_expected_limitations.csv", "results/tables/chembl_endpoint_temporal_critical_failures.csv"),
    ("endpoint_transformer", "results/tables/chembl_endpoint_transformer_expected_limitations.csv", "results/tables/chembl_endpoint_transformer_critical_failures.csv"),
    ("label_shuffle", "results/tables/label_shuffle_expected_limitations.csv", "results/tables/label_shuffle_critical_failures.csv"),
    ("cyp_sequence", "results/tables/cyp_extension_sequence_expected_limitations.csv", "results/tables/cyp_extension_sequence_critical_failures.csv"),
    ("cyp_label_shuffle_rescue", "results/tables/cyp_extension_label_shuffle_rescue_expected_limitations.csv", "results/tables/cyp_extension_label_shuffle_rescue_critical_failures.csv"),
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def csv_rows(path: Path) -> int:
    if not path.exists():
        return -1
    try:
        return int(len(pd.read_csv(path)))
    except EmptyDataError:
        return 0


def latest_freeze() -> dict[str, str]:
    summaries = sorted((ROOT / "results" / "archive").glob("moltrustbench_data_freeze_*_summary.json"), key=lambda p: p.stat().st_mtime)
    if not summaries:
        return {}
    data = json.loads(summaries[-1].read_text(encoding="utf-8"))
    archive = Path(data.get("archive", ""))
    manifest = Path(data.get("manifest", ""))
    return {
        "timestamp": str(data.get("timestamp", "")),
        "archive": archive.name if archive.name else str(data.get("archive", "")),
        "manifest": manifest.name if manifest.name else str(data.get("manifest", "")),
        "sha256": str(data.get("archive_sha256", "")),
        "file_count": str(data.get("file_count", "")),
        "total_bytes": str(data.get("total_bytes", "")),
    }


def write_expected_limitations() -> Path:
    rows = []
    for block, expected_rel, critical_rel in EXPECTED_LIMITATION_FILES:
        expected = ROOT / expected_rel
        critical = ROOT / critical_rel
        rows.append(
            {
                "evidence_block": block,
                "expected_limitation_path": expected_rel,
                "expected_limitation_rows": csv_rows(expected),
                "critical_failure_path": critical_rel,
                "critical_failure_rows": csv_rows(critical),
                "interpretation": "expected exposure-removed/class-limit boundary, not paper evidence failure",
            }
        )
    out = TABLES / "Table_S23_expected_limitations_summary.csv"
    pd.DataFrame(rows).to_csv(out, index=False)
    return out


def read_csv_safe(rel_path: str) -> pd.DataFrame:
    path = ROOT / rel_path
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except EmptyDataError:
        return pd.DataFrame()


REVIEWER_COLUMN_RENAMES = {
    "median_label_conflict_score": "median_derived_label_discordance_score",
}


def write_reviewer_table_copy(src: Path, dst: Path) -> None:
    """Copy a compact reviewer-facing CSV while normalizing conservative terms."""
    if src.suffix.lower() != ".csv":
        shutil.copy2(src, dst)
        return
    try:
        df = pd.read_csv(src)
    except EmptyDataError:
        dst.write_text("", encoding="utf-8")
        return
    df = df.rename(columns=REVIEWER_COLUMN_RENAMES)
    df.to_csv(dst, index=False)


def read_parquet_rows(path: Path) -> tuple[int | None, str]:
    if not path.exists():
        return None, "missing"
    try:
        return len(pd.read_parquet(path)), "available"
    except Exception as exc:  # pragma: no cover - depends on optional parquet backend
        return None, f"unreadable: {type(exc).__name__}"


def parse_label_counts(value: object) -> tuple[int | None, int | None, bool | None]:
    if pd.isna(value):
        return None, None, None
    try:
        counts = json.loads(str(value).replace("'", '"'))
    except json.JSONDecodeError:
        return None, None, None
    positive = 0
    negative = 0
    for key, count in counts.items():
        key_text = str(key)
        if key_text in {"1", "1.0", "True", "true"}:
            positive += int(count)
        elif key_text in {"0", "0.0", "False", "false"}:
            negative += int(count)
    classes = sum(1 for count in counts.values() if int(count) > 0)
    return negative, positive, classes < 2


def task_from_annotation_path(value: object) -> str:
    text = str(value or "")
    stem = Path(text).stem
    if not stem:
        return ""
    stem = stem.replace("_exposure", "")
    stem = stem.replace("chembl_", "")
    stem = stem.replace("moleculenet_", "")
    return stem


def split_task_dir(source_name: object, task_name: object) -> Path:
    source = str(source_name or "").strip()
    task = str(task_name or "").strip()
    if source == "chembl_bioactivity":
        return ROOT / "data" / "splits" / f"chembl_bioactivity_{task}"
    return ROOT / "data" / "splits" / f"{source}_{task}"


def infer_annotation_path(source_name: object, task_name: object) -> Path | None:
    source = str(source_name or "").strip()
    task = str(task_name or "").strip()
    candidates = []
    if source and task:
        candidates.extend(
            [
                ROOT / "results" / "benchmark_annotations" / f"{source}_{task}_exposure.parquet",
                ROOT / "results" / "benchmark_annotations" / f"moleculenet_{task}_exposure.parquet",
                ROOT / "data" / "processed" / "benchmarks" / f"{source}_{task}.parquet",
                ROOT / "data" / "processed" / "benchmarks" / f"chembl_{task}.parquet",
            ]
        )
    for candidate in candidates:
        if candidate.exists():
            return candidate
    matches = list((ROOT / "results" / "benchmark_annotations").glob(f"*{task}*_exposure.parquet"))
    if matches:
        return matches[0]
    matches = list((ROOT / "data" / "processed" / "benchmarks").glob(f"*{task}*.parquet"))
    return matches[0] if matches else None


def _to_int(value: object) -> int | None:
    if value is None or value == "":
        return None
    try:
        if pd.isna(value):
            return None
    except TypeError:
        pass
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _count_matches(observed: object, expected: int | None) -> bool:
    observed_int = _to_int(observed)
    return expected is None or observed_int == expected


def _count_binary_labels(labels: pd.Series) -> tuple[int, int, int, bool]:
    numeric = pd.to_numeric(labels, errors="coerce").dropna()
    positive = int((numeric == 1.0).sum())
    negative = int((numeric == 0.0).sum())
    test_n = int(len(numeric))
    return negative, positive, test_n, positive == 0 or negative == 0


def label_counts_from_prediction(record: pd.Series, expected_test_n: int | None) -> tuple[int | None, int | None, int | None, bool | None, str]:
    run_id = str(record.get("run_id", "") or "")
    if not run_id:
        return None, None, None, None, "missing_run_id"
    pred_path = ROOT / "results" / "predictions" / f"{run_id}.parquet"
    if not pred_path.exists():
        return None, None, None, None, "missing_prediction_table"
    try:
        pred = pd.read_parquet(pred_path)
    except Exception as exc:  # pragma: no cover - depends on optional parquet backend
        return None, None, None, None, f"unreadable_prediction_table:{type(exc).__name__}"
    label_col = "label" if "label" in pred.columns else "y_true" if "y_true" in pred.columns else ""
    if not label_col:
        return None, None, None, None, "missing_prediction_label_column"
    neg, pos, test_n, one_class = _count_binary_labels(pred[label_col])
    if not _count_matches(test_n, expected_test_n):
        return None, None, None, None, f"prediction_test_n_mismatch:{test_n}!={expected_test_n}"
    return neg, pos, test_n, one_class, f"results/predictions/{run_id}.parquet"


def label_counts_from_split(source_name: object, task_name: object, split_name: object, expected_test_n: int | None = None) -> tuple[int | None, int | None, int | None, bool | None, str]:
    split = str(split_name or "").strip()
    annotation_path = infer_annotation_path(source_name, task_name)
    if annotation_path is None or not split:
        return None, None, None, None, "missing_annotation_or_split"
    try:
        df = pd.read_parquet(annotation_path)
    except Exception as exc:  # pragma: no cover - depends on optional parquet backend
        return None, None, None, None, f"unreadable_annotation:{type(exc).__name__}"
    split_path = split_task_dir(source_name, task_name) / f"{split}.json"
    label_col = "label" if "label" in df.columns else ""
    if not label_col:
        return None, None, None, None, "missing_label_column"
    if split_path.exists():
        try:
            split_data = json.loads(split_path.read_text(encoding="utf-8"))
        except Exception as exc:
            return None, None, None, None, f"unreadable_split_json:{type(exc).__name__}"
        test_indices = split_data.get("indices", {}).get("test", [])
        if test_indices:
            labels = df.iloc[test_indices][label_col]
            neg, pos, test_n, one_class = _count_binary_labels(labels)
            if _count_matches(test_n, expected_test_n):
                return neg, pos, test_n, one_class, "split_json"
        elif expected_test_n in {None, 0}:
            return 0, 0, 0, True, "split_json"
    if "split" in df.columns:
        subset = df[df["split"].astype(str).str.lower() == "test"].copy()
        if split == "exact_removed" and "exact_exposed" in subset.columns:
            subset = subset[~subset["exact_exposed"].astype(bool)]
        elif split == "scaffold_removed" and "scaffold_exposed" in subset.columns:
            subset = subset[~subset["scaffold_exposed"].astype(bool)]
        elif split == "nn08_removed" and "nn_exposed_08" in subset.columns:
            subset = subset[~subset["nn_exposed_08"].astype(bool)]
        elif split != "standard":
            return None, None, None, None, "missing_split_json"
        neg, pos, test_n, one_class = _count_binary_labels(subset[label_col])
        if _count_matches(test_n, expected_test_n):
            return neg, pos, test_n, one_class, "annotation_test_split_fallback"
        return None, None, None, None, f"annotation_test_n_mismatch:{test_n}!={expected_test_n}"
    else:
        return None, None, None, None, "missing_split_json"


def split_summary_count_map() -> dict[tuple[str, str, str], dict[str, object]]:
    mapping: dict[tuple[str, str, str], dict[str, object]] = {}
    for rel_path in [
        "results/tables/bace_tox21_c3_split_summary.csv",
        "results/tables/cyp_endpoint_extension_split_summary.csv",
        "results/tables/dili_hepatotoxicity_split_summary.csv",
    ]:
        df = read_csv_safe(rel_path)
        for _, record in df.iterrows():
            neg, pos, one_class = parse_label_counts(record.get("test_label_counts"))
            key = (str(record.get("source_name", "")), str(record.get("task_name", "")), str(record.get("split_name", "")))
            mapping[key] = {
                "negative_n": neg,
                "positive_n": pos,
                "test_n": record.get("test_n", ""),
                "one_class_flag": one_class,
                "class_count_source": rel_path,
            }
    for rel_path in [
        "results/tables/temporal_split_summary.csv",
        "results/tables/bace_tox21_c3_temporal_split_summary.csv",
    ]:
        df = read_csv_safe(rel_path)
        for _, record in df.iterrows():
            split_name = str(record.get("split_name", ""))
            if not split_name.endswith("_test"):
                continue
            key = (str(record.get("source_name", "")), str(record.get("task_name", "")), "temporal_future")
            positive = record.get("positive_n", "")
            negative = record.get("negative_n", "")
            try:
                one_class = int(positive) == 0 or int(negative) == 0
            except Exception:
                one_class = ""
            mapping[key] = {
                "negative_n": negative,
                "positive_n": positive,
                "test_n": record.get("n", ""),
                "one_class_flag": one_class,
                "class_count_source": rel_path,
            }
    return mapping


def ci_key_set() -> set[tuple[str, str, str, str]]:
    keys: set[tuple[str, str, str, str]] = set()
    for rel_path in [
        "results/tables/exposure_delta_ci.csv",
        "results/tables/sequence_delta_ci.csv",
    ]:
        df = read_csv_safe(rel_path)
        for _, record in df.iterrows():
            keys.add(
                (
                    str(record.get("source_name", "")),
                    str(record.get("task_name", "")),
                    str(record.get("model_id", "")),
                    str(record.get("comparison_split", "")),
                )
            )
    df = read_csv_safe("results/tables/regression_delta_ci.csv")
    for _, record in df.iterrows():
        keys.add(
            (
                str(record.get("source_name", "")),
                str(record.get("task_name", "")),
                str(record.get("model_id", "")),
                str(record.get("comparison_split", "")),
            )
        )
    return keys


def ci_source_for(row: dict[str, object], ci_keys: set[tuple[str, str, str, str]]) -> tuple[bool, str]:
    key = (
        str(row.get("source_name", "")),
        str(row.get("task_name", "")),
        str(row.get("model_id", "")),
        str(row.get("split_name", "")),
    )
    if key not in ci_keys:
        return False, ""
    task = key[1]
    if task in {"ESOL", "Lipophilicity"}:
        return True, "results/tables/regression_delta_ci.csv"
    if key[2] in {"smiles_cnn", "smiles_gru", "smiles_transformer"} and task in {"BACE", "Tox21"}:
        return True, "results/tables/sequence_delta_ci.csv"
    return True, "results/tables/exposure_delta_ci.csv"


def counts_for_metric(record: pd.Series, summary_counts: dict[tuple[str, str, str], dict[str, object]]) -> dict[str, object]:
    source = str(record.get("source_name", ""))
    task = str(record.get("task_name", ""))
    split = str(record.get("split_name", ""))
    expected_test_n = _to_int(record.get("test_n", record.get("n", "")))

    neg, pos, test_n, one_class, count_source = label_counts_from_prediction(record, expected_test_n)
    if test_n is not None:
        return {
            "negative_n": neg if neg is not None else "",
            "positive_n": pos if pos is not None else "",
            "test_n": test_n,
            "one_class_flag": one_class if one_class is not None else "",
            "class_count_source": count_source,
        }

    key = (source, task, split)
    if key in summary_counts:
        summary = summary_counts[key]
        if _count_matches(summary.get("test_n", ""), expected_test_n):
            return summary

    neg, pos, test_n, one_class, count_source = label_counts_from_split(source, task, split, expected_test_n)
    if test_n is not None:
        return {
            "negative_n": neg if neg is not None else "",
            "positive_n": pos if pos is not None else "",
            "test_n": test_n,
            "one_class_flag": one_class if one_class is not None else "",
            "class_count_source": count_source,
        }

    if key in summary_counts and not _count_matches(summary_counts[key].get("test_n", ""), expected_test_n):
        count_source = f"summary_test_n_mismatch:{summary_counts[key].get('test_n', '')}!={expected_test_n};{count_source}"
    return {
        "negative_n": neg if neg is not None else "",
        "positive_n": pos if pos is not None else "",
        "test_n": expected_test_n if expected_test_n is not None else record.get("test_n", ""),
        "one_class_flag": one_class if one_class is not None else "",
        "class_count_source": count_source,
    }


def write_slice_validity_master() -> Path:
    """Create a reviewer table for slice validity and expected limitations."""

    summary_counts = split_summary_count_map()
    ci_keys = ci_key_set()
    rows: list[dict[str, object]] = []
    metric_sources = [
        ("core_slice_metrics", "results/tables/slice_metrics.csv"),
        ("bace_tox21_classical_metrics", "results/tables/bace_tox21_c3_slice_metrics.csv"),
        ("bace_tox21_sequence_metrics", "results/tables/bace_tox21_sequence_slice_metrics.csv"),
        ("endpoint_temporal_metrics", "results/tables/chembl_endpoint_temporal_metrics.csv"),
        ("endpoint_transformer_metrics", "results/tables/chembl_endpoint_transformer_metrics.csv"),
        ("cyp_sequence_metrics", "results/tables/cyp_extension_sequence_metrics.csv"),
        ("dili_sequence_metrics", "results/tables/dili_hepatotoxicity_sequence_metrics.csv"),
        ("fm_molformer_metrics", "results/tables/fm_embedding_slice_metrics.csv"),
        ("fm_chemberta_metrics", "results/tables/chemberta_100m_fm_slice_metrics.csv"),
        ("regression_sequence_metrics", "results/tables/regression_sequence_slice_metrics.csv"),
    ]
    for block_name, rel_path in metric_sources:
        df = read_csv_safe(rel_path)
        for _, record in df.iterrows():
            counts = counts_for_metric(record, summary_counts)
            is_regression = str(record.get("task_type", "")).lower() == "regression" or str(record.get("task_name", "")) in {"ESOL", "Lipophilicity"}
            row = {
                "source_name": record.get("source_name", ""),
                "task_name": record.get("task_name", ""),
                "model_id": record.get("model_id") or record.get("architecture") or record.get("fm_model_id") or "",
                "split_name": record.get("split_name", ""),
            }
            ci_available, ci_source = ci_source_for(row, ci_keys)
            has_metric = any(pd.notna(record.get(col)) for col in ["auroc", "auprc", "rmse", "mae", "r2", "primary_score"])
            has_counts = _to_int(counts.get("positive_n", "")) is not None and _to_int(counts.get("negative_n", "")) is not None
            positive_n = counts.get("positive_n", "")
            negative_n = counts.get("negative_n", "")
            one_class_flag = counts.get("one_class_flag", "")
            known_one_class = one_class_flag is True or str(one_class_flag).lower() == "true"
            if has_metric and not has_counts and is_regression:
                positive_n = "not_applicable_regression"
                negative_n = "not_applicable_regression"
                one_class_flag = "not_applicable"
                metric_valid = True
                reason = "VALID_REGRESSION_METRIC_CLASS_COUNTS_NOT_APPLICABLE"
            elif has_metric and has_counts and known_one_class and not is_regression:
                metric_valid = False
                reason = "ONE_CLASS_AUROC_INVALID"
            elif has_metric and not has_counts:
                positive_n = "not_recoverable_from_archived_source"
                negative_n = "not_recoverable_from_archived_source"
                one_class_flag = "unknown"
                metric_valid = True
                reason = "VALID_METRIC_CLASS_COUNTS_NOT_RECOVERABLE_FROM_ARCHIVE"
            else:
                metric_valid = bool(has_metric)
                reason = "VALID_METRIC_WITH_CLASS_COUNTS" if has_metric else "NO_VALID_PRIMARY_METRIC"
            rows.append(
                {
                    "source_table": rel_path,
                    "source_block": block_name,
                    "source_name": row["source_name"],
                    "task_name": row["task_name"],
                    "model_family": record.get("model_family") or record.get("model_backend") or record.get("fm_model_id") or "",
                    "model_id": row["model_id"],
                    "split_name": row["split_name"],
                    "test_n": counts.get("test_n", record.get("test_n", "")),
                    "positive_n": positive_n,
                    "negative_n": negative_n,
                    "one_class_flag": one_class_flag,
                    "metric_validity_flag": metric_valid,
                    "ci_available": ci_available,
                    "ci_source_table": ci_source,
                    "class_count_source": counts.get("class_count_source", ""),
                    "reason_code": reason,
                    "reviewer_note": "Report sample size, class balance, and CI coverage before interpreting exposure-adjusted deltas.",
                }
            )

    for block, expected_rel, _critical_rel in EXPECTED_LIMITATION_FILES:
        df = read_csv_safe(expected_rel)
        for _, record in df.iterrows():
            rows.append(
                {
                    "source_table": expected_rel,
                    "source_block": block,
                    "source_name": "",
                    "task_name": task_from_annotation_path(record.get("annotation_path")),
                    "model_family": record.get("architecture", ""),
                    "model_id": record.get("architecture", ""),
                    "split_name": record.get("split_name", ""),
                    "test_n": "",
                    "positive_n": "",
                    "negative_n": "",
                    "one_class_flag": True,
                    "metric_validity_flag": False,
                    "ci_available": False,
                    "ci_source_table": "",
                    "class_count_source": expected_rel,
                    "reason_code": record.get("failure_class") or "EXPECTED_EXPOSURE_REMOVED_SLICE_LIMITATION",
                    "reviewer_note": str(record.get("error", ""))[:240],
                }
            )

    out = TABLES / "Table_S24_slice_validity_master.csv"
    pd.DataFrame(rows).to_csv(out, index=False)
    return out


def write_standardization_audit() -> Path:
    report_path = ROOT / "data" / "processed" / "standardization_report.json"
    report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.exists() else {}
    rejected = ROOT / "data" / "processed" / "rejected_molecules.csv"
    rejected_rows = csv_rows(rejected) if rejected.exists() else 0
    columns = [
        "dataset_id",
        "dataset_kind",
        "raw_rows",
        "standardized_rows",
        "rejected_rows",
        "unique_inchikeys",
        "duplicate_rows_retained",
        "duplicate_rows_removed",
        "duplicate_policy",
        "scaffold_available_rows",
        "exact_annotation_rows",
        "exposure_annotation_rows",
        "standardization_backend",
        "policy_notes",
    ]
    rows: list[dict[str, object]] = [
        {
            "dataset_id": "ChEMBL release index",
            "dataset_kind": "release_index",
            "raw_rows": report.get("compound_index_rows", ""),
            "standardized_rows": report.get("compound_index_rows", ""),
            "rejected_rows": "",
            "unique_inchikeys": report.get("compound_index_rows", ""),
            "duplicate_rows_retained": "",
            "duplicate_rows_removed": "",
            "duplicate_policy": "collapsed to earliest public release by standard InChIKey and scaffold",
            "scaffold_available_rows": "",
            "exact_annotation_rows": "",
            "exposure_annotation_rows": "",
            "standardization_backend": ";".join(report.get("standardization_backends", [])),
            "policy_notes": report.get("note", ""),
        }
    ]
    for path in sorted((ROOT / "data" / "processed" / "benchmarks").glob("*.parquet")):
        row_count, status = read_parquet_rows(path)
        if path.name.startswith(("moleculenet", "tdc")) and isinstance(row_count, int) and row_count < 100:
            # These tiny processed files are smoke fixtures. The reviewer-facing
            # standardization audit uses real exposure-annotation tables below.
            continue
        unique_inchikeys = ""
        scaffold_rows = ""
        exposure_rows = ""
        exact_rows = ""
        try:
            df = pd.read_parquet(path)
            if "standard_inchikey" in df.columns:
                unique_inchikeys = int(df["standard_inchikey"].dropna().nunique())
            if "murcko_scaffold_smiles" in df.columns:
                scaffold_rows = int(df["murcko_scaffold_smiles"].notna().sum())
            if "exact_exposed" in df.columns:
                exact_rows = int(df["exact_exposed"].notna().sum())
                exposure_rows = int(len(df))
        except Exception:
            pass
        rows.append(
            {
                "dataset_id": path.stem,
                "dataset_kind": "endpoint_native_processed_benchmark",
                "raw_rows": row_count if row_count is not None else "",
                "standardized_rows": row_count if row_count is not None else "",
                "rejected_rows": 0 if row_count is not None else "",
                "unique_inchikeys": unique_inchikeys,
                "duplicate_rows_retained": (row_count - unique_inchikeys) if isinstance(row_count, int) and isinstance(unique_inchikeys, int) else "",
                "duplicate_rows_removed": 0 if row_count is not None else "",
                "duplicate_policy": "dataset rows retained unless downstream split construction removes duplicates",
                "scaffold_available_rows": scaffold_rows,
                "exact_annotation_rows": exact_rows,
                "exposure_annotation_rows": exposure_rows,
                "standardization_backend": "rdkit_benchmark_standardization",
                "policy_notes": f"{status}; salts/mixtures/stereochemistry handled by deterministic RDKit standardization where represented",
            }
        )
    for path in sorted((ROOT / "results" / "benchmark_annotations").glob("*_exposure.parquet")):
        row_count, status = read_parquet_rows(path)
        unique_inchikeys = ""
        scaffold_rows = ""
        exact_rows = ""
        try:
            df = pd.read_parquet(path)
            if "standard_inchikey" in df.columns:
                unique_inchikeys = int(df["standard_inchikey"].dropna().nunique())
            if "murcko_scaffold_smiles" in df.columns:
                scaffold_rows = int(df["murcko_scaffold_smiles"].notna().sum())
            if "exact_exposed" in df.columns:
                exact_rows = int(df["exact_exposed"].notna().sum())
        except Exception:
            pass
        rows.append(
            {
                "dataset_id": path.stem,
                "dataset_kind": "real_benchmark_exposure_annotation",
                "raw_rows": row_count if row_count is not None else "",
                "standardized_rows": row_count if row_count is not None else "",
                "rejected_rows": 0 if row_count is not None else "",
                "unique_inchikeys": unique_inchikeys,
                "duplicate_rows_retained": (row_count - unique_inchikeys) if isinstance(row_count, int) and isinstance(unique_inchikeys, int) else "",
                "duplicate_rows_removed": 0 if row_count is not None else "",
                "duplicate_policy": "annotation table preserves benchmark row identity and adds exposure fields",
                "scaffold_available_rows": scaffold_rows,
                "exact_annotation_rows": exact_rows,
                "exposure_annotation_rows": row_count if row_count is not None else "",
                "standardization_backend": "moltrustbench exposure annotation",
                "policy_notes": status,
            }
        )
    out = TABLES / "Table_S25_standardization_audit.csv"
    pd.DataFrame(rows, columns=columns).to_csv(out, index=False)
    return out


def write_assay_flag_dictionary() -> Path:
    rows = [
        {
            "flag_or_score": "duplicate_compound_count",
            "definition": "number of benchmark molecules with more than one public ChEMBL activity record under the provenance query",
            "denominator": "benchmark molecules with at least one matched ChEMBL activity record",
            "source_columns": "standard_inchikey, assay_id, document_id, activity_id",
            "interpretation_limit": "duplicate records indicate provenance heterogeneity, not necessarily label error",
        },
        {
            "flag_or_score": "conflicting_label_count",
            "definition": "number of molecules with threshold-derived positive and negative activity calls under the specified endpoint rule",
            "denominator": "molecules with activity records sufficient for threshold-derived calls",
            "source_columns": "standard_type, standard_relation, standard_value, standard_units, pchembl_value",
            "interpretation_limit": "derived-label discordance is a label-source reliability risk, not proof that the original benchmark label is wrong",
        },
        {
            "flag_or_score": "unit_inconsistency_count",
            "definition": "number of molecules with activity records reported in multiple standard units or incompatible units for the same endpoint family",
            "denominator": "molecules with public ChEMBL activity records",
            "source_columns": "standard_units, standard_type",
            "interpretation_limit": "unit heterogeneity may reflect assay/reporting diversity and requires endpoint-specific curation",
        },
        {
            "flag_or_score": "threshold_sensitive_count",
            "definition": "number of molecules whose derived label can change near the chosen activity threshold or under censored relation handling",
            "denominator": "molecules with quantitative or threshold-interpretable ChEMBL records",
            "source_columns": "standard_relation, standard_value, standard_units, pchembl_value",
            "interpretation_limit": "threshold sensitivity is reported as an audit flag, not a universal statement about biological activity",
        },
        {
            "flag_or_score": "binary_label_conflict",
            "definition": "DILI/hepatotoxicity text-evidence records contain both positive and negative/no-evidence labels before final filtering",
            "denominator": "molecules in the DILI/hepatotoxicity text-evidence provenance pilot",
            "source_columns": "positive_record_count, negative_record_count, activity_comment_count",
            "interpretation_limit": "text-derived provenance is a pilot source and should be treated as supplementary",
        },
        {
            "flag_or_score": "derived_label_discordance_score",
            "definition": "molecule-level continuous score summarizing threshold-derived label discordance across public activity records",
            "denominator": "molecules with multiple or threshold-interpretable ChEMBL records",
            "source_columns": "pchembl_min, pchembl_max, pchembl_range, positive_record_count, total_record_count",
            "interpretation_limit": "score is a provenance-risk descriptor and should not be used as ground-truth biological error",
        },
    ]
    out = TABLES / "Table_S26_assay_flag_dictionary.csv"
    pd.DataFrame(rows).to_csv(out, index=False)
    return out


def write_assay_examples() -> Path:
    rows: list[dict[str, object]] = []
    activities_rel = "results/tables/assay_provenance_activities.csv"
    activities = read_csv_safe(activities_rel)
    if not activities.empty:
        wanted_tasks = ["BBBP", "ClinTox", "hERG_pchembl5_pilot"]
        for task in wanted_tasks:
            task_df = activities[activities["task_name"].astype(str) == task].copy()
            if task_df.empty:
                continue
            group = task_df.groupby("standard_inchikey", dropna=False)
            task_df["duplicate_activity_count"] = task_df["standard_inchikey"].map(group.size())
            task_df["unit_count_for_molecule"] = task_df["standard_inchikey"].map(group["standard_units"].nunique(dropna=True))
            task_df["document_count_for_molecule"] = task_df["standard_inchikey"].map(group["document_id"].nunique(dropna=True))
            task_df["pchembl_numeric"] = pd.to_numeric(task_df.get("pchembl_value"), errors="coerce")
            task_df["derived_label"] = task_df["pchembl_numeric"].map(lambda value: "positive" if pd.notna(value) and value >= 5.0 else "negative" if pd.notna(value) else "not_threshold_interpretable")
            task_df["threshold_sensitive"] = task_df["pchembl_numeric"].between(4.5, 5.5, inclusive="both").fillna(False)
            task_df = task_df.sort_values(
                ["duplicate_activity_count", "unit_count_for_molecule", "threshold_sensitive"],
                ascending=[False, False, False],
            )
            for _, r in task_df.head(4).iterrows():
                rows.append(
                    {
                        "source_table": activities_rel,
                        "source_name": r.get("source_name", ""),
                        "task_name": r.get("task_name", ""),
                        "standard_inchikey": r.get("standard_inchikey", ""),
                        "assay_id": r.get("assay_id", ""),
                        "document_id": r.get("document_id", ""),
                        "document_chembl_id": r.get("document_chembl_id", ""),
                        "target_chembl_id": r.get("target_chembl_id", ""),
                        "standard_type": r.get("standard_type", ""),
                        "standard_relation": r.get("standard_relation", ""),
                        "standard_value": r.get("standard_value", ""),
                        "standard_units": r.get("standard_units", ""),
                        "pchembl_value": r.get("pchembl_value", ""),
                        "derived_label": r.get("derived_label", ""),
                        "duplicate_activity_count": int(r.get("duplicate_activity_count", 0)),
                        "unit_inconsistency_flag": bool(r.get("unit_count_for_molecule", 0) > 1),
                        "document_heterogeneity_flag": bool(r.get("document_count_for_molecule", 0) > 1),
                        "threshold_sensitive_flag": bool(r.get("threshold_sensitive", False)),
                        "reviewer_note": "Record-level example; derived labels are audit flags, not ground-truth corrections.",
                    }
                )

    for rel_path in [
        "data/processed/benchmarks/chembl_CYP1A2_pchembl5_temporal.parquet",
        "data/processed/benchmarks/chembl_CYP2C19_pchembl5_temporal.parquet",
    ]:
        path = ROOT / rel_path
        if not path.exists():
            continue
        try:
            cyp = pd.read_parquet(path)
        except Exception:
            continue
        cyp = cyp.sort_values(["source_activity_count", "unique_assay_count", "unique_document_count"], ascending=False)
        for _, r in cyp.head(3).iterrows():
            rows.append(
                {
                    "source_table": rel_path,
                    "source_name": r.get("source_name", "chembl_bioactivity"),
                    "task_name": r.get("task_name", ""),
                    "standard_inchikey": r.get("standard_inchikey", ""),
                    "assay_id": "aggregate_endpoint_dataset",
                    "document_id": "aggregate_endpoint_dataset",
                    "document_chembl_id": "",
                    "target_chembl_id": r.get("target_chembl_id", ""),
                    "standard_type": "pChEMBL aggregate",
                    "standard_relation": "thresholded_at_endpoint_rule",
                    "standard_value": r.get("median_pchembl", r.get("mean_pchembl", "")),
                    "standard_units": "pChEMBL",
                    "pchembl_value": r.get("median_pchembl", r.get("mean_pchembl", "")),
                    "derived_label": int(r.get("label", 0)) if pd.notna(r.get("label", "")) else "",
                    "duplicate_activity_count": int(r.get("source_activity_count", 0)),
                    "unit_inconsistency_flag": False,
                    "document_heterogeneity_flag": bool(int(r.get("unique_document_count", 0)) > 1),
                    "threshold_sensitive_flag": abs(float(r.get("median_pchembl", r.get("mean_pchembl", 0))) - float(r.get("endpoint_threshold_pchembl", 5.0))) <= 0.5,
                    "reviewer_note": "Endpoint-native CYP aggregate row; assay/document IDs are not redistributed in this compact table.",
                }
            )

    dili = read_csv_safe("results/tables/dili_hepatotoxicity_assay_provenance_summary.csv")
    if not dili.empty:
        for _, r in dili.sort_values(["binary_label_conflict", "label_conflict_score"], ascending=False).head(4).iterrows():
            rows.append(
                {
                    "source_table": "results/tables/dili_hepatotoxicity_assay_provenance_summary.csv",
                    "source_name": "chembl_bioactivity",
                    "task_name": "DILI_hepatotoxicity_binary_temporal",
                    "standard_inchikey": r.get("standard_inchikey", ""),
                    "assay_id": "text_evidence_summary",
                    "document_id": "text_evidence_summary",
                    "document_chembl_id": "",
                    "target_chembl_id": "",
                    "standard_type": "text-evidence binary label",
                    "standard_relation": "derived_from_activity_comment",
                    "standard_value": "",
                    "standard_units": "",
                    "pchembl_value": "",
                    "derived_label": "discordant" if bool(r.get("binary_label_conflict", False)) else "single_direction",
                    "duplicate_activity_count": int(r.get("duplicate_activity_count", 0)),
                    "unit_inconsistency_flag": bool(r.get("unit_inconsistency", False)),
                    "document_heterogeneity_flag": bool(int(r.get("unique_document_count", 0)) > 1),
                    "threshold_sensitive_flag": bool(r.get("threshold_sensitive", False)),
                    "reviewer_note": "Text-evidence provenance pilot; retained as supplementary label-source heterogeneity evidence.",
                }
            )
    out = TABLES / "Table_S27_assay_provenance_examples.csv"
    pd.DataFrame(rows).to_csv(out, index=False)
    return out


def write_required_controls_table() -> Path:
    rows = [
        ("R1", "State that public observability is not model-specific training inclusion.", "supported", "Interpretation-limits paragraph and conservative captions are in the manuscript."),
        ("R2", "Report density-matched controls, NN-threshold sensitivity, CI checks, and train-label-shuffle null controls.", "supported_with_caveats", "Controls are available, but they bound interpretation rather than proving causality."),
        ("R3", "Distinguish MolTrustBench from ADMET reliability, OOD, scaffold, activity-cliff, FM, and agent benchmarks.", "supported", "Novelty-boundary table keeps the article framed as a protocol/reporting standard."),
        ("R4", "Treat ChEMBL release dates as public-observability anchors, not model pretraining dates.", "supported", "Release-date interpretation is explicit in the abstract, methods, and figure captions."),
        ("R5", "Separate ChEMBL observability from whether models used ChEMBL.", "supported_with_caveats", "Model registry and FM wrapper text keep model-specific ChEMBL use unknown unless documented."),
        ("R6", "Show that the work is more than data cleaning.", "supported", "Exposure-adjusted evaluation, CIs, provenance, null controls, and trust cards are present."),
        ("R7", "Document FM wrapper scope without turning it into a broad FM leaderboard.", "supported_with_caveats", "MolFormer and ChemBERTa-100M are supplement-only wrapper-applicability checks."),
        ("R8", "Report exposure-removed slice size, class balance, metric validity, and expected limitations.", "supported_with_caveats", "Table S24 records slice validity and expected sample-size/class-balance limitations."),
        ("R9", "Show that standardization choices are auditable.", "supported", "Table S25 reports raw-to-standardized accounting and policy notes."),
        ("R10", "Define assay-provenance heterogeneity and threshold-derived label discordance.", "supported", "Tables S26-S27 define flags and provide record-derived examples."),
    ]
    out = TABLES / "Table_S20_required_controls.csv"
    df = pd.DataFrame(rows, columns=["risk", "required_control", "status", "caveat"])
    df.to_csv(out, index=False)
    return out


def write_fm_supplement_summary(table_id: str, source_rel: str, out_name: str) -> Path:
    df = read_csv_safe(source_rel)
    out = TABLES / out_name
    if df.empty:
        pd.DataFrame(columns=["fm_model_id", "task_name", "split_name", "valid_metric_rows", "expected_invalid_slice_rows", "wrapper_scope_note"]).to_csv(out, index=False)
        return out
    df = df.copy()
    for local_col in ["source_output_dir", "source_artifact_path", "metric_file", "metric_dir", "fm_model_artifact"]:
        if local_col in df.columns:
            df = df.drop(columns=[local_col])
    classification_cols = [col for col in ["auroc_mean", "auprc_mean", "auroc", "auprc"] if col in df.columns]
    balanced_cols = [col for col in ["balanced_accuracy_mean", "balanced_accuracy"] if col in df.columns]
    regression_cols = [col for col in ["rmse_mean", "mae_mean", "r2_mean", "rmse", "mae", "r2"] if col in df.columns]
    metric_cols = classification_cols + balanced_cols + regression_cols
    if metric_cols:
        df["valid_metric_value_count"] = df[metric_cols].notna().sum(axis=1)
        def metric_status(row: pd.Series) -> str:
            if classification_cols and row[classification_cols].notna().any():
                return "valid_auroc_auprc_rows"
            if regression_cols and row[regression_cols].notna().any():
                return "valid_regression_rows"
            if balanced_cols and row[balanced_cols].notna().any():
                return "balanced_accuracy_only_rows"
            return "expected_invalid_or_not_applicable_slice"

        df["metric_status"] = df.apply(metric_status, axis=1)
    else:
        df["valid_metric_value_count"] = 0
        df["metric_status"] = "summary_without_metric_columns"
    df["wrapper_scope_note"] = "supplement-only frozen-embedding wrapper applicability evidence; not model-specific ChEMBL-use evidence"
    df["source_table"] = source_rel
    df.to_csv(out, index=False)
    return out


def trust_card_schema_rows() -> list[dict[str, object]]:
    return [
        ("dataset_id", "string", True, "moleculenet:BBBP", "stable benchmark/task identifier", "C5"),
        ("cutoff_release", "string", True, "CHEMBL30", "public-observability cutoff used for exposure labels", "C1/C2"),
        ("n_molecules", "integer", True, 2039, "number of audited benchmark molecules", "C1"),
        ("exact_public_exposure_rate", "number", True, 0.8377, "fraction exactly observed by cutoff in indexed releases", "C1"),
        ("scaffold_public_exposure_rate", "number", True, 0.8779, "fraction with scaffold observed by cutoff", "C2"),
        ("nn_exposure_rate_08", "number", True, 0.8892, "fraction with nearest-neighbor similarity >=0.8 before cutoff", "C2"),
        ("exposure_removed_test_n", "integer", True, 331, "test size after exposure removal, with class-balance validity reported separately", "C3/R8"),
        ("assay_provenance_available", "boolean", True, True, "whether matched public assay provenance was extracted", "C4"),
        ("label_conflict_summary", "object", False, "{\"conflicting_label_count\": 677}", "provenance heterogeneity summary", "C4/R10"),
        ("primary_limitations", "array", True, "[\"ChEMBL-only lower bound\"]", "required caveats for interpretation", "R1/R4/R8"),
        ("source_artifacts", "array", True, "[\"results/tables/...\"]", "machine-readable artifacts behind the card", "C5"),
    ]


def write_trust_card_schema() -> tuple[Path, Path]:
    rows = [
        {
            "field_name": name,
            "type": typ,
            "required": required,
            "example": example,
            "description": description,
            "claim_role": claim_role,
        }
        for name, typ, required, example, description, claim_role in trust_card_schema_rows()
    ]
    csv_out = TABLES / "Table_S28_trust_card_schema.csv"
    pd.DataFrame(rows).to_csv(csv_out, index=False)

    examples_dir = SUPP / "trust_cards"
    examples_dir.mkdir(parents=True, exist_ok=True)
    required_fields = {str(row["field_name"]) for row in rows if bool(row["required"])}
    assay_frames = [
        read_csv_safe("results/tables/assay_provenance_task_summary_with_dili.csv"),
        read_csv_safe("results/tables/cyp_endpoint_extension_assay_provenance_summary.csv"),
    ]
    assay = pd.concat([df for df in assay_frames if not df.empty], ignore_index=True, sort=False) if any(not df.empty for df in assay_frames) else pd.DataFrame()
    assay_summaries: dict[tuple[str, str], dict[str, object]] = {}
    if not assay.empty:
        summary_fields = [
            ("molecules_with_activity", "molecules_with_activity"),
            ("duplicate_compound_count", "duplicate_compound_count"),
            ("conflicting_label_count", "conflicting_label_count"),
            ("unit_inconsistency_count", "unit_inconsistency_count"),
            ("threshold_sensitive_count", "threshold_sensitive_count"),
            ("median_label_conflict_score", "median_derived_label_discordance_score"),
            ("binary_label_conflict_count", "binary_label_conflict_count"),
            ("activity_coverage_rate", "activity_coverage_rate"),
        ]
        for _, r in assay.iterrows():
            key = (str(r.get("source_name", "")), str(r.get("task_name", "")))
            summary: dict[str, object] = {}
            for source_field, output_field in summary_fields:
                value = r.get(source_field, "")
                if pd.notna(value) and value != "":
                    if output_field.endswith("_count") or output_field == "molecules_with_activity":
                        summary[output_field] = int(value)
                    else:
                        summary[output_field] = float(value)
            if summary:
                assay_summaries[key] = summary
    assay_keys = set(assay_summaries)
    trust_source = read_csv_safe("results/tables/trust_card_examples.csv")
    if trust_source.empty:
        trust_source = read_csv_safe("results/tables/benchmark_coverage_exposure_summary.csv")
    records = [record.to_dict() for _, record in trust_source.iterrows()]
    seen = {(str(record.get("source_name", "")), str(record.get("task_name", ""))) for record in records}
    for path in sorted((ROOT / "results" / "report_cards").glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        key = (str(data.get("source_name", "")), str(data.get("task_name", "")))
        if key not in seen:
            data["exact_clean_molecules"] = data.get("exact_clean_molecules", data.get("exposure_removed_test_n", 0))
            records.append(data)
            seen.add(key)
    for record in records:
        source_name = str(record.get("source_name", ""))
        task_name = str(record.get("task_name", ""))
        dataset_id = f"{source_name}:{task_name}"
        provenance_summary = assay_summaries.get((source_name, task_name), {})
        if not provenance_summary and task_name == "hERG":
            provenance_summary = assay_summaries.get(("chembl_bioactivity", "hERG_pchembl5_pilot"), {})
        card = {
            "dataset_id": dataset_id,
            "source_name": source_name,
            "task_name": task_name,
            "cutoff_release": record.get("cutoff_release", "CHEMBL30"),
            "n_molecules": int(record.get("n_molecules", record.get("molecule_count", 0))),
            "exact_public_exposure_rate": float(record.get("exact_public_exposure_rate", record.get("exact_exposure_rate", 0.0))),
            "scaffold_public_exposure_rate": float(record.get("scaffold_public_exposure_rate", record.get("scaffold_exposure_rate", 0.0))),
            "nn_exposure_rate_08": float(record.get("nn_exposure_rate_08", record.get("nn_exposure_rate_08", 0.0))),
            "exposure_removed_test_n": int(record.get("exact_clean_molecules", record.get("exact_unobserved_count", 0))),
            "assay_provenance_available": bool(provenance_summary) or (source_name, task_name) in assay_keys or task_name in {"BBBP", "ClinTox", "hERG", "CYP1A2_pchembl5_temporal", "CYP2C19_pchembl5_temporal", "DILI_hepatotoxicity_binary_temporal"},
            "label_conflict_summary": provenance_summary,
            "primary_limitations": [
                "ChEMBL-indexed observable lower bound, not model-specific training evidence",
                "Exposure-removed subset size and class balance must be checked before interpreting deltas",
            ],
            "source_artifacts": [
                "results/tables/benchmark_coverage_exposure_summary.csv",
                "results/tables/trust_card_examples.csv",
                "paper/supplement/tables/Table_S24_slice_validity_master.csv",
                "paper/supplement/tables/Table_S28_trust_card_schema.csv",
            ],
            "interpretation": "Observable public-exposure lower bound; not evidence of model-specific training exposure.",
        }
        missing = sorted(required_fields.difference(card.keys()))
        if missing:
            raise ValueError(f"Trust-card example {dataset_id} missing required fields: {missing}")
        if not isinstance(card["primary_limitations"], list) or not isinstance(card["source_artifacts"], list):
            raise TypeError(f"Trust-card example {dataset_id} has invalid list fields")
        if not isinstance(card["label_conflict_summary"], dict):
            raise TypeError(f"Trust-card example {dataset_id} has invalid label_conflict_summary")
        out_name = f"{source_name}_{task_name}_card.json".replace("/", "_")
        (examples_dir / out_name).write_text(json.dumps(card, indent=2, sort_keys=True), encoding="utf-8")
    json_out = examples_dir / "trust_card_schema.json"
    schema = {
        "schema_name": "MolTrustBench benchmark trust card",
        "version": "2026-05-29",
        "interpretation": "public observability lower bound; not model-specific training-inclusion or memorization evidence",
        "fields": rows,
    }
    json_out.write_text(json.dumps(schema, indent=2), encoding="utf-8")
    return csv_out, json_out


def write_figure_source_data_map() -> Path:
    rows = [
        ("Fig. 1", "workflow_schematic.pdf", "results/tables/workflow_artifact_map.csv", "C5", "workflow stage-to-artifact source data"),
        ("Fig. 2", "release_histogram.pdf", "results/tables/chembl_release_counts.csv", "C1/R4", "ChEMBL release dates and molecule counts"),
        ("Fig. 3", "exposure_heatmap_coverage.pdf", "results/tables/benchmark_coverage_exposure_summary.csv", "C1/C2", "four-task exposure rates at CHEMBL30"),
        ("Fig. 4", "exposure_delta_ci.pdf", "results/tables/fig4_exposure_delta_ci_source.csv", "C3/R8", "standard-minus-comparison delta CI source"),
        ("Fig. 5A", "bace_tox21_sequence_model_family.pdf", "results/tables/fig5_sequence_family_delta_source.csv", "C3", "sequence-family AUROC deltas"),
        ("Fig. 5B", "bace_tox21_sequence_model_family.pdf", "results/tables/fig5_sequence_family_comparison_size_source.csv", "C3/R8", "comparison-slice test sizes"),
        ("Fig. 6", "assay_conflict_map.pdf", "results/tables/assay_provenance_task_summary_with_dili.csv", "C4/R10", "assay-provenance heterogeneity rates"),
        ("Fig. 7", "trust_card_examples.pdf", "results/tables/trust_card_examples.csv", "C5", "trust-card plotted examples"),
        ("Fig. S7", "label_shuffle_null_control.pdf", "results/tables/figS7_label_shuffle_source.csv", "R2/R6", "supplementary train-label-shuffle null-control source"),
    ]
    out_rows = []
    for figure, figure_file, source_path, claim, note in rows:
        src = ROOT / source_path
        supplement_source_path = ""
        status = "missing"
        if src.exists():
            safe_name = f"Source_{figure.replace(' ', '_').replace('.', '').replace('~', '')}_{Path(source_path).name}"
            dst = TABLES / safe_name
            write_reviewer_table_copy(src, dst)
            supplement_source_path = dst.relative_to(SUPP).as_posix()
            status = "available"
        out_rows.append(
            {
                "figure": figure,
                "figure_file": figure_file,
                "source_data_path": source_path,
                "supplement_source_path": supplement_source_path,
                "claim_or_risk": claim,
                "note": note,
                "source_status": status,
            }
        )
    out = TABLES / "Table_S29_figure_source_data_map.csv"
    pd.DataFrame(out_rows).to_csv(out, index=False)
    return out


def write_generated_reviewer_tables() -> list[dict[str, str]]:
    generated_specs = [
        ("Table_S13", "Frozen MolFormer embedding summary", lambda: write_fm_supplement_summary("Table_S13", "results/tables/fm_embedding_summary.csv", "Table_S13_fm_embedding_summary.csv"), "C3", "R5/R7", "Sanitized supplement-only MolFormer wrapper summary; local run paths removed."),
        ("Table_S14", "Frozen ChemBERTa-100M embedding summary", lambda: write_fm_supplement_summary("Table_S14", "results/tables/chemberta_100m_fm_summary.csv", "Table_S14_chemberta_100m_fm_summary.csv"), "C3", "R5/R7", "Sanitized supplement-only ChemBERTa-100M wrapper summary; local run paths removed."),
        ("Table_S20", "Current reviewer controls and reporting checklist", write_required_controls_table, "C5", "R1-R10", "Current reviewer-risk controls regenerated from the BIB hardening status."),
        ("Table_S24", "Slice-validity master table", write_slice_validity_master, "C3", "R8", "Sample sizes, class balance, metric validity, CI availability, and reason codes."),
        ("Table_S25", "Standardization audit summary", write_standardization_audit, "C1/C2", "R9", "Raw-to-standardized accounting and molecule-standardization policy notes."),
        ("Table_S26", "Assay-provenance flag dictionary", write_assay_flag_dictionary, "C4", "R10", "Definitions and denominators for assay-provenance heterogeneity flags."),
        ("Table_S27", "Assay-provenance example rows", write_assay_examples, "C4", "R10", "Compact examples showing how provenance flags are derived from records."),
        ("Table_S28", "Machine-readable trust-card schema", write_trust_card_schema, "C5", "R6", "Trust-card fields, required status, types, and JSON schema/examples."),
        ("Table_S29", "Figure source-data map", write_figure_source_data_map, "C5", "R6", "Source-data table for each main figure and key supplement figure."),
    ]
    rows = []
    for table_id, title, writer, claim, reviewer_role, note in generated_specs:
        generated = writer()
        if isinstance(generated, tuple):
            path = generated[0]
            extra = generated[1]
            note = f"{note} JSON schema/examples: {extra.relative_to(SUPP).as_posix()}."
        else:
            path = generated
        rows.append(
            {
                "table_id": table_id,
                "title": title,
                "claim": claim,
                "reviewer_role": reviewer_role,
                "source_path": "generated by scripts/make_bib_supplement_package.py",
                "supplement_path": path.relative_to(SUPP).as_posix(),
                "status": "available",
                "rows": str(csv_rows(path)),
                "bytes": str(path.stat().st_size),
                "sha256": sha256(path),
                "note": note,
            }
        )
    return rows


def copy_tables() -> list[dict[str, str]]:
    TABLES.mkdir(parents=True, exist_ok=True)
    manifest_rows: list[dict[str, str]] = []
    copied_paths: list[Path] = []

    for spec in TABLE_PLAN:
        src = ROOT / spec.source
        out_name = f"{spec.table_id}_{Path(spec.source).name}"
        dst = TABLES / out_name
        if src.exists():
            write_reviewer_table_copy(src, dst)
            copied_paths.append(dst)
        manifest_rows.append(
            {
                "table_id": spec.table_id,
                "title": spec.title,
                "claim": spec.claim,
                "reviewer_role": spec.reviewer_role,
                "source_path": spec.source,
                "supplement_path": f"tables/{out_name}" if src.exists() else "",
                "status": "available" if src.exists() else "missing",
                "rows": str(csv_rows(src)) if src.exists() else "",
                "bytes": str(dst.stat().st_size) if src.exists() else "",
                "sha256": sha256(dst) if src.exists() else "",
                "note": spec.note,
            }
        )

    expected = write_expected_limitations()
    manifest_rows.append(
        {
            "table_id": "Table_S23",
            "title": "Expected limitation and critical-failure accounting",
            "claim": "C3/C5",
            "reviewer_role": "R8",
            "source_path": "derived from expected-limitation and critical-failure tables",
            "supplement_path": "tables/Table_S23_expected_limitations_summary.csv",
            "status": "available",
            "rows": str(csv_rows(expected)),
            "bytes": str(expected.stat().st_size),
            "sha256": sha256(expected),
            "note": "Separates expected exposure-removed slice limits from critical failures.",
        }
    )
    copied_paths.append(expected)

    manifest_rows.extend(write_generated_reviewer_tables())
    manifest_rows.sort(key=lambda row: int(str(row["table_id"]).split("_S", 1)[1]))

    manifest = SUPP / "supplement_manifest.csv"
    with manifest.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(manifest_rows[0].keys()))
        writer.writeheader()
        writer.writerows(manifest_rows)
    return manifest_rows


def write_markdown(manifest_rows: list[dict[str, str]]) -> None:
    freeze = latest_freeze()
    lines = [
        "# MolTrustBench Supplementary Tables",
        "",
        "This supplement is organized as an audit-ready evidence package for Briefings in Bioinformatics. It maps compact source-data tables to claims C1-C5 and risk controls R1-R10. Large generated tables and raw-size artifacts are referenced through the data-freeze archive rather than duplicated here.",
        "",
        "Terminology: public exposure, observable exposure lower bound, temporal validity, exposure-adjusted evaluation, assay provenance, train-label-shuffle null control, and expected exposure-removed slice limitations.",
        "",
        "## Table Map",
        "",
        "| Table | Title | Claim | Reviewer role | Rows | Supplement file |",
        "| --- | --- | --- | --- | ---: | --- |",
    ]
    for row in manifest_rows:
        lines.append(
            f"| {row['table_id']} | {row['title']} | {row['claim']} | {row['reviewer_role']} | {row['rows'] or 'NA'} | `{row['supplement_path']}` |"
        )
    lines.extend(
        [
            "",
            "## Reviewer-Use Notes",
            "",
            "- Tables S1-S2 support public-exposure claims and should be read as observability lower bounds, not direct model-training evidence.",
            "- Tables S3-S12 support exposure-adjusted evaluation, CI stability checks, and train-label-shuffle null controls. They do not prove causality.",
            "- Tables S13-S14 are supplement-only frozen foundation-model wrapper checks. They do not imply that MolFormer or ChemBERTa-100M used ChEMBL during pretraining.",
            "- Tables S15-S18 support assay-provenance and DILI/hepatotoxicity evidence. DILI exact/NN/temporal/density exposure-removed slices are expected one-class limitations.",
            "- Table S23 is the expected-limitation boundary table: expected limitations are audit outputs, while critical-failure rows should remain zero for paper-facing claims.",
            "- Table S24 is the slice-validity master table and should be used whenever a score delta is interpreted.",
            "- Table S25 documents standardization assumptions and row accounting for R9.",
            "- Tables S26-S27 define assay-provenance flags and give compact record-derived examples for R10.",
            "- Table S28 and `trust_cards/` provide the machine-readable trust-card schema and examples behind the plotted cards.",
            "- Table S29 maps each main figure to its compact source-data table.",
            "",
            "## Data-Freeze Pointer",
            "",
        ]
    )
    if freeze:
        lines.extend(
            [
                f"- Current local freeze archive: `{freeze['archive']}`",
                f"- Manifest: `{freeze['manifest']}`",
                f"- SHA256: `{freeze['sha256']}`",
                f"- File count: `{freeze['file_count']}`",
                "",
                "If a newer freeze archive is created after this supplement, regenerate the package with `python scripts/make_bib_supplement_package.py`.",
            ]
        )
    else:
        lines.append("- No freeze archive found yet; create one before submission.")

    (SUPP / "supplementary_tables.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_data_availability() -> None:
    freeze = latest_freeze()
    archive_text = (
        f"`results/archive/{freeze['archive']}` (SHA256 `{freeze['sha256']}`; manifest `{freeze['manifest']}`)"
        if freeze
        else "`results/archive/<archive-to-be-deposited>.tgz`"
    )
    text = f"""# Data Availability Statement For BIB Submission

The data availability statement below is ready to paste after replacing the repository placeholder with a DOI or accession.

## Ready-To-Paste Draft

All processed data, exposure annotations, generated benchmark splits, summary tables, figure source data, supplementary tables, trust-card JSON examples, and analysis manifests needed to reproduce the results in this article are provided in the MolTrustBench evidence archive and supplement package: **[repository DOI/accession to be inserted]**. The local archive corresponding to this draft is {archive_text}. The supplement package under `paper/supplement/` includes Tables S1-S29, including slice validity, standardization audit, assay-flag definitions, provenance examples, trust-card schema, and figure source-data mapping. The archive excludes raw ChEMBL database dumps, local secrets, transient caches, and third-party model checkpoints. ChEMBL source releases are publicly available from the official ChEMBL downloads page, and benchmark datasets are available from their original public sources. Frozen foundation-model checkpoint artifacts are not redistributed in the archive; scripts record the staged checkpoint identifiers and reproduce embeddings when the corresponding public checkpoint is available under its own license. Code is available at the project repository **[GitHub URL and commit SHA to be inserted]**.

## Repository Actions Before Submission

- Deposit the current data-freeze archive, manifest, and BIB supplement package in a DOI-issuing repository such as Zenodo, Figshare, OSF, or Harvard Dataverse.
- Add the DOI/accession to the statement above and to `paper/latex/moltrustbench_main.tex`.
- Add the GitHub commit SHA or tagged release corresponding to the submitted manuscript.
- Include dataset citations in the reference list for ChEMBL and any third-party benchmark datasets used in the article.

## Placeholder Search Before Submission

- `[repository DOI/accession to be inserted]`
- `[GitHub URL and commit SHA to be inserted]`
- `DOI added during production`
- `Date added during production`
- `author@example.com`
- author, affiliation, funding, acknowledgment, and conflict-of-interest placeholders

## Risk Flags

- Do not state that raw ChEMBL SQLite or raw ChEMBL release tarballs are redistributed unless their licensing and size are explicitly handled by the repository deposit.
- Do not use "available on request" for generated result tables; BIB requires a Data Availability statement and strongly encourages public availability where ethically feasible.
- Model checkpoints should be cited or linked through their original hosts, not republished inside the evidence archive unless license terms allow it.
"""
    (SUPP / "data_availability_statement.md").write_text(text, encoding="utf-8")
    (ROOT / "paper" / "data_availability_bib.md").write_text(text, encoding="utf-8")


def write_readme() -> None:
    deposit = ROOT / "paper" / "deposit_readme.md"
    if deposit.exists():
        shutil.copy2(deposit, SUPP / "deposit_readme.md")
    text = """# MolTrustBench BIB Supplement Package

Contents:

- `supplementary_tables.md`: audit map from supplement tables to claims and risk controls.
- `supplement_manifest.csv`: source paths, row counts, checksums, and claim mapping.
- `data_availability_statement.md`: ready-to-paste BIB data availability draft with DOI placeholders.
- `deposit_readme.md`: repository-deposit checklist for DOI archive preparation.
- `tables/`: compact source-data CSVs for main and supplementary claims.
- `trust_cards/`: machine-readable trust-card schema and example JSON cards.

Large generated tables and raw-size artifacts are traceable through the data-freeze archive listed in `supplementary_tables.md`.
"""
    (SUPP / "README.md").write_text(text, encoding="utf-8")


def validate_package_tables() -> None:
    manifest = pd.read_csv(SUPP / "supplement_manifest.csv")
    missing = manifest[manifest["status"].astype(str) != "available"]
    if not missing.empty:
        raise ValueError(f"Supplement manifest has unavailable tables: {missing['table_id'].tolist()}")

    s20 = pd.read_csv(TABLES / "Table_S20_required_controls.csv")
    stale = s20[s20["status"].astype(str).str.contains("missing|pending", case=False, na=False)]
    if not stale.empty:
        raise ValueError(f"Table S20 has stale missing/pending statuses: {stale['risk'].tolist()}")

    s24 = pd.read_csv(TABLES / "Table_S24_slice_validity_master.csv")
    one_class_valid = s24[
        s24["one_class_flag"].astype(str).str.lower().eq("true")
        & s24["metric_validity_flag"].astype(str).str.lower().eq("true")
    ]
    if not one_class_valid.empty:
        raise ValueError("Table S24 marks one-class classification rows as metric-valid")

    s25 = pd.read_csv(TABLES / "Table_S25_standardization_audit.csv")
    fixture_rows = s25[
        s25["dataset_id"].astype(str).isin(["moleculenet_BBBP", "tdc_admet_hERG"])
        & (pd.to_numeric(s25["raw_rows"], errors="coerce") < 100)
    ]
    if not fixture_rows.empty:
        raise ValueError("Table S25 still exposes smoke-fixture row accounting as reviewer-facing benchmark accounting")

    s27 = pd.read_csv(TABLES / "Table_S27_assay_provenance_examples.csv")
    required_tasks = {"BBBP", "ClinTox", "hERG_pchembl5_pilot", "CYP1A2_pchembl5_temporal", "CYP2C19_pchembl5_temporal"}
    observed_tasks = set(s27.get("task_name", pd.Series(dtype=str)).astype(str))
    missing_tasks = sorted(required_tasks.difference(observed_tasks))
    if missing_tasks:
        raise ValueError(f"Table S27 missing provenance examples for: {missing_tasks}")

    s29 = pd.read_csv(TABLES / "Table_S29_figure_source_data_map.csv")
    if "Fig. 8" in set(s29["figure"].astype(str)):
        raise ValueError("Table S29 still maps a main Fig. 8 even though label shuffle is supplement-first")
    unavailable_sources = s29[s29["source_status"].astype(str) != "available"]
    if not unavailable_sources.empty:
        raise ValueError(f"Table S29 has missing source-data rows: {unavailable_sources['figure'].tolist()}")

    schema = pd.read_csv(TABLES / "Table_S28_trust_card_schema.csv")
    required_fields = set(schema[schema["required"].astype(str).str.lower().eq("true")]["field_name"].astype(str))
    for path in (SUPP / "trust_cards").glob("*_card.json"):
        card = json.loads(path.read_text(encoding="utf-8"))
        missing_fields = sorted(required_fields.difference(card))
        if missing_fields:
            raise ValueError(f"{path.name} missing trust-card fields: {missing_fields}")
        if card.get("assay_provenance_available") and card.get("task_name") in {"BBBP", "ClinTox"} and not card.get("label_conflict_summary"):
            raise ValueError(f"{path.name} has assay provenance but an empty label_conflict_summary")


def zip_package() -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = SUPP / f"MolTrustBench_BIB_supplement_package_{stamp}.zip"
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(SUPP.rglob("*")):
            if path == out or path.suffix == ".zip":
                continue
            if path.is_file():
                zf.write(path, path.relative_to(SUPP).as_posix())
    return out


def reset_generated_outputs() -> None:
    for path in (TABLES, SUPP / "trust_cards"):
        if path.exists():
            shutil.rmtree(path)
        path.mkdir(parents=True, exist_ok=True)


def main() -> None:
    SUPP.mkdir(parents=True, exist_ok=True)
    reset_generated_outputs()
    manifest_rows = copy_tables()
    write_markdown(manifest_rows)
    write_data_availability()
    write_readme()
    validate_package_tables()
    package = zip_package()
    print(f"SUPPLEMENT_PACKAGE={package}")
    print(f"SUPPLEMENT_MANIFEST={SUPP / 'supplement_manifest.csv'}")


if __name__ == "__main__":
    main()
