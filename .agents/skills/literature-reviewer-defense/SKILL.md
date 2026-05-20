---
name: literature-reviewer-defense
description: Audit MolTrustBench novelty and reviewer risks before major design decisions. Use when comparing against ADMET reliability benchmarks, molecular OOD benchmarks, molecular foundation model papers, LLM contamination studies, or drug discovery agent benchmarks.
---

# Literature Reviewer Defense

Use this skill before high-impact design or paper-positioning decisions.

Required outputs:
- `paper/novelty_notes/<topic>.md`
- `paper/reviewer_risks.md`
- `results/tables/required_controls.csv`

Workflow:
1. Check whether the planned contribution duplicates ADMET reliability, molecular OOD, or agent benchmarks.
2. State the novelty boundary in one paragraph.
3. Map likely reviewer attacks R1-R10 to mitigation experiments.
4. Prefer controls over rhetoric.

Failure checks:
- Do not frame the paper as a new ADMET leaderboard.
- Do not frame public exposure as confirmed model leakage.
- Do not ignore density-matched controls when interpreting exposure effects.
