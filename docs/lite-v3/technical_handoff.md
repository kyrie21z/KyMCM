# KyMCM Lite technical HANDOFF

HANDOFF is a neutral technical transfer derived from an explicitly accepted RESULT and real machine evidence. It gives modelers, reviewers, diagnostic-visualization executors, and other downstream technical collaborators a complete, traceable account of what was executed and what may safely be reused. It is not a formal fact source, a second RESULT, or a writing artifact. A successful machine check is only structural/evidence readiness; it is not acceptance.

## Authority

1. The base RESULT set defines the original certified scope, status, limitations, and downstream frozen interfaces.
2. Completed Supplement Result entries add evidence or replace only their explicitly named scope in S1, S2, ... order.
3. Machine evidence defines actual values, tables, diagnostics, and data products.
4. HANDOFF explains and organizes the current effective state without expanding certification.
5. Later modeling keeps exact base RESULT dependency tokens and reads applicable Supplement entries during semantic review; it never inherits HANDOFF.

If HANDOFF conflicts with a base RESULT or accepted Supplement Result, repair HANDOFF. If a HANDOFF value conflicts with machine evidence, repair it from the evidence. If a formal contract conflicts with evidence, return to contract/evidence audit. Never choose a convenient value silently.

## Identity and timing

Use one fixed problem-level `HANDOFF_QN.md` for every official question, in both single and split modes. For a single question, create or refresh it only in a new independent HANDOFF task after `RESULT_QN.md` passes `check-result`, the user/ChatGPT has explicitly accepted the RESULT after execution, and formal plus selected auxiliary evidence is stable. For a split question, wait until every contiguous `START_QN_K.md` has a matching `RESULT_QN_K.md`, every RESULT passes `check-result --subproblem K`, and the complete RESULT set has been explicitly accepted; then use a separate HANDOFF task. Partial split completion remains valid modeling progress but cannot produce the current standard HANDOFF. Acceptance cannot be inferred from tests, CI, commits, clean evidence, or a zero checker exit code.

Never create a new `HANDOFF_QN_K.md`. Existing suffixed files are retained as ordinary legacy notes without deletion, renaming, merging, or checker impact. PRE continues to use fixed `HANDOFF_PRE.md`.

After base completion, keep the existing HANDOFF as the last accepted snapshot while a new base or Supplement Result is pending acceptance. A newly accepted Result still does not refresh it automatically: only a separate explicit HANDOFF task may refresh the problem-level HANDOFF after the accepted Result and evidence are available. List the base RESULT path(s) first under `正式上游`, then the one Supplement Result path when it contains recorded entries. Do not create an aggregate RESULT, index, manifest, or state object.

## Required technical content

For single mode, read the complete START_QN, accepted RESULT_QN, all RESULT-declared evidence, and selected auxiliary evidence. For split mode, read every contiguous START_QN_K, every matching accepted RESULT_QN_K, all evidence declared by each RESULT, and selected auxiliary evidence. If Supplement files exist, read their complete ordered accepted Start/Result entries and all mapped evidence. Preserve each base unit and Sx identity, status, impact mode, and certification boundary; do not merge them into a newly certified claim. Record:

- task or data-stage identity and certified conclusions;
- actual inputs, data scope, transforms, model, parameters, solver settings, and authorized deviations;
- every certified result and useful evidence-supported auxiliary result, labeled separately;
- validation, anomalies, failed attempts, fallbacks, and omitted L1/L2 work;
- workspace-relative data, result-table, diagnostic, log, and asset paths mapped to their exact RESULT or split unit;
- causal, population, time, scenario, numerical, robustness, and extrapolation boundaries;
- exact downstream inputs, outputs, schemas, units, interfaces, and final review points.

Apply completed Sx entries in order and only within their explicit scope. In section 4, distinguish current effective results from superseded historical results. In section 5, disclose failed or aborted entries and implementation repairs. In section 6, map Supplement evidence to its Sx. In sections 7 and 8, state the current limitations, pending risks, and final effective downstream interface. An unmatched pending Supplement Start does not change formal state, but disclose it when the planned change may affect downstream reuse.

An auxiliary result may explain behavior or expose a limitation, but it cannot be presented as certified. Missing or failed work must be disclosed when it affects downstream interpretation.

## Evidence and asset mapping

Map each important claim or reusable asset to an existing workspace-relative path. State whether it is formal or auxiliary, what it contains, and what downstream consumer may use it for. Never invent files, copy values without provenance, or use HANDOFF as the only location of a critical number.

HANDOFF may list existing diagnostic assets, identify them as internal diagnostics, and expose structured data interfaces that a later figure task may read. It must not initiate that task, select final display graphics, prescribe chart type, visual style, captions, placement, or presentation format. Explicitly requested final-figure work remains a separate `figure/` workspace.

## Boundaries

- No prose drafting, document structure, placement advice, recommended wording, or final visual selection.
- No new computation merely to improve presentation; execute more work only for formal success criteria, a named unresolved risk, user direction, or result certification.
- HANDOFF is never a later modeling dependency and is never copied into appendix outputs.
- Appendix organization may read base RESULT, accepted Supplement Result, and HANDOFF as internal technical context only.
- No HANDOFF checker, state, approval, hash, JSON, manifest, aggregate RESULT, or success report is introduced.

HANDOFF is a read-only phase: do not run new model computation, change code/data, or modify START/RESULT/Supplement contracts while writing it. If the accepted Result and evidence conflict, stop and return to Result/evidence audit instead of repairing formal facts inside HANDOFF. Python validates neither HANDOFF identity, completeness, acceptance, nor timing. The executor performs semantic review against the accepted RESULT set, complete accepted Supplement files, and machine evidence, and downstream consumers recheck critical values and interfaces before use.
