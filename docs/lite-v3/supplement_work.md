# Question-level Supplement work

## Purpose and authority

Use Supplement only after an official question's base contracts are complete and checked. It records post-result validation, a model/data/certification revision, or an implementation repair without overwriting the visible identity of the base START/RESULT. It is an append-only question-level extension, not a second workflow or a Git replacement.

Current effective technical state is the base RESULT set plus completed Supplement Result entries applied in S1, S2, ... order. A completed entry adds evidence or replaces only the content it explicitly names. Unmentioned base and earlier-Sx conclusions remain effective. Machine evidence controls actual values, files, and diagnostics; HANDOFF summarizes but is never a fact source or modeling dependency.

Do not use Supplement while base work is incomplete. In single mode, require `RESULT_QN.md` to exist and pass `check-result --problem N`. In split mode, require every contiguous START unit to have a matching RESULT and every `check-result --problem N --subproblem K` to pass. Until then, revise the active base START, code, and execution plan.

## Identity and lifecycle

Each official question has at most this one pair in single and split modes:

```text
problems/qN/spec/SUPPLEMENT_START_QN.md
problems/qN/result/SUPPLEMENT_RESULT_QN.md
```

Never create suffixed Supplement contracts, `followups/`, `supplements/`, Sx subdirectories, a state machine, or a PRE Supplement. `init` creates no Supplement file. Existing user-created same-name files are not migrated automatically; review and organize them manually before the next use.

Append Start entries continuously as S1, S2, S3, ... without gaps, reuse, deletion, or reordering. A Result entry must have the matching prior Start, and Result entries form a continuous prefix of Start entries. Keep titles identical or unambiguously corresponding.

For every Sx:

1. Read the complete base START/RESULT set, all earlier Supplement Start/Result entries, and relevant machine evidence.
2. Append and semantically review the complete Sx plan before running any Sx-specific code.
3. Execute the work without rewriting the plan from hindsight.
4. Append the matching Sx result, including deviations, failure, fallback, and omitted work.
5. Refresh the one question-level HANDOFF from the new current effective state.

Completed Start/Result entries are frozen. Correct later semantic, mathematical, data, numeric, evidence, replacement-scope, or downstream-interpretation problems through the next Sy entry. Only meaning-neutral spelling, formatting, or dead-link repair may edit a completed entry directly.

## Types and impact modes

Use exactly one type:

- `补充验证`: preserve model meaning while adding seeds, out-of-sample/time/scenario checks, sensitivity, robustness, ablation, stress tests, omitted L1/L2, constraint audits, or error diagnostics.
- `方案修订`: change a model, objective, constraint, decision rule, data scope, feature, estimation, metric, validation design, success criterion, or certification meaning.
- `实现修复`: preserve the mathematical definition while repairing code such as indexing, units, boundaries, sorting, aggregation, solver parameters, export, readback, or result calculation.

Use exactly one impact mode: `追加证据`, `局部替代`, `完全替代`, or `不改变正式状态`. A revision identifies every replaced base/earlier-Sx item, every continuing item, the new formal values and interface, and its exact target units. An implementation repair explains mathematical invariance, invalid old outputs, recomputation scope, and replacement evidence. Never write only “use the new result.”

Result conclusion is exactly `完成`, `中止`, or `失败`. Only `完成` with an explicit impact scope may add to or replace current formal state. `中止` and `失败` preserve technical history and may add limitations, risks, or failed-attempt records, but cannot create new formal numeric conclusions. Disclose material failure or abort information in HANDOFF.

## Units, evidence, and overwrite safety

Single mode targets exact `QN`. Split mode lists one or more exact `QN_K`; a whole-question entry lists every affected unit and never uses a wildcard. Supplement-specific code, configuration, derived data, outputs, and notes remain in the existing QN directories and should use new `sN_` paths. Do not overwrite base or earlier-Sx artifacts. Modify shared modules only when directly necessary, then record compatibility and recomputation scope.

Evidence scope remains the current QN's `code/`, `data/derived/`, `outputs/`, and `notes/`. Supplement Markdown contracts themselves are not machine-evidence paths and cannot be copied into appendix. Current Supplement code and result attachments may enter appendix through existing whitelist rules; superseded implementations and results stay out unless a competition explicitly requires historical comparison.

Formal Supplement work remains non-visual by default. Use structured evidence and only the smallest diagnostic required for a named risk. Final display work remains an explicit separate `figure/` task and cannot create Supplement conclusions silently. PRE remains governed by START_PRE/RESULT_PRE and downstream impact review.

## Dependencies, HANDOFF, and impact review

Dependency grammar does not change. A later START still names only exact base RESULT tokens such as `Q1` or `Q2_1`; `S1`, `Q1@S1`, and `SUPPLEMENT_Q1` are invalid dependency identities. When a dependency question has Supplement files, read its complete base pair, complete Supplement Start/Result files, all completed entries targeting that token, and cross-unit entries affecting shared data, interfaces, or limitations.

An unmatched pending Start does not change formal state, but treat a material planned upstream change as a prominent pending risk. Stop and ask one highest-impact question when numbering has a gap, a Result lacks a plan, replacement scope is ambiguous, evidence conflicts, or the current interface cannot be determined.

A material completed Supplement Result triggers impact review of completed downstream questions. If downstream work must change, create that downstream question's own next Supplement entry rather than overwriting its base RESULT.

Refresh `problems/qN/notes/HANDOFF_QN.md` after every new Supplement Result. List base RESULT files first under `正式上游`, then `SUPPLEMENT_RESULT_QN.md`. Preserve base-unit and Sx provenance, distinguish effective from superseded history, disclose failures and repairs, map Supplement evidence, and state the final current interface. HANDOFF remains derived, non-formal, unchecked by Python, and excluded from appendix.

Python does not enforce Sx continuity, plan-before-execution, replacement scope, mathematical correctness, or HANDOFF currency. Agent semantic review and final human review remain mandatory.
