# `kymcm-flowchart-content-v1`

> **KyMCM Lite 流程图内容容量与节点文本规范 v1**
> 上游：`kymcm-flowchart-selection-v1`
> 证据基线：固定 73 幅 strict CUMCM 流程图 / 747 个普通流程节点 / 726 个可测文本节点。
> 职责：回答 **HOW MUCH INFORMATION**——类型选定后，一张流程图应承载多少节点、节点写多少文字、何时应压缩、拆阶段、抽 subprocess 或返回 selection 复核。
> 规范源：`skills/kymcm-lite/references/kymcm-flowchart-content-v1.md`；其仓库镜像 `docs/lite-v3/kymcm-flowchart-content-v1.md` 必须保持字节一致。
> 本规范通过后不进入自动 KyMCM 布局阶段；最终空间布局、几何、走线与绘制由用户/人类作者负责（**human-owned**）。

---

# 0. 职责边界

职责链保持单一边界：

```text
selection-v1 → WHAT / WHEN
content-v1   → HOW MUCH INFORMATION
human/user   → final layout / geometry / routing / drawing
```

因此 `content-v1`：

- 不重新选择 M1–M6 / A1–A6；
- 可以要求“返回 selection 复核”，但不得静默改类型；
- 不规定 TB/LR、坐标、lane、edge routing；
- 不规定字体、颜色、边框、箭头；
- 不允许以缩小字号或压缩几何间距来掩盖内容过载；
- 不创建或调用 flowchart `layout-v1`、`style-v1`、`exec-v1`、渲染器或自动布局工具路线。

---

# 1. Evidence Base

- 固定样本：73 幅，不扩大语料；
- Macro：40 幅；Algorithm：33 幅；
- 普通节点：747；
- Container title：18，独立统计，不计入普通节点数；
- 可测文本节点：726；
- 21 个节点因无标签或无法可靠辨认，不进入字数分布；
- Figure-level 置信度：high 58 / medium 13 / low 2。

节点恒等式：

```text
node_count_total
= process + decision + terminal + io + subprocess + other_node
```

---

# 2. 规范语言

## 2.1 Typical Range

定义为固定样本的 **Q1–Q3**，即中间 50% 经验区间。Typical 是默认参考，不是硬允许区间。

## 2.2 Review Trigger

当 `node_count > type_Q3` 或节点文本超过相应 role 的 Q3 时触发 review。超过 Q3 的含义是“高于该类型常见区间上界”，不是“错误”。

## 2.3 Long-tail Node

当 role 证据足够且单节点文字 `L > type_role_P90` 时，标记 `long-tail-node`，优先检查：压缩短语、移正文、拆真实步骤、抽 subprocess。

## 2.4 Strong Overload Candidate

仅当**结构容量与文本容量同时偏高**时进入 strong overload：

```text
node_count > type_Q3
AND
(
  median_process_text > type_process_Q3
  OR
  median_decision_text > applicable_decision_Q3
)
```

反复出现 ≥3 行普通节点是附加增强信号，但本 v1 不把其设为硬失败条件。

---

# 3. Evidence Strength

本规范内部使用：

```text
High   : 同类型 >= 6 幅图
Medium : 同类型 4–5 幅图
Low    : 同类型 <= 3 幅图
```

角色级文字规范还要求可测节点来自多个样本。因此：

- A2/A3 Decision 可形成类型特异 recommendation；
- A4 Decision 作为 Medium preference；
- Macro Decision 证据总体不足，不冻结统一 Macro decision 阈值；
- A5/A6 类型数值仅作描述，不进入稳定自动阈值。

---

# 4. 核心原则

## 4.1 最低充分信息

流程图只保留理解过程结构所必需的信息。若一句解释删除后不改变流程顺序、分支、迭代、阶段、输入输出语义，则优先留在正文。

## 4.2 复杂度预算交换

固定样本支持：

**节点越多，单节点文字通常越短；节点越少，单节点可以稍长。**

典型对照：

- M3 分层分支-汇合：节点数 Q1–Q3 = 10.2–14.2；Process Q1–Q3 = 3–6 字。
- M4 阶段分组模块化：节点数 Q1–Q3 = 12–19；Process Q1–Q3 = 2–6 字。
- A1 线性顺序：节点数 Q1–Q3 = 5–6.8；Process Q1–Q3 = 10.8–18.2 字。

因此禁止：节点很多 → 继续写完整句 → 再缩小字号硬塞。

正确顺序：

```text
删冗余解释
→ 改为短语
→ 移正文
→ 抽 subprocess / Stage
→ 必要时拆图或返回 selection 复核
→ 最后才交给用户/人类作者做最终布局
```

## 4.3 一个节点一个主要语义单元

推荐：`计算适应度`、`更新粒子位置`、`是否满足收敛条件？`。

不推荐把多个具有真实先后关系的动作压进一个长句节点。

---

# 5. 字数与行数口径

## 5.1 `char_count_raw`

本规范主指标：汉字、英文字母、数字、可见标点、数学符号各按 1；空格与换行不计。本文所称“字数”均指该指标。

## 5.2 `char_count_cjk_equiv`

仅作为用户/人类作者进行最终布局时的近似宽度信号，不用于本规范主要语义阈值。

## 5.3 行数

726 个可测普通节点中：1 行 68.0%，2 行 19.6%，≥3 行 12.4%；median = 1 行，Q3 = 2 行，P90 = 3 行。

因此冻结：**普通节点优先 1–2 行。** ≥3 行不是自动错误，但反复出现时进入 `multiline-density-review`。

---

# 6. 跨类型节点角色规范

## 6.1 Process

Macro pooled process（n=312）：Q1/median/Q3/P90 = 3/5/9/16 字。

常规 Algorithm A2–A4 process（n=131）：Q1/median/Q3/P90 = 5/8/12/23 字。

因此 A2–A4 的跨类型 fallback 是 **约 5–12 字，中心约 8 字**。若类型自身有 High/Medium 证据，优先类型特异 profile。

## 6.2 Decision

A2–A4 decision（n=50）：Q1/median/Q3/P90 = 6/8/10/13 字。

因此常规算法 Decision fallback：**约 6–10 字；超过 P90≈13 字进入强压缩复核。**

Decision 应写短条件，不写完整推理说明。Macro decision 证据不足，不直接套用为 Macro 的统计结论。

## 6.3 Terminal

Terminal（n=39）：Q1/median/Q3 = 2/2/2 字，主要来自“开始/结束”。

因此 Terminal 应保持极短；若终点承担大量输出说明，应检查它是否其实属于 `io` 或 `process`。

## 6.4 Container Title

Container title（n=18）：Q1/median/Q3/P90/max = 6/6.5/8/8/12 字。

Evidence-derived typical band：**约 6–8 字**。

---

# 7. 类型统计总表

| 类型 | n图 | 证据 | 节点数 Q1–Q3 | Process Q1–Q3 | Decision Q1–Q3 | ≥3行 |
|---|---:|---|---|---|---|---:|
| M1 线性/阶段链 | 7 | High | 5–7.5 | 4–8 (n=37) | 6–6 (n=1) | 2.1% |
| M2 多源/多支路汇聚 | 11 | High | 6–8 | 5–11.8 (n=62) | —–— (n=0) | 23.5% |
| M3 分层分支-汇合 | 6 | High | 10.2–14.2 | 3–6 (n=55) | 6–6 (n=1) | 0.0% |
| M4 阶段分组模块化 | 8 | High | 12–19 | 2–6 (n=100) | 14–22.2 (n=4) | 4.8% |
| M5 双通道/对称 | 4 | Medium | 9.5–11 | 4–11 (n=29) | —–— (n=0) | 0.0% |
| M6 反馈/循环系统 | 4 | Medium | 5.2–10 | 4–16 (n=29) | —–— (n=0) | 6.5% |
| A1 线性顺序 | 6 | High | 5–6.8 | 10.8–18.2 (n=28) | —–— (n=0) | 2.7% |
| A2 单循环迭代 | 10 | High | 7–9 | 5–12 (n=52) | 7–10.5 (n=15) | 10.1% |
| A3 嵌套循环/多判定迭代 | 9 | High | 11–13 | 3–13.5 (n=56) | 7–10 (n=26) | 5.5% |
| A4 分支/搜索 | 4 | Medium | 8.5–11.8 | 7.5–11 (n=23) | 4–8 (n=9) | 2.3% |
| A5 并行子算法 | 1 | Low | 19–19 | 7–11.5 (n=11) | 6.2–11 (n=6) | 0.0% |
| A6 密集判定/调度网络 | 3 | Low | 18.5–22 | 17–31 (n=37) | 11–20 (n=21) | 75.4% |

说明：A5/A6 的分位数只描述固定样本，不自动转为规范阈值。

---

# 8. Type-Specific Profiles

## M1 线性/阶段链

**图级证据：7 幅；Evidence=High。**

- Node count：Q1=5，median=6，Q3=7.5，P90=10.4，observed max=14。
- 可读 typical band：**约 5–8 个普通节点**。
- Node-count review trigger：**N > 8**；A5/A6 仅描述，不用于稳定自动阈值。
- Process：n=37，覆盖 6 幅；Q1/median/Q3/P90 = 4/6/8/16.4 字。
- Process typical：**约 4–8 字**；>Q3≈8 记 `long-node`；>P90≈16.4 记 `long-tail-node`。
- Decision：可测 n=1，覆盖 1 幅；证据不足以建立稳定类型特异阈值。
- 行数分布：1 行 66.7% / 2 行 31.2% / ≥3 行 2.1%。

**重构规则：**
- 若节点数超过 typical 上界但流程仍完全线性，先压缩文本或交给用户/人类作者处理长链布局；不要为了少节点伪造阶段。
- 若增长来自真实阶段边界，返回 selection 复核 M4；来自并行汇聚，复核 M2/M3。

## M2 多源/多支路汇聚

**图级证据：11 幅；Evidence=High。**

- Node count：Q1=6，median=7，Q3=8，P90=10，observed max=10。
- 可读 typical band：**约 6–8 个普通节点**。
- Node-count review trigger：**N > 8**；A5/A6 仅描述，不用于稳定自动阈值。
- Process：n=62，覆盖 11 幅；Q1/median/Q3/P90 = 5/8/11.8/19 字。
- Process typical：**约 5–12 字**；>Q3≈11.8 记 `long-node`；>P90≈19 记 `long-tail-node`。
- Decision：无足够类型特异证据。
- 行数分布：1 行 56.8% / 2 行 19.8% / ≥3 行 23.5%。

**重构规则：**
- 节点偏高但文字短时，优先由 fan-in / merge 结构承载。
- 若每个支路内部继续多层展开，返回 selection 复核 M3；若节点与文字同时偏高，拆支路内部说明。

## M3 分层分支-汇合

**图级证据：6 幅；Evidence=High。**

- Node count：Q1=10.2，median=11.5，Q3=14.2，P90=16.5，observed max=18。
- 可读 typical band：**约 10–14 个普通节点**。
- Node-count review trigger：**N > 15**；A5/A6 仅描述，不用于稳定自动阈值。
- Process：n=55，覆盖 6 幅；Q1/median/Q3/P90 = 3/4/6/8 字。
- Process typical：**约 3–6 字**；>Q3≈6 记 `long-node`；>P90≈8 记 `long-tail-node`。
- Decision：可测 n=1，覆盖 1 幅；证据不足以建立稳定类型特异阈值。
- 行数分布：1 行 73.6% / 2 行 26.4% / ≥3 行 0.0%。

**重构规则：**
- 该类型的稳定组合是“较多节点 + 极短 process”；复杂性主要由层级承载。
- 若节点与文字同时超过 typical 上界，优先拆子层级、移正文或抽 subprocess。

## M4 阶段分组模块化

**图级证据：8 幅；Evidence=High。**

- Node count：Q1=12，median=14，Q3=19，P90=22.3，observed max=30。
- 可读 typical band：**约 12–19 个普通节点**。
- Node-count review trigger：**N > 19**；A5/A6 仅描述，不用于稳定自动阈值。
- Process：n=100，覆盖 8 幅；Q1/median/Q3/P90 = 2/3/6/15 字。
- Process typical：**约 2–6 字**；>Q3≈6 记 `long-node`；>P90≈15 记 `long-tail-node`。
- Decision：可测 n=4，覆盖 4 幅；证据不足以建立稳定类型特异阈值。
- 行数分布：1 行 89.7% / 2 行 5.6% / ≥3 行 4.8%。
- Container title pooled typical：**约 6–8 字**。

**重构规则：**
- M4 是高节点容量类型，节点多本身不是错误，前提是真实 Stage 吸收复杂度。
- 若某 Stage 内部持续出现长节点，应拆该 Stage 的局部过程，而不是继续增加外层 Stage。
- 不存在真实阶段边界时，不得为排版虚构 Stage。

## M5 双通道/对称

**图级证据：4 幅；Evidence=Medium。**

- Node count：Q1=9.5，median=10.5，Q3=11，P90=11，observed max=11。
- 可读 typical band：**约 10–11 个普通节点**。
- Node-count review trigger：**N > 11**；A5/A6 仅描述，不用于稳定自动阈值。
- Process：n=29，覆盖 4 幅；Q1/median/Q3/P90 = 4/6/11/14.2 字。
- Process typical：**约 4–11 字**；>Q3≈11 记 `long-node`；>P90≈14.2 记 `long-tail-node`。
- Decision：无足够类型特异证据。
- 行数分布：1 行 75.0% / 2 行 25.0% / ≥3 行 0.0%。

**重构规则：**
- 两条 lane 应保持相近语义粒度；若只是普通多支路而无对应语义，返回 selection 复核 M2。
- 若单个 lane 自身变成复杂算法，优先拆为独立子图。

## M6 反馈/循环系统

**图级证据：4 幅；Evidence=Medium。**

- Node count：Q1=5.2，median=7.5，Q3=10，P90=11.8，observed max=13。
- 可读 typical band：**约 5–10 个普通节点**。
- Node-count review trigger：**N > 10**；A5/A6 仅描述，不用于稳定自动阈值。
- Process：n=29，覆盖 4 幅；Q1/median/Q3/P90 = 4/6/16/24.4 字。
- Process typical：**约 4–16 字**；>Q3≈16 记 `long-node`；>P90≈24.4 记 `long-tail-node`。
- Decision：无足够类型特异证据。
- 行数分布：1 行 90.3% / 2 行 3.2% / ≥3 行 6.5%。

**重构规则：**
- 图级证据仅 4 幅且 process 分布很宽，不把较长 process 当推荐常态。
- 若反馈环包围大量正文式节点，优先抽局部 subprocess；若核心其实是迭代控制，返回 selection 复核 A2/A3。

## A1 线性顺序

**图级证据：6 幅；Evidence=High。**

- Node count：Q1=5，median=5.5，Q3=6.8，P90=8，observed max=9。
- 可读 typical band：**约 5–7 个普通节点**。
- Node-count review trigger：**N > 7**；A5/A6 仅描述，不用于稳定自动阈值。
- Process：n=28，覆盖 6 幅；Q1/median/Q3/P90 = 10.8/12.5/18.2/21.9 字。
- Process typical：**约 11–18 字**；>Q3≈18.2 记 `long-node`；>P90≈21.9 记 `long-tail-node`。
- Decision：无足够类型特异证据。
- 行数分布：1 行 62.2% / 2 行 27.0% / ≥3 行 2.7%。

**重构规则：**
- A1 允许“少节点、稍长 process”，但仍不应写成正文段落。
- 若出现真实循环，复核 A2；出现分支主导，复核 A4；不要用无限延长 A1 表达控制流。

## A2 单循环迭代

**图级证据：10 幅；Evidence=High。**

- Node count：Q1=7，median=7.5，Q3=9，P90=10，observed max=10。
- 可读 typical band：**约 7–9 个普通节点**。
- Node-count review trigger：**N > 9**；A5/A6 仅描述，不用于稳定自动阈值。
- Process：n=52，覆盖 10 幅；Q1/median/Q3/P90 = 5/7/12/18.9 字。
- Process typical：**约 5–12 字**；>Q3≈12 记 `long-node`；>P90≈18.9 记 `long-tail-node`。
- Decision：n=15，覆盖 10 幅；typical **约 7–10 字**；P90≈12.2。
- 行数分布：1 行 70.9% / 2 行 19.0% / ≥3 行 10.1%。
- A2 Decision recommendation：约 7–10 字；>P90≈12 字进入强压缩复核。

**重构规则：**
- A2 典型节点预算稳定；明显超过 typical 上界时检查是否隐藏了第二层循环或把步骤切得过细。
- 真实内外层循环/多级终止控制 → 返回 selection 复核 A3；仅文字过长 → 保持 A2 并压缩文案。

## A3 嵌套循环/多判定迭代

**图级证据：9 幅；Evidence=High。**

- Node count：Q1=11，median=12，Q3=13，P90=15，observed max=15。
- 可读 typical band：**约 11–13 个普通节点**。
- Node-count review trigger：**N > 13**；A5/A6 仅描述，不用于稳定自动阈值。
- Process：n=56，覆盖 9 幅；Q1/median/Q3/P90 = 3/8.5/13.5/24.5 字。
- Process typical：**约 3–14 字**；>Q3≈13.5 记 `long-node`；>P90≈24.5 记 `long-tail-node`。
- Decision：n=26，覆盖 9 幅；typical **约 7–10 字**；P90≈14。
- 行数分布：1 行 81.8% / 2 行 12.7% / ≥3 行 5.5%。
- A3 Decision recommendation：约 7–10 字；>P90≈14 字进入强压缩复核。

**重构规则：**
- A3 可承载更多节点，但 decision 仍应短；复杂控制流不能通过长判断句表达。
- 若嵌套循环可消去而不丢语义，复核 A2；若已变成密集调度网络，最后才复核 A6。

## A4 分支/搜索

**图级证据：4 幅；Evidence=Medium。**

- Node count：Q1=8.5，median=9.5，Q3=11.8，P90=14.9，observed max=17。
- 可读 typical band：**约 8–12 个普通节点**。
- Node-count review trigger：**N > 12**；A5/A6 仅描述，不用于稳定自动阈值。
- Process：n=23，覆盖 4 幅；Q1/median/Q3/P90 = 7.5/9/11/12.8 字。
- Process typical：**约 8–11 字**；>Q3≈11 记 `long-node`；>P90≈12.8 记 `long-tail-node`。
- Decision：n=9，覆盖 3 幅；typical **约 4–8 字**；P90≈12.8。
- 行数分布：1 行 46.5% / 2 行 51.2% / ≥3 行 2.3%。
- A4 Decision preference：约 4–8 字；Evidence=Medium。

**重构规则：**
- Decision 应比 process 更短，搜索/分支语义优先由拓扑表达。
- 若分支内部发展成长期迭代，复核 A2/A3；若成为高密调度网络，再复核 A6。

## A5 并行子算法

**图级证据：1 幅；Evidence=Low。**

- Node count：Q1=19，median=19，Q3=19，P90=19，observed max=19。
- 可读 typical band：**约 19–19 个普通节点**。
- Node-count review trigger：**N > 19**；A5/A6 仅描述，不用于稳定自动阈值。
- Process：n=11，覆盖 1 幅；Q1/median/Q3/P90 = 7/8/11.5/31 字。
- Process 数值仅作描述，不冻结类型特异阈值。
- Decision：可测 n=6，覆盖 1 幅；证据不足以建立稳定类型特异阈值。
- 行数分布：1 行 100.0% / 2 行 0.0% / ≥3 行 0.0%。

**重构规则：**
- 只有 1 幅主证据；当前数值仅描述，不形成类型特异自动阈值。
- 若某个 lane 内部本身复杂，应拆成独立子图；不得从 n=1 的分位数制造硬规范。

## A6 密集判定/调度网络

**图级证据：3 幅；Evidence=Low。**

- Node count：Q1=18.5，median=20，Q3=22，P90=23.2，observed max=24。
- 可读 typical band：**约 18–22 个普通节点**。
- Node-count review trigger：**N > 22**；A5/A6 仅描述，不用于稳定自动阈值。
- Process：n=37，覆盖 3 幅；Q1/median/Q3/P90 = 17/24/31/40.8 字。
- Process 数值仅作描述，不冻结类型特异阈值。
- Decision：可测 n=21，覆盖 3 幅；证据不足以建立稳定类型特异阈值。
- 行数分布：1 行 0.0% / 2 行 24.6% / ≥3 行 75.4%。

**重构规则：**
- 仅 3 幅主证据，且节点数、文字长度、多行率都高；这是高密度现实，不是推荐 target。
- A6 是最后选择项；若可拆成 A2/A3/A4 + subprocess，应优先拆解。

---

# 9. Overload Detection

## 9.1 Node-count

对 High/Medium 类型：

```text
N < Q1          → compact / below-typical
Q1 <= N <= Q3  → typical
N > Q3          → node-count-review
```

A5/A6 只报告观察值，不执行稳定 type-specific 自动阈值。

## 9.2 Per-node text

证据充分时：

```text
L <= Q3         → typical-or-compact
Q3 < L <= P90  → long-node
L > P90         → long-tail-node
```

Q1 以下不算问题；本规范防止信息过载，不要求节点达到最低字数。

## 9.3 Figure text density

```text
median_process_text > type_process_Q3
→ process-density-review

median_decision_text > applicable_decision_Q3
→ decision-density-review

多个普通节点 >=3 行
→ multiline-density-review
```

## 9.4 Strong overload

```text
node-count-review
AND
(process-density-review OR decision-density-review)
```

Strong overload 进入重构决策，不自动失败。

---

# 10. 过载重构决策树

```text
发现 content overload
│
├─ 节点是否包含正文式解释？
│   ├─ 是 → 删除 / 移正文 / 压缩短语
│   └─ 否
│
├─ 一个节点是否包含多个真实先后动作？
│   ├─ 是 → 拆为真实步骤
│   └─ 否
│
├─ 连续节点是否构成可命名子过程？
│   ├─ 是 → 抽 subprocess，必要时另画局部图
│   └─ 否
│
├─ 是否存在真实阶段边界？
│   ├─ 是 → 返回 selection 复核 M4
│   └─ 否
│
├─ 是否暴露出原类型遗漏的真实结构？
│   ├─ M2 多层展开 → 复核 M3
│   ├─ A2 多层循环 → 复核 A3
│   ├─ A4/A3 密集调度 → 最后才复核 A6
│   └─ 其他 → 返回 selection-v1
│
└─ 类型仍正确且信息都不可删？
    ├─ 是 → overview + local subflow
    └─ 否 → 保持当前内容并交给用户/人类作者做最终布局
```

---

# 11. Stage / Subprocess / 拆图准入

## 11.1 Stage

只有真实功能边界存在时才允许 Stage。禁止“节点太多 → 每 4 个框一组”的伪分阶段。

## 11.2 Subprocess

只有多个步骤能够被一个稳定、可命名的局部过程替代时才抽 subprocess。Subprocess 不是删除细节的借口；必要时应提供局部子图。

## 11.3 拆成两张图

满足以下任一条件可考虑：

- 类型正确但 Strong Overload 持续存在；
- 存在内部逻辑完整的 subprocess；
- Overview 与局部过程都具有独立解释价值；
- 保持单图会迫使大量普通节点进入 ≥3 行；
- 拆图不会破坏主流程连续理解。

推荐：Overview + Local Subflow，而不是机械把一条简单长链切成上下两张。

---

# 12. Agent Content Contract

```yaml
flowchart_type: A2
content_budget:
  evidence_level: high
  node_count:
    planned: 8
    typical_q1_q3: [7, 9]
    status: typical
  process_text:
    planned_median_chars: 8
    typical_q1_q3: [5, 12]
    status: typical
  decision_text:
    planned_median_chars: 8
    typical_q1_q3: [7, 10.5]
    status: typical
  multiline:
    nodes_ge_3_lines: 0
    status: preferred
overload:
  node_count_review: false
  process_density_review: false
  decision_density_review: false
  multiline_density_review: false
  strong_overload: false
actions: []
layout_status: human-owned / pending-human
style_status: human-owned / pending-human
tool_route_status: none / human-choice
```

Content 层不得输出坐标、字体、颜色、Graphviz/Mermaid/TikZ 参数。

---

# 13. 验收清单

1. 类型已由 selection-v1 决定；
2. 普通节点总数已计算，Container 未混入；
3. 每个普通节点只有一个主要语义单元；
4. Process 未承担正文解释；
5. Decision 是短条件，不是完整推理段落；
6. Terminal 保持简短；
7. 普通节点优先 1–2 行；
8. 超过 type Q3 的节点数已触发 review；
9. 超过 role Q3/P90 的长节点已被标记；
10. 节点数与文字密度同时偏高时已进入 Strong Overload review；
11. Stage 仅来自真实阶段；
12. Subprocess 仅来自真实可封装子过程；
13. 结构事实变化时返回 selection-v1，而非静默改类型；
14. 未通过缩字号/缩 padding 解决 content overload；
15. A5/A6 没有使用低证据统计作为稳定硬阈值；
16. 通过 content audit 后才交给用户/人类作者进行最终布局与绘制。

---

# 14. Machine-Safe Policy Object

```python
FLOWCHART_CONTENT_V1 = {
    "authority": "HOW_MUCH_INFORMATION",
    "primary_length_metric": "char_count_raw",
    "typical_definition": "Q1_to_Q3",
    "node_count_review": "N > type_Q3",
    "long_node": "L > type_role_Q3",
    "long_tail_node": "L > type_role_P90_when_supported",
    "preferred_lines": [1, 2],
    "strong_overload": "node_count_review AND (process_density_review OR decision_density_review)",
    "hard_max_node_count": None,
    "hard_max_chars": None,
    "forbid_font_shrink_as_content_fix": True,
    "low_evidence_types": ["A5", "A6"],
    "selection_mutation": "forbidden; return_for_review",
}
```

---

# 15. 不设置统一 Hard Max

本 v1 不冻结“所有图最多 X 节点 / 所有 process 最多 Y 字 / 所有 decision 最多 Z 字”。

理由：不同类型容量显著不同；73 图足以刻画 typical 与异常，但不足以证明样本极值之外一定错误；A5/A6 证据量低。

本 v1 的强要求是：**过载必须被检查和解释，而不是超过某个数字直接失败。**

---

# 16. 与 human-owned 最终布局 / 绘制的接口

Content 输出：type、semantic nodes、roles、node labels、edge/branch meanings、semantic grouping、node-count/text status 与 overload flags。

通过 content audit 后，用户/人类作者才开始最终布局与绘制。人类作者决定 TB/LR、single spine、fan-in、stage zone、lane、outer loop、nested shell、network 等空间表达，并判断坐标、节点尺寸、lane 位置、edge bends、字体字号、视觉样式和导出工具。

Content 不得预设方向、坐标、节点几何、lane 位置、边的弯折、字体字号、视觉样式或 renderer 参数。ChatGPT/Codex 只交付语义节点、边、分支、分组和内容计划，并以 `layout_status: human-owned / pending-human` 停止。

若一个已经通过 content audit 的图无法在正常字号下排下，应由人类作者重新判断布局或拆图；不得自动删语义或缩字体。若 content audit 已判定过载，也不得以更紧密排版掩盖问题。

KyMCM Lite 0.9.12 不新增 flowchart layout/style/exec 规范，不选择 Graphviz、Mermaid、TikZ、SVG、PPT 或其他自动 renderer/tool route。

---

# 17. v1 冻结结论

1. Selection 与 Content 分离；
2. `content-v1` 只控制 HOW MUCH INFORMATION；
3. Typical 使用固定 census 的 Q1–Q3；
4. `N > type_Q3` 是 review trigger，不是禁止线；
5. Process/Decision 的类型特异 Q3/P90 仅在证据足够时使用；
6. 常规 Algorithm Decision fallback 为约 6–10 字，P90≈13 字；
7. 普通节点优先 1–2 行；
8. 复杂度由节点数量与节点文字密度联合判断；
9. 节点数偏高但文字短，优先由语义层级承载，并交给人类作者判断最终布局；
10. 节点数正常但文字长，优先压缩文案；
11. 节点数与文字同时偏高，进入 Strong Overload review；
12. Stage/Subprocess 必须有真实语义；
13. A5/A6 只保留描述性数字，不设置稳定自动阈值；
14. 不设置统一 Hard Max；
15. 不允许通过缩字号修复 content overload；
16. 若过载揭示原类型不忠实，返回 selection-v1 复核；
17. 通过 content audit 后才交给用户/人类作者完成最终布局、走线与绘制。

---

## 一句话原则

**先控制信息容量，再解决几何排布；复杂性应由真实结构承载，而不是由长文本和小字号承载。**
