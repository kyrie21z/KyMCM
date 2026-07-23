# KyMCM Lite v3 Protocol

## Workspace identity

`.kymcm/mode.json` contains exactly:

```json
{"workflow":"kymcm_lite","version":3}
```

No other persistent JSON, workflow state, event log, approval, or review hash is used. Full, historical Lite v2, marker-less Legacy, malformed, and unknown workspaces fail closed.

## Managed layout and question discovery

Managed roots are `.kymcm/`, `input/`, `paper/`, `reports/`, and `problems/`. Each `problems/qN/` has `spec/`, `code/`, `data/derived/`, `outputs/`, `notes/`, and `result/`.

Question count is derived from immediate directories matching `q[1-9][0-9]*`. At least q1 is required; numbers must be contiguous from 1 through the maximum. Unknown root entries and unknown entries under `problems/` are allowed unless they interfere with managed paths.
A legacy `FROZEN_CONTEXT.md` is an ignored root: no command opens, validates, hashes, warns about, migrates, or deletes it.

## Formal headings and dependencies

`problems/qN/spec/START_QN.md` uses:

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

Section 8 must reduce to `无`, `None`, or `N/A` before execution.

Section 2 contains exactly one visible dependency declaration:

```markdown
**前问依赖：** 无
```

or a strict ascending direct-predecessor list such as:

```markdown
**前问依赖：** Q1, Q2
```

Q1 uses `无`. Every named predecessor is earlier than the current question and must provide ordinary, non-symlink, UTF-8 START and RESULT files with valid titles and heading structure. Comments and fenced examples do not count. Static checks do not recurse into the predecessor's full validation and do not judge mathematical meaning.

Before authoring, materially revising, reviewing, or executing a dependent START, Codex reads the complete current START and every declared upstream START and RESULT. It compares only inherited or redefined symbols, units, scope, preprocessing, parameters, objectives, constraints, decision rules, paths, values, limitations, and certification claims. Authorized RESULT deviations form part of the effective upstream contract. No-conflict review creates no artifact. A material conflict is reported with exact locations and consequence; execution stops for one highest-impact user decision. See `references/dependency_review.md`.

`problems/qN/result/RESULT_QN.md` uses:

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

Section 2 states `无偏差` or an `授权偏差` with its evidence path. Evidence syntax is exactly:

```markdown
- E1 — `problems/q1/outputs/summary.csv` — 主结果表
```

IDs are unique. Paths are workspace-relative, contain no `..`, and resolve through non-symlink components to ordinary files inside the current question's `code`, `data/derived`, `outputs`, or `notes`.

## Commands and diagnostics

`init --questions N` refuses any existing managed root before writing, creates the exact marker and variable question tree, and creates no START, RESULT, global context, appendix, root code, Git repository, state, content JSON, or evidence. `doctor`, `check-start`, `check-result`, `check-appendix-start`, and `check-appendix-result` are read-only and never execute user code.

Diagnostics use `ERROR|WARNING <ID> <location>: <message>` followed by `SUMMARY errors=N warnings=N`. Errors return 1, warnings alone return 0, and unexpected UTF-8, I/O, subprocess, or environment failure returns 2 with `LITE-TOOL-001`.

Git availability and question-scoped dirty state are advisory. Evidence existence and safety are blocking.

## Optional independent appendix stage

After modeling and the paper/result scope are stable, an author may create `reports/appendix/APPENDIX_START.md`. It is the sole source-to-target whitelist. The modeling workflow has no FROZEN_CONTEXT surface. START_QN and RESULT_QN are contextual references only.

The two submitted surfaces are distinct:

- `appendix/` contains the minimal reproducibility package, formal result attachments, exactly three generated environment files, optional necessary external input, and optional official `Result.xlsx`.
- root `code/` contains only direct concise core-algorithm files for placement after the paper body.

Whitelist entries use:

```markdown
- A001 — COPY — `source/path` → `appendix/target/path` — purpose
- A002 — CURATE — `source/one`; `source/two` → `appendix/target/path` — purpose
- A090 — GENERATE — `appendix/environment/README.md` — purpose
- C001 — COPY — `problems/q1/code/core.py` → `code/q1_core_algorithm.py` — purpose
```

`A[0-9]{3,}` IDs belong to the appendix whitelist and `C[0-9]{3,}` IDs to the root-code whitelist; IDs and targets are globally unique. COPY has one existing source, CURATE has one or more exact `; `-separated sources, and GENERATE is limited to `appendix/environment/README.md`, `requirements.txt`, and `system_info.txt`. Paths are workspace-relative, non-symlink, contain no traversal or absolute syntax, and obey the source/target/mode rules in `references/appendix_organization.md`.

APPENDIX_START section 7 declares exactly one of `外部资料：无` / ``外部资料：`appendix/input` `` and exactly one of `强制结果文件：无` / ``强制结果文件：`appendix/Result.xlsx` ``. Section 9 reduces exactly to `无`, `None`, or `N/A`.

After whitelist-first organization, `reports/appendix/APPENDIX_RESULT.md` accounts for every whitelist ID, records deviations and evidence, and indexes `reports/appendix/evidence/source_integrity.csv`. The CSV header is exactly `path,before_sha256,after_sha256,status`; each source row has identical lowercase SHA-256 values and status `unchanged`. This is execution-provided integrity evidence, not an independent cryptographic timestamp.

`check-appendix-result` enforces the exact declared file set, COPY hashes, directory rules, forbidden/duplicate artifacts, Python syntax and obvious local imports, quoted C/C++ includes, practical literal CMake references, basic XLSX ZIP/XML structure, sensitive information, and visible certification-boundary conflicts. It parses but never imports or executes user code and never invokes solvers, CMake, or compilers. Actual compilation/build and substantive workbook/result checks belong in execution evidence and human review.

## Non-goals

Lite 0.3.0 does not validate mathematical correctness in Python, discover dependencies from prose, expand transitive dependencies, automatically reconcile contradictions, manage approvals/state, migrate Full or Lite v2 workspaces, generate papers or figures, orchestrate solvers or agents, provide `add-problem`, emit JSON diagnostics, build/delete appendix trees, prove result equivalence, fully resolve dynamic imports/CMake, or verify Excel formula/format semantics.
