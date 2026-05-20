---
name: paper-architect
description: Maintain MolTrustBench paper claims, evidence matrices, manuscript skeletons, and claim-to-artifact traceability. Use for edits to paper/claims.md, paper/evidence_matrix.md, paper/manuscript_skeleton.md, and any experiment that must map to claims C1-C5.
---

# Paper Architect

Keep every repo change tied to the target paper.

Required outputs:
- `paper/claims.md`
- `paper/evidence_matrix.md`
- `paper/manuscript_skeleton.md`

Workflow:
1. Identify the paper claim C1-C5 supported by the change.
2. Record scripts, outputs, figures, and tables in the evidence matrix.
3. Update claim status only when an artifact exists.
4. Use conservative language: public exposure, potential exposure, observable exposure lower bound, temporal validity, benchmark trustworthiness.

Failure checks:
- No experiment may be claim-free.
- Do not upgrade evidence from preliminary to supported without a result artifact.
- Do not claim confirmed leakage unless model training data exposure is directly proven.
