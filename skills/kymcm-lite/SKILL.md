---
name: kymcm-lite
description: Execute and review Markdown-first mathematical-modeling handoffs and optional appendix organization with structural and evidence checks, without workflow state or content JSON.
---

# KyMCM Lite

Resolve the explicit contest workspace before acting. Require exactly `{"workflow":"kymcm_lite","version":3}` in `.kymcm/mode.json`; fail closed for Full, Lite v2, Legacy, malformed, absent, or unknown modes.

For modeling, treat the selected `START_QN.md`/`RESULT_QN.md` single contract or `START_QN_K.md`/`RESULT_QN_K.md` split contract and RESULT-declared evidence as the only formal Lite surfaces. One official question uses either one unsuffixed pair or contiguous split START units, never both; missing split RESULT units are allowed while work is incomplete. Choose granularity by modeling dependency and execution boundary, not printed subquestion count. The workflow has no `FROZEN_CONTEXT.md` surface; never read a legacy copy even when it remains in a workspace. Use `scripts/lite.py` for initialization and read-only checks, and follow `references/markdown_format.md`.

START section 2 contains exactly one visible `**前问依赖：**` declaration: `无` or a strictly ordered list of exact earlier-question units such as `Q1, Q2_1`. Bare tokens name only single-mode contracts; suffixed tokens name exact split units and never expand. Same-question dependencies are forbidden. Do not copy upstream definitions, constraints, rules, or summaries into the current START. Other section-2 content may name current inputs and necessary upstream result paths.

While authoring or materially revising a dependent START, before implementing it, and whenever reviewing it, read the complete selected current START plus the exact complete START and RESULT pair for every declared direct dependency. Do not compare sibling split units unless one explicitly depends on an earlier official question unit; 0.3.1 forbids same-question dependency edges. Perform the semantic contradiction review in `references/dependency_review.md`. Treat authorized RESULT deviations and formal RESULT values, files, limitations, and certification boundaries as the effective upstream contract. If there is no conflict, continue without a consistency report, state, approval, event, hash, evidence file, or copied summary. If there is a material conflict, identify every conflict with exact current/upstream locations and practical consequences, ask one highest-impact user question, and stop without executing or changing upstream files.

Preserve mathematical meaning, parameters, constraints, decision rules, data semantics, budgets, and fallback rules. Choose implementation details independently only when they cannot alter conclusions. Ask one highest-impact question and stop when semantic uncertainty remains. Stop when a discovered data issue changes values, missingness, sample membership, pairing, or model input. Repair parser, path, syntax, cache, logging, and plotting mechanics locally when semantics do not change.

Disclose every authorized START deviation in RESULT. Never create Full JSON artifacts, workflow state, approvals, events, review hashes, or content-level JSON. Never self-approve mathematical conclusions.

## Optional appendix organization

Begin this independent stage only after all required START/RESULT work is complete and the paper, formal result versions, and certification boundary are stable. Read `reports/appendix/APPENDIX_START.md` completely. The modeling workflow has no FROZEN_CONTEXT surface. Single or split START and RESULT contracts may be contextual references during appendix work.

Run `check-appendix-start` before copying. Construct only the frozen whitelist targets; never copy an entire project and trim it reactively. Treat original `problems/`, `input/`, and `paper/` files as read-only. Preserve runtime/build dependency closure, and keep the submission `appendix/` tree distinct from the concise root `code/` core-algorithm appendix.

Perform actual compilation, build, workbook, and source-integrity verification without changing original sources. Store evidence under `reports/appendix/evidence/`, write `APPENDIX_RESULT.md`, then run `check-appendix-result`. The checker validates structure and evidence, not mathematical correctness. Stop for human review whenever mathematical meaning, result equivalence, or certification scope remains ambiguous. Follow `references/appendix_organization.md`.
