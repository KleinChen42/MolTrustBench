"""Generate paper/auto_report.md from result artifacts."""

from __future__ import annotations

from pathlib import Path
import json

import pandas as pd

from moltrustbench.reporting.make_report_cards import load_report_cards


def _table_or_empty(path: str | Path) -> pd.DataFrame:
    src = Path(path)
    if not src.exists():
        return pd.DataFrame()
    return pd.read_csv(src)


def _markdown_table(df: pd.DataFrame) -> str:
    if df.empty:
        return ""
    text_df = df.copy()
    for column in text_df.columns:
        text_df[column] = text_df[column].map(lambda value: f"{value:.4g}" if isinstance(value, float) else str(value))
    header = "| " + " | ".join(text_df.columns) + " |"
    divider = "| " + " | ".join(["---"] * len(text_df.columns)) + " |"
    rows = ["| " + " | ".join(row) + " |" for row in text_df.astype(str).to_numpy().tolist()]
    return "\n".join([header, divider, *rows])


def generate_auto_report(output_path: str | Path = "paper/auto_report.md") -> Path:
    exposure = _table_or_empty("results/tables/exposure_summary.csv")
    metrics = _table_or_empty("results/tables/slice_metrics.csv")
    sanity = _table_or_empty("results/tables/sanity_report.csv")
    cards = load_report_cards()
    standardization_report_path = Path("data/processed/standardization_report.json")
    standardization_report = json.loads(standardization_report_path.read_text(encoding="utf-8")) if standardization_report_path.exists() else {}
    mode = standardization_report.get("mode", "unknown")
    real_mode = mode == "real_data_audit"
    failed_sanity = 0 if sanity.empty else int((sanity["status"] == "fail").sum())
    c1_status = "supported" if real_mode and failed_sanity == 0 else "preliminary"
    c2_status = "supported" if real_mode and failed_sanity == 0 else "preliminary"
    provenance_sentence = (
        "This report is based on real ChEMBL release-index artifacts and RDKit standardization."
        if real_mode
        else "This report is based on fixture smoke artifacts; it validates the pipeline but is not paper evidence from real ChEMBL releases."
    )

    lines = [
        "# MolTrustBench Auto Report",
        "",
        "## Executive Summary",
        "",
        "MolTrustBench audits benchmark trustworthiness through observable public-exposure lower bounds, exposure-adjusted evaluation, and paper-facing trust cards. Milestone 1 implements the release-index, exposure-annotation, baseline-evaluation, figure, and sanity-check spine.",
        "",
        f"Data provenance: {provenance_sentence}",
        "",
        "## Claim-By-Claim Evidence Status",
        "",
        f"- C1 {c1_status}: exposure annotations and summary tables are generated.",
        f"- C2 {c2_status}: exact, scaffold, and nearest-neighbor exposure are separated.",
        "- C3 preliminary: standard and exact-removed baseline metrics are generated.",
        "- C4 missing: assay-provenance extraction remains a later-phase module.",
        "- C5 preliminary: benchmark trust cards and reporting checks are generated.",
        "",
        "## Exposure Audit Summary",
        "",
    ]
    if exposure.empty:
        lines.append("No exposure summary table found.")
    else:
        lines.append(_markdown_table(exposure))
    lines.extend(["", "## Performance Delta Summary", ""])
    if metrics.empty:
        lines.append("No slice metrics found.")
    else:
        display_cols = [col for col in ["source_name", "task_name", "model_id", "split_name", "test_n", "auroc", "auprc", "primary_score", "exposure_delta"] if col in metrics]
        lines.append(_markdown_table(metrics[display_cols]))
    lines.extend(["", "## Benchmark Trust Cards", ""])
    if not cards:
        lines.append("No trust cards found.")
    else:
        for card in cards:
            lines.append(
                f"- {card['source_name']}:{card['task_name']} cutoff {card['cutoff_release']} - "
                f"exact exposure {card['exact_public_exposure_rate']:.2f}, "
                f"scaffold exposure {card['scaffold_public_exposure_rate']:.2f}, "
                f"NN>=0.8 exposure {card['nn_exposure_rate_08']:.2f}, risk {card['risk_level']}."
            )
    lines.extend(
        [
            "",
            "## Reviewer Risk Table",
            "",
            "The core limitation is explicit: public exposure is an observable lower bound, not proof that a model trained on a molecule or memorized its label. Density-matched controls and assay-provenance diagnostics remain required before stronger causal claims.",
            "",
            "## Sanity Check Summary",
            "",
        ]
    )
    if sanity.empty:
        lines.append("No sanity report found.")
    else:
        failed = sanity[sanity["status"] == "fail"]
        lines.append(f"Critical/warning checks run: {len(sanity)}. Failed checks: {len(failed)}.")
        if not failed.empty:
            lines.append(_markdown_table(failed))
    lines.extend(
        [
            "",
            "## Next Experiments",
            "",
            "- Replace fixture smoke data with full CHEMBL24/27/30/33/36 SQLite release indexes.",
            "- Expand benchmark ingestion to more TDC ADMET, MoleculeNet selected tasks, and MoleculeACE.",
            "- Add scaffold-removed, NN-removed, temporal-future, and density-matched clean splits.",
            "- Implement assay-provenance extraction and conflict scoring for ChEMBL-derived endpoints.",
            "",
            "## Target Journal Positioning",
            "",
            "Primary target: Briefings in Bioinformatics as a reproducible bioinformatics resource and reporting standard. Patterns is appropriate for the benchmark-validity data-science framing. Archives of Toxicology becomes stronger after assay-provenance and ADMET/Tox label-conflict analyses are complete.",
            "",
        ]
    )
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    return out
