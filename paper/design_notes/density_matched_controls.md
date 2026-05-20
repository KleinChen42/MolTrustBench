# Density-Matched Controls

## Purpose

Density-matched controls test whether exposure effects are separable from
ordinary chemical-space density. This is a reviewer-defense module rather than
a leaderboard module.

## Paper Claim Supported

- C3: model performance can differ across standard, exposure-removed, and
  exposure-aware subsets.

This module does not by itself make C3 supported. It enables the control needed
before C3 can move beyond `preliminary`.

## Reviewer Objection Addressed

- R2: Exposure is just chemical-space density.
- R8: Clean subsets are too small.

## Proof Artifacts

- `data/splits/<task>/density_matched_clean.json`
- `results/tables/density_matched_controls.csv`
- `results/tables/slice_metrics.csv` rows for `density_matched_clean`

## Sanity Checks

- The density-matched test subset contains only non-exact-exposed molecules.
- The split reuses the original train/validation rows and does not move test
  molecules into train.
- The control table reports exposed, clean, and selected clean counts by density bin.
- Empty matched subsets are critical failures, not silent successes.
