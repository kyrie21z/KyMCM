# Paper-writing HANDOFF

## Purpose and authority

Create a matching HANDOFF only after its RESULT passes `check-result` and the formal and supporting evidence used for paper writing is stable. HANDOFF is the sole complete collaboration document from the modeling/programming executor to the paper writer. It is a derived explanation layer, not a formal fact source and not a second contract alongside RESULT.

Apply this authority order:

1. RESULT defines the formally certified conclusions, deviations, limitations, and downstream interfaces.
2. Machine evidence defines actual numeric, tabular, and graphical content.
3. HANDOFF selects, organizes, explains, and bounds those materials for paper writing.
4. The paper writer uses HANDOFF by default and rechecks critical numbers against its evidence paths before finalization.

Stop paper handoff when HANDOFF conflicts with RESULT scope, conclusion status, or limitations; repair HANDOFF to match RESULT. Stop when a HANDOFF value conflicts with machine evidence; repair HANDOFF from the evidence. If RESULT conflicts with machine evidence, treat it as a formal-result defect and return to RESULT/evidence audit. Never reinterpret evidence to expand RESULT's certified conclusions.

## Identity and lifecycle

Use exactly:

- single mode: `problems/qN/notes/HANDOFF_QN.md` with `# HANDOFF QN`;
- split mode: `problems/qN/notes/HANDOFF_QN_K.md` with `# HANDOFF QN_K`.

Match one completed RESULT identity exactly. Never mix single and split HANDOFF files for one question, create an unsuffixed aggregate HANDOFF for a split question, create a question-level HANDOFF index/manifest/subdirectory, or pre-create a paper-ready HANDOFF for a missing or unchecked RESULT.

Before authoring or updating HANDOFF, read the complete matching START and RESULT, every RESULT-declared evidence file, and each selected auxiliary evidence file. Use `templates/HANDOFF_QN.template.md`. After authoring, review it semantically against the RESULT and evidence. A successful review creates no state, approval, hash, report, manifest, or JSON.

Review and update HANDOFF before continuing paper work whenever the matching RESULT, formal evidence, or paper-relevant auxiliary evidence changes materially. Ignore changes limited to timestamps, unrelated caches, or logs that cannot alter paper material. HANDOFF never becomes a downstream modeling dependency; later modeling inherits only formal RESULT. Appendix organization may reference HANDOFF as internal context but must never copy it or treat it as a certification source.

## Complete but selective content

Make HANDOFF self-contained enough that the paper writer need not read the complete START or RESULT first. Include:

- the unit's role in the paper and usable conclusions;
- actual sample, units, filtering, missingness, preprocessing, and execution scope;
- actual model, notation, key formulas, parameter rationale, solver and experiment settings, and decision rules;
- complete paper-relevant values, comparisons, rankings, intervals, and table-ready content;
- executed L0/L1/L2 checks, robustness and sensitivity results, anomalies, failed experiments, and their effect on conclusions;
- recommended figures/tables and how to use them;
- recommended interpretation, conclusion strength, scope, and forbidden overstatement;
- cross-question relationships and final manual checks.

Do not paste complete logs, CSV/JSON files, all intermediate variables, all code, irrelevant failed attempts, or content whose volume obscures the primary result. For every important result, state what the value is, what it means, what conclusion it supports, and what it cannot support.

## Formal and auxiliary separation

Label each paper-relevant item:

- `正式`: within RESULT's certified scope and usable for principal conclusions;
- `辅助`: supported by real question-level evidence but not promoted by RESULT to a formal conclusion, usable only for explanation, limitation, appendix, or discussion.

Never mix the two classes silently or use auxiliary material to enlarge the main conclusion. When an item combines formal and auxiliary components, split it into separate entries and state their different uses.

## Evidence mapping

Give every important number, table, figure, anomaly, and conclusion a workspace-relative evidence path. Prefer this form:

```markdown
- H1 — 正式 — `problems/q2/data/derived/main_results.csv` — 论文表 3 的核心数值
- H2 — 辅助 — `problems/q2/outputs/sensitivity.png` — 只用于敏感性讨论
```

Keep each ID unique within the HANDOFF and each entry limited to one backticked path. Prefer the current question's `data/derived`, `outputs`, or `notes`. Cite code only to explain implementation, never as numeric evidence. A HANDOFF may cite its matching RESULT and necessary exact upstream RESULT/HANDOFF paths for navigation, but HANDOFF itself never proves a fact. Python checkers do not parse this syntax.

## Paper assets and expression boundaries

For every recommended figure or table, specify:

- path and numeric source;
- proposed title or purpose;
- core message;
- main-text, appendix, or optional placement;
- required crop, redraw, merge, or reformatting;
- finalization checks.

For recommended prose, specify the permitted conclusion strength and applicable scope. Explicitly forbid unsupported absolute, causal, universal, or extrapolative wording. Downgrade or repair paper prose that exceeds the HANDOFF boundary.

## Final semantic review

Before handing off, confirm:

- identity and formal-upstream path match the completed RESULT;
- all eight sections are complete and prioritized;
- every important value and asset maps to real evidence;
- formal and auxiliary material are separated;
- RESULT scope and limitations are preserved;
- actual execution, anomalies, failed experiments, and omissions are disclosed where paper-relevant;
- asset use and final numeric checks are actionable;
- claims include both usable wording and explicit boundaries;
- no aggregate HANDOFF, workflow state, downstream dependency, or appendix source is introduced.
