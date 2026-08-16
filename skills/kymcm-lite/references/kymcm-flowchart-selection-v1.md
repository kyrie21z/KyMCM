# KyMCM Lite flowchart selection specification

Identifier: `kymcm-flowchart-selection-v1`

## Authority and scope

This is KyMCM Lite's evidence-derived authority for **WHAT / WHEN** flowchart decisions. Its byte-identical repository mirror is `docs/lite-v3/kymcm-flowchart-selection-v1.md`. It decides whether a flowchart is appropriate, selects Macro or Algorithm, and then selects one primary M1–M6 or A1–A6 semantic type. It does not decide content capacity or final spatial layout.

The fixed evidence base contains 73 strict CUMCM main-evidence flowcharts: Macro 40 and Algorithm 33.

| Track | Type | Chinese name | Samples |
|---|---|---|---:|
| Macro | M1 | 线性/阶段链 | 7 |
| Macro | M2 | 多源/多支路汇聚 | 11 |
| Macro | M3 | 分层分支-汇合 | 6 |
| Macro | M4 | 阶段分组模块化 | 8 |
| Macro | M5 | 双通道/对称 | 4 |
| Macro | M6 | 反馈/循环系统 | 4 |
| Algorithm | A1 | 线性顺序 | 6 |
| Algorithm | A2 | 单循环迭代 | 10 |
| Algorithm | A3 | 嵌套循环/多判定迭代 | 9 |
| Algorithm | A4 | 分支/搜索 | 4 |
| Algorithm | A5 | 并行子算法 | 1 |
| Algorithm | A6 | 密集判定/调度网络 | 3 |

A5 and A6 are low-evidence conditional types. Use them only when their real semantics are present; their sparse observations are not preferred targets.

## Flowchart qualification gate

Use this flowchart system only when arrows or links primarily express a directed process, execution, state progression, branching or iteration, or a clear input–process–output flow. Keep static indicator hierarchies, conceptual taxonomies, causal diagrams, component structures, and generic relationship networks outside this taxonomy.

If a flowchart is appropriate, make the first split:

- **Macro** answers how stages, modules, information, or processes are organized at a high level.
- **Algorithm** answers how an executable algorithm proceeds through steps, decisions, updates, iterations, searches, and termination.

## Macro types

- **M1 — 线性/阶段链:** one main path; stage order is the primary information.
- **M2 — 多源/多支路汇聚:** same-level parallel sources or branches converge. Prefer M2 for one-layer fan-in.
- **M3 — 分层分支-汇合:** branches contain meaningful multiple levels or subflows before convergence.
- **M4 — 阶段分组模块化:** true stage boundaries themselves carry explanatory value.
- **M5 — 双通道/对称:** two same-level corresponding or symmetric paths, not merely two arbitrary branches.
- **M6 — 反馈/循环系统:** system- or module-level feedback is a core semantic relation. Do not confuse it with algorithm iteration.

## Algorithm types

- **A1 — 线性顺序:** no core decision or loop; one execution path.
- **A2 — 单循环迭代:** one main loop with one main continue/termination logic.
- **A3 — 嵌套循环/多判定迭代:** nested loops, multi-level termination or iteration controls, or multiple irreducible iteration states.
- **A4 — 分支/搜索:** path selection, search, or classification is primary rather than loop control.
- **A5 — 并行子算法:** true execution-level parallel subalgorithms; low-evidence conditional type.
- **A6 — 密集判定/调度网络:** dense rules, jumps, or interacting paths that A2/A3/A4 cannot faithfully express; last-resort low-evidence type.

## Minimum sufficient complexity principle

> Choose the lowest-complexity flowchart type that faithfully expresses the real process logic.

Real parallelism, convergence, hierarchy, stage grouping, symmetry, feedback, decision, loop, nested loop, or search/routing can justify an upgrade. Visual sophistication, page filling, or making a diagram look advanced cannot.

Select exactly one primary type; do not invent mixed type IDs. Resolve conflicts by the information goal and the structure that most changes reader understanding, not by mechanically counting diamonds or arrows. Upgrade or downgrade only when real structural semantics require it.

## Layout decoupling

Type selection does not bind left-to-right or top-to-bottom orientation, fixed coordinates, grids, or final geometry. A2, A3, and the other Algorithm types do not bind a serpentine layout. The 73-sample evidence contains only two obvious serpentine samples, both Macro/M1 rather than Algorithm, so it does not support default algorithm serpentine.

This specification does not select Graphviz, Mermaid, TikZ, SVG, PowerPoint, or any renderer. Final layout, geometry, routing, and visual drawing are outside this authority and are manually judged and drawn by the user/human author.

## Semantic planning output

An agent may return a Markdown planning record such as:

```text
flowchart_needed
track
type
information_goal
primary_structure
selection_reason
upgrade_triggers
rejected_alternatives
layout_status: human-owned / pending-human
```

This is a semantic handoff, not runtime state or a JSON contract. After type selection, read `kymcm-flowchart-content-v1.md` to determine how much information the flowchart should contain.
