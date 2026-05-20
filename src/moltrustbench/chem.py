"""Molecule standardization and lightweight fingerprint utilities."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import re
from typing import Iterable

import numpy as np


class StandardizationError(ValueError):
    """Raised when a molecule cannot be standardized."""


@dataclass(frozen=True)
class StandardizedMolecule:
    input_smiles: str
    canonical_smiles: str
    standard_smiles: str
    standard_inchikey: str
    murcko_scaffold_smiles: str
    standardization_backend: str


def _load_rdkit():
    try:
        from rdkit import Chem, DataStructs
        from rdkit.Chem import AllChem
        from rdkit.Chem.Scaffolds import MurckoScaffold

        return Chem, AllChem, DataStructs, MurckoScaffold
    except Exception:
        return None


def rdkit_available() -> bool:
    return _load_rdkit() is not None


def standardize_smiles(smiles: str, *, allow_fallback: bool = False) -> StandardizedMolecule:
    raw = "" if smiles is None else str(smiles).strip()
    if not raw or raw.lower() == "nan":
        raise StandardizationError("empty SMILES")

    rdkit = _load_rdkit()
    if rdkit is not None:
        Chem, _, _, MurckoScaffold = rdkit
        mol = Chem.MolFromSmiles(raw)
        if mol is None:
            raise StandardizationError("RDKit could not parse SMILES")
        Chem.SanitizeMol(mol)
        canonical = Chem.MolToSmiles(mol, canonical=True, isomericSmiles=True)
        inchikey = Chem.MolToInchiKey(mol)
        scaffold_mol = MurckoScaffold.GetScaffoldForMol(mol)
        scaffold = Chem.MolToSmiles(scaffold_mol, canonical=True) if scaffold_mol.GetNumAtoms() else ""
        return StandardizedMolecule(
            input_smiles=raw,
            canonical_smiles=canonical,
            standard_smiles=canonical,
            standard_inchikey=inchikey,
            murcko_scaffold_smiles=scaffold,
            standardization_backend="rdkit",
        )

    if not allow_fallback:
        raise StandardizationError("RDKit is not installed; fallback standardizer disabled")

    canonical = _fallback_canonical(raw)
    return StandardizedMolecule(
        input_smiles=raw,
        canonical_smiles=canonical,
        standard_smiles=canonical,
        standard_inchikey="FALLBACK-" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:24],
        murcko_scaffold_smiles=_fallback_scaffold(canonical),
        standardization_backend="fallback-fixture-only",
    )


def _fallback_canonical(smiles: str) -> str:
    return re.sub(r"\s+", "", smiles)


def _fallback_scaffold(smiles: str) -> str:
    ring_patterns = ("c1ccccc1", "c1ccncc1", "C1CCCCC1")
    for pattern in ring_patterns:
        if pattern in smiles:
            return pattern
    atoms = re.findall(r"Cl|Br|[A-Z][a-z]?|[cnops]", smiles)
    atoms = [a.upper() if len(a) == 1 else a for a in atoms]
    if len(atoms) >= 2:
        return "-".join(atoms[:2])
    return atoms[0] if atoms else ""


def fingerprint_bits(smiles: str, *, allow_fallback: bool = False, n_bits: int = 2048) -> set[int]:
    rdkit = _load_rdkit()
    if rdkit is not None:
        Chem, AllChem, _, _ = rdkit
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise StandardizationError("RDKit could not parse SMILES for fingerprint")
        bitvect = AllChem.GetMorganFingerprintAsBitVect(mol, radius=2, nBits=n_bits)
        return {idx for idx in range(n_bits) if bitvect.GetBit(idx)}

    if not allow_fallback:
        raise StandardizationError("RDKit is not installed; fallback fingerprints disabled")

    tokens = _fallback_tokens(smiles)
    bits: set[int] = set()
    for token in tokens:
        bits.add(int(hashlib.sha256(token.encode("utf-8")).hexdigest(), 16) % n_bits)
    return bits


def fingerprint_array(smiles_list: Iterable[str], *, allow_fallback: bool = False, n_bits: int = 2048) -> np.ndarray:
    rows = []
    for smiles in smiles_list:
        bits = fingerprint_bits(smiles, allow_fallback=allow_fallback, n_bits=n_bits)
        row = np.zeros(n_bits, dtype=np.float32)
        if bits:
            row[list(bits)] = 1.0
        rows.append(row)
    return np.vstack(rows) if rows else np.zeros((0, n_bits), dtype=np.float32)


def tanimoto_from_bits(left: set[int], right: set[int]) -> float:
    if not left and not right:
        return 0.0
    union = len(left | right)
    return len(left & right) / union if union else 0.0


def _fallback_tokens(smiles: str) -> list[str]:
    compact = _fallback_canonical(smiles)
    tokens = set()
    for width in (1, 2, 3):
        for idx in range(max(0, len(compact) - width + 1)):
            tokens.add(compact[idx : idx + width])
    tokens.update(re.findall(r"Cl|Br|[A-Z][a-z]?|[cnops]", compact))
    return sorted(tokens)
