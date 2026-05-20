---
name: experiment-reporting
description: Generate MolTrustBench experiment matrices, sanity reports, figures, tables, and paper auto reports. Use after metrics or exposure artifacts are created and before claiming paper evidence.
---

# Experiment Reporting

Required outputs:
- `results/tables/sanity_report.csv`
- `results/figures/*.pdf`
- `results/tables/*.csv`
- `paper/auto_report.md`

Workflow:
1. Run sanity checks before updating paper claims.
2. Generate figures from result files, not hand-entered numbers.
3. Summarize evidence claim by claim.
4. Keep reviewer risks visible in `paper/auto_report.md`.

Failure checks:
- Missing required artifacts are critical.
- NaN metrics, empty slices, and split overlaps are critical.
- Figures must be reproducible from committed scripts and result tables.
