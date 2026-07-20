# KyMCM Lite v3 Phase 1 — Protocol Freeze and Synthetic Handoff Validation

Status: Planned; begins only after RFC review
Scope: Documentation and synthetic fixtures only

## 1. Phase objective

Validate that the Lite protocol can carry an externally developed model from ChatGPT or team discussion to Codex execution and back to external review, without implementing a workflow engine.

## 2. Deliverables

Phase 1 plans these files:

```text
docs/lite-v3-rfc.md
docs/lite-v3-phase1-plan.md
docs/lite-v3/
├── FROZEN_CONTEXT.template.md
├── START_QN.template.md
├── RESULT_QN.template.md
├── diagnostics.md
├── benchmark-method.md
├── benchmark-report.md
└── reviewer-record.md
tests/fixtures/lite_synthetic_handoff/
├── .kymcm/mode.json
├── FROZEN_CONTEXT.md
├── input/...
├── problems/q1/spec/START_Q1.md
├── problems/q1/result/RESULT_Q1.md
├── problems/q1/outputs/...
├── problems/q2/spec/START_Q2.md
├── problems/q2/result/RESULT_Q2.md
├── problems/q2/outputs/...
├── problems/q3/spec/START_Q3.md
├── problems/q3/result/RESULT_Q3.md
├── problems/q3/outputs/...
└── review_snapshots/before_q2/FROZEN_CONTEXT.md
tests/test_lite_v3_phase1.py
```

The scenario will be wholly invented. It models a collaboration pattern and does not reproduce a real contest problem.

## 3. Synthetic scenario requirements

The fixture will use a small, invented planning problem with three dependent questions:

- Q1 produces a baseline allocation or ranking.
- Q2 receives an externally authored uncertainty/risk adaptation and inherits Q1 outputs.
- Q3 receives an externally authored interaction/sensitivity extension and inherits Q1/Q2 interfaces.
- Files remain tiny, deterministic, and understandable without numerical solvers.
- Evidence may be hand-authored CSV or text because Phase 1 validates handoff semantics rather than computation.
- One RESULT discloses one authorized START deviation.
- Every RESULT provides explicit downstream frozen outputs.
- No fixture includes real contest wording, data, names, paths, or outputs.

## 4. Protocol review tasks

1. Materialize the three Markdown templates exactly from the RFC.
2. Write a diagnostic catalog containing identifier, severity, trigger, blocking behavior, and message intent.
3. Build complete Q1–Q3 synthetic handoffs.
4. Conduct a manual reviewer test:
   - the Q2 implementer reads only `FROZEN_CONTEXT.md` and `START_Q2.md`;
   - the Q2 reviewer reads those files plus `RESULT_Q2.md` and its listed evidence;
   - record missing context and duplicated content.
5. Compare Lite formal artifacts with the existing Full synthetic flow by formal-file count, total bytes, duplicated semantic representations, required approval transitions, and evidence-path coverage.
6. Revise the RFC only when the exercise demonstrates an ambiguity; do not add speculative features.
7. Present the RFC, templates, diagnostics, synthetic handoff, and benchmark report for user review before coding.

## 5. Provisional diagnostic catalog

Phase 1 defines identifiers but does not implement them. The initial catalog must include at least:

| Identifier | Severity | Trigger | Blocking | Intended message |
|---|---|---|---|---|
| `LITE-MODE-001` | Error | Marker is missing, unknown, or not exactly Lite v3 | Yes | Select or initialize the correct workspace; never guess the mode |
| `LITE-LAYOUT-001` | Error | A required managed path is missing or an unsafe managed symlink is found | Yes | Name the managed path and required safe form |
| `LITE-START-001` | Error | START identity or required heading structure is invalid | Yes | Name the first structural mismatch and expected contract |
| `LITE-START-UNRESOLVED-001` | Error | START section 8 contains content other than `无`, `None`, or `N/A` | Yes | Resolve the open issue before execution |
| `LITE-RESULT-001` | Error | RESULT identity, headings, or deviation statement is invalid | Yes | Name the missing or malformed handoff element |
| `LITE-EVIDENCE-001` | Error | Evidence syntax, existence, file type, symlink safety, or question scope is invalid | Yes | Identify the entry and its safe allowed locations |
| `LITE-GIT-WARN-001` | Warning | Git is unavailable, absent, or relevant paths are dirty | No | Explain the review risk without preventing checking |

The expanded catalog may split these families into more precise stable identifiers. It must preserve severity and blocking semantics defined by the RFC.

## 6. Benchmark and reviewer record

`benchmark-method.md` will define reproducible inclusion rules before measuring. It will report, rather than estimate:

- number and total UTF-8 bytes of formal artifacts;
- which meanings, if any, appear in more than one authoritative representation;
- number of required approval transitions;
- count and resolution rate of RESULT evidence paths;
- the Full comparison fixture and exact measurement commands;
- reviewer-test omissions and duplicated content.

Generated caches, source-control internals, implementation code, and ordinary solver output are excluded unless they are themselves formal workflow artifacts. This keeps the comparison about protocol overhead.

## 7. Success criteria

Phase 1 passes when:

1. all template headings match the RFC exactly;
2. the synthetic Q1–Q3 handoff is self-contained;
3. no content-level JSON, approval state, or event log appears;
4. every RESULT evidence entry resolves to an existing safe fixture file;
5. Q2 and Q3 use `FROZEN_CONTEXT.md` rather than duplicating whole predecessor Results;
6. the authorized deviation is visible in the relevant RESULT;
7. a reviewer can identify the direct answer, actual configuration, validation, evidence, limitations, and downstream interface without reading code;
8. the benchmark reports actual artifact counts and byte totals;
9. Full tests remain green;
10. release-tree, privacy, and link checks remain green;
11. no installable `skills/kymcm-lite/` exists yet;
12. the user explicitly accepts the RFC before Phase 2 implementation.

## 8. Verification

After the RFC-writing run:

```bash
python -m unittest tests.test_release_tree -v
git diff --check
```

During the later Phase 1 materialization run, add a small docs/fixture test module and run the Full suites to confirm product isolation. The new tests should verify exact headings, safe evidence resolution, fixture privacy, and reported benchmark counts without importing Full runtime.

## 9. Stop and review gate

At the end of Phase 1, present the RFC, templates, diagnostic catalog, synthetic handoff, reviewer record, and measured benchmark to the user. Stop before creating a Lite runtime, CLI, or installable Skill. Phase 2 starts only after explicit user acceptance of the RFC.
