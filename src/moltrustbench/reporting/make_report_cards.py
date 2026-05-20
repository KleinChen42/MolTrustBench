"""Report-card helpers."""

from __future__ import annotations

from pathlib import Path

from moltrustbench.io import read_json


def load_report_cards(card_dir: str | Path = "results/report_cards") -> list[dict]:
    return [read_json(path) for path in sorted(Path(card_dir).glob("*_card.json"))]
