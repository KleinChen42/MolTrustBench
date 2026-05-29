"""Generate paper-facing MolTrustBench submission figures."""

from __future__ import annotations

import json
from pathlib import Path

from moltrustbench.visualization.plot_trust_cards import plot_trust_cards
from moltrustbench.visualization.plot_workflow import plot_workflow


def main() -> None:
    trust_cards = plot_trust_cards()
    workflow = plot_workflow()
    summary = {
        "workflow_rows": int(len(workflow)),
        "trust_card_rows": int(len(trust_cards)),
        "figures": [
            "results/figures/workflow_schematic.pdf",
            "results/figures/workflow_schematic.svg",
            "results/figures/trust_card_examples.pdf",
            "results/figures/trust_card_examples.svg",
        ],
        "tables": [
            "results/tables/workflow_artifact_map.csv",
            "results/tables/trust_card_examples.csv",
        ],
    }
    Path("results/tables/submission_figure_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
