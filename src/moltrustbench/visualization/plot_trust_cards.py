"""Plot benchmark trust-card examples from generated report-card JSON files."""

from __future__ import annotations

import argparse
from pathlib import Path
from textwrap import fill

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
import pandas as pd

from moltrustbench.reporting.make_report_cards import load_report_cards


REAL_TASK_ORDER = ["BBBP", "ClinTox", "BACE", "Tox21"]


def _setup_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
            "pdf.fonttype": 42,
            "svg.fonttype": "none",
            "font.size": 7,
            "axes.spines.right": False,
            "axes.spines.top": False,
        }
    )


def _risk_color(risk: str) -> tuple[str, str]:
    risk = str(risk).lower()
    if risk == "high":
        return "#f7e8df", "#b05a3c"
    if risk == "medium":
        return "#edf1df", "#7b8a35"
    return "#e7f0ef", "#39766a"


def _load_display_cards(card_dir: str | Path) -> list[dict]:
    cards = load_report_cards(card_dir)
    by_task = {card.get("task_name"): card for card in cards}
    selected = [by_task[task] for task in REAL_TASK_ORDER if task in by_task]
    if selected:
        return selected
    return sorted(cards, key=lambda item: (item.get("source_name", ""), item.get("task_name", "")))[:4]


def write_trust_card_table(cards: list[dict], output: str | Path) -> pd.DataFrame:
    rows = []
    for card in cards:
        rows.append(
            {
                "source_name": card.get("source_name"),
                "task_name": card.get("task_name"),
                "cutoff_release": card.get("cutoff_release"),
                "n_molecules": card.get("n_molecules"),
                "exact_public_exposure_rate": card.get("exact_public_exposure_rate"),
                "scaffold_public_exposure_rate": card.get("scaffold_public_exposure_rate"),
                "nn_exposure_rate_08": card.get("nn_exposure_rate_08"),
                "exposure_removed_test_n": card.get("exposure_removed_test_n", card.get("exact_clean_molecules")),
                "risk_level": card.get("risk_level"),
                "interpretation": card.get("interpretation"),
            }
        )
    table = pd.DataFrame(rows)
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(path, index=False)
    return table


def _draw_meter(ax, x: float, y: float, width: float, label: str, value: float, color: str) -> None:
    value = max(0.0, min(1.0, float(value)))
    ax.text(x, y + 0.026, label, fontsize=6.0, ha="left", va="bottom", color="#333333")
    ax.add_patch(Rectangle((x, y), width, 0.016, facecolor="#e6e6e6", edgecolor="none"))
    ax.add_patch(Rectangle((x, y), width * value, 0.016, facecolor=color, edgecolor="none"))
    ax.text(x + width + 0.012, y + 0.008, f"{value:.2f}", fontsize=6.0, ha="left", va="center", color="#333333")


def plot_trust_cards(
    *,
    card_dir: str | Path = "results/report_cards",
    output_pdf: str | Path = "results/figures/trust_card_examples.pdf",
    output_svg: str | Path | None = "results/figures/trust_card_examples.svg",
    output_table: str | Path = "results/tables/trust_card_examples.csv",
) -> pd.DataFrame:
    cards = _load_display_cards(card_dir)
    if not cards:
        raise FileNotFoundError(f"No report-card JSON files found in {card_dir}")
    table = write_trust_card_table(cards, output_table)
    _setup_style()

    fig, axes = plt.subplots(2, 2, figsize=(7.2, 4.7))
    axes_flat = axes.ravel()
    for ax in axes_flat:
        ax.set_axis_off()
    for ax, card in zip(axes_flat, cards):
        face, edge = _risk_color(card.get("risk_level", "unknown"))
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.add_patch(
            FancyBboxPatch(
                (0.02, 0.04),
                0.96,
                0.9,
                boxstyle="round,pad=0.012,rounding_size=0.014",
                linewidth=1.0,
                edgecolor=edge,
                facecolor=face,
            )
        )
        task = card.get("task_name", "Task")
        source = card.get("source_name", "source")
        ax.text(0.07, 0.88, task, fontsize=11, weight="bold", ha="left", va="center")
        ax.text(0.07, 0.815, f"{source} | cutoff {card.get('cutoff_release', 'NA')}", fontsize=6.4, color="#444444")
        risk = str(card.get("risk_level", "unknown")).upper()
        ax.text(0.92, 0.875, risk, fontsize=6.4, weight="bold", ha="right", va="center", color=edge)

        ax.text(0.07, 0.72, f"n = {int(card.get('n_molecules', 0)):,}", fontsize=7.0, ha="left")
        exposure_removed_n = int(card.get("exposure_removed_test_n", card.get("exact_clean_molecules", 0)))
        ax.text(0.36, 0.72, f"exact-unobserved n = {exposure_removed_n:,}", fontsize=7.0, ha="left")
        _draw_meter(ax, 0.07, 0.60, 0.52, "Exact public exposure", card.get("exact_public_exposure_rate", 0.0), edge)
        _draw_meter(ax, 0.07, 0.49, 0.52, "Scaffold public exposure", card.get("scaffold_public_exposure_rate", 0.0), edge)
        _draw_meter(ax, 0.07, 0.38, 0.52, "NN@0.8 public exposure", card.get("nn_exposure_rate_08", 0.0), edge)

        note = str(card.get("interpretation", "Observable public-exposure lower bound."))
        legacy_phrase = "confirmed model " + "leakage"
        note = note.replace(legacy_phrase, "model-specific training exposure")
        ax.text(0.07, 0.25, fill(note, width=46), fontsize=6.0, ha="left", va="top", color="#333333")
        ax.text(0.07, 0.105, "Report standard, exposure-removed, exposed, and caveats together.", fontsize=5.8, color="#555555")

    fig.suptitle("Benchmark trust-card examples", fontsize=10, weight="bold", x=0.04, ha="left", y=0.99)
    fig.text(
        0.04,
        0.945,
        "Trust cards expose public observability and exposure-removed subset limits before leaderboard scores are interpreted.",
        fontsize=7,
        color="#444444",
        ha="left",
    )
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    output_pdf = Path(output_pdf)
    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_pdf, bbox_inches="tight")
    if output_svg:
        fig.savefig(output_svg, bbox_inches="tight")
    plt.close(fig)
    return table


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--card-dir", default="results/report_cards")
    parser.add_argument("--output-pdf", default="results/figures/trust_card_examples.pdf")
    parser.add_argument("--output-svg", default="results/figures/trust_card_examples.svg")
    parser.add_argument("--output-table", default="results/tables/trust_card_examples.csv")
    args = parser.parse_args(argv)
    table = plot_trust_cards(
        card_dir=args.card_dir,
        output_pdf=args.output_pdf,
        output_svg=args.output_svg,
        output_table=args.output_table,
    )
    print(table.to_string(index=False))


if __name__ == "__main__":
    main()
