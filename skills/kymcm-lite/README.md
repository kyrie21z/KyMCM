# KyMCM Lite

KyMCM Lite 0.5.0 is a Markdown-first execution protocol for mathematical-modeling teams. It combines execution-first plan design with a derived paper-writing HANDOFF: RESULT stays the concise formal contract and downstream modeling interface, while HANDOFF is the paper writer's sole complete collaboration document. Each official question may still use one `QN` contract or contiguous independent `QN_K` contracts; the marker, commands, START/RESULT headings, and optional appendix stage remain unchanged.

## Installation

Copy the complete `kymcm-lite` directory into your Codex Skills directory. The copied directory is self-contained and the core requires only Python 3.11–3.13 standard library.

## Commands

```bash
python scripts/lite.py init --workspace PATH --questions 3
python scripts/lite.py doctor --workspace PATH
python scripts/lite.py check-start --workspace PATH --problem 1
python scripts/lite.py check-result --workspace PATH --problem 1
python scripts/lite.py check-start --workspace PATH --problem 2 --subproblem 1
python scripts/lite.py check-result --workspace PATH --problem 2 --subproblem 1
python scripts/lite.py check-appendix-start --workspace PATH
python scripts/lite.py check-appendix-result --workspace PATH
```

Exit code 0 means structurally valid (warnings may exist), 1 means contract or evidence invalid, and 2 means an unexpected tool or environment failure.

The formal modeling surfaces are the selected START, matching RESULT, and RESULT-declared evidence. A question uses either unsuffixed single mode or contiguous split START suffixes; partial split RESULT completion is valid. A dependent START uses exact tokens such as `**前问依赖：** Q1, Q2_1`, never wildcards or same-question edges, and does not copy upstream definitions. Codex reads each exact upstream START/RESULT pair, stops on semantic contradiction, and writes no consistency artifact when there is no conflict.

Before authoring, materially revising, reviewing, or executing a START, Codex reads `references/modeling_plan_design.md`. It establishes the minimum deliverable, audits inputs, preflights whether the model can be identified and solved, runs the smallest end-to-end smoke test, stages expensive work with artifacts and reuse boundaries, calculates total cost, and runs high-cost validation only for a named remaining risk. This is semantic Skill behavior, not a new workspace file or Python checker contract.

After a RESULT passes `check-result` and evidence is stable, create the exact matching `notes/HANDOFF_QN[_K].md` from `templates/HANDOFF_QN.template.md` and `references/paper_handoff.md`. HANDOFF gives the paper writer the complete model explanation, paper-relevant values, validation, assets, evidence links, and expression boundaries. It is derived from RESULT and machine evidence, cannot expand formal conclusions, and is never a downstream modeling dependency. `check-result` does not require HANDOFF and no HANDOFF checker or state is added.

The appendix stage begins only after modeling is complete. `APPENDIX_START.md` is the sole whitelist, `APPENDIX_RESULT.md` is the execution report, `appendix/` is the minimal reproducibility/result attachment, and root `code/` contains only concise core algorithms. Appendix checks are read-only and standard-library-only. Appendix organization may reference START, RESULT, and HANDOFF as internal context, but cannot copy them.

KyMCM Full is the review-gated end-to-end workflow. KyMCM Lite is a low-friction execution handoff. Users choose one Skill explicitly; neither guesses or converts the other workspace mode.

See `docs/protocol.md` for the complete standalone contract.
