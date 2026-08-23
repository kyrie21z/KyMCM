# Optional rapid Explore work

Stable identifier: `kymcm-explore-v1`

## Purpose and non-purpose

Explore is an optional, lightweight research loop for one concrete material uncertainty that may change the formal modeling or algorithm route. Its question is: **does this idea deserve formal investment?** Formal START/RESULT work instead asks for the final defensible and auditable answer.

Use Explore only when the current route is not yet clear enough for a responsible, formally complete START. When the route is clear, proceed directly to START; creating an Explore workspace is neither required nor noteworthy.

Explore is scratch work. It creates no formal contract, accepted state, approval object, dependency, HANDOFF content, formal evidence, Appendix source, or final figure.

## Optional trigger

Enter Explore when a specific uncertainty could materially change the route, for example whether:

- one of two algorithms gives a materially better search signal;
- a strict domain reduction preserves known good candidates while improving discovery;
- seed diversity is more useful than deeper search in the same basin;
- a formulation is computationally viable at the relevant scale;
- a surrogate, decomposition, or objective has enough signal to formalize.

Difficulty, lack of prior runs, or a general desire for more experiments is not by itself a trigger. No concrete material uncertainty means no Explore workspace.

## Workspace

When Explore is explicitly entered for QN, create or reuse exactly one problem-level workspace:

```text
problems/qN/explore/
├── EXPLORE_QN.md
├── code/
└── outputs/
```

`EXPLORE_QN.md` is the durable reasoning and decision log. `code/` holds disposable experiment programs; `outputs/` holds coarse results, logs, diagnostics, traces, and temporary tables. Prefer `tN_` artifact prefixes when useful, but naming is not machine-enforced. Trial files may be replaced or removed; append new decisions to the log and retain failed directions so they are not rediscovered.

The same problem-level workspace applies to single and split mode. Name a split unit in Trial prose when relevant; do not create suffixed Explore logs or dependency tokens. v1 has no PRE Explore workspace.

Lite `init` does not create this directory. Existing workspaces need no migration, and Lite Python does not manage, parse, or validate its contents.

## One Trial

Each Trial records only what is needed to make the decision:

```text
Hypothesis
one falsifiable idea

Test
the cheapest experiment expected to distinguish it

Budget
one natural hard maximum

Decision rule
evidence that would justify PROMOTE, DROP, or NEXT

Result
actual observations

Decision
PROMOTE | DROP | NEXT after ChatGPT/user review
```

Trial numbers such as T1 and T2 are human traceability only. Fields, numbering, continuity, immutability, and correspondence are not Python grammar. Add a comparator, metric, failure note, artifact link, or next-test idea only when it improves the decision.

## Minimum sufficient experiment

Run only the minimum experiment sufficient to change the current decision. Appropriate fidelity follows from the hypothesis and may be a reduced instance, coarse search, a few generations, one or a few seeds, a simplified evaluator, one counterexample, a microbenchmark, a data subset, a partial pipeline, or a toy proof of concept. There is no universal fidelity ladder.

Examples:

```text
Hypothesis: seed diversity is more valuable than deeper search in one basin.
Test: compare one additional seed with one additional same-seed coarse cycle
      under one small fixed budget.
Then STOP.
```

```text
Hypothesis: a layered objective improves candidate discovery.
Test: run only its cheap first layer; fusion and fine certification are outside
      this decision test.
Then STOP.
```

## Budget

Use one natural hard budget unless the test is effectively instantaneous, for example `<= 3 min`, `<= 5000 candidate evaluations`, or `20 generations`. The budget is a maximum, not a target. Stop early on decisive evidence. When the budget ends without enough evidence, stop and submit the Trial for `NEXT` review rather than continuing to convergence.

Comparable budgets are useful for an A/B hypothesis, but are not a universal requirement for unrelated tests.

## Mandatory STOP gate

After the stated Test executes:

1. record the actual Result;
2. stop execution;
3. return the evidence to ChatGPT/user;
4. wait for semantic review and an explicit `PROMOTE`, `DROP`, or `NEXT` decision.

The executor reports evidence and may leave Decision pending. It does not spend unused budget or automatically run another seed, generation, higher-fidelity search, Pattern Search, local optimization, certification, L0, export, formal RESULT, or the next Trial.

The correct loop is:

```text
Hypothesis -> Minimum useful Test -> STOP -> PROMOTE / DROP / NEXT
```

## Decisions

- `PROMOTE`: the idea deserves formalization. The scratch result itself is not formally accepted.
- `DROP`: stop investing in the idea unless a materially new hypothesis or evidence appears. Preserve the decision in the log.
- `NEXT`: current evidence is insufficient. Design one newly approved cheapest discriminating Trial; do not execute it until explicitly requested.

`NEXT` may change the seed, metric, baseline, reduced instance, counterexample, or test design. It does not imply a fidelity increase.

## Before START

Use Explore before START only when a material unresolved route choice prevents a responsible formal plan. PROMOTION informs the route, but the later START must remain self-contained and independently meet every existing requirement for identifiability, feasibility, boundedness, solvability, smoke, staged recovery, resources, L0/L1/L2, reuse, and formal success.

The formal plan must recreate or deliberately transfer the needed implementation to managed paths and rerun it at formal fidelity. It must not depend on reading `EXPLORE_QN.md` or scratch outputs.

## Detour during formal execution

If a new material uncertainty about the route appears after START, pause formal execution, run at most the explicitly approved Explore Trial, and stop for review. Explore never silently changes START.

- If a promoted insight is compatible with the existing mathematics, validation, and success criteria, transfer it to the formal code path and rerun it under formal audit rules.
- If it materially changes the model, algorithm, validation, success criteria, or resource tradeoff, revise START under existing rules, rerun its checker and semantic reviews, invalidate affected artifacts or caches, and only then resume.
- `DROP` returns to the existing route only if it remains viable. `NEXT` keeps formal work paused until the next Trial is approved.

If START already names the same risk-triggered L1 experiment as the correct formal test, run L1. Explore is not a route for evading the formal contract.

## Before Supplement

After an accepted base RESULT, proceed directly to Supplement when the needed validation, revision, or repair is known. If the problem is known but the repair route is materially uncertain, the same problem-level Explore workspace may test one idea first.

Explore reserves no Sx number and changes no accepted state. A promoted repair must become the next legitimate Supplement Start and be rerun/revalidated under it before affecting formal state.

## Scratch-to-formal boundary

`problems/qN/explore/**` is outside every formal surface:

- no formal START/RESULT or Supplement evidence path may resolve there;
- no `EXPLORE`, Trial, or Explore path is a dependency token;
- HANDOFF describes only later accepted formal work, never scratch findings as results;
- Appendix cannot copy from Explore into nested code/results or root assets;
- Explore plots remain diagnostics and cannot enter the formal figure bundle;
- existing final AI-use disclosure remains the authority for AI-assisted Explore activity.

Promotion is a modeling decision, not accepted state. Recreate or transfer and rerun all required code, data, results, and figures under the existing managed formal workflow before relying on them.

## What Lite Python does not enforce

Lite Python does not decide when Explore is useful; create its workspace; parse the log; enforce fields, numbering, budgets, STOP, or decisions; validate experiments; guarantee scratch reproducibility; promote artifacts; or delete stale files. The executor, ChatGPT, and user own these semantic responsibilities.
