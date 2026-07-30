# KyMCM Lite 0.7.0

KyMCM Lite 0.7.0 refocuses the product as a programming-side mathematical-modeling workflow: optional PRE data preparation, recoverable QN implementation and computation, evidence-linked formal RESULT contracts, neutral technical HANDOFF documents, and optional submission-appendix curation.

Lite no longer generates, plans, reads, modifies, or checks contest manuscripts and does not select final display graphics. The old writing-oriented HANDOFF reference is replaced by mirrored `technical_handoff.md` guidance. RESULT remains the formal boundary and only modeling-inheritance surface; HANDOFF records actual execution, complete and auxiliary results, validation, failures, evidence paths, boundaries, interfaces, and review points without becoming a second contract.

The marker remains exactly `{"workflow":"kymcm_lite","version":3}`. Python 3.11, 3.12, and 3.13, the eight public commands, QN START/RESULT headings, PRE START/RESULT headings, single/split identities, dependency grammar, evidence rules, and stateless design are unchanged.

The commands remain exactly `init`, `doctor`, `check-preprocess-start`, `check-preprocess-result`, `check-start`, `check-result`, `check-appendix-start`, and `check-appendix-result`.

## Workspace and appendix changes

New workspaces contain `.kymcm/`, `input/`, `reports/`, and `problems/`; `paper/` is no longer created or required. Existing legacy `paper/` directories are retained and completely ignored, including invalid UTF-8 content and symlinks. They are no longer appendix sources.

Appendix organization depends on formal RESULT contracts, machine evidence, and explicit submission requirements. `appendix/` remains the complete formal solve code package with plotting excluded; root `code/` remains authentic representative implementation for a final submission document. COPY, CURATE, GENERATE, integrity, dependency, safety, and authenticity rules remain in force.

Existing appendix contracts require two manual heading changes:

```text
APPENDIX_START:
论文引用、正式结果与认证边界
→ 正式结果与认证边界

APPENDIX_RESULT:
正式结果与论文一致性
→ 正式结果一致性
```

Any old source entry rooted at `paper/` must be removed or replaced by a real source under `problems/` or `input/`. Existing HANDOFF files are not automatically migrated; use the new neutral template on the next material update.

## Scope and limitations

Lite does not add a FIGURE stage, manuscript generator, HANDOFF checker, appendix builder, solver orchestration, workflow state, content JSON, approvals, manifests, automatic migration, or external similarity service. Diagnostic visualization is permitted only when it directly validates data or a model. HANDOFF completeness and factual consistency, appendix coverage and authenticity, CURATE semantic equivalence, and mathematical correctness remain semantic review responsibilities.

Users who copied the Skill must reinstall the complete 0.7.0 directory. Full 1.0.0 and historical Lite v2 remain separate and unchanged.

## Historical releases

- 0.6.0 (2026-07-29) added optional fixed PRE contracts, commands, dependencies, and appendix mappings.
- 0.5.1 (2026-07-29) defined the complete formal-solve appendix package and expanded authentic representative-code eligibility.
- 0.5.0 (2026-07-29) introduced the original writing-oriented HANDOFF layer.
- 0.4.0 (2026-07-29) added the execution-first modeling-plan standard.
- 0.3.1 (2026-07-24) added independent split units and exact dependency tokens.
- 0.3.0 (2026-07-23) removed the active FROZEN_CONTEXT surface and introduced direct dependency review.
- 0.2.0 (2026-07-23) added independent appendix contracts and checks.
- 0.1.0 (2026-07-20) introduced standalone Lite v3.
