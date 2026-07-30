# KyMCM Lite

KyMCM Lite 0.7.0 is a Markdown-first programming-side workflow for mathematical-modeling teams. It supports optional shared-data preprocessing, execution-first model implementation, recoverable computation, evidence-linked formal results, neutral technical handoffs, and submission-appendix curation without workflow state or content JSON.

Lite does not generate, plan, read, modify, or check contest manuscripts, and it does not select final display graphics. Existing legacy `paper/` directories are retained but completely ignored.

## Installation

Copy the complete `kymcm-lite` directory into the Codex Skills directory. The copied directory is self-contained and requires only the Python 3.11–3.13 standard library.

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

When PRE is used, author/check/execute START_PRE, write/check RESULT_PRE, and prepare HANDOFF_PRE only when a complete downstream technical transfer is useful. RESULT_PRE remains the downstream data authority.

After RESULT and evidence stabilize, create the matching `notes/HANDOFF_QN[_K].md` from `templates/HANDOFF_QN.template.md` and `references/technical_handoff.md`. HANDOFF neutrally records actual execution, complete and auxiliary results, validation, failures, evidence paths, boundaries, interfaces, and review points. RESULT remains formal and is the only modeling-inheritance surface. HANDOFF has no checker or state and cannot enter appendix outputs.

The optional appendix stage starts only after formal results, explicit submission requirements, and certification boundaries are stable. `APPENDIX_START.md` is the sole whitelist and `APPENDIX_RESULT.md` the execution report. `appendix/` contains the complete formal solve package with plotting excluded; root `code/` contains authentic representative code for a final submission document. Inputs are limited to `problems/` and `input/`. COPY/CURATE remains traceable; copying, obfuscation, junk code, and similarity-driven changes are forbidden.

KyMCM Full is the separate review-gated end-to-end workflow. Users choose one Skill explicitly; neither guesses or converts the other workspace mode.

See `docs/protocol.md` for the complete standalone contract.
