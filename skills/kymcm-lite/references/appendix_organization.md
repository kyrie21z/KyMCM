# KyMCM Lite 附录整理规范

附录整理是正式结果、提交要求和认证边界稳定后的可选独立阶段。`appendix/` 是排除绘图后的完整正式求解代码与正式结果附件，服务提交和复现；根 `code/` 是从本队真实工程选择、用于最终提交文档代码附录的代表性代码。二者用途不同、互不替代。唯一正式计划是 `reports/appendix/APPENDIX_START.md`，唯一执行报告是 `reports/appendix/APPENDIX_RESULT.md`。

The modeling workflow has no FROZEN_CONTEXT surface. Appendix organization may reference START, RESULT, and HANDOFF only as internal context.

## 基本原则

1. 先冻结结构和白名单，再从白名单正向构造，禁止先复制整个工程再反向删除。
2. `appendix/` 以正式流程完整性为先；根 `code/` 以真实性、提交展示价值、实现辨识度和可读性为先。
3. `problems/`、`input/` 以及正式 START/RESULT 和技术 HANDOFF 始终只读；复制、裁剪、重命名和机械清理仅发生在 `appendix/`、`code/` 与 `reports/appendix/evidence/`。
4. 单一或拆分 START/RESULT 契约及匹配 HANDOFF 只能作为上下文参考，不能复制进、授权或扩展最终包；HANDOFF 也不是正式认证来源。
5. 不引入附录状态机、审批对象、事件日志、哈希对象、内容 JSON、持久化清单或外部相似度服务。

## 两个代码交付面的职责

`appendix/problems/qN/code/` 与可选的 `appendix/problems/preprocess/code/` 保留生成正式结果实际使用的代码全集及传递依赖，不为追求文件数最少而删去正式流程。根 `code/` 不承担完整复现职责，只选择与正式方法、数据处理、执行可靠性或结果审计有明确关系的代表性直接文件。

两类代码都必须来自本队真实工程并可追溯到 APPENDIX_START 中的准确源路径。根 `code/` 可以同时展示核心模型与非核心工程实现，不要求每题一个文件，也不要求只展示最常见的核心算法。

## `appendix/`：完整正式求解代码

`appendix/problems/qN/` 和 `appendix/problems/preprocess/` 只能有 `code/` 和 `result/` 后代。PRE 的 code 来源仅限 `problems/preprocess/code/`；其 result 来源可来自 `data/derived/`、`outputs/` 和非合同 `notes/`。START_PRE、RESULT_PRE、HANDOFF_PRE 与所有 QN 合同同样禁止复制。代码白名单覆盖正式流程实际使用的输入解析、清洗、预处理、特征/参数/情景生成、模型构建、目标与约束、求解器调用、任务调度、批量或并行执行、断点续算、阶段恢复、缓存复用、失败隔离与重试、状态回读、验证审计、结果核验与正式导出，以及这些路径依赖的本地模块和配置代码。

排除测试、缓存和字节码、日志和运行输出、历史/废弃/试验实现、临时调试脚本、归档与二进制、模型 checkpoint 数据、求解中间状态、可再生运行产物、内部桥接、凭据、个人环境文件和无关基础设施。调度、恢复、状态、监控或审计语义本身不是排除理由；`scheduler.py`、`checkpoint.py`、`run_status.py`、`resource_monitor.py`、`audit.py` 等真实源码可以进入。

结果只保留最终策略、代表性或最坏轨迹、核心汇总表和必要证书，排除 RESULT Markdown、日志、manifest、checkpoint 数据、阶段账本数据、内部审计报告和可重建中间文件。每项结论只保留一个正式结果版本。比赛强制的 `Result.xlsx`（如适用）只能在 `appendix/Result.xlsx` 出现一次，沿用官方模板、数值一致，并接受 COPY 哈希和基本可打开性检查。

`appendix/environment/` 只能包含 `README.md`、`requirements.txt` 与 `system_info.txt`。`appendix/input/` 仅在确实使用了审稿人无法取得且验证必需的非标准外部资料时存在，绝不创建空目录。

## 绘图代码排除

绘图代码不进入 `appendix/problems/qN/code/`、`appendix/problems/preprocess/code/` 或根 `code/`。独立 `figure/` 工作区不是 appendix 来源。主要职责为生成最终展示图、调整视觉样式/排版、转换结果为 PNG/PDF/SVG，或仅为可视化读取结果而不参与正式数值计算的代码都应排除。

正式计算与少量绘图逻辑同文件时，优先从真实源文件机械 CURATE：仅删除绘图入口或函数，不重写数学部分。若无法安全分离，停止并记录人工决策，不静默改写。自动 checker 不根据文件名或 import 猜测全部绘图职责；APPENDIX_START 白名单、Codex 语义审查和人工终审承担该边界。

## 根 `code/`：代表性真实实现

根 `code/` 只含直接文件，不引入完整源码树、数据、结果、README、环境文件、日志、测试或绘图文件。允许选择核心模型、求解逻辑、多阶段调度、情景批处理、断点续算、结果复用、失败隔离与重试、输入审计、结果回读、约束核验、参数配置和实验控制。

每个 C 条目必须说明源文件、正式流程中的真实职责、适合提交展示的理由、COPY/CURATE 模式，以及 CURATE 删除的展示无关内容和保持不变的数学与执行语义。代码不得硬编码最终数值答案，也不得改变模型语义、计算顺序、随机性、平局规则、恢复规则或认证边界。

## COPY 与 CURATE

`appendix/` 默认优先 COPY 并保留原相对结构。CURATE 仅用于机械分离同文件绘图、调整提交所需 import/相对路径、合并少量真实小模块，或删除日志、调试入口和未调用包装；不得删去正式依赖或改变数学与执行行为。

根 `code/` 可 COPY 真实源文件，也可 CURATE 一个或少量真实源文件形成可读片段。可以补充必要注释、类型或入口说明，但不得虚构行为。所有源文件都进入 `source_integrity.csv` 的只读核验。

## 真实性、原创性与相似性边界

合理做法是从本队真实正式工程选择具有实现辨识度的代表性代码。禁止复制、改写或拼接其他队伍、网络答案或不合规来源；禁止只为改变相似度乱改变量名、插入无效分支/死代码/垃圾注释、拆乱表达式或控制流、使用混淆器或自动差异工具，以及添加未参与正式流程的“个性化”代码。

目标是让提交代码准确说明本队如何实现，并减少通用核心实现自然相似造成的误判风险，不是规避查重。不得以“降低查重率”描述任何白名单用途，也不设置外部代码数据库、在线查重、相似度阈值或自动原创性结论。

## 验证、结果、环境与只读规则

所有输出不得含绝对本地路径、用户名路径、凭据、令牌或敏感机器信息。部分验证、有限策略类、受限状态覆盖或有限时域偏离分析不得被表述为全局最优或完整均衡认证。

验证应覆盖完整正式入口、传递依赖、调度/恢复路径、实际编译或构建、COPY 哈希、CURATE 语义边界、绘图排除、根 `code/` 来源真实性、结果唯一性、环境最小化、敏感信息和源文件只读。无法安全分离绘图与计算或无法确认语义等价时停止人工复核。

## 自动 checker 的能力边界

检查器只读且不执行用户代码、不导入用户模块、不运行求解器或编译器。它检查精确白名单、路径、文件类型、结构、COPY 哈希、静态 Python/import、C/C++ include、有限 CMake 字面路径、XLSX ZIP/XML 基本结构和高置信敏感信息。

检查器不自动判断正式代码覆盖、绘图职责、原创性、外部相似度、CURATE 语义等价、数学正确性、完整动态导入、完整 CMake、Excel 数值/公式/格式或提交展示质量；这些由 Codex 执行证据与人工终审承担。
