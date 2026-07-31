# KyMCM Lite

KyMCM Lite 0.9.1 is a Markdown-first programming-side workflow for mathematical-modeling teams. It supports optional shared-data preprocessing, execution-first model implementation, recoverable computation, evidence-linked formal results, optional question-level incremental Supplements, neutral technical handoffs, explicitly requested final figures, and submission-appendix curation without workflow state or content JSON.

Formal PRE/QN execution is non-visual by default: structured numbers, tables, logs, schemas, error metrics, and constraint audits come first. Only the smallest diagnostic graphic needed to resolve a named risk is allowed. Lite does not generate, plan, read, modify, or check contest manuscripts.

## Installation

Copy the complete `kymcm-lite` directory into the Codex Skills directory. The copied directory is self-contained and requires only the Python 3.11–3.13 standard library.

## Complete ChatGPT Project Source

The repository also provides a deterministic, complete single-file specification for ChatGPT Project Sources. From the repository root, generate it after normative changes and verify that it is synchronized:

```bash
python scripts/export_kymcm_lite_full_spec.py \
  --output docs/lite-v3/KyMCM_Lite_FULL_SPEC.md
python scripts/export_kymcm_lite_full_spec.py \
  --output docs/lite-v3/KyMCM_Lite_FULL_SPEC.md --check
```

Upload `docs/lite-v3/KyMCM_Lite_FULL_SPEC.md` to the ChatGPT project when a complete rule mirror is needed. The generated file is intentionally long, must not be edited by hand, and does not belong in a contest workspace, evidence directory, or appendix.

## Commands

```bash
python scripts/lite.py init --workspace PATH --questions 3 --preprocess
python scripts/lite.py doctor --workspace PATH
python scripts/lite.py check-preprocess-start --workspace PATH
python scripts/lite.py check-preprocess-result --workspace PATH
python scripts/lite.py check-start --workspace PATH --problem 1
python scripts/lite.py check-result --workspace PATH --problem 1
python scripts/lite.py check-appendix-start --workspace PATH
python scripts/lite.py check-appendix-result --workspace PATH
```

Exit code 0 means structurally valid (warnings may exist), 1 means a contract or evidence failure, and 2 means an unexpected tool or environment failure.

The formal modeling surfaces are START, matching RESULT, and RESULT-declared evidence. Each question uses either unsuffixed single mode or contiguous split units. Exact earlier-unit dependencies and optional PRE dependencies are structurally checked; semantic contradiction review reads each complete declared upstream START/RESULT pair.

Before authoring, revising, reviewing, or executing START, use `references/modeling_plan_design.md`. It defines the minimum formally complete deliverable, input and solvability preflight, smallest representative smoke test, recoverable stages, reuse boundaries, explicit cost, and risk-triggered L0/L1/L2 validation. Final display assets and document composition are out of scope.

When the user explicitly requests final figures after results and data stabilize, use the `nature-figure` skill and keep all figure-generation work under workspace-level `figure/`. The root is optional, not created by init, unconstrained internally, and excluded from formal evidence, modeling dependencies, and appendix sources.

When PRE is used, author/check/execute START_PRE, write/check RESULT_PRE, and prepare HANDOFF_PRE only when a complete downstream technical transfer is useful. RESULT_PRE remains the downstream data authority.

After the complete base RESULT set passes, optional post-result validation, revision, or implementation repair uses the one problem-level `SUPPLEMENT_START_QN.md` / `SUPPLEMENT_RESULT_QN.md` pair. Append and review each Sx plan before execution, append the matching result afterward, never overwrite completed entries or old evidence, and use exact impact scope. Current state is base RESULT plus completed Supplement Result entries. See `references/supplement_work.md`; no Supplement checker or command is added.

After RESULT and evidence stabilize, create one `notes/HANDOFF_QN.md` per official question from `templates/HANDOFF_QN.template.md` and `references/technical_handoff.md`. Split mode waits for every contiguous RESULT unit to pass before assembling the problem-level transfer. Refresh it after every Supplement Result, preserving base-unit and Sx provenance. Exact base RESULT tokens remain modeling dependencies; HANDOFF has no checker or state and cannot enter appendix outputs.

The optional appendix stage starts only after formal results, completed Supplement work, explicit submission requirements, and certification boundaries are stable. Supplement Markdown contracts are internal context and cannot be copied, while current effective Supplement code and result assets remain eligible under existing mappings. `APPENDIX_START.md` is the sole whitelist and `APPENDIX_RESULT.md` the execution report.

KyMCM Full is the separate review-gated end-to-end workflow. Users choose one Skill explicitly; neither guesses or converts the other workspace mode.

See `docs/protocol.md` for the complete standalone contract.
