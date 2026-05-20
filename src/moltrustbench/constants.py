"""Project-wide constants for MolTrustBench."""

from __future__ import annotations

from dataclasses import dataclass


PROJECT_NAME = "MolTrustBench"
TOOL_NAME = "MolLeakTrace"
VERSION = "0.1.0"


@dataclass(frozen=True)
class ReleaseInfo:
    release_id: str
    order: int
    date: str
    doi: str


CHEMBL_RELEASES: dict[str, ReleaseInfo] = {
    "CHEMBL24": ReleaseInfo("CHEMBL24", 24, "2018-05", "10.6019/CHEMBL.database.24"),
    "CHEMBL27": ReleaseInfo("CHEMBL27", 27, "2020-05", "10.6019/CHEMBL.database.27"),
    "CHEMBL30": ReleaseInfo("CHEMBL30", 30, "2022-02", "10.6019/CHEMBL.database.30"),
    "CHEMBL33": ReleaseInfo("CHEMBL33", 33, "2023-05", "10.6019/CHEMBL.database.33"),
    "CHEMBL36": ReleaseInfo("CHEMBL36", 36, "2025-07", "10.6019/CHEMBL.database.36"),
}

EXPOSURE_THRESHOLDS = (0.6, 0.7, 0.8, 0.9)

PUBLIC_EXPOSURE_TERMS = (
    "public exposure",
    "potential exposure",
    "observable exposure lower bound",
    "temporal validity",
    "benchmark trustworthiness",
    "exposure-adjusted evaluation",
    "assay provenance",
    "benchmark trust card",
)
