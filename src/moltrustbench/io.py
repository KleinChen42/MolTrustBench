"""Small IO helpers."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd


def ensure_parent(path: str | Path) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    return out


def ensure_dir(path: str | Path) -> Path:
    out = Path(path)
    out.mkdir(parents=True, exist_ok=True)
    return out


def write_json(data: dict[str, Any], path: str | Path) -> Path:
    out = ensure_parent(path)
    out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out


def read_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_dataframe(df: pd.DataFrame, path: str | Path) -> Path:
    out = ensure_parent(path)
    if out.suffix == ".csv":
        df.to_csv(out, index=False)
    elif out.suffix == ".jsonl":
        df.to_json(out, orient="records", lines=True)
    else:
        df.to_parquet(out, index=False)
    return out


def read_dataframe(path: str | Path) -> pd.DataFrame:
    src = Path(path)
    if src.suffix == ".csv":
        return pd.read_csv(src)
    if src.suffix == ".jsonl":
        return pd.read_json(src, orient="records", lines=True)
    return pd.read_parquet(src)


def stable_hash_text(text: str, prefix: str = "") -> str:
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}{digest}" if prefix else digest


def dataframe_manifest_id(df: pd.DataFrame, prefix: str = "df-") -> str:
    payload = df.to_json(orient="split", date_format="iso", index=False)
    return stable_hash_text(payload, prefix=prefix)


def file_sha256(path: str | Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()
