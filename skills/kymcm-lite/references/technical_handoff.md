# KyMCM Lite technical HANDOFF

HANDOFF is a neutral technical transfer derived from a checked RESULT and real machine evidence. It gives modelers, reviewers, diagnostic-visualization executors, and other downstream technical collaborators a complete, traceable account of what was executed and what may safely be reused. It is not a formal fact source, a second RESULT, or a writing artifact.

## Authority

1. RESULT defines certified scope, status, limitations, and downstream frozen interfaces.
2. Machine evidence defines actual values, tables, diagnostics, and data products.
3. HANDOFF explains and organizes those materials without expanding certification.
4. Later modeling inherits RESULT only, never HANDOFF.

If HANDOFF conflicts with RESULT, repair HANDOFF. If a HANDOFF value conflicts with machine evidence, repair it from the evidence. If RESULT conflicts with evidence, return to RESULT/evidence audit. Never choose a convenient value silently.

## Identity and timing

Use one fixed problem-level `HANDOFF_QN.md` for every official question, in both single and split modes. For a single question, create it only after `RESULT_QN.md` passes `check-result` and formal plus selected auxiliary evidence is stable. For a split question, wait until every contiguous `START_QN_K.md` has a matching `RESULT_QN_K.md`, every RESULT passes `check-result --subproblem K`, and all formal plus selected auxiliary evidence is stable. Partial split completion remains valid modeling progress but cannot produce the current standard HANDOFF.

Never create a new `HANDOFF_QN_K.md`. Existing suffixed files are retained as ordinary legacy notes without deletion, renaming, merging, or checker impact. PRE continues to use fixed `HANDOFF_PRE.md`.

Review the problem-level HANDOFF after any material RESULT or downstream-relevant evidence change, or after adding a split unit. Do not create an aggregate RESULT, index, manifest, or state object.

## Required technical content

For single mode, read the complete START_QN, RESULT_QN, all RESULT-declared evidence, and selected auxiliary evidence. For split mode, read every contiguous START_QN_K, every matching RESULT_QN_K, all evidence declared by each RESULT, and selected auxiliary evidence. Preserve each unit's identity and certification boundary; do not merge multiple RESULTs into a newly certified claim. Record:

- task or data-stage identity and certified conclusions;
- actual inputs, data scope, transforms, model, parameters, solver settings, and authorized deviations;
- every certified result and useful evidence-supported auxiliary result, labeled separately;
- validation, anomalies, failed attempts, fallbacks, and omitted L1/L2 work;
- workspace-relative data, result-table, diagnostic, log, and asset paths mapped to their exact RESULT or split unit;
- causal, population, time, scenario, numerical, robustness, and extrapolation boundaries;
- exact downstream inputs, outputs, schemas, units, interfaces, and final review points.

An auxiliary result may explain behavior or expose a limitation, but it cannot be presented as certified. Missing or failed work must be disclosed when it affects downstream interpretation.

## Evidence and asset mapping

Map each important claim or reusable asset to an existing workspace-relative path. State whether it is formal or auxiliary, what it contains, and what downstream consumer may use it for. Never invent files, copy values without provenance, or use HANDOFF as the only location of a critical number.

HANDOFF may list existing diagnostic assets, identify them as internal diagnostics, and expose structured data interfaces that a later figure task may read. It must not initiate that task, select final display graphics, prescribe chart type, visual style, captions, placement, or presentation format. Explicitly requested final-figure work remains a separate `figure/` workspace.

## Boundaries

- No prose drafting, document structure, placement advice, recommended wording, or final visual selection.
- No new computation merely to improve presentation; execute more work only for formal success criteria, a named unresolved risk, user direction, or result certification.
- HANDOFF is never a later modeling dependency and is never copied into appendix outputs.
- Appendix organization may read HANDOFF as internal technical context only.
- No HANDOFF checker, state, approval, hash, JSON, manifest, aggregate RESULT, or success report is introduced.

Python validates neither HANDOFF identity nor completeness. The executor performs semantic review against RESULT and machine evidence, and downstream consumers recheck critical values and interfaces before use.
