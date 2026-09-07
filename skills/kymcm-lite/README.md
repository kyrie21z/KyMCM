# KyMCM Lite

KyMCM Lite 1.0.0 is a Markdown-first programming-side workflow for mathematical-modeling teams. Formal validation planning follows Claim–Risk–Evidence: L0 is Claim-required, L1 is risk-triggered, and L2 only strengthens already adequate evidence; method names and cost do not determine level. The unchanged five-section AI-use report takes actual contest tools, purposes, two representative cases and concrete adoption/modification/verification, normally with three screenshots and at most five. Human review precedes the existing frozen-PDF COPY interface. Validation guidance is calibrated against the fixed historical 63-paper CUMCM excellent-paper corpus without treating frequency as authority. Optional Explore, recoverable evidence-linked modeling, RESULT-gated handoffs, requested final figures, pre-Appendix AI-use details, and COPY-only root submission assets retain their existing boundaries without workflow-state, approval, or manifest JSON.

Formal PRE/QN execution is non-visual by default: structured numbers, tables, logs, schemas, error metrics, and constraint audits come first. Only the smallest diagnostic graphic needed to resolve a named risk is allowed. Lite does not generate, plan, read, modify, or check contest manuscripts.

Using KyMCM Lite itself is AI tool usage. After accepted substantive work and requested HANDOFF/figures, compile and human-review `reports/ai-usage/AI 工具使用详情.pdf` before Appendix. Appendix copies only that frozen PDF to `appendix/AI 工具使用详情.pdf`; contest-required result files are also declared COPY-only root assets, while ordinary support results remain under `appendix/problems/**/result/`. Lite adds no AI command, state, JSON, manifest, approval, or generation step.

## Installation

Copy the complete `kymcm-lite` directory into the Codex Skills directory. The Lite core runtime is self-contained and requires only the Python 3.11–3.13 standard library. Formal 2D Matplotlib execution optionally installs `requirements-figure.txt`; intrinsic-3D execution installs `requirements-figure-3d.txt` and requires headless-capable VTK/EGL/OpenGL.

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

Before authoring, revising, reviewing, or executing START, use `references/modeling_plan_design.md`. It defines the minimum formally complete deliverable, input and solvability preflight, smallest representative smoke test, recoverable stages, reuse boundaries, explicit cost, and Claim–Risk–Evidence validation with a meaningful STOP boundary. Evidence is L0 when the current core Claim requires it even if costly, L1 only for a named material-risk trigger, and L2 only when it strengthens already adequate evidence. Final display assets and document composition are out of scope.

When one concrete material uncertainty could change the formal route, optionally read `references/explore_work.md` and use `problems/qN/explore/{EXPLORE_QN.md,code/,outputs/}`. One Trial runs the cheapest discriminating test under one hard budget, then stops for ChatGPT/user PROMOTE/DROP/NEXT review. `init` never creates Explore, and promoted scratch work must be recreated/rerun through START or Supplement before it affects formal state. If the route is already clear, proceed directly to START.

When the user explicitly requests final figures after accepted results and a current HANDOFF, read the core and selection references and choose L0/L1/L2/L3 from the real information need. Ordinary 2D expression uses Matplotlib `figure_exec.py`; only intrinsic-3D information uses `final_figure_3d.md` and PyVista `figure_3d_exec.py`, with no decorative 3D or `mplot3d` fallback. Both programmatic routes render PDF/PNG, keep the same-stem PY as the reproducible entrypoint, write the paper-facing title/caption to TXT, and pass `figure_bundle.py` before ChatGPT/user review. A 3D PDF is an exact-size formal container and may contain the rasterized VTK scene. Flowcharts remain semantic plans followed by human-owned layout and require no Python bundle. Keep work under the optional unmanaged `figure/`; no route adds CLI, state, manifest, or managed workflow semantics.

When PRE is used, author/check/execute START_PRE, write/check RESULT_PRE, stop for explicit user/ChatGPT acceptance, and prepare HANDOFF_PRE only in a new independent read-only HANDOFF_PRE task after acceptance. RESULT_PRE remains the downstream data authority; `check-preprocess-result` alone is not acceptance.

After the complete base RESULT set passes, optional post-result validation, revision, or implementation repair uses the one problem-level `SUPPLEMENT_START_QN.md` / `SUPPLEMENT_RESULT_QN.md` pair. Record S1, S2, ... plans before execution and matching results afterward; run the machine check and stop for explicit user/ChatGPT acceptance. The latest unadopted Sx may be edited, have its old Result removed/invalidated, and be rerun in place; an adopted Sx, a non-latest Sx, or an Sx with a later Sy is frozen. Only that latest Sx may rebuild its own `sN_` artifacts; base and adopted history remains protected. Current adopted state is base RESULT plus accepted, currently valid Supplement Result entries; a pending Result does not change the last accepted HANDOFF snapshot. See `references/supplement_work.md`; no Supplement checker or command is added.

After RESULT and evidence stabilize, the user/ChatGPT must explicitly accept the RESULT; only a new independent, read-only HANDOFF task may then create or refresh one `notes/HANDOFF_QN.md` per official question from `templates/HANDOFF_QN.template.md` and `references/technical_handoff.md`. Split mode waits for every contiguous RESULT unit to pass and the complete Result set to be accepted. A new Supplement Result never refreshes HANDOFF automatically. Exact base RESULT tokens remain modeling dependencies; HANDOFF has no checker or state and cannot enter appendix outputs.

Appendix keeps root `code/` as faithful excerpts that need not run independently and `appendix/` as the minimal complete formal runtime package. Preserve necessary writers, configuration and Python/native builds. In the existing APPENDIX_START, predeclare inputs/commands/scope/budget/comparisons/stop, then actually run an isolated copy with independent outputs. Distinguish full replay, short execution and fixed-artifact recalculation; keep sources, inputs and frozen root assets unchanged. Checker success is not actual reproduction. Old packages are not migrated or retroactively certified. See `references/appendix_organization.md`.

The optional appendix stage starts only after formal results are accepted, requested HANDOFF/figures are complete, the AI PDF is frozen, and submission requirements are stable. Current templates declare the AI root target and any safe `.xlsx`/`.csv`/`.txt` mandatory root results. Legacy Appendix plans without the AI declaration remain readable; re-author from the current template to opt into root-asset behavior. Explore scratch paths are never Appendix sources.

KyMCM Full is the separate review-gated end-to-end workflow. Users choose one Skill explicitly; neither guesses or converts the other workspace mode.

See `docs/protocol.md` for the complete standalone contract.

## Lite 1.0.0 stabilization

This release fixes Appendix PRE structure, declared package-local native relative dependencies, executable text-source permissions, and equal-byte independent support results. Duplicate authoritative assets, source/path/type/integrity checks and read-only behavior stay protected. Only completed, still-valid, explicitly accepted Supplement Results affect the declared scope; required evidence cannot be waived by a limitation. CI discovers all tests and requires real TeX/C++ builds in Python 3.12. The current Full Spec excludes historical RFC/release-note bodies; commands, marker, figures, AI-use template and Full stay unchanged.
