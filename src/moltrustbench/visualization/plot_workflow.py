"""Publication workflow schematic for MolTrustBench."""

from __future__ import annotations

import argparse
from pathlib import Path
from textwrap import fill

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import pandas as pd


WORKFLOW_STEPS = [
    {
        "step_id": "inputs",
        "title": "Benchmark inputs",
        "subtitle": "MoleculeNet, TDC, ChEMBL tasks",
        "module": "benchmark ingestion",
        "artifact": "data/processed/benchmarks",
        "x": 0.05,
        "y": 0.66,
    },
    {
        "step_id": "standardize",
        "title": "Standardization audit",
        "subtitle": "SMILES, InChIKey, scaffolds",
        "module": "standardization",
        "artifact": "data/processed/standardization_report.json",
        "x": 0.25,
        "y": 0.66,
    },
    {
        "step_id": "release_index",
        "title": "Release-time index",
        "subtitle": "ChEMBL releases, first-seen dates",
        "module": "release index",
        "artifact": "results/release_index/compound_release_index.parquet",
        "x": 0.45,
        "y": 0.66,
    },
    {
        "step_id": "exposure",
        "title": "Public-exposure audit",
        "subtitle": "Exact, scaffold, NN lower bounds",
        "module": "exposure annotation",
        "artifact": "results/tables/benchmark_coverage_exposure_summary.csv",
        "x": 0.65,
        "y": 0.66,
    },
    {
        "step_id": "evaluation",
        "title": "Exposure-adjusted evaluation",
        "subtitle": "Slices, intervals, limitations",
        "module": "score sensitivity",
        "artifact": "results/tables/exposure_delta_ci.csv",
        "x": 0.25,
        "y": 0.27,
    },
    {
        "step_id": "provenance",
        "title": "Assay provenance",
        "subtitle": "Assays, units, thresholds",
        "module": "label-source audit",
        "artifact": "results/tables/assay_provenance_task_summary.csv",
        "x": 0.45,
        "y": 0.27,
    },
    {
        "step_id": "trust_cards",
        "title": "Trust-card reporting",
        "subtitle": "Cards, schema, caveats",
        "module": "reporting standard",
        "artifact": "results/figures/trust_card_examples.pdf",
        "x": 0.65,
        "y": 0.27,
    },
]


def _setup_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            "font.size": 7,
            "axes.spines.right": False,
            "axes.spines.top": False,
        }
    )


def _artifact_status(root: Path, artifact: str) -> str:
    path = root / artifact
    if "*" in artifact:
        return "available" if list(root.glob(artifact)) else "planned"
    if path.is_dir():
        return "available" if any(path.iterdir()) else "planned"
    return "available" if path.exists() and path.stat().st_size > 0 else "planned"


def write_workflow_table(root: Path, output: Path) -> pd.DataFrame:
    rows = []
    for step in WORKFLOW_STEPS:
        rows.append(
            {
                "step_id": step["step_id"],
                "title": step["title"],
                "audit_module": step["module"],
                "proof_artifact": step["artifact"],
            }
        )
    table = pd.DataFrame(rows)
    output.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(output, index=False)
    return table


def _assert_no_text_overlap(fig: plt.Figure, text_groups: dict[str, list[plt.Text]]) -> None:
    """Fail fast if labels inside any workflow box overlap after rendering."""
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for step_id, artists in text_groups.items():
        boxes = []
        for artist in artists:
            bbox = artist.get_window_extent(renderer=renderer).expanded(1.01, 1.08)
            boxes.append((artist.get_text(), bbox))
        for i, (left_text, left_box) in enumerate(boxes):
            for right_text, right_box in boxes[i + 1 :]:
                if left_box.overlaps(right_box):
                    raise RuntimeError(
                        f"Workflow text overlap in {step_id!r}: {left_text!r} overlaps {right_text!r}"
                    )


def plot_workflow(
    *,
    root: str | Path = ".",
    output_pdf: str | Path = "results/figures/workflow_schematic.pdf",
    output_svg: str | Path | None = "results/figures/workflow_schematic.svg",
    output_table: str | Path = "results/tables/workflow_artifact_map.csv",
) -> pd.DataFrame:
    root_path = Path(root)
    table = write_workflow_table(root_path, Path(output_table))
    _setup_style()

    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    ax.set_axis_off()
    fig.patch.set_facecolor("white")

    layout = {
        "inputs": (0.05, 0.69, 0.24, 0.14),
        "standardize": (0.38, 0.69, 0.24, 0.14),
        "release_index": (0.71, 0.69, 0.24, 0.14),
        "exposure": (0.25, 0.47, 0.50, 0.14),
        "evaluation": (0.07, 0.25, 0.38, 0.14),
        "provenance": (0.55, 0.25, 0.38, 0.14),
        "trust_cards": (0.25, 0.055, 0.50, 0.14),
    }
    colors = {
        "available": ("#eef5f2", "#3c7c66"),
        "planned": ("#f4f4f4", "#8a8a8a"),
    }
    text_groups: dict[str, list[plt.Text]] = {}

    for step in WORKFLOW_STEPS:
        status = _artifact_status(root_path, step["artifact"])
        face, edge = colors[status]
        x, y, box_w, box_h = layout[step["step_id"]]
        patch = FancyBboxPatch(
            (x, y),
            box_w,
            box_h,
            boxstyle="round,pad=0.012,rounding_size=0.010",
            linewidth=1.0,
            edgecolor=edge,
            facecolor=face,
        )
        ax.add_patch(patch)
        title_width = 22 if box_w < 0.30 else (31 if box_w < 0.4 else 44)
        subtitle_width = 28 if box_w < 0.30 else (46 if box_w < 0.4 else 62)
        title = ax.text(
            x + 0.018,
            y + box_h - 0.026,
            fill(step["title"], width=title_width),
            weight="bold",
            fontsize=7.0,
            va="top",
            ha="left",
            linespacing=1.05,
        )
        subtitle = ax.text(
            x + 0.018,
            y + box_h - 0.068,
            fill(step["subtitle"], width=subtitle_width),
            fontsize=5.35,
            va="top",
            ha="left",
            color="#333333",
            linespacing=1.08,
        )
        module = ax.text(
            x + 0.018,
            y + 0.016,
            fill(step["module"], width=title_width),
            fontsize=5.35,
            va="bottom",
            ha="left",
            color=edge,
            weight="bold",
        )
        text_groups[step["step_id"]] = [title, subtitle, module]

    def mid_right(step_id: str) -> tuple[float, float]:
        x, y, w, h = layout[step_id]
        return x + w, y + h / 2

    def mid_left(step_id: str) -> tuple[float, float]:
        x, y, _, h = layout[step_id]
        return x, y + h / 2

    def top_center(step_id: str) -> tuple[float, float]:
        x, y, w, h = layout[step_id]
        return x + w / 2, y + h

    def bottom_center(step_id: str) -> tuple[float, float]:
        x, y, w, _ = layout[step_id]
        return x + w / 2, y

    arrows = [
        (mid_right("inputs"), mid_left("standardize"), 0.0),
        (mid_right("standardize"), mid_left("release_index"), 0.0),
        (bottom_center("release_index"), top_center("exposure"), 0.0),
        (bottom_center("exposure"), top_center("evaluation"), 0.12),
        (bottom_center("exposure"), top_center("provenance"), -0.12),
        (bottom_center("evaluation"), top_center("trust_cards"), -0.08),
        (bottom_center("provenance"), top_center("trust_cards"), 0.08),
    ]
    for start_xy, end_xy, rad in arrows:
        arrow = FancyArrowPatch(
            start_xy,
            end_xy,
            arrowstyle="-|>",
            mutation_scale=10,
            linewidth=0.8,
            color="#5f6b73",
            connectionstyle=f"arc3,rad={rad}",
        )
        ax.add_patch(arrow)

    ax.text(
        0.04,
        0.93,
        "MolTrustBench workflow: from public observability to exposure-adjusted reporting",
        fontsize=9.6,
        weight="bold",
        ha="left",
    )
    ax.text(
        0.04,
        0.875,
        "ChEMBL release dates are treated as public observability dates, not model-specific pretraining dates.",
        fontsize=6.6,
        color="#444444",
        ha="left",
    )
    ax.text(
        0.04,
        0.018,
        "Each stage writes machine-readable artifacts used by the trust-card and supplement tables.",
        fontsize=6.3,
        color="#555555",
        ha="left",
    )
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    fig.tight_layout()
    _assert_no_text_overlap(fig, text_groups)

    output_pdf = Path(output_pdf)
    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_pdf, bbox_inches="tight")
    if output_svg:
        fig.savefig(output_svg, bbox_inches="tight")
    plt.close(fig)
    return table


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--output-pdf", default="results/figures/workflow_schematic.pdf")
    parser.add_argument("--output-svg", default="results/figures/workflow_schematic.svg")
    parser.add_argument("--output-table", default="results/tables/workflow_artifact_map.csv")
    args = parser.parse_args(argv)
    table = plot_workflow(
        root=args.root,
        output_pdf=args.output_pdf,
        output_svg=args.output_svg,
        output_table=args.output_table,
    )
    print(table.to_string(index=False))


if __name__ == "__main__":
    main()
