# KyMCM Lite 可选 Preprocess 阶段

`problems/preprocess/` 是可选、固定且不可拆分的公共数据准备与探索性分析单元。它与 `qN` 同级，依赖方向只能为 `PRE → QN`。启用前确认至少两个问题共享数据口径、清洗或基础 EDA；若处理只服务一个问题或模型，留在对应 QN。

用 `scripts/lite.py init --workspace PATH --questions N --preprocess` 可创建空 PRE 目录；init 不创建合同。精确合同必须分别从 `templates/START_PRE.template.md`、`templates/RESULT_PRE.template.md` 和 `templates/HANDOFF_PRE.template.md` 编写，保留模板给定的标题与八个 heading。RESULT_PRE 第 7 节证据行使用精确格式 `- E1 — \`problems/preprocess/data/derived/file.csv\` — 用途`。HANDOFF_PRE 没有 Python checker，须按 RESULT_PRE 与机器证据做语义复核。

## 权威与边界

- 原始数据决定未经处理的事实。
- RESULT_PRE 决定正式公共字段、单位、时间范围、样本粒度、处理规则、冻结数据产品与限制。
- 声明 PRE 的 START_QN 决定如何使用这些输出，并可增加问题专属处理。
- RESULT_QN 决定问题模型结论。
- HANDOFF_PRE 组织数据层论文材料，但不是事实来源或建模依赖。

PRE 不选择或认证最终模型，不执行正式优化/预测/评价/机理求解，不生成 QN 答案，不把探索相关写成因果，也不承担单模型专属特征工程或默认训练/验证划分。公共处理若改变某题数学假设、目标变量或评价边界，必须同时在 RESULT_PRE 和该题 START 明示。

## 执行顺序

1. 编写 START_PRE 并运行 `check-preprocess-start`。
2. 盘点原始文件、工作表、schema、单位、编码、时区、粒度、主键和关联键。
3. 运行最小 parse-transform-write-readback smoke test。
4. 持久化原始质量审计。
5. 按冻结规则完成公共清洗、关联、转换和确定性派生。
6. 回读输出并核对 schema、单位、范围、行数和样本 accounting。
7. 只做服务问题理解的聚焦 EDA。
8. 仅在已触发的数据风险上运行 L1；仅在有用且可承受时运行 L2。
9. 写 RESULT_PRE，运行 `check-preprocess-result`。
10. 论文协作开始时创建或更新 HANDOFF_PRE。

复用 `modeling_plan_design.md` 的 execution-first、阶段持久化、cache/resume、预算和失败隔离原则，但不要把模型可识别性等术语机械强加给简单清洗。

## 审计、清洗与冻结输出

先冻结检测条件，再执行处理；禁止根据正式模型结果反向修改清洗。每项缺失、重复、非法/异常值、单位转换和多表关联规则都记录检测、动作、处理数量、样本影响、停止条件与证据。

冻结数据产品必须有稳定 workspace-relative 路径、schema、字段语义、单位、粒度、行数、适用范围、禁止用途和数据字典。记录处理前后样本、删除/修正/插补数量、关联损失、关键缺失与异常。输出回读必须确认实际磁盘内容而非仅相信内存对象。

## Smoke、L0、L1 与 L2

- Smoke：用最小代表性切片贯通解析、转换、写出和回读。
- L0：schema、行数、单位、唯一性、缺失、关联损失、范围、确定性和输出回读；失败即阻断。
- L1：仅处理已触发的高缺失、异常规则敏感性、关联损失、时间泄漏或代表性风险。
- L2：替代插补、稳健统计或扩展 EDA；资源不足时可删除，不得替代基本审计。

## EDA 与表述边界

每项 EDA 必须有问题相关目的、统计量/图形、分组口径、证据和可支持/不可支持表述。区分描述性事实、探索性发现和待验证假设。相关、组间差异和时间共变不证明因果；样本外、时间外、空间外或未覆盖群体不得无依据外推。预测任务在任何全样本变换、时间切分和目标衍生前检查泄漏。

## 下游冲突与变化

声明 PRE 的 QN 必须完整读取 START_PRE 和 RESULT_PRE，核对字段、单位、时间/时区、粒度、样本、筛选/关联、缺失/异常/插补、数据路径/schema、泄漏和外推边界。冲突时列出精确位置与影响并停止询问；不得在 QN 内私自覆盖公共数据错误。

RESULT_PRE 或关键数据产品实质变化后，复核所有声明 PRE 的已完成 QN，判断是否需要重跑并更新 HANDOFF。mtime 提示仅是陈旧启发式，不是版本认证、依赖图或自动重跑。

## Checker 与人工边界

checker 只读检查目录、合同结构、声明语法、证据路径/存在性、安全性、Git advisory 和 mtime advisory。它不执行清洗或 EDA，不判断规则合理性、统计/因果正确性、EDA 完整性、数据泄漏是否已彻底排除，也不决定下游重跑范围。成功检查不创建状态、审批、hash、manifest、内容 JSON 或报告。
