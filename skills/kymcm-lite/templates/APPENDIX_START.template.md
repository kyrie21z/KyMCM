# APPENDIX START

## 1. 提交范围与比赛要求

<!-- 说明正式提交要求和附件限制。appendix/ 收录排除绘图后的完整正式求解代码；根 code/ 选择用于论文 PDF 的真实代表性代码；两者都不收录绘图代码。 -->

## 2. 论文引用、正式结果与认证边界

<!-- 列出论文实际引用的结果、唯一正式版本，以及有限策略类或有限时域等认证边界。 -->

## 3. appendix 目标结构

<!-- 冻结 appendix/ 的完整正式求解代码结构和根 code/ 的代表性直接文件；不要先复制整个工程。 -->

## 4. appendix 文件白名单

<!-- 覆盖正式求解流程实际使用的所有代码和传递依赖，并明确排除绘图、测试、历史实现和运行产物。每个目标一行；示例仅供格式参考：
- A001 — COPY — `problems/q1/code/solve.py` → `appendix/problems/q1/code/solve.py` — 正式入口
- A002 — COPY — `problems/q1/code/scheduler.py` → `appendix/problems/q1/code/scheduler.py` — 正式任务调度
- A003 — CURATE — `problems/q1/code/model.py` → `appendix/problems/q1/code/model.py` — 仅机械删除绘图入口
PRE 示例可从 `problems/preprocess/code/clean.py` 映射至 `appendix/problems/preprocess/code/clean.py`，或从 `problems/preprocess/data/derived/clean.csv` 映射至 `appendix/problems/preprocess/result/clean.csv`；不得列入 START_PRE、RESULT_PRE 或 HANDOFF_PRE。
-->
- A090 — GENERATE — `appendix/environment/README.md` — 复现入口说明
- A091 — GENERATE — `appendix/environment/requirements.txt` — 最小依赖清单
- A092 — GENERATE — `appendix/environment/system_info.txt` — 非敏感版本信息

## 5. code 文件白名单

<!-- 选择来自本队真实正式工程、具有论文相关性和实现辨识度的代表性直接文件；核心模型以及调度、恢复、审计等非核心实现均可。说明真实职责、展示理由和 COPY/CURATE；禁止复制、混淆、垃圾代码或仅为改变相似度的改写。示例仅供格式参考：
- C001 — CURATE — `problems/q1/code/run_scenarios.py`; `problems/q1/code/checkpoint.py` → `code/q1_scenario_execution.py` — 展示正式情景调度与断点续算
-->

## 6. 依赖闭包与机械裁剪规则

<!-- 区分 appendix code 的正式流程完整性与 root code 的论文展示代表性；记录绘图排除、COPY/CURATE 来源、入口与传递依赖，以及不得改变数学语义、执行顺序、随机性、恢复规则和结果边界。 -->

## 7. 环境、外部资料与强制结果文件

外部资料：无

强制结果文件：无

<!-- 如声明 appendix/input，请补充资料来源、用途及不可替代性。 -->

## 8. 验收方法与停止规则

<!-- 说明正式代码覆盖、绘图排除、根 code 来源追溯、编译/构建、工作簿、哈希和敏感信息审查；禁止混淆、垃圾代码和非正式代码。计算与绘图无法安全分离时停止并人工确认。 -->

## 9. 未决问题

无
