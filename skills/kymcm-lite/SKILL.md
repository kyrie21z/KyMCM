---
name: kymcm-lite
description: Execute and review Markdown-first mathematical-modeling workflows with optional shared preprocessing, recoverable computation, evidence-linked results, neutral technical handoffs, request-driven final figures, and submission appendix curation without workflow state or content JSON.
---

# KyMCM Lite

Resolve the explicit contest workspace before acting. Require exactly `{"workflow":"kymcm_lite","version":3}` in `.kymcm/mode.json`; fail closed for Full, Lite v2, Legacy, malformed, absent, or unknown modes. Use `scripts/lite.py` for initialization and read-only checks, follow `references/markdown_format.md`, and never read legacy `FROZEN_CONTEXT.md` or `paper/` content.

For modeling, treat the selected `START_QN.md`/`RESULT_QN.md` single contract or contiguous `START_QN_K.md`/`RESULT_QN_K.md` split contracts plus RESULT-declared evidence as the only formal surfaces. Never mix single and split mode; missing split RESULT units are allowed while work remains incomplete. Choose granularity from modeling dependency and execution boundaries, not printed subquestion count.

## Optional preprocess stage

Treat `problems/preprocess/`, when present, as one fixed optional unit before dependent questions, never Q0, split, or stateful. Initialize its empty tree with `scripts/lite.py init --workspace PATH --questions N --preprocess`; init creates no contracts. Read `references/preprocess_stage.md`. Author START_PRE from `templates/START_PRE.template.md`, run `check-preprocess-start`, pass the minimal parse-transform-write-readback smoke test, execute recoverable stages, complete L0 audit, author RESULT_PRE from `templates/RESULT_PRE.template.md`, and run `check-preprocess-result`.

When a complete downstream technical transfer is needed, derive HANDOFF_PRE from `templates/HANDOFF_PRE.template.md` and review it semantically against RESULT_PRE and machine evidence. It has no Python checker. PRE owns shared audit, deterministic cleaning, common field/unit semantics, sample accounting, shared derived data, and bounded EDA for data understanding, model design, or risk identification. Question-specific features, splits, objectives, validation, and conclusions remain in QN. PRE is non-visual by default and does not select final display graphics.

A QN START declares exactly one visible `**预处理依赖：** 无|PRE` before its separate `**前问依赖：**` declaration. Legacy START files without the PRE declaration remain valid when PRE is absent and receive only an advisory warning when PRE exists. A PRE declaration requires the exact complete START_PRE/RESULT_PRE pair and the semantic contradiction review in `references/dependency_review.md`. Stop on conflicts in fields, units, samples, missingness, joins, time scope, transforms, leakage, limitations, or formal paths. Impact-review dependent completed QN work after material RESULT_PRE changes.

START section 2 also contains exactly one visible `**前问依赖：**` declaration: `无` or a strictly ordered list of exact earlier-question units such as `Q1, Q2_1`. Bare tokens name only single-mode contracts; suffixed tokens name exact split units and never expand. Same-question dependencies are forbidden.

Before implementing or materially revising a dependent START, read the complete selected current START and every exact declared upstream START/RESULT pair. Perform `references/dependency_review.md`. Treat authorized RESULT deviations, formal values, paths, limitations, and certification boundaries as effective upstream rules. Continue without an artifact when no conflict exists. On material conflict, identify every exact location and consequence, ask one highest-impact user question, and stop without changing upstream files.

## Modeling-plan design and execution

Before authoring, reviewing, revising, or executing START, read `references/modeling_plan_design.md` completely. Define the minimum formally complete deliverable; audit dependencies and inputs; preflight identifiability, feasibility, boundedness, numerical meaning, and computational solvability; design the smallest end-to-end smoke test; divide formal work into recoverable stages with inspectable artifacts and exact cache/reuse conditions; estimate nested run count, time, memory, parallelism, and worst-case recomputation; classify experiments as mandatory L0, risk-triggered L1, or resource-permitting L2.

Run in order: author START, run its checker, complete dependency and modeling-plan semantic reviews, pass smoke, execute formal stages, pass basic/L0 audit, run L1 only for its named triggered risk, and run L2 only when affordable and it reduces an explicit remaining risk or strengthens required certification. Do not add computation for presentation value. A failed smoke blocks formal work; a failed basic audit returns to the responsible stage.

Repair deterministic engineering omissions transparently, then rerun the checks and semantic reviews. Ask one highest-impact question before changing mathematics, validation strength, formal success criteria, or a material resource tradeoff. Return to design if the model is unidentifiable, infeasible, unbounded, unsupported, or irreconcilable with budget. Preserve mathematical meaning, parameters, constraints, decisions, data semantics, budgets, and fallback rules. Disclose every authorized START deviation in RESULT.

Formal PRE/QN execution is non-visual by default. Prefer structured evidence: numeric checks, tables, logs, schemas, error metrics, and constraint audits. Produce only the smallest diagnostic visualization required when non-visual evidence cannot resolve a named data- or model-validity risk; record that risk and the diagnostic stopping condition. Do not plan or generate final display graphics, styles, captions, layouts, document placement, or high-resolution delivery assets, and do not include final-figure work in L0/L1/L2 or the formal modeling budget. Never create Full artifacts, workflow state, approvals, events, review hashes, manifests, or content JSON.

## Technical result handoff

Use one fixed problem-level `HANDOFF_QN.md` for each official question. In single mode, create or refresh it only after the complete START/RESULT pair passes `check-result` and formal plus selected auxiliary evidence is stable. In split mode, wait until every contiguous START unit has a matching RESULT, run `check-result --subproblem K` successfully for every unit, then read all START/RESULT pairs, their declared evidence, and selected auxiliary evidence before creating the one problem-level HANDOFF. Partial split completion cannot produce the current standard HANDOFF.

Follow `references/technical_handoff.md` and `templates/HANDOFF_QN.template.md`. Never create a new `HANDOFF_QN_K.md`; retain any existing suffixed files as ordinary legacy notes without deleting, renaming, merging, or treating them as the current entry point. Treat HANDOFF as a neutral complete technical transfer derived from the question's RESULT set and machine evidence. Preserve every split unit's identity and certification boundary rather than forming a new aggregate conclusion. RESULT remains the concise formal boundary and only downstream modeling inheritance surface; later START dependencies continue to name exact RESULT units. Separate formal from auxiliary results; disclose actual execution, validation, anomalies, failed attempts, omitted L1/L2, paths, limitations, and exact downstream interfaces. HANDOFF must not draft prose, propose document structure or placement, recommend wording, choose final graphics, or trigger extra computation.

Repair HANDOFF when it conflicts with RESULT or evidence; return to RESULT/evidence audit when RESULT conflicts with evidence. Review it after material RESULT or downstream-relevant evidence changes. Create no HANDOFF checker, state, approval, hash, JSON, manifest, aggregate RESULT, or success report. Never use HANDOFF as a later modeling dependency or copy it into appendix outputs.

## Optional final figure workspace

Enter final-figure work only when the user explicitly requests it after relevant RESULT, HANDOFF, structured data, and machine evidence are stable. Use the `nature-figure` skill and keep figure-generation code, prepared plotting data, and generated assets under the workspace-level `figure/` root. Do not infer which figures are wanted, silently retrain or resolve models, or alter RESULT certification; if required data are missing, return to PRE/QN for additional evidence first. Mechanical selection, ordering, joining of certified results, format conversion, and unit-display conversion are allowed only when they preserve numerical meaning.

`figure/` is optional, unconstrained internally, and created only for an explicit request. It is not a managed root, formal evidence scope, modeling dependency, RESULT/HANDOFF contract, or appendix source. Add no figure command, checker, contract, manifest, state, approval, hash ledger, or content JSON, and do not bundle or import `nature-figure`.

## Optional submission appendix organization

Begin only after required START/RESULT work, explicit submission requirements, formal result versions, and certification boundaries are stable. Read `reports/appendix/APPENDIX_START.md`, then run `check-appendix-start`. Construct only its frozen whitelist targets. Treat original `problems/` and `input/` as read-only; `paper/` and `figure/` are outside appendix source scope. START, RESULT, and HANDOFF are internal references only and cannot be copied.

Make `appendix/` cover the complete formal solve pipeline and dependencies while excluding plotting. Select authentic representative root `code/` files for the final submission document's code appendix; core modeling, preprocessing, scheduling, recovery, audit, and other relevant execution code are eligible.

Keep COPY/CURATE traceable to the team's real source. Never copy others' code, obfuscate, add junk/dead code, or rewrite for similarity manipulation. If computation and plotting cannot be separated safely, stop for human confirmation. Perform compilation, build, workbook, and source-integrity verification without modifying original sources. Store evidence under `reports/appendix/evidence/`, write APPENDIX_RESULT, and run `check-appendix-result`. The checker validates structure and evidence, not plotting responsibility, originality, external similarity, complete formal-code coverage, CURATE semantic equivalence, or mathematical correctness. Follow `references/appendix_organization.md`.
