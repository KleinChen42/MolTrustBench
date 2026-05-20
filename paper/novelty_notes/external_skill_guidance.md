# External Skill Guidance For MolTrustBench

This note records how two external skill collections inform the next MolTrustBench steps. They are process guidance, not evidence for paper claims.

## Sources

- Yuan1z0825/nature-skills: https://github.com/Yuan1z0825/nature-skills
- Imbad0202/academic-research-skills: https://github.com/Imbad0202/academic-research-skills

## Installed Local Skills

Installed for future Codex sessions:

- `nature-writing`
- `nature-figure`
- `nature-data`
- `nature-response`
- `deep-research`
- `academic-paper`
- `academic-pipeline`

The current session uses these by direct `SKILL.md` inspection because newly
installed skills may require a Codex restart before automatic triggering.

## Nature-Skills Adaptation

Relevant skills:

- `nature-writing`: use for Results narratives that build an evidence ladder rather than a chronological log.
- `nature-figure`: use for publication figures with non-redundant panel logic; each panel must answer a distinct scientific question.
- `nature-data`: use for data availability, repository planning, FAIR metadata, and reproducibility statements.
- `nature-response`: use later for reviewer-risk tables and point-by-point response drafts.

MolTrustBench adaptation:

- Each figure must map to one paper claim C1-C5 and one reviewer defense R1-R10.
- Main figures should prioritise overview -> deviation -> relationship:
  - Fig. 2 release histogram: public observability timeline.
  - Fig. 3 exposure heatmap: benchmark-level exposure risk.
  - Fig. 4 performance drop: consequence of exposure-aware evaluation.
- Do not add decorative panels. A panel is only valid if it changes how a reviewer interprets benchmark trustworthiness.

## Academic-Research-Skills Adaptation

Relevant workflow:

- Stage 1 research produces the research question and method blueprint.
- Experiment Agent executes and validates experiments before writing.
- Integrity gates check fabricated references, metric errors, unsupported claims, and revision regressions.
- Academic reviewer / Devil's Advocate passes stress-test the manuscript before submission.

MolTrustBench adaptation:

- Treat the current work as the Experiment Agent bridge between the research question and paper writing.
- Before C1/C2 become `supported`, require real ChEMBL artifacts plus sanity checks.
- Before C3 becomes `supported`, require exposure-removed and density-matched controls on real benchmark tasks.
- Before C4 becomes `preliminary`, require assay provenance extraction from real ChEMBL activity tables.
- Before any manuscript section is drafted as final, run an integrity gate:
  - every quantitative claim has a result artifact;
  - every citation is verified;
  - every limitation uses observable-exposure language rather than confirmed-leakage language.

## Next-Step Rule

The immediate next step is not more prose. It is a real-data experiment gate:

1. Create a remote RDKit/PyTDC environment on H200.
2. Run the GPU0-only real audit from the GitHub clone.
3. Promote C1/C2 only if `results/logs/real_audit_gpu0/summary.json` reports zero critical sanity failures.

## Operational Gate Added

See `paper/design_notes/real_data_exposure_gate.md`. This is the active bridge
between the external skill guidance and MolTrustBench Milestone 1 execution.
