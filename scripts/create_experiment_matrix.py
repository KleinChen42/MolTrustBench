from __future__ import annotations

import argparse
from pathlib import Path

import yaml


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a simple Milestone 1 experiment matrix.")
    parser.add_argument("--output", default="configs/generated/milestone1_matrix.yaml")
    args = parser.parse_args()
    matrix = {
        "tasks": ["tdc_admet:hERG", "moleculenet:BBBP"],
        "models": ["morgan_logreg", "morgan_xgb"],
        "splits": ["standard", "exact_removed"],
        "seeds": [0],
        "cutoff_release": "CHEMBL30",
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(yaml.safe_dump(matrix, sort_keys=False), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
