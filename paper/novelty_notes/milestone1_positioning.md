# Novelty Note: Milestone 1 Positioning

MolTrustBench should be framed as a benchmark trustworthiness audit, not as an ADMET reliability leaderboard. Existing ADMET and OOD benchmarks evaluate performance under distribution shift, data scarcity, imbalance, activity cliffs, and related chemical-space stressors. Milestone 1 instead asks whether benchmark molecules, scaffolds, and close neighbors were already publicly observable before a chosen cutoff release.

The first proof target is therefore not superior model accuracy. It is a reproducible evidence chain:

- ChEMBL release index.
- Benchmark standardization.
- Exact, scaffold, and nearest-neighbor public-exposure annotation.
- Exposure-removed evaluation slices.
- Trust cards and sanity checks.

This supports conservative claims about observable public-exposure lower bounds and temporal validity. It does not prove confirmed leakage or model memorization.
