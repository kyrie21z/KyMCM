# KyMCM Lite v3 Protocol

KyMCM Lite 0.8.1 is a programming-side, Markdown-first mathematical-modeling protocol. It covers optional shared preprocessing, recoverable modeling execution, evidence-linked formal results, question-level neutral technical handoffs, explicitly requested final figures, and optional submission-appendix curation. It does not generate, plan, read, modify, or check contest manuscripts.

## Workspace identity and layout

`.kymcm/mode.json` contains exactly:

```json
{"workflow":"kymcm_lite","version":3}
```

No other persistent JSON, workflow state, event log, approval, review hash, or manifest is used. Full, historical Lite v2, marker-less Legacy, malformed, and unknown workspaces fail closed.

Managed roots are `.kymcm/`, `input/`, `reports/`, and `problems/`. Each `problems/qN/` has `spec/`, `code/`, `data/derived/`, `outputs/`, `notes/`, and `result/`. The optional fixed `problems/preprocess/` unit has the same directory set, is not Q0, cannot split, and uses `START_PRE.md`, `RESULT_PRE.md`, and optional `HANDOFF_PRE.md`.

`figure/` is an optional known root for explicitly requested final-figure work. It is not managed, required, initialized, structurally checked, reported, or traversed by Lite commands. Question directories are immediate `q[1-9][0-9]*` children, contiguous from q1. A legacy root `FROZEN_CONTEXT.md` or `paper/` directory is completely ignored: no Lite command opens, parses, validates, hashes, migrates, warns about, or deletes it. Unknown root entries remain allowed unless they interfere with managed paths.

## Contract modes and dependencies

Each question independently uses exactly one mode:

- single: `START_QN.md` and optional/completed `RESULT_QN.md`;
- split: contiguous `START_QN_1.md` through `START_QN_K.md`, with RESULT files for any completed subset.

Single and split START files cannot coexist. Suffixes are positive decimal integers without leading zero. Contracts remain directly in `spec/` and `result/`; no aggregate contract, subproblem directory, manifest, or state is introduced.

QN START uses the exact title and headings:

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

Section 8 must reduce to `无`, `None`, or `N/A`. Section 2 may declare `**预处理依赖：** 无` or `**预处理依赖：** PRE`, followed by exactly one visible `**前问依赖：** 无` or strictly ordered exact earlier-unit list such as `Q1, Q2_1`. PRE requires valid START_PRE and RESULT_PRE. Bare dependency tokens name single units only; suffixed tokens name one split unit and never expand. Same-question edges, wildcards, duplicates, missing contracts, and invalid identities are rejected.

Before authoring, materially revising, reviewing, or executing a dependent START, Codex reads the complete current START and each declared upstream START/RESULT pair. It compares inherited or redefined symbols, units, scope, preprocessing, parameters, objectives, constraints, rules, paths, values, limitations, and certification claims. Material contradiction stops execution for one highest-impact decision. A successful review creates no artifact.

QN RESULT uses the exact title and headings:

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

Section 2 states `无偏差` or an authorized deviation with evidence. Evidence paths are workspace-relative, traversal-free, non-symlink ordinary files within the selected unit's `code`, `data/derived`, `outputs`, or `notes`.

## Optional preprocessing

START_PRE and RESULT_PRE use the exact eight headings in their mirrored templates. PRE runs before dependent QN work: author and check START_PRE, complete semantic review and a minimum parsing/transformation smoke test, execute recoverable stages, perform L0 audit, write and check RESULT_PRE, and create HANDOFF_PRE only when a fuller downstream technical transfer is useful.

RESULT_PRE is the authority for common fields, units, row universe, cleaning and transformation rules, shared data products, audit results, and limitations. HANDOFF_PRE is a derived neutral technical handoff for QN executors, reviewers, a future request-driven graphics stage, or other downstream technical collaborators. It is not inherited by modeling and cannot enter appendix outputs.

EDA serves data understanding, model design, or risk identification only and is non-visual by default. Structured statistics, quality tables, and data products take priority. A smallest necessary diagnostic graphic is allowed only when non-visual evidence cannot resolve a named distribution, anomaly, missingness, association, or leakage risk. It must not expand for display needs or decide final graphics.

## Modeling-plan design and execution

`references/modeling_plan_design.md` is the semantic standard. For each selected unit, Codex authors START and passes `check-start`; reviews dependencies and final plan quality; passes the smallest representative end-to-end smoke test; executes recoverable formal stages; completes mandatory L0 audit; runs L1 only for a named remaining risk; runs L2 only when resources permit and it reduces a named risk, strengthens formal evidence, satisfies an explicit user requirement, or is needed for result certification; then writes RESULT with deviations, omitted optional work, evidence, and limitations.

The START defines the minimum formally complete deliverable, authoritative inputs, identifiability/solvability preflight, smoke-test pass condition, recoverable stages, artifacts, cache and reuse rules, resume point, failure behavior, nested cost, peak memory, parallelism, worst-case recomputation, and budget-pressure deletion order. Formal PRE/QN execution is non-visual by default and prefers structured numeric checks, tables, logs, schemas, error metrics, and constraint audits. Only the smallest diagnostic graphic needed to resolve a named risk may enter L0/L1; final display graphics never belong to L0/L1/L2, the modeling budget, or formal delivery.

L0 is mandatory and blocking. L1 has a named trigger. L2 is resource-permitting and non-blocking unless explicitly promoted. The Python checker does not parse these levels, count experiments, judge proportionality or mathematics, or create semantic-review state.

## Technical result handoff

Each official question uses exactly one current problem-level `HANDOFF_QN.md` in both single and split modes. Single mode may create it after `RESULT_QN.md` passes `check-result` and relevant evidence is stable. Split mode may create it only when every contiguous START unit has a matching RESULT, every RESULT passes `check-result --subproblem K`, and all relevant evidence is stable. Partial split RESULT completion remains valid execution progress but cannot produce the current standard HANDOFF. PRE continues to use `HANDOFF_PRE.md`.

Never create a new suffixed `HANDOFF_QN_K.md`. Existing suffixed files remain ordinary legacy notes and are not deleted, renamed, merged, checked, or treated as the current HANDOFF. Adding a split unit or materially changing any RESULT or downstream-relevant evidence requires semantic review and refresh of `HANDOFF_QN.md`.

QN HANDOFF uses:

```markdown
# HANDOFF QN

**正式上游：**

<!-- 单一模式列出 RESULT_QN.md；拆分模式按 K 升序列出全部 RESULT_QN_K.md。 -->

## 1. 任务定位与已认证结论
## 2. 数据口径与实际执行
## 3. 模型、参数与判定规则
## 4. 完整结果与辅助结果
## 5. 验证、异常与失败尝试
## 6. 数据、表格与资产索引
## 7. 结论适用边界与禁止推断
## 8. 下游接口与复核事项
```

PRE HANDOFF uses:

```markdown
# HANDOFF PRE

**正式上游：** `problems/preprocess/result/RESULT_PRE.md`

## 1. 数据阶段定位与已认证结论
## 2. 数据来源、样本与字段
## 3. 数据清洗、转换与样本变化
## 4. 描述统计与探索性发现
## 5. 数据产品与资产索引
## 6. 使用边界与禁止推断
## 7. 各问题数据接口
## 8. 下游复核事项
```

Each RESULT remains the formal boundary for its exact unit and the only modeling-inheritance surface; machine evidence controls actual values and assets; HANDOFF is a derived problem-level explanation and indexing layer. In split mode it reads all completed unit pairs only after the complete RESULT set passes, preserves unit-specific identities and limits, and does not create an aggregate RESULT or new certified conclusion. It records actual execution, full and auxiliary results, validation, anomalies, failed attempts, unrun optional work, evidence paths, scope limits, downstream interfaces, and review points. Later dependencies still name exact RESULT units; HANDOFF cannot become a modeling dependency or be copied to appendix outputs. See `references/technical_handoff.md`.

HANDOFF has no command, checker, state, approval, hash, report, JSON, or manifest. Identity, completeness, synchronization, and factual consistency require semantic review.

## Commands and diagnostics

`init --questions N` refuses any existing managed root before writing and creates the marker plus the requested empty question tree. Optional `--preprocess` adds the PRE directories. It creates no contracts, legacy content root, appendix, root code, Git repository, state, content JSON, or evidence.
It also does not create `figure/`; that root is created only for an explicit final-figure request.

The exact eight public commands are `init`, `doctor`, `check-preprocess-start`, `check-preprocess-result`, `check-start`, `check-result`, `check-appendix-start`, and `check-appendix-result`. All checks are read-only and never execute user code. Diagnostics use `ERROR|WARNING <ID> <location>: <message>` followed by `SUMMARY errors=N warnings=N`; exit codes are 0 for valid/warnings, 1 for contract failure, and 2 for unexpected tool/environment failure. Git availability and relevant managed-scope dirtiness are advisory.

## Optional final figure workspace

Final-figure work begins only after an explicit user request and after relevant RESULT, HANDOFF, structured data, and machine evidence are stable. Use the external `nature-figure` skill and keep figure-generation code, prepared plotting data, and generated assets under workspace-level `figure/`. KyMCM Lite neither bundles nor imports that skill and remains independently runnable without it.

The root has no required internal structure, contract, checker, CLI, manifest, state, approval, hash ledger, or JSON. Figure work cannot become formal evidence, a modeling dependency, or change RESULT certification. If required fields, granularity, scenarios, or intermediate results are absent, return to PRE/QN to produce evidence rather than silently retraining or resolving. Only meaning-preserving mechanical preparation is allowed in `figure/`.

## Optional submission appendix organization

After formal results, explicit submission requirements, and certification boundaries are stable, a user may create `reports/appendix/APPENDIX_START.md`. It is the sole source-to-target whitelist. Inputs come only from `problems/` and `input/`; `figure/` is not a source, and internal START, RESULT, and HANDOFF contracts are contextual references that cannot be copied.

The two output surfaces are:

- `appendix/`: the complete formal solve code package with plotting excluded, formal result attachments, exactly three generated environment files, optional necessary external input, and optional official `Result.xlsx`;
- root `code/`: authentic representative implementation for a final submission document, including applicable core modeling, scheduling, recovery, batch execution, and audit code.

The whitelist covers the formal solve pipeline and runtime/build closure. Plotting, tests, caches, logs, historical experiments, runtime data, credentials, and unrelated infrastructure stay out. COPY and CURATE remain traceable and cannot alter mathematics, execution order, randomness, recovery rules, or result boundaries. Similarity manipulation, copied code, obfuscation, junk/dead code, and unrelated additions are forbidden.

APPENDIX_START uses:

```markdown
# APPENDIX START

## 1. 提交范围与比赛要求
## 2. 正式结果与认证边界
## 3. appendix 目标结构
## 4. appendix 文件白名单
## 5. code 文件白名单
## 6. 依赖闭包与机械裁剪规则
## 7. 环境、外部资料与强制结果文件
## 8. 验收方法与停止规则
## 9. 未决问题
```

APPENDIX_RESULT uses:

```markdown
# APPENDIX RESULT

## 1. 最终交付结构
## 2. 实际整理方案与 APPENDIX_START 偏差
## 3. 白名单执行结果
## 4. 依赖闭包与编译构建验证
## 5. 正式结果一致性
## 6. 强制结果文件核验
## 7. 排除项与敏感信息扫描
## 8. 原始工程只读验证
## 9. 证据索引
## 10. 局限性与人工复核事项
```

Whitelist grammar remains `A[0-9]{3,}` for appendix entries and `C[0-9]{3,}` for root-code entries with COPY, CURATE, and the three fixed GENERATE targets. Section 7 has exact external-material and mandatory-result declarations; section 9 is cleared with `无`, `None`, or `N/A`.

`check-appendix-result` checks declared files, COPY hashes, path/directory rules, source integrity, common dependency references, Python syntax, basic XLSX structure, sensitive information, and visible certification-boundary conflicts without importing or executing user code. It does not judge originality, external similarity, complete solve coverage, plotting responsibility, mathematical correctness, or CURATE semantic equivalence.

## Compatibility and non-goals

The Lite v3 marker, eight public commands, all START/RESULT/HANDOFF/APPENDIX headings, START/RESULT single/split identities, dependency grammar, evidence rules, figure workspace, and appendix rules remain unchanged from 0.8.0. Existing workspaces need not create `figure/`; an existing user-created root is known and ignored internally. Existing split `HANDOFF_QN_K.md` files remain ordinary legacy notes without automatic migration; create the one current `HANDOFF_QN.md` at the next needed technical transfer. Historical plotting code is not moved automatically. Existing legacy content directories remain ignored.

Lite 0.8.1 does not validate mathematics, plan or EDA quality, causality, or HANDOFF semantics; infer PRE use or contract granularity; execute cleaning, solvers, compilers, or user code; discover prose dependencies; reconcile contradictions automatically; manage approvals/state; migrate old HANDOFF files or other products; generate or check contest manuscripts; infer or automatically select final graphics; silently retrain for graphics; orchestrate agents; add problems dynamically; emit content JSON; build/delete appendix trees; classify plotting code; judge originality; prove result equivalence; or fully interpret dynamic imports, CMake, and spreadsheet semantics. It adds no SUPPLEMENT or followups protocol.
