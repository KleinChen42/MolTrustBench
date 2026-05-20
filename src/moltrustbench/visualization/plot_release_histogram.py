"""Plot ChEMBL release histogram."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from moltrustbench.io import ensure_parent


def plot_release_histogram(counts: pd.DataFrame, output_path: str | Path = "results/figures/release_histogram.pdf") -> Path:
    out = ensure_parent(output_path)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(counts["chembl_release"], counts["unique_standard_inchikey"], color="#3b6ea8")
    ax.set_xlabel("ChEMBL release")
    ax.set_ylabel("Unique standardized molecules")
    ax.set_title("Public release index coverage")
    ax.tick_params(axis="x", rotation=30)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)
    return out
