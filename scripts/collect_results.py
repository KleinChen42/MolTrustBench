from __future__ import annotations

from moltrustbench.evaluation.slice_metrics import write_slice_metrics


if __name__ == "__main__":
    table = write_slice_metrics()
    print(f"rows={len(table)}")
