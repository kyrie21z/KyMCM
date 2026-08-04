# Question-level Supplement work

## Purpose and authority

Use Supplement only after an official question's base contracts are complete and checked. It records post-result validation, a model/data/certification revision, or an implementation repair without overwriting the visible identity of the base START/RESULT. It is an optional question-level extension, not a second workflow or a Git replacement.

The current effective technical state is the base RESULT set plus completed, currently valid and explicitly accepted Supplement Result entries applied in S1, S2, ... order. A completed entry adds evidence or replaces only the content it explicitly names. Until the user/ChatGPT accepts an Sx Result, the entry remains pending and does not change the adopted effective state. Unmentioned base and earlier-Sx conclusions remain effective. Machine evidence controls actual values, files, and diagnostics; HANDOFF summarizes but is never a fact source or modeling dependency.

Do not use Supplement while base work is incomplete. In single mode, require `RESULT_QN.md` to exist and pass `check-result --problem N`. In split mode, require every contiguous START unit to have a matching RESULT and every `check-result --problem N --subproblem K` to pass. Until then, revise the active base START, code, and execution plan.

## Identity and lifecycle

Each official question has at most this one pair in single and split modes:

```text
problems/qN/spec/SUPPLEMENT_START_QN.md
problems/qN/result/SUPPLEMENT_RESULT_QN.md
```

Never create suffixed Supplement contracts, `followups/`, `supplements/`, Sx subdirectories, a state machine, or a PRE Supplement. `init` creates no Supplement file. Existing user-created same-name files are not migrated automatically; review and organize them manually before the next use.

Sx entries still begin at S1 and use continuous S1, S2, S3, ... numbering. A Result entry requires the matching prior Start, and Result entries form a continuous prefix of Start entries. Do not reorder, reuse, or renumber an adopted entry.

For every Sx:

1. Read the complete base START/RESULT set, all earlier Supplement Start/Result entries, and relevant machine evidence.
2. Append and semantically review the complete Sx plan before running any Sx-specific code.
3. Execute the work without rewriting the plan from hindsight.
4. Append the matching Sx result, including deviations, failure, fallback, omitted work, evidence, impact, and downstream consequences.
5. Run the applicable machine check, self-review the Result, and stop for explicit user/ChatGPT semantic acceptance. Do not create or refresh HANDOFF in this execution phase.

## Editable and adopted entries

The latest numbered Sx is the **current editable Sx** only when all of the following remain true: it has no later Sy Start or Result; no completed downstream question has used its current interface or conclusion; no later Supplement names it as an inheritance baseline; its code, data, or results have not entered an appendix, formal submission package, or other confirmed delivery; the user has not confirmed it as frozen; and an edit will not silently invalidate an externally used value, interface, or certification boundary.

An Sx is **adopted** and frozen when any of the following occurs: the user/ChatGPT explicitly accepts or freezes its formal Result; a later question completes work based on its current interface; a later Sy names it as an inheritance baseline; its artifacts enter an appendix, formal submission package, or external delivery; or changing it would invalidate completed downstream work, formal delivery, or a certification statement. Merely committing, running locally, passing a checker, refreshing HANDOFF, or creating the entry does not adopt it. HANDOFF use by a downstream question does adopt it under the downstream-use rule.

When adoption cannot be established, treat Sx as frozen and create the next Sy. An adopted Sx may never be rewritten; a change uses the next number and undergoes the ordinary downstream impact review.

The current editable Sx may be edited and rerun in place: revise its target, parameters, scope, budget, stopping rule, or output plan; repair its implementation; remove or replace its same-number Result; and rebuild its own `sN_` artifacts. It may not modify the base START/RESULT, an adopted or non-latest Sx, another Sx's artifacts, or a shared interface without recording compatibility and recomputation scope.

## Start/Result validity and failures

The plan-before-execution rule remains strict. If a current editable Sx already has a Result and its Start receives a material change affecting execution or conclusions, that old Result immediately becomes invalid. Before rerunning, remove the same-number Result entry or replace it with an explicit non-formal incomplete placeholder; prefer removing it so the Result file returns to the previous continuous completed prefix. Only after the revised plan is executed may the same-number Result be written again. After the new Result is checked, stop for acceptance; the existing HANDOFF stays unchanged until the new Result is accepted and a separate HANDOFF task is requested. Never leave a material “new Start + old Result” pair as a valid state.

Meaning-neutral spelling, formatting, or dead-link repairs need not rerun, but the reviewer must confirm that mathematics, data, paths, execution, and conclusions are unchanged.

Ordinary engineering failures in a current editable Sx may be fixed and rerun without a new number: path, syntax, index, configuration, small parameter-selection, or temporary runtime errors that do not affect model meaning or the certified interface. Material failures affecting mathematics, feasibility, model choice, conclusion boundaries, or downstream interfaces must be disclosed in the final Sx Result; they must not be written into HANDOFF before acceptance. A failed or aborted entry does not create a new formal numeric conclusion.

## Types and impact modes

Use exactly one type:

- `补充验证`: preserve model meaning while adding seeds, out-of-sample/time/scenario checks, sensitivity, robustness, ablation, stress tests, omitted L1/L2, constraint audits, or error diagnostics.
- `方案修订`: change a model, objective, constraint, decision rule, data scope, feature, estimation, metric, validation design, success criterion, or certification meaning.
- `实现修复`: preserve the mathematical definition while repairing code such as indexing, units, boundaries, sorting, aggregation, solver parameters, export, readback, or result calculation.

Use exactly one impact mode: `追加证据`, `局部替代`, `完全替代`, or `不改变正式状态`. A revision identifies every replaced base/earlier-Sx item, every continuing item, the new formal values and interface, and its exact target units. An implementation repair explains mathematical invariance, invalid old outputs, recomputation scope, and replacement evidence. Never write only “use the new result.”

Result conclusion is exactly `完成`, `中止`, or `失败`. Only `完成` with an explicit impact scope may add to or replace current formal state. `中止` and `失败` preserve technical history and may add limitations, risks, or failed-attempt records, but cannot create new formal numeric conclusions. A Result removed or invalidated during an editable redo is not part of current formal state.

## Units, evidence, and overwrite safety

Single mode targets exact `QN`. Split mode lists one or more exact `QN_K`; a whole-question entry lists every affected unit and never uses a wildcard. Supplement-specific code, configuration, derived data, outputs, and notes remain in the existing QN directories and should use new `sN_` paths.

Base artifacts, adopted Sx artifacts, and non-latest Sx artifacts are never overwritten. The latest current editable Sx may overwrite or rebuild only its own `sN_` code, configuration, derived data, outputs, and notes after its old Result has been removed/invalidated when required. Shared modules may change only when directly necessary, with compatibility and recomputation scope recorded. Once Sx is adopted, all later changes use new `s(N+1)_` artifacts. Evidence scope remains the current QN's `code/`, `data/derived/`, `outputs/`, and `notes/`; Supplement Markdown contracts are not machine-evidence paths and cannot be copied into appendix.

Formal Supplement work remains non-visual by default. Use structured evidence and only the smallest diagnostic required for a named risk. Final display work remains an explicit separate `figure/` task and cannot create Supplement conclusions silently. PRE remains governed by START_PRE/RESULT_PRE and downstream impact review.

## Dependencies, HANDOFF, and impact review

Dependency grammar does not change. A later START still names only exact base RESULT tokens such as `Q1` or `Q2_1`; `S1`, `Q1@S1`, and `SUPPLEMENT_Q1` are invalid dependency identities. When a dependency question has Supplement files, read its complete base pair, complete Supplement Start/Result files, all completed entries targeting that token, and cross-unit entries affecting shared data, interfaces, or limitations.

If an editable Sx Result is removed or invalidated, downstream work must not read its old interface. If downstream work has already completed, assume that Sx was adopted and refuse an in-place edit. If downstream work has not started, it may read a newly completed same-number Result only after semantic acceptance. A material accepted Result triggers impact review of completed downstream questions; if their work must change, create that downstream question's own next Supplement rather than overwriting its base RESULT.

An unmatched pending Start does not change formal state, but treat a material planned upstream change as a prominent pending risk. Stop and ask one highest-impact question when numbering has a gap, a Result lacks a plan, replacement scope is ambiguous, evidence conflicts, or the current interface cannot be determined.

After writing a new Supplement Result, keep `problems/qN/notes/HANDOFF_QN.md` unchanged while the Result is pending acceptance. Once the user/ChatGPT accepts the Result, only a separate explicit HANDOFF task may refresh it. List base RESULT files first under `正式上游`, then `SUPPLEMENT_RESULT_QN.md`. Preserve base-unit and Sx provenance, distinguish effective from superseded history, omit ordinary debug values discarded by an editable redo, disclose material failures and repairs, map Supplement evidence, and state the final current interface. HANDOFF remains derived, non-formal, unchecked by Python, and excluded from appendix. RESULT acceptance adopts/freezes an Sx; HANDOFF refresh alone does not freeze an Sx or authorize the transfer.

Python does not enforce whether Sx is editable or adopted, adoption triggers, Start/Result invalidation, overwrite permission, downstream impact, Sx continuity, plan-before-execution, replacement scope, mathematical correctness, Result acceptance, HANDOFF authorization/timing, or HANDOFF currency. Agent semantic review and final human review remain mandatory.
