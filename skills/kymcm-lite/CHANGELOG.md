# Changelog

## 0.9.2 - 2026-08-04

- Allow the latest unadopted Supplement Sx to be edited and rerun after removing or invalidating its same-number Result.
- Freeze adopted/non-latest entries and their artifacts, retain continuous numbering and exact impact semantics, and keep adoption and downstream review outside Python runtime state.
- Preserve the Lite v3 marker, eight commands, workspace contracts, Full, and 0.9.0/0.9.1 workspace compatibility.

## 0.9.1 - 2026-07-31

- Add a complete machine-enforced runtime contract alongside the existing protocol and diagnostics catalog.
- Add the repository-maintained deterministic full-spec export for ChatGPT Project Sources with source hashes, mirror validation, and stale checks.
- Preserve the Lite v3 marker, eight commands, workspace behavior, valid 0.9.0 workspaces, and Full.

## 0.9.0 - 2026-07-30

- Add one optional problem-level `SUPPLEMENT_START_QN.md` / `SUPPLEMENT_RESULT_QN.md` pair per official question after complete checked base results.
- Keep single/split identity question-scoped and append S1/S2/... plans before execution with matching results, three work types, four explicit impact modes, and no completed-history overwrite.
- Define current effective state as the base RESULT set plus completed Supplement Result entries, refresh HANDOFF after each result, and keep exact base RESULT dependency tokens.
- Exclude Supplement Markdown contracts from appendix while retaining eligibility for current effective Supplement code, derived data, outputs, and representative implementation.
- Preserve the marker, eight commands, base/PRE headings and discovery, evidence scope, figure rules, stateless runtime, existing 0.8.1 workspaces, and Full.

## 0.8.1 - 2026-07-30

- Use one problem-level `HANDOFF_QN.md` per official question in both single and split modes.
- Require every contiguous split unit to have a checked RESULT before creating the question-level HANDOFF, while preserving each RESULT identity and certification boundary.
- Retain existing suffixed HANDOFF files as ordinary legacy notes without automatic deletion, renaming, merging, or migration.
- Preserve RESULT dependencies, HANDOFF_PRE, headings, runtime, eight commands, figure/appendix behavior, and Full.

## 0.8.0 - 2026-07-30

- Make formal PRE and QN work non-visual by default: structured evidence comes first, and only the smallest diagnostic needed for a named unresolved risk is permitted.
- Recognize an optional, request-driven root `figure/` workspace for final figures created through the separate `nature-figure` skill after results and evidence are stable.
- Keep `figure/` outside managed layout, initialization, doctor output, contracts, evidence, appendix sources, workflow state, and all eight checker commands.
- Preserve the Lite v3 marker, frozen contract headings, command surface, appendix grammar, standard-library runtime, and Full.

## 0.7.0 - 2026-07-30

- Refocus Lite on programming-side preprocessing, recoverable modeling execution, evidence-linked results, neutral technical handoffs, and submission-appendix curation.
- Replace `paper_handoff.md` with mirrored `technical_handoff.md` guidance and neutral QN/PRE HANDOFF templates.
- Remove `paper/` from managed roots and appendix sources while completely ignoring existing legacy directories without deletion or migration.
- Migrate the two appendix certification headings while preserving the Lite v3 marker, eight commands, START/RESULT/PRE identities, dependencies, evidence rules, and Full.

## 0.6.0 - 2026-07-29

- Add the optional fixed `problems/preprocess/` stage with exact START_PRE, RESULT_PRE, and HANDOFF_PRE templates and guidance.
- Add `init --preprocess`, read-only preprocess checks, explicit QN PRE dependencies, downstream staleness warnings, and PRE appendix mappings.
- Preserve the Lite v3 marker, QN headings and modes, stateless design, and all valid PRE-free 0.5.1 workspaces.

## 0.5.1 - 2026-07-29

- Treat `appendix/` code as the complete formal solve pipeline with plotting excluded, rather than a mechanically minimal core.
- Allow root `code/` to present authentic representative scheduling, recovery, audit, and other paper-relevant execution code.
- Narrow name-based runtime exclusions while preserving runtime-data, unsafe-path, binary, cache, log, and source-integrity safeguards.

## 0.5.0 - 2026-07-29

- Add mirrored `paper_handoff.md` guidance and an eight-section HANDOFF template for complete executor-to-paper-writer collaboration.
- Keep RESULT as the concise formal contract and sole downstream modeling interface; HANDOFF remains a derived, evidence-linked writing layer with explicit formal/auxiliary and expression boundaries.
- Explicitly reject single and split HANDOFF files as appendix sources while preserving six commands, Lite v3 marker, existing checker semantics, and valid 0.4.0 workspaces.

## 0.4.0 - 2026-07-29

- Integrate the user-authored execution-first modeling-plan design standard as a byte-exact bundled reference.
- Require semantic preflight, minimal smoke testing, recoverable staged execution, explicit nested cost estimation, and L0/L1/L2 risk-triggered validation when authoring, reviewing, or executing START plans.
- Preserve the Lite v3 marker, eight START and seven RESULT headings, six commands, single/split contracts, checker semantics, appendix workflow, and valid 0.3.1 workspaces.

## 0.3.1 - 2026-07-24

- Allow each official question to use either one unsuffixed START/RESULT pair or contiguous suffixed START units with independently completed RESULT units.
- Add exact `QN_K` dependency tokens, `--subproblem` selection on the two modeling checks, layout diagnostics, and split-aware appendix references.
- Preserve the Lite v3 marker, headings, six commands, standard-library runtime, and compatibility with valid 0.3.0 single-mode workspaces.

## 0.3.0 - 2026-07-23

- Remove `FROZEN_CONTEXT.md` from initialization, managed layout, runtime checks, and active templates.
- Require one exact direct-dependency declaration in START section 2 and validate declared upstream START/RESULT structure.
- Add mandatory Codex semantic contradiction review without consistency state or artifacts; preserve appendix behavior.

## 0.2.0 - 2026-07-23

- Add optional, independent APPENDIX_START/APPENDIX_RESULT contracts and two read-only appendix commands.
- Enforce whitelist-first exact output sets, COPY hashes, source-integrity records, dependency closure, XLSX structure, and sensitive-data checks.
- Keep Lite v3 marker and existing modeling contracts/checker behavior unchanged; appendix commands never read `FROZEN_CONTEXT.md`.

## 0.1.0 - 2026-07-20

- Ship a standalone, Markdown-first Lite v3 Skill with variable-question initialization.
- Provide read-only doctor, START, RESULT, and evidence checks with stable diagnostics and exit codes.
- Reject unsafe evidence paths and symlinks without opening or executing evidence content.
- Support standalone copying on Python 3.11–3.13 using only the standard library and no Full runtime modules.
