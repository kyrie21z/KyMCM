# Direct-dependency contradiction review

This semantic review is mandatory while authoring or materially revising a dependent START, before implementing it, and whenever a dependent START is reviewed. Treat the selected `QN` or `QN_K` contract as one independent modeling unit. If `**预处理依赖：** PRE` is declared, first read the complete `START_PRE.md` and `RESULT_PRE.md` pair. For every exact direct dependency named by `**前问依赖：**`, read its complete matching upstream START and RESULT pair. Then read the complete selected current START. Bare question tokens address single-mode units; suffixed tokens address exact split units and never expand. PRE is a separate fixed optional stage, not Q0 and not a question token. Do not compare sibling split units automatically, and never read a legacy `FROZEN_CONTEXT.md`.

Treat each upstream START as the intended contract. Its matching RESULT section 2 authorizes deviations, and the RESULT supplies actual values, formal files, limitations, and certification boundaries. Compare only upstream material the current START uses, redefines, or assumes. For PRE, pay special attention to sample-accounting rules, row/field meanings, units, missingness, deduplication, transforms, split/fold rules, leakage boundaries, and the exact formal derived-data paths. For question dependencies, also check symbols, scope, parameters, objectives, constraints, decision and stopping rules, result values and paths, and claims of feasibility, optimality, robustness, or certification. An additional scenario, metric, validation layer, or constraint is an extension rather than a contradiction when it preserves upstream meanings and outputs.

If there is no contradiction, continue without writing a consistency report, state object, approval, event, hash, evidence file, or copied upstream summary.

If a material contradiction exists, do not execute or silently choose a side. Report all conflicts with the exact current and upstream file/section locations, the two rules, and the practical consequence. Ask one highest-impact user question and stop. After confirmation, revise the affected current START rule directly. For an intentional override, record one concise sentence at that rule, such as `用户已确认：Q2 在此处覆盖 Q1 的价格假设，仅限本题及其下游。`, then rerun this review.

Use this compact shape:

```text
发现依赖矛盾：

1. 当前：START_Q2 §4 使用……
   上游：START_Q1[_K] §4 / RESULT_Q1[_K] §2 使用……
   影响：……

需要确认：本题应继续沿用 Q1 正式口径，还是明确授权 Q2 改用新口径？
```

## Reviewer cases

1. **No-conflict extension.** Q2 keeps Q1's population, units, and formal output while adding a stress scenario. Continue; create no consistency artifact.
2. **Symbol or units conflict.** Q2 treats Q1's kilograms as tonnes without conversion. Report both sections and stop because inherited values are scaled incorrectly.
3. **Formal-result-path conflict.** Q2 reads `solution_dry_run.csv` while RESULT_Q1 designates `solution.csv` as formal. Report and stop because the inherited output is non-authoritative.
4. **Authorized RESULT deviation conflict.** START_Q1 planned a threshold of 0.8, RESULT_Q1 section 2 authorizes 0.75, and Q2 assumes 0.8. The effective upstream threshold is 0.75; report and stop.
5. **Certification-boundary conflict.** RESULT_Q1 certifies only sampled scenarios while Q2 claims global robustness from it. Report and stop because the downstream claim exceeds the upstream boundary.
6. **User-confirmed override.** The user authorizes Q2 to replace Q1's price assumption. Add a concise local override sentence to Q2's affected rule, rerun review, and do not create a global approval table.
7. **PRE row-universe conflict.** RESULT_PRE formally excludes duplicate entity rows, but Q1 silently restores them from raw input. Report and stop because sample accounting and downstream estimates are no longer comparable.
8. **PRE leakage conflict.** START_PRE freezes training-only fitting for normalization, while Q2 fits the transform on all rows. Report and stop because the downstream validation is contaminated.
