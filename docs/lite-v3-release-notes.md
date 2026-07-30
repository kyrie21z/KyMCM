# KyMCM Lite 0.8.0

KyMCM Lite 0.8.0 makes formal PRE and QN execution non-visual by default. Structured statistics, tables, machine-readable data, validation records, and other reproducible evidence come first. A diagnostic plot is allowed only when a named risk or stopping condition cannot be resolved adequately from non-visual evidence, and then only the smallest diagnostic needed for that decision. Final display figures are never L0/L1/L2 validation and do not consume the formal validation budget.

When a user explicitly requests final figures after RESULT, HANDOFF, data, and evidence are stable, the separate `nature-figure` skill may work under the optional workspace root `figure/`. Lite does not infer a figure request, select chart styles, or silently rerun modeling to improve a display. Missing or inconsistent inputs return to PRE or QN work through the existing contracts.

`figure/` is a known optional root, not a managed root. `init` does not create it; `doctor` ignores its contents and does not report it as unknown or as workflow status. It has no required structure, contracts, checker, command, manifest, JSON, workflow state, or dependency semantics. It is outside evidence scope and is not an appendix source. Existing workspaces with or without `figure/` need no migration.

The marker remains exactly `{"workflow":"kymcm_lite","version":3}`. Python 3.11, 3.12, and 3.13, the eight public commands, all QN/PRE/appendix headings, single/split identities, dependency grammar, evidence rules, appendix whitelist grammar, and stateless design are unchanged.

The commands remain exactly `init`, `doctor`, `check-preprocess-start`, `check-preprocess-result`, `check-start`, `check-result`, `check-appendix-start`, and `check-appendix-result`.

## Formal workflow boundary

RESULT remains the formal boundary and only modeling-inheritance surface. The mirrored `technical_handoff.md` guidance keeps HANDOFF as a neutral technical transfer for actual execution, formal plus selected auxiliary results, validation, failures, evidence paths, boundaries, interfaces, and review points. HANDOFF may expose a structured data interface usable by a later explicit figure request, but it does not recommend a chart, style, layout, caption, or export format and does not launch figure work.

Appendix organization continues to depend on formal RESULT contracts, machine evidence, and explicit submission requirements. `appendix/` remains the complete formal solve code package with plotting excluded; root `code/` remains authentic representative implementation for a final submission document. COPY, CURATE, GENERATE, integrity, dependency, safety, and authenticity rules remain in force. Neither `paper/` nor `figure/` is an appendix source.

## Compatibility and limitations

Lite 0.8.0 does not add a FIGURE stage, final-graphics selector, manuscript generator, HANDOFF checker, appendix builder, solver orchestration, workflow state, content JSON, approvals, manifests, automatic migration, or external similarity service. It does not bundle or import `nature-figure`; that skill is an optional separate capability invoked only for an explicit final-figure request.

Valid 0.7.0 workspaces remain valid. The two appendix certification headings introduced in 0.7.0 remain current. Existing legacy `paper/` directories and optional `figure/` directories are retained and ignored without reading their contents, including invalid UTF-8 files and symlinks. Existing HANDOFF files are not automatically migrated.

Users who copied the Skill must reinstall the complete 0.8.0 directory. Full 1.0.0 and historical Lite v2 remain separate and unchanged.

## Historical releases

- 0.7.0 (2026-07-30) refocused Lite on programming-side execution and neutral technical handoffs.
- 0.6.0 (2026-07-29) added optional fixed PRE contracts, commands, dependencies, and appendix mappings.
- 0.5.1 (2026-07-29) defined the complete formal solve code package and expanded authentic representative-code eligibility.
- 0.5.0 (2026-07-29) introduced the original writing-oriented HANDOFF layer.
- 0.4.0 (2026-07-29) added the execution-first modeling-plan standard.
- 0.3.1 (2026-07-24) added independent split units and exact dependency tokens.
- 0.3.0 (2026-07-23) removed the active FROZEN_CONTEXT surface and introduced direct dependency review.
- 0.2.0 (2026-07-23) added independent appendix contracts and checks.
- 0.1.0 (2026-07-20) introduced standalone Lite v3.
