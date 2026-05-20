from __future__ import annotations

from pathlib import Path


if __name__ == "__main__":
    for path in sorted(Path("results/logs").glob("*.json")):
        print(path)
