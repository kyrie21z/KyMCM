# KyMCM Lite

KyMCM Lite 0.9.13 is a Markdown-first programming-side workflow for mathematical-modeling teams. It supports optional shared-data preprocessing, recoverable evidence-linked modeling, RESULT-gated handoffs, explicitly requested programmatic figures as same-stem PDF/PNG/PY/TXT bundles, ordinary 2D rendering through the existing Matplotlib path, intrinsic-3D rendering through an optional fail-closed PyVista/VTK path, and evidence-derived flowchart specifications with human-owned layout, without workflow state or content JSON.

Formal PRE/QN execution is non-visual by default: structured numbers, tables, logs, schemas, error metrics, and constraint audits come first. Only the smallest diagnostic graphic needed to resolve a named risk is allowed. Lite does not generate, plan, read, modify, or check contest manuscripts.

Using KyMCM Lite itself is AI tool usage. After accepted results, HANDOFF, and stable Appendix work, use `references/ai_tool_usage_details.md` and copy `templates/AI_TOOL_USAGE_DETAILS.template.tex`; each competition replaces only the two real screenshots and compiles `AI 工具使用详情.pdf`. The fixed declaration snippet belongs before paper references when required. This material is outside RESULT/HANDOFF, Appendix, evidence, modeling dependencies, and final-figure work; Lite does not generate it from workspace files and adds no CLI, checker, state, JSON, manifest, or approval. XeLaTeX is an optional final-material build dependency, and factual/privacy/visual review remains human work.

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

Before authoring, revising, reviewing, or executing START, use `references/modeling_plan_design.md`. It defines the minimum formally complete deliverable, input and solvability preflight, smallest representative smoke test, recoverable stages, reuse boundaries, explicit cost, and risk-triggered L0/L1/L2 validation. Final display assets and document composition are out of scope.

When the user explicitly requests final figures after accepted results and a current HANDOFF, read the core and selection references and choose L0/L1/L2/L3 from the real information need. Ordinary 2D expression uses Matplotlib `figure_exec.py`; only intrinsic-3D information uses `final_figure_3d.md` and PyVista `figure_3d_exec.py`, with no decorative 3D or `mplot3d` fallback. Both programmatic routes render PDF/PNG, keep the same-stem PY as the reproducible entrypoint, write the paper-facing title/caption to TXT, and pass `figure_bundle.py` before ChatGPT/user review. A 3D PDF is an exact-size formal container and may contain the rasterized VTK scene. Flowcharts remain semantic plans followed by human-owned layout and require no Python bundle. Keep work under the optional unmanaged `figure/`; no route adds CLI, state, manifest, or managed workflow semantics.

When PRE is used, author/check/execute START_PRE, write/check RESULT_PRE, stop for explicit user/ChatGPT acceptance, and prepare HANDOFF_PRE only in a new independent read-only HANDOFF_PRE task after acceptance. RESULT_PRE remains the downstream data authority; `check-preprocess-result` alone is not acceptance.

After the complete base RESULT set passes, optional post-result validation, revision, or implementation repair uses the one problem-level `SUPPLEMENT_START_QN.md` / `SUPPLEMENT_RESULT_QN.md` pair. Record S1, S2, ... plans before execution and matching results afterward; run the machine check and stop for explicit user/ChatGPT acceptance. The latest unadopted Sx may be edited, have its old Result removed/invalidated, and be rerun in place; an adopted Sx, a non-latest Sx, or an Sx with a later Sy is frozen. Only that latest Sx may rebuild its own `sN_` artifacts; base and adopted history remains protected. Current adopted state is base RESULT plus accepted, currently valid Supplement Result entries; a pending Result does not change the last accepted HANDOFF snapshot. See `references/supplement_work.md`; no Supplement checker or command is added.

After RESULT and evidence stabilize, the user/ChatGPT must explicitly accept the RESULT; only a new independent, read-only HANDOFF task may then create or refresh one `notes/HANDOFF_QN.md` per official question from `templates/HANDOFF_QN.template.md` and `references/technical_handoff.md`. Split mode waits for every contiguous RESULT unit to pass and the complete Result set to be accepted. A new Supplement Result never refreshes HANDOFF automatically. Exact base RESULT tokens remain modeling dependencies; HANDOFF has no checker or state and cannot enter appendix outputs.

The optional appendix stage starts only after formal results and completed Supplement work are accepted, any requested HANDOFF is current, and explicit submission requirements and certification boundaries are stable. Supplement Markdown contracts are internal context and cannot be copied, while current effective Supplement code and result assets remain eligible under existing mappings. `APPENDIX_START.md` is the sole whitelist and `APPENDIX_RESULT.md` the execution report.

KyMCM Full is the separate review-gated end-to-end workflow. Users choose one Skill explicitly; neither guesses or converts the other workspace mode.

See `docs/protocol.md` for the complete standalone contract.
