# RFC: KyMCM Lite v3

> Historical KyMCM Lite 0.1.0 design record. It does not describe current 0.9.12 behavior; see `skills/kymcm-lite/docs/protocol.md` and the generated complete Project Source. Preserved without rewriting historical decisions.

Current 0.9.12 execution boundary: Codex stops after writing and machine-checking RESULT/RESULT_PRE, waits for explicit user/ChatGPT semantic acceptance, and handles HANDOFF only in a new independent read-only task after acceptance. After an explicit final-figure request, data figures retain `kymcm-figure-selection-v1` and the fail-closed `kymcm-figure-exec-v1` path before ChatGPT/user acceptance. Flowcharts instead use `kymcm-flowchart-selection-v1` and `kymcm-flowchart-content-v1`, then stop before user-owned manual layout/drawing. `nature-figure` remains optional read-only specialist advice only on explicit request. No core command, state, manifest, renderer, or tool route is added. Appendix and final AI-use compliance behavior retain their accepted boundaries; the historical design below remains preserved.

Status: Implemented and release-candidate validated for KyMCM Lite 0.1.0
Product: KyMCM Lite
Protocol marker: `{"workflow":"kymcm_lite","version":3}`
Planned Skill name: `kymcm-lite`
Initial product version: `0.1.0-dev`

## 1. Status and terminology

This RFC freezes the proposed Lite product boundary and workspace protocol before an installable Lite Skill is created. The product version (`0.1.0-dev`) describes the planned software release. The protocol generation (`version: 3`) identifies the Lite workspace contract. They may evolve independently.

KyMCM Full v1.0.0 remains a separate product with its own internal Model Spec v3 and ResultRecord v2 schemas. The repeated number 3 does not imply that Lite v3 is compatible with Full Model Spec v3, nor does it permit either product to read the other's artifacts.

Normative terms such as **must**, **must not**, **should**, and **may** describe requirements for a future conforming implementation.

## 2. Motivation

The collaboration pattern that motivates Lite is:

```text
teammate / user / ChatGPT
    -> discusses and adapts the mathematical plan
    -> START_Qi.md
    -> Codex implements, solves, validates, and produces evidence
    -> RESULT_Qi.md
    -> ChatGPT/user reviews and requests targeted revisions
```

This describes roles and handoffs only; it does not depend on or reproduce a private conversation.

> Lite does not need to own mathematical discovery. Its primary job is reliable, low-friction execution handoff.

Full remains valuable when Codex is expected to conduct solo, end-to-end modeling with formal approvals, state, recovery, and revision binding. Lite instead serves time-critical teams that develop mathematical meaning externally and need a compact, auditable boundary between planning, execution, and review.

## 3. Product boundary

### 3.1 Lite owns

- workspace initialization;
- a concise cross-question frozen-context document;
- one self-contained Start contract per question;
- one self-contained Result handoff per question;
- read-only structural and evidence checks;
- a clear Codex execution-boundary policy;
- optional Git diagnostics;
- Markdown and safe-path conventions.

### 3.2 Lite does not own

- whole-problem Problem Definition approval;
- content-level JSON schemas;
- model discovery or method selection;
- submit, accept, replan, recover, or stale state machines;
- event logs or prescribed approval wording;
- deterministic JSON-to-Markdown rendering;
- automatic paper generation;
- solver orchestration;
- multi-agent scheduling;
- automatic acceptance of mathematical conclusions.

> Full is an end-to-end modeling workflow. Lite is an execution protocol.

## 4. Design principles

1. **Author once.** Mathematical meaning is written once in Markdown, not duplicated in JSON.
2. **Markdown is the interface.** Human-authored Markdown is authoritative.
3. **Machine checks are read-only.** Checkers diagnose; they do not rewrite contracts or advance hidden state.
4. **External modeling is first-class.** A teammate or ChatGPT may author the plan.
5. **Execution must be constrained.** Codex may choose implementation details but may not silently change mathematics, data meaning, parameters, or decision rules.
6. **Current context over process history.** Git history records prior versions; formal documents contain the current contract only.
7. **Evidence over ceremony.** Result claims link to real files, but no approval state machine is required.
8. **Speed is a feature.** The workflow must not add avoidable tool calls, serialization, or approval loops.
9. **Full remains isolated.** Lite must not import or depend on Full checkpoint runtime.
10. **Safe failure.** Semantic uncertainty or input-changing anomalies stop execution; implementation defects are repaired locally.

## 5. Workspace identity and persistent state

Every new Lite workspace uses exactly this marker in `.kymcm/mode.json`:

```json
{"workflow":"kymcm_lite","version":3}
```

For the MVP, this is the only required persistent JSON file. Lite creates no workflow-state JSON, event log, artifact cache, review hash, or approval record. Checkers may emit deterministic diagnostics but must not persist them.

Full and Lite markers are mutually exclusive within one workspace. An unknown marker fails closed. A Lite tool must never silently accept, convert, or treat a Full workspace as Lite.

## 6. Workspace layout

The intended managed layout is:

```text
CUMCM_Workspace/
├── .kymcm/
│   └── mode.json
├── FROZEN_CONTEXT.md
├── input/
├── paper/
├── reports/
└── problems/
    ├── q1/
    │   ├── spec/
    │   │   └── START_Q1.md
    │   ├── code/
    │   ├── data/
    │   │   └── derived/
    │   ├── outputs/
    │   ├── notes/
    │   └── result/
    │       └── RESULT_Q1.md
    └── qN/ ...
```

START and RESULT retain the proven Full locations so that cross-agent handoff habits remain stable. Initialization accepts a variable positive question count and creates problem directories from `--questions N`; it does not force Q1–Q4. A dynamic `add-problem` command is deferred unless MVP implementation proves it simpler.

Unknown root files are allowed. Lite validates only managed paths and safe evidence references. Initialization creates empty managed structure only: it does not copy inputs, initialize Git, or create formal START/RESULT content.

Question count is derived without another state file: discover immediate `problems/qN` directories matching `q[1-9][0-9]*`, require at least q1, and require contiguous numbers from 1 through the maximum. Every discovered question must contain the managed subdirectories shown above. Unknown entries under `problems/` remain informational unless they interfere with a managed path, and `--problem N` must select a discovered positive question number.

## 7. `FROZEN_CONTEXT.md`

`FROZEN_CONTEXT.md` is the concise current source of truth for information needed by more than one question. It is neither a complete Problem Definition nor an approval object. It has exactly these required headings, in order:

```markdown
# FROZEN CONTEXT

## 1. 共享定义与符号
## 2. 全局数据口径
## 3. 已冻结参数与规则
## 4. 跨题输出与文件接口
## 5. 当前限制与注意事项
```

Authors keep only cross-question information here and must not copy complete START or RESULT documents. Current values are updated in place; Git records history. Q1 may begin with a sparse context. From Q2 onward, inherited outputs and file interfaces must be explicit. MVP checkers verify that the file exists and is readable but do not attempt semantic parsing.

## 8. START contract

The authoritative path is `problems/qN/spec/START_QN.md`. The path identifies the question; MVP START files have no YAML front matter and no companion JSON.

Required headings, exactly and in order, are:

```markdown
# START QN

## 1. 问题目标与直接交付
## 2. 已冻结输入与前问继承
## 3. 数据口径与预处理
## 4. 数学模型、参数与判定规则
## 5. Codex 执行边界
## 6. 输出与证据清单
## 7. 验证、求解预算与停止规则
## 8. 未决问题
```

The sections have these normative meanings:

1. State what must be answered, not merely a method name.
2. Link to relevant `FROZEN_CONTEXT.md` entries and predecessor outputs.
3. Define observation units, sample scope, missing-value treatment, pairing, normalization, and every anomaly that changes model input.
4. State the actual mathematics, parameter values, objective, constraints, decision logic, and permitted approximations.
5. Separate immutable mathematical choices from implementation choices Codex may make.
6. Name expected outputs and evidence files; they need not exist before execution.
7. Define validation, runtime, optimality-gap or iteration limits, fallback behavior, and completion criteria.
8. Contain only `无`, `None`, or `N/A` before execution is allowed.

The document must be self-contained enough for Codex to implement the question without the originating chat.

## 9. Codex execution policy

After receiving a START, Codex must:

1. read `FROZEN_CONTEXT.md` and the complete current START;
2. inspect only relevant input and predecessor evidence;
3. preserve all stated mathematical semantics, parameters, constraints, and decision rules;
4. choose ordinary implementation details independently when they do not alter conclusions;
5. stop and ask one highest-impact question when semantic ambiguity remains;
6. stop if newly discovered data issues change values, missingness, sample membership, pairing, or model input;
7. repair parsers, paths, syntax, caches, logging, plotting mechanics, and other implementation defects without rewriting START;
8. never silently replace an infeasible model, change a parameter, reduce scenario count, relax a constraint, or alter a stopping rule;
9. record every authorized deviation from START in RESULT;
10. avoid recreating Full JSON artifacts or hidden workflow state.

## 10. RESULT contract

The authoritative path is `problems/qN/result/RESULT_QN.md`. Required headings, exactly and in order, are:

```markdown
# RESULT QN

## 1. 直接答案
## 2. 实际执行方案与 START 偏差
## 3. 关键结果
## 4. 验证与审计
## 5. 证据索引
## 6. 局限性与风险
## 7. 下游冻结输出
```

The sections have these normative meanings:

1. Answer the question directly.
2. State the actual configuration and every deviation, or explicitly state `无偏差`.
3. Report interpretable values rather than raw logs.
4. Report applicable feasibility, residuals, solver status, gap, stability, sensitivity, or sample-out diagnostics.
5. List concrete workspace-relative evidence.
6. Identify limitations and prevent overstated conclusions.
7. Identify exactly what later questions may inherit and what should be copied into `FROZEN_CONTEXT.md`.

MVP evidence entries use this syntax:

```markdown
- E1 — `problems/q1/outputs/summary.csv` — 主结果表
- E2 — `problems/q1/code/solve.py` — 正式求解代码
- E3 — `problems/q1/outputs/figure1.png` — 论文图
```

Each evidence bullet contains exactly one path in backticks. The path must be workspace-relative, must contain neither an absolute prefix nor a `..` segment, and must resolve to an existing ordinary file inside the current question's `code`, `data/derived`, `outputs`, or `notes` directory. Symlinked evidence is unsafe. RESULT summarizes a handoff but does not replace its evidence, and Lite creates no ResultRecord JSON.

## 11. Intended checker interface and semantics

The planned standard-library-only entry point is `skills/kymcm-lite/scripts/lite.py`, with these intended commands:

```bash
python lite.py init --workspace PATH --questions 3
python lite.py doctor --workspace PATH
python lite.py check-start --workspace PATH --problem 1
python lite.py check-result --workspace PATH --problem 1
```

This interface is specified for review; it is not implemented in Phase 1.

### 11.1 `init`

- requires a positive `--questions` value;
- refuses an existing target containing conflicting managed paths;
- writes the exact Lite marker;
- creates `FROZEN_CONTEXT.md` and the requested question directories;
- creates no START, RESULT, copied input, model, evidence, state, Git repository, or paper content beyond empty managed directories and a minimal context template.

### 11.2 `doctor`

`doctor` read-only checks the exact marker, managed-directory completeness, Python version, unsafe symlinks in managed paths, optional Git availability, and a START/RESULT discovery summary. Unknown root files are informational only.

### 11.3 `check-start`

Blocking errors are: wrong mode; missing or unreadable `FROZEN_CONTEXT.md`; missing START; incorrect `# START QN` identity; missing, duplicate, or reordered required headings; section 8 containing content other than the permitted semantic-empty sentinels `无`, `None`, or `N/A` after trimming whitespace; and unsafe managed-path symlinks.

Warnings are: sparse `FROZEN_CONTEXT.md` for Q2 or later; no Git repository; and unusually empty required sections. Expected evidence named in section 6 may be future output and is not required to exist before execution.

### 11.4 `check-result`

Blocking errors are: any `check-start` blocking error; missing RESULT; incorrect `# RESULT QN` identity; missing, duplicate, or reordered required headings; missing START-deviation statement; malformed evidence bullets; and unsafe, missing, symlinked, or out-of-question evidence files.

Warnings are: no Git repository; dirty current-question code or derived data; missing validation detail; no downstream frozen outputs; and a RESULT whose modification time predates START. Modification time is only an advisory staleness heuristic.

### 11.5 Exit codes and side effects

```text
0 = structurally valid; warnings may exist
1 = contract/evidence invalid
2 = tool or environment error
```

Checkers must never modify documents, Git state, or evidence and must never execute user code.

## 12. Git and evidence policy

Git is not required for START or RESULT checking. Git presence and current-question dirty state are diagnostics, not blocking gates in the MVP. Users should commit a finalized START before long execution and code/evidence before external review, but Lite performs no automatic commit, tag, branch, stash, or hand-entered Markdown hash workflow. Strict revision binding remains a Full feature.

Evidence existence and path safety remain blocking because missing or misleading evidence breaks the handoff.

## 13. Full/Lite coexistence

After Lite implementation the repository will contain sibling Skills:

```text
skills/kymcm-full/
skills/kymcm-lite/
```

Users invoke one explicitly; no generic `kymcm` Skill guesses the workflow. Lite must not import `checkpoint_full`, `full_checkpoint.py`, Full workflow modes, Full schemas, or Full state storage. It may copy small Markdown or style references into its standalone directory, but may not create a runtime dependency on Full. Shared behavior must be justified by demonstrated Lite use rather than copied wholesale. Full v1 compatibility and release tests remain intact.

## 14. Security and privacy

- Managed paths reject symlink escape.
- Evidence paths reject absolute paths and `..` segments.
- Checkers do not execute user code.
- Fixtures ship no API credentials, conversation exports, real contest materials, or personal paths.
- Lite core uses only the Python standard library.
- Optional modeling dependencies belong to contest code, not Lite workflow runtime.

## 15. Efficiency objectives

1. A current-question handoff requires reading at most three formal Markdown files: `FROZEN_CONTEXT.md`, `START_QN.md`, and, during review, `RESULT_QN.md`.
2. Mathematical meaning has one authoritative representation.
3. Required persistent machine metadata stays below 1 KiB for the MVP mode marker.
4. `doctor`, `check-start`, and `check-result` complete in under one second on the synthetic fixture under ordinary local conditions.
5. The synthetic comparison shows no content-level JSON and no duplicate rendered review document.
6. The number of blocking human checkpoints is zero; meaningful modeling discussion remains external.
7. Formal-artifact bytes should be lower than the equivalent Full synthetic flow; Phase 1 measures and reports the actual reduction instead of asserting an unsupported percentage.

## 16. Non-goals for Lite 0.1

- automatic paper assembly;
- a deterministic figure-rendering system;
- Result Git-hash binding;
- automatic migration from Full;
- conversion of Full JSON to Lite Markdown;
- a remote collaboration service;
- task scheduling or agent orchestration;
- semantic formula parsing;
- automatic validation of mathematical correctness;
- dynamic `add-problem` unless MVP feedback requires it;
- Markdown front matter or a plugin-specific database.

## 17. Decisions recommended for RFC acceptance

| Decision | Recommendation |
|---|---|
| Question count | `init --questions N`, variable count |
| Root allowlist | No strict allowlist; validate managed paths only |
| Git requirement | Advisory, not blocking |
| Content JSON | None |
| Front matter | None in MVP |
| Evidence syntax | One backticked workspace-relative path per bullet |
| Figure system | Deferred; ordinary contest code may generate figures |
| Full code reuse | No runtime reuse |
| Approval/state machine | None |
| FROZEN_CONTEXT | Required file, semantically light for Q1 |

These are the complete product-level recommendations for this draft; no additional unresolved product decision is hidden by the protocol.

## 18. RFC acceptance criteria

The RFC is ready for user acceptance only when:

1. Full and Lite responsibilities are unambiguous.
2. START and RESULT are the only per-question formal handoff documents.
3. No content-level JSON or hidden state is required.
4. The exact marker, paths, headings, evidence syntax, checker behavior, and exit codes are specified.
5. Semantic-change versus implementation-repair behavior is explicit.
6. Variable question count and a permissive root layout are explicit.
7. Git is advisory while evidence existence and safety are blocking.
8. Lite runtime independence from Full is explicit.
9. Efficiency objectives are measurable.
10. The document contains no private simulation content or unsupported marketing claim.
