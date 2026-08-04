# KyMCM Lite 0.9.2 machine-enforced contract

Status: normative runtime contract for the Lite v3 Skill. This document describes
observable behavior implemented by the Python standard-library runtime and frozen
by the Lite tests. It complements `docs/lite-v3/diagnostics.md`: that catalog is
the exact diagnostic directory, while this document explains the complete
layout, discovery, safety, and read-only behavior. Agent and human semantic
review remains authoritative for mathematical meaning.

## 1. Scope and authority

The runtime contract is below the Python runtime and its frozen tests in the
authority order used by the complete ChatGPT Source export. If this prose and
the runtime disagree, the runtime result and the named diagnostic are the
observable contract; the documentation must then be repaired. The runtime is
not a solver, model selector, manuscript writer, approval state machine, or
hidden project database.

Lite version `0.9.2` is a product release identifier. It is independent of the
workspace protocol marker, which remains Lite v3. Existing valid 0.9.0 and
0.9.1 workspaces need no migration because this release changes semantic
Supplement guidance and documentation, not a workspace file or checker.

## 2. Identity, marker, and fail-closed behavior

Every command except an initialization conflict check requires a Lite v3
workspace marker at `.kymcm/mode.json`. Its exact bytes are:

```text
{"workflow":"kymcm_lite","version":3}\n
```

The JSON value and the bytes must both match. Missing, invalid UTF-8, malformed,
Full, historical Lite v2, unknown, or whitespace-altered content emits
`LITE-MODE-001` and is rejected. A symlink marker emits
`LITE-LAYOUT-SYMLINK-001`. The marker is not the same thing as `VERSION`, and
the product version is never written into the workspace marker.

Lite creates no content JSON, state file, event log, approval record, review
hash, dependency manifest, or generated success report. The only persistent JSON
written by `init` is the exact marker above.

## 3. Workspace roots and path safety

The four managed roots are `.kymcm/`, `input/`, `reports/`, and `problems/`.
Each official `problems/qN/` has exactly the required managed directories
`spec/`, `code/`, `data/`, `data/derived/`, `outputs/`, `notes/`, and `result/`.
Question directories are immediate `q[1-9][0-9]*` children of `problems/` and
must be contiguous from `q1`; missing q numbers emit `LITE-LAYOUT-001`.

The optional fixed unit `problems/preprocess/` uses the same directory set. It
is one shared unit, never Q0, never split, and has these exact contracts:

```text
problems/preprocess/spec/START_PRE.md
problems/preprocess/result/RESULT_PRE.md
problems/preprocess/notes/HANDOFF_PRE.md       (optional semantic handoff)
```

`figure/` is a known optional root for explicitly requested final figures. It is
not managed, required, initialized, checked, traversed, an evidence scope, a
dependency, or an appendix source. A legacy `FROZEN_CONTEXT.md` or `paper/`
directory is completely ignored: Lite does not open, decode, hash, migrate,
warn about, or delete its contents, even when they are invalid UTF-8 or
symlinked. `appendix/` and root `code/` are known to `doctor` as submission
outputs, but are not modeling managed roots. Other root entries remain allowed
and appear in `doctor`'s informational unknown-root line.

The workspace itself, every traversed managed component, every contract, and
every evidence component must be an ordinary non-symlink path. A symlink at a
parent component is unsafe even when its final target is a regular file. Path
checks reject absolute POSIX and Windows paths, drive letters, leading slashes,
control characters, and any `..` component. Runtime checks never follow a
symlink in order to accept content.

## 4. Initialization and rollback

`init --workspace PATH --questions N` creates the four managed roots, the exact
question directory tree, and `.kymcm/mode.json`. `--preprocess` additionally
creates the fixed PRE tree. It creates no START, RESULT, PRE, Supplement,
HANDOFF, APPENDIX, figure, evidence, output, state, or manifest file. The
initializer refuses a symlink/non-directory target and refuses when any managed
root already exists, returning `1` with `LITE-LAYOUT-001`.

Initialization is transactional. If directory or marker creation fails, paths
created by this invocation are removed in reverse order; unrelated existing
files and an existing parent directory are preserved. The exception is reported
as `LITE-TOOL-001` with exit code `2`. A pre-existing unrelated file such as a
legacy `FROZEN_CONTEXT.md` is never removed.

## 5. PRE contract

PRE is completely optional. If the PRE root is absent, ordinary QN work remains
valid and no PRE diagnostic is required. If the root exists, all seven required
directories must be ordinary directories; split, misplaced, malformed, or
symlinked `START_PRE`, `RESULT_PRE`, or `HANDOFF_PRE` contract-like entries are
errors. `check-preprocess-start` requires the complete PRE layout and
`START_PRE.md`; `check-preprocess-result` additionally requires
`RESULT_PRE.md`. `HANDOFF_PRE.md` has no Python checker and is a derived,
semantic-only technical transfer.

The PRE START title is exactly `# START PRE` and its headings, in order, are:

```text
## 1. 预处理目标与下游交付
## 2. 原始数据、口径与数据字典
## 3. 数据质量审计与处理规则
## 4. 探索性分析计划与表述边界
## 5. Codex 执行边界
## 6. 输出与证据清单
## 7. 验证、计算预算与停止规则
## 8. 未决问题
```

The PRE RESULT title is exactly `# RESULT PRE` and its headings, in order, are:

```text
## 1. 预处理结论
## 2. 实际执行方案与 START_PRE 偏差
## 3. 数据质量与样本变化
## 4. 探索性分析结果
## 5. 冻结数据产品与数据字典
## 6. 验证与审计
## 7. 证据索引
## 8. 局限性与下游使用边界
```

The PRE START checker warns when one of sections 1–7 has no visible author
content; it does not synthesize that content. The unresolved section must
reduce to `无`, `None`, or `N/A`. RESULT_PRE section 2 must state `无偏差` or an
authorized deviation with a safe evidence path. RESULT_PRE emits its validation
warning when section 6 lacks meaningful audit detail, while other semantic
content remains outside Python enforcement. PRE evidence is limited to
`problems/preprocess/{code,data/derived,outputs,notes}` and uses the same
ordinary-file, traversal, and symlink rules as QN evidence.

A QN START may contain exactly one visible
`**预处理依赖：** 无` or `**预处理依赖：** PRE` declaration before its
`**前问依赖：**` line. `PRE` requires both exact PRE contracts and their
headings; `无` does not. A legacy QN START without a declaration remains valid
when PRE is absent, and receives `LITE-START-PREPROCESS-WARN-001` when PRE
exists. A PRE declaration after the question dependency or a duplicate,
malformed, or incomplete declaration is blocking. RESULT older than RESULT_PRE
produces only the advisory `LITE-PREPROCESS-STALE-WARN-001`.

## 6. QN contract discovery and modes

For question `N`, single contracts are exactly:

```text
problems/qN/spec/START_QN.md
problems/qN/result/RESULT_QN.md
```

Split contracts are directly in the same directories and use positive decimal
suffixes without leading zero:

```text
START_QN_1.md ... START_QN_K.md
RESULT_QN_1.md ... RESULT_QN_K.md
```

The regular expressions are `^START_Q([1-9][0-9]*)(?:_([1-9][0-9]*))?\.md$`
and the corresponding `RESULT` form. Contract-like names beginning with
`START_Q` or `RESULT_Q` that do not match, are misplaced, symlinked, or not
ordinary files emit `LITE-CONTRACT-LAYOUT-001`.

One question is either single, split, or empty. Single and split START files
cannot coexist. Split START suffixes must be exactly `1..K`; a gap is blocking.
Every discovered RESULT must match an active START identity and mode. Partial
split RESULT completion is legal while work continues; an orphan or
unsuffixed RESULT in split mode is not.

`check-start` and `check-result` select the unsuffixed unit in single mode. In
split mode they require `--subproblem K`, and K must be one of the active START
units. Omission, an unavailable unit, or an invalid layout emits
`LITE-CONTRACT-SELECT-001`. `check-result` checks the selected START first, so a
base contract error remains visible even when the RESULT is present.

## 7. QN START and RESULT structure

The exact QN START title is `# START QN` or `# START QN_K`, matching the selected
identity. Its eight headings, in order, are:

```text
## 1. 问题目标与直接交付
## 2. 已冻结输入与前问继承
## 3. 数据口径与预处理
## 4. 数学模型、参数与判定规则
## 5. Codex 执行边界
## 6. 输出与证据清单
## 7. 验证、求解预算与停止规则
## 8. 未决问题
```

The exact QN RESULT title is `# RESULT QN` or `# RESULT QN_K`. Its seven
headings, in order, are:

```text
## 1. 直接答案
## 2. 实际执行方案与 START 偏差
## 3. 关键结果
## 4. 验证与审计
## 5. 证据索引
## 6. 局限性与风险
## 7. 下游冻结输出
```

Heading validation counts exactly one active occurrence of each heading and
rejects missing, duplicate, or reordered headings. Markdown inside fenced code
blocks and HTML comments is invisible for heading, declaration, unresolved,
meaningful-content, and evidence checks. A required START/PRE section without
visible author content produces a warning, not an error. START section 8 must
reduce to `无`, `None`, or `N/A`. RESULT section 2 must state `无偏差`, or state
an authorized deviation and include at least one safe relative evidence path.
RESULT section 4 and section 7 may produce non-blocking validation/downstream
warnings when they lack meaningful content.

## 8. Dependencies

QN section 2 contains exactly one visible dependency declaration with the exact
prefix `**前问依赖：** ` followed by `无` or a comma-plus-space ordered list.
Accepted token forms are `Q1`, `Q2`, `Q2_1`, and the parser's legacy-shaped
`Q0`/negative forms only long enough to reject them by scope. The final scope
rule is strict: tokens are unique, ascending, exact active units, refer only to
existing earlier questions, and Q1 must use `无`. A bare token identifies an
unsuffixed single unit; a suffixed token identifies one exact split unit and
never expands to all siblings. Same-question, forward, wildcard, duplicate,
unknown, unsorted, and mode-mismatched dependencies are errors.

For every declared upstream unit, the checker reads the exact upstream START
and RESULT paths and verifies title and frozen headings. Missing, unsafe,
invalid-UTF-8, or structurally invalid upstream contracts emit
`LITE-START-DEPENDENCY-CONTRACT-001`. This is a lightweight structural check;
symbol/unit/meaning contradictions remain a Codex or human semantic review and
produce no consistency artifact.

Supplement files do not add dependency tokens. Python never applies Supplement
semantic scope or HANDOFF state while parsing dependencies.

## 9. Evidence safety and scope

QN RESULT evidence uses one bullet per item:

```text
- E1 — `relative/path` — description
```

The line must match the frozen bullet grammar, contain exactly one backticked
path, and use a unique `E<number>` identifier. The path must be relative,
non-empty, traversal-free, free of control characters and Windows drive/UNC
prefixes, and resolve under the selected question's `code/`, `data/derived/`,
`outputs/`, or `notes/` directory. It must be an existing ordinary file and no
path component may be a symlink. Missing, unsafe, out-of-question, symlinked,
or malformed evidence is blocking. The checker never executes, imports,
compiles, or otherwise interprets an evidence file.

PRE evidence uses the same grammar and restrictions under the PRE unit's four
evidence directories. Appendix evidence is a separate contract described below
and may point only to its declared evidence/output roots.

## 10. Git and read-only semantics

Git diagnostics are advisory. If Git is unavailable or the workspace is not
inside a Git repository, `doctor`, `check-start`, and `check-result` emit
`LITE-GIT-WARN-001` without invalidating the contract. `check-result` also
reports `LITE-GIT-DIRTY-WARN-001` when the current question's `code/` or
`data/derived/` is dirty; PRE RESULT applies the analogous PRE scope. RESULT
older than START emits `LITE-STALE-WARN-001`, an mtime heuristic only.

Doctor and all seven read-only checks never clean, rewrite, delete, initialize,
compile, solve, run user code, contact a network, or alter Git state. They read
only the selected contracts and the paths required for diagnosis. They do not
open legacy `paper/` or `FROZEN_CONTEXT.md`, optional `figure/`, or unrelated
user files. The exporter described elsewhere is a repository maintenance tool,
not a Lite command.

## 11. Supplement, HANDOFF, and figure boundaries

After the complete base RESULT set passes, an official question may have at most
one problem-level pair:

```text
problems/qN/spec/SUPPLEMENT_START_QN.md
problems/qN/result/SUPPLEMENT_RESULT_QN.md
```

The base discoverer ignores these names. `init` creates neither. There is no
suffixed Supplement, Sx directory, `followups/`, PRE Supplement, Supplement
checker, command, state, JSON, manifest, approval, hash ledger, or dependency
token. S1/S2/... continuity, plan-before-execution, exact work type, impact
scope, effective state, editable/adopted boundary, Start/Result invalidation,
artifact overwrite permission, downstream impact, and HANDOFF currency are
semantic review obligations, not Python-enforced facts. Only the latest
unadopted Sx may be edited in place; an adopted Sx, a non-latest Sx, or an Sx
with a later Sy is frozen. A material Start edit invalidates its old Result
until the revised execution writes a replacement. HANDOFF refresh alone does
not adopt an Sx; actual downstream use, formal delivery, later Sy baseline, or
explicit acceptance can do so.
Supplement Markdown is an internal appendix source and is rejected with
`LITE-APPENDIX-SOURCE-PATH-001`; current effective code/data/output assets may
use the existing appendix mappings.

There is one neutral problem-level `HANDOFF_QN.md` per official question. The
checker does not require it for `check-result`, does not validate it, and does
not treat it as a dependency. Split mode waits for every contiguous checked
RESULT before a semantic reviewer assembles it. Existing suffixed legacy
handoffs are retained as ordinary notes. HANDOFF, like START/RESULT/SUPPLEMENT,
is rejected as an appendix source.

`figure/` remains optional and known only. It is created solely for an explicit
final-figure request, is not read by any checker, is not formal evidence or an
appendix source, and cannot change formal state or silently rerun a model.

## 12. Appendix runtime contract

Appendix commands operate only when explicitly invoked. The contracts are:

```text
reports/appendix/APPENDIX_START.md
reports/appendix/APPENDIX_RESULT.md
reports/appendix/evidence/source_integrity.csv
```

`APPENDIX_START` is titled `# APPENDIX START` and has these nine headings, in
order:

```text
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

`APPENDIX_RESULT` is titled `# APPENDIX RESULT` and has these ten headings:

```text
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

The unresolved sentinel is exact `无`, `None`, or `N/A`. Section 7 declarations
are exactly `外部资料：无` or `外部资料：`appendix/input`` and
`强制结果文件：无` or `强制结果文件：`appendix/Result.xlsx``. External
materials must state visible source, purpose, and necessity; whitelist targets
must agree with both declarations.

Whitelist bullets use an identifier beginning `A` for appendix targets or `C`
for root code, `COPY`/`CURATE` with safe backticked sources and target, or
`GENERATE` only for the three exact environment files:
`appendix/environment/README.md`, `requirements.txt`, and `system_info.txt`.
COPY has exactly one source; CURATE has at least one. Targets are limited to
`appendix/problems/qN/{code,result}/`, `appendix/problems/preprocess/{code,result}/`,
`appendix/input/`, `appendix/Result.xlsx`, the environment paths, and direct
files under root `code/`. IDs and targets are globally unique.

Sources must be relative ordinary files under `problems/` or `input/`, without
symlink components, and must satisfy the source-to-target mapping. Sources under
`reports/`, `appendix/`, root `code/`, `.kymcm/`, `.git/`, `paper/`, or
`figure/` are rejected. START, RESULT, PRE, Supplement, and matching HANDOFF
Markdown contracts are contextual internal documents and cannot be copied.
Original `problems/` and `input/` remain read-only.

`appendix/` and root `code/` must contain exactly the declared ordinary files;
extra files, missing targets, symlinks, empty/undeclared directories, and
misplaced question directories are errors. Root `code/` permits direct files
only. COPY target bytes must equal the source SHA-256. Every declared source is
listed in `source_integrity.csv` with the exact header
`path,before_sha256,after_sha256,status`, equal lowercase SHA-256 values, and
status `unchanged`.

Static checks reject hidden/cache/build/archive/test/tmp directories, logs,
bytecode, binaries, runtime checkpoint data, temporary/backup/final-like names,
executables, root-code README/data files, duplicate byte-identical formal
results, and sensitive paths/credentials/private keys/machine identity. They do
not reject operational names such as scheduler, checkpoint, status, monitor,
ledger, or audit by name alone. Python sources are parsed with `ast`; obvious
local modules must be present and dynamic imports/execution are advisory
warnings. C/C++ local includes and literal CMake sources must be present;
macro/generated closure is an advisory warning. Declared XLSX is checked as a
ZIP/XML workbook with at least one sheet. No submitted code, solver, compiler,
build command, or user program is executed by the checker.

Appendix result must account for every whitelist ID, reject unknown IDs, state no
deviation or an authorized deviation with safe evidence, index at least one
evidence bullet and `reports/appendix/evidence/source_integrity.csv`, and retain
the exact source/output tree. Certification wording is warned when visible
finite/partial limitations conflict with an unqualified global claim.

## 13. CLI and exit codes

The public Lite CLI has exactly eight commands and no aliases or exporter
subcommand:

```text
init
doctor
check-preprocess-start
check-preprocess-result
check-start
check-result
check-appendix-start
check-appendix-result
```

Only `check-start` and `check-result` accept optional positive `--subproblem`.
Every command accepts the required workspace argument; `init` additionally
requires positive `--questions` and may take `--preprocess`.

The process exit contract is:

```text
0 = structure/evidence is valid; warnings are allowed
1 = a contract, layout, selection, or evidence rule is invalid
2 = an unexpected tool, I/O, encoding, subprocess, or environment failure
```

`LITE-TOOL-001` is the tool-failure diagnostic. Normal diagnostics render a
workspace-relative location and a final `SUMMARY errors=N warnings=M`. Tool
errors are rendered on stderr without a traceback. The exporter has its own
maintenance-tool exit contract and is deliberately not part of these eight.

The stable diagnostic families include marker/layout and symlink errors;
contract discovery/selection, START/RESULT heading/dependency/evidence rules;
PRE layout/contract/staleness rules; advisory Git and mtime rules; and appendix
declaration, whitelist, source, output, integrity, dependency, XLSX, sensitive,
duplicate, and certification rules. The complete identifier/severity/trigger
table is `docs/lite-v3/diagnostics.md` and is included in the full Source export.

## 14. Semantic and mathematical limitations

Runtime checks do not prove mathematical correctness, identifiability,
causality, feasibility, boundedness, numerical meaning, plan quality, smoke-test
adequacy, L0/L1/L2 proportionality, recoverability, nested-cost realism,
cleaning or EDA quality, or the correctness of a final conclusion. They do not
decide whether PRE is semantically appropriate or whether an upstream symbol,
unit, sample, transform, limitation, or certification claim is contradictory.

They do not enforce Supplement numbering/timing/impact/effective-state
semantics, whether an Sx is editable or adopted, adoption triggers,
Start/Result invalidation, artifact overwrite permission, completed-entry
immutability, downstream impact, HANDOFF identity or currency, final-figure selection, plotting responsibility, code originality,
semantic CURATE equivalence, complete formal-source coverage, or external
similarity. They do not validate every dynamic import, CMake interpretation,
Excel formula/cache/format/numerical agreement, solver behavior, or submitted
program execution. These boundaries require Codex semantic review and final
human review. A warning is not a mathematical certification.

## 15. Non-goals and external full specification

The complete ChatGPT Project Source exporter is repository maintenance only. It
does not enter a contest workspace, evidence tree, appendix, or managed root; it
is not initialized by `init`; it adds no state, JSON, manifest, dependency, or
command; and it must not be copied into user workspaces. Rebuild the generated
full specification after normative source changes and verify it with the
exporter's `--check` mode. The generated document is a deterministic repository
mirror, not a new runtime contract.
