---
name: molecule-standardization
description: Enforce deterministic molecule standardization for MolTrustBench using RDKit when available and explicit rejected-molecule reports. Use whenever benchmark or ChEMBL molecules are converted to canonical SMILES, InChIKey, scaffolds, or fingerprints.
---

# Molecule Standardization

Required outputs:
- standardized parquet files
- `data/processed/rejected_molecules.csv`
- `data/processed/standardization_report.json`

Workflow:
1. Prefer RDKit canonicalization and standard InChIKey generation.
2. Record rejected molecules with source, task, row id, SMILES, and reason.
3. Keep fallback standardization only for tests or smoke fixtures.
4. Keep canonicalization deterministic across runs.

Failure checks:
- Silent molecule drops are critical.
- Changing standardization policy invalidates exposure counts and must be recorded.
- Fallback hashes must never be presented as chemical InChIKeys in paper claims.
