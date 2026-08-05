# APPENDIX START

## 1. 提交范围与比赛要求

<!-- 说明用户明确给出的比赛提交要求和附件限制。appendix/ 与根 code/ 只收录可审计计算核心；正式结果附件独立交付，不由附录代码重新生成；两者都不收录绘图、显示、接口或报告导出代码。 -->

## 2. 正式结果与认证边界

<!-- 按顺序读取并列出基础 RESULT、已完成 Supplement Result、当前 HANDOFF、当前有效数据产品、机器证据、独立正式结果附件，以及有限策略类或有限时域等认证边界；这些 Markdown 合同只作内部上下文，均不得复制。 -->

## 3. appendix 目标结构

<!-- 冻结 appendix/ 的计算核心结构、独立 result 资产和根 code/ 的代表性直接文件；不要先复制整个工程，也不要规划运行后导出结果。 -->

## 4. appendix 文件白名单

<!-- 覆盖当前有效计算核心实际使用的所有代码和传递依赖，以及独立、已接受且符合路径规则的结果附件；明确排除绘图、显示/接口、测试、被替代的旧实现/旧结果、日志、缓存、checkpoint、临时文件和任何导出器（比赛明确要求历史对照除外）。代码不得生成结果表或持久化运行状态；每个目标一行；示例仅供格式参考：
- A001 — COPY — `problems/q1/code/solve.py` → `appendix/problems/q1/code/solve.py` — 输入、模型、优化与内存中结果核心
- A002 — COPY — `problems/q1/outputs/formal.csv` → `appendix/problems/q1/result/formal.csv` — 已接受正式结果附件，独立于代码交付
- A003 — CURATE — `problems/q1/code/model.py` → `appendix/problems/q1/code/model.py` — 仅机械删除显示入口并保留计算语义
PRE 示例可从 `problems/preprocess/code/clean.py` 映射至 `appendix/problems/preprocess/code/clean.py`，或从允许的 `problems/preprocess/data/derived/clean.csv` 映射至 `appendix/problems/preprocess/result/clean.csv`；不得列入 START_PRE、RESULT_PRE 或 HANDOFF_PRE。
-->
- A090 — GENERATE — `appendix/environment/README.md` — 复现入口说明
- A091 — GENERATE — `appendix/environment/requirements.txt` — 最小依赖清单
- A092 — GENERATE — `appendix/environment/system_info.txt` — 非敏感版本信息

## 5. code 文件白名单

<!-- 选择来自本队当前有效正式工程、具有提交展示价值、实现辨识度和可读性的代表性计算核心直接文件；当前 Supplement 的真实代表性代码以及特征、模型、优化、统计、预测、约束和审计实现均可。仅在不产生文件/目录/持久化副作用时展示调度或恢复片段。说明真实职责、选择理由和 COPY/CURATE；禁止复制、混淆、垃圾代码或仅为改变相似度的改写。示例仅供格式参考：
- C001 — CURATE — `problems/q1/code/model.py`; `problems/q1/code/constraints.py` → `code/q1_model_core.py` — 展示模型、约束和内存中验证，不生成结果文件
-->

## 6. 依赖闭包与机械裁剪规则

<!-- 区分 appendix code 的计算核心与独立结果资产、root code 的代表性核心；每个 CURATE 条目必须记录：保留的计算核心、第一层（文件写入与持久化副作用）删除内容、第二层（结果与文档构造）删除内容、第三层（展示/导出入口与孤儿代码清理）删除内容，以及保持不变的数学、数据和执行语义；同时记录绘图/显示/接口排除、来源、入口与传递依赖，以及不得写文件/建目录或改变数学语义、执行顺序、随机性、恢复规则和结果边界。 -->

## 7. 环境、外部资料与强制结果文件

外部资料：无

强制结果文件：无

<!-- 如声明 appendix/input，请补充资料来源、用途及不可替代性。 -->

## 8. 验收方法与停止规则

<!-- 说明计算核心覆盖、独立结果与 RESULT 一致性、静态副作用扫描、第二层结果/文档构造人工审查、第三层展示/导出入口删除与裁剪后孤儿 import/变量/常量/函数/模块清理、绘图/显示/接口排除、根 code 来源追溯、编译/构建、工作簿、哈希和敏感信息审查；禁止混淆、垃圾代码、结果导出器和运行状态文件。计算与显示无法安全分离时停止并人工确认。 -->

## 9. 未决问题

无
