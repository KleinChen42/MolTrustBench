"""Foundation model wrapper registry for later MolTrustBench phases."""

from __future__ import annotations


MODEL_REGISTRY = {
    "ChemBERTa": {"auditability": "low", "milestone_1": False},
    "MolFormer": {"auditability": "medium", "milestone_1": False},
    "MolE": {"auditability": "high", "milestone_1": False},
}
