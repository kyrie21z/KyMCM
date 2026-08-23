# KyMCM Lite 附录整理规范

附录整理是正式结果、提交要求、认证边界和 AI 工具使用详情 PDF 均冻结后的可选独立阶段。`appendix/` 根文件是独立最终提交附件，`appendix/problems/**` 是审计/复现支持；根 `code/` 只收录本队真实工程中的代表性可审计计算核心。根级提交附件和独立正式结果均不由附录代码重新生成。唯一正式计划是 `reports/appendix/APPENDIX_START.md`，唯一执行报告是 `reports/appendix/APPENDIX_RESULT.md`。

The modeling workflow has no FROZEN_CONTEXT surface. Appendix organization may reference base START/RESULT, accepted Supplement Result, and the current HANDOFF only as internal context; none of those contracts may be copied.

## 基本原则

1. 先冻结结构和白名单，再从白名单正向构造，禁止先复制整个工程再反向删除。
2. `appendix/problems/qN/code/` 与可选的 `appendix/problems/preprocess/code/` 是可审计的计算核心：输入、特征/参数、模型、优化、统计、预测、约束、验证和审计路径可以保留，但不承担正式结果表、接口/报告文本、导出或运行状态文件的生成。
3. 根 `code/` 是提交文档中的真实代表性计算核心，可以选择一题或多题的核心实现；它不承担完整复现，也不能用来规避 appendix 的计算边界。
4. `appendix/AI 工具使用详情.pdf` 与比赛明确要求单独提交的根结果文件只做 COPY；普通审计/复现结果保留在 `appendix/problems/qN/result/` 或 `appendix/problems/preprocess/result/`。checker 只核验，不运行附录代码、不重新生成或编辑提交附件。
5. `problems/`、`input/` 以及正式 START/RESULT、Supplement 和技术 HANDOFF 始终只读；修改只发生在 `appendix/`、根 `code/` 与 `reports/appendix/evidence/`。
6. 不引入附录状态机、审批对象、事件日志、哈希对象、内容 JSON、持久化清单、自动迁移或外部相似度服务。

## 计算核心与结果资产的边界

计算核心可以读取输入、构造特征和情景、建立目标与约束、调用求解器、执行统计和预测、核验约束并组装内存中的结果对象。正式结果表、接口协议、Markdown/HTML/JSON 报告、CSV/XLSX/Parquet/Feather/NPY/NPZ/Joblib/Pickle 导出、缓存、checkpoint、阶段账本、临时目录、数据库和模型持久化均属于独立结果/运行副作用，不得由提交代码生成。

高置信写入包括 Python 的显式写模式 `open`、`Path` 写入/建目录、pandas/NumPy/SciPy/joblib/pickle/JSON/YAML writer、临时文件、shutil copy/move、OS 建目录、shelve/SQLite、torch/model save，以及 C/C++ 的 `fopen` 写模式、`ofstream`、输出型 `fstream`、写标志 `open` 和目录/复制 API。静态 checker 以 `LITE-APPENDIX-CODE-SIDE-EFFECT-001` 阻断这些调用；只读打开、内存对象和不构成写入的纯函数允许保留。动态包装器、运行时拼接字符串、间接库调用和语义等价仍需人工审查。

三层删除规则必须同时满足，不能用笼统标签替代：

- **第一层：文件写入与持久化副作用**。删除结果、报告、缓存、checkpoint、模型、数据库、临时文件和目录的写入，包括 CSV、Markdown、Excel、JSON、JOBLIB、NPY/NPZ、pickle、parquet、feather、日志、缓存和临时目录生成。高置信 API 由 `LITE-APPENDIX-CODE-SIDE-EFFECT-001` 静态阻断。
- **第二层：结果与文档构造**。即使最终写入已经删除，仍删除硬编码结果表/接口表（如 `Q2-03`—`Q2-11`）、RESULT/HANDOFF/Supplement/APPENDIX RESULT/依赖审查/状态报告/日志文案、正式结果表和证据索引拼装、仅为导出准备的格式化列，以及不再参与计算的结果包装对象。该层由 Codex 语义审查和人工终审负责，不使用过宽的 DataFrame 或字符串扫描。
- **第三层：展示/导出入口与孤儿代码清理**。删除只调用导出、报告、缓存或展示逻辑的 `main()`/CLI、只服务于输出目录/文件名/接口编号/报告路径的参数常量、前两层删除后失去调用者的函数和模块、未使用 import/变量/常量/辅助函数，以及只打印正式结果而不参与计算或审计的入口。保留的入口必须真正驱动输入读取、模型计算和合法性审计，并只返回内存结果或执行断言。

每个 `CURATE` 条目都必须记录：保留的计算核心、第一层删除内容、第二层删除内容、第三层删除内容，以及保持不变的数学、数据和执行语义。

## `appendix/` 交付面

`appendix root submission asset` 指比赛最终提交在嵌套审计/复现材料之外独立要求的文件。当前模板支持两类：固定的 `appendix/AI 工具使用详情.pdf`，以及 APPENDIX_START 明确声明的 `appendix/<official-required-filename>` 强制结果文件。前者只能由 `reports/ai-usage/AI 工具使用详情.pdf` COPY；后者只能由已接受的正式结果源 COPY，并允许在计划中映射为比赛要求的官方文件名。两类都必须保持源/目标字节相同、进入 `source_integrity.csv`，不得 CURATE、GENERATE 或由附录计算覆盖。

比赛明确要求某结果文件作为独立提交附件时，才将它声明为根结果；只用于审计、复现或支持的结果继续嵌套。根结果后缀仅允许 `.xlsx`、`.csv`、`.txt`，名称必须是安全的非隐藏直接子文件；AI PDF 是独立保留目标，不属于通用后缀集合。每个官方结果只有一个权威根副本，不得以相同源或相同字节在 `appendix/problems/**/result/` 再放一个正式副本。未来需要其他后缀时先扩展产品合同，不接受任意压缩包或二进制。

当前目标结构为：

```text
appendix/
├── AI 工具使用详情.pdf
├── <mandatory-result>.xlsx|.csv|.txt   # 仅在比赛明确要求时
├── problems/
│   ├── preprocess/{code,result}/       # 仅在实际需要时
│   └── qN/{code,result}/
├── environment/{README.md,requirements.txt,system_info.txt}
└── input/                              # 仅在确有必要时
```

不创建空目录。当前 APPENDIX_START 只有在 `reports/ai-usage/AI 工具使用详情.pdf` 已生成并人工复核后开始；checker 只机器验证该普通非空源已存在。视觉、隐私、真实性、比赛是否确实要求某根结果及其数学正确性仍由计划证据和人工复核负责。

`problems/qN/explore/**` 是非正式临时工作区，不是 Appendix 来源：其中代码、输出或图像均不得复制到嵌套 `appendix/problems/**`、根 `code/` 或任何根提交资产。被 PROMOTE 的内容必须先进入正式 START/Supplement 路径并重跑、复核和接受，再依据既有 Appendix 映射选择正式源。

`appendix/problems/qN/` 和 `appendix/problems/preprocess/` 只能有 `code/` 和 `result/` 后代。PRE 的 code 来源仅限 `problems/preprocess/code/`；其 result 可来自允许的 `data/derived/`、`outputs/` 和非合同 `notes/`。START_PRE、RESULT_PRE、HANDOFF_PRE、Supplement 合同及基础 QN 合同禁止复制。

代码白名单覆盖当前正式结果所依赖的输入解析、清洗、预处理、特征/参数/情景生成、模型构建、目标与约束、求解器调用、统计/预测、验证审计和本地传递模块。调度、批处理、并行、恢复和监控源码只有在仍属于计算核心或验证路径、且不写入缓存/checkpoint/日志/结果接口时才可进入；`scheduler.py` 这类名称本身不是排除理由。

嵌套结果只保留已接受的最终策略、代表性或最坏轨迹、核心汇总表和必要证书，排除 RESULT Markdown、接口/报告文本、日志、manifest、checkpoint 数据、阶段账本、内部审计报告和可重建中间文件。每项结论只保留一个正式结果版本；每个声明的根 XLSX 接受 ZIP/XML 基本结构检查，根 CSV/TXT 必须非空且可安全解码。`appendix/Result.xlsx` 仍是有效特例，但不再是唯一允许的官方文件名。

`appendix/environment/` 只能包含 `README.md`、`requirements.txt` 与 `system_info.txt`。`appendix/input/` 仅在审稿人无法取得且验证确实必需的非标准外部资料存在时使用，绝不创建空目录。

## 绘图、显示和接口代码排除

绘图代码、最终展示排版、图像/表格转换、仅读取结果的显示脚本、交互式接口和报告/导出构造器不进入 appendix code 或根 `code/`。独立 `figure/` 工作区不是 appendix 来源。

正式计算与少量绘图逻辑同文件时，优先从真实源文件机械 CURATE：仅删除显示入口或函数，不重写数学部分；若无法安全分离，停止并记录人工决策，不静默改写。自动 checker 不根据文件名或 import 猜测全部职责；APPENDIX_START 白名单、Codex 语义审查和人工终审承担该边界。

## 根 `code/`：代表性真实实现

根 `code/` 只含直接文件，不引入完整源码树、数据、结果、README、环境文件、日志、测试或绘图文件。允许选择核心模型、求解逻辑、特征/统计/预测、约束核验、参数配置和必要的内存中实验控制；只有不产生提交副作用的计算调度或恢复片段才可展示。

每个 C 条目必须说明源文件、正式流程中的真实职责、提交展示理由、COPY/CURATE 模式、删除的显示/接口部分和保持不变的数学与执行语义。代码不得硬编码最终数值答案，不得改变模型语义、计算顺序、随机性、平局规则、恢复规则或认证边界。

## COPY 与 CURATE

`appendix/` 默认优先 COPY 并保留原相对结构。CURATE 仅用于机械分离显示代码、调整提交所需 import/相对路径、合并少量真实小模块或删除未调用的展示包装；不得删去正式计算依赖、改写算法或恢复写入副作用。

根 `code/` 可 COPY 真实源文件，也可 CURATE 一个或少量真实源文件形成可读片段。可以补充必要注释、类型或入口说明，但不得虚构行为。所有源文件都进入 `source_integrity.csv` 的只读核验；结果资产不因代码 CURATE 而自动重算。

## 真实性、原创性与相似性边界

合理做法是从本队真实正式工程选择具有实现辨识度的代表性代码。禁止复制、改写或拼接其他队伍、网络答案或不合规来源；禁止只为改变相似度乱改变量名、插入无效分支/死代码/垃圾注释、拆乱表达式或控制流、使用混淆器或自动差异工具，以及添加未参与正式流程的“个性化”代码。

目标是准确说明本队如何实现，不是规避查重。不得以“降低查重率”描述任何白名单用途，也不设置外部代码数据库、在线查重、相似度阈值或自动原创性结论。

## 验证、结果、环境与只读规则

所有输出不得含绝对本地路径、用户名路径、凭据、令牌或敏感机器信息。有限策略、受限状态覆盖或有限时域偏离分析不得被表述为全局最优或完整均衡认证。

验证应覆盖核心入口和本地依赖、静态副作用扫描、实际编译/构建（如适用）、独立结果资产与已接受 RESULT 的一致性、COPY 哈希、CURATE 语义边界、绘图/接口排除、根 `code/` 来源真实性、结果唯一性、环境最小化、敏感信息和源文件只读。无法安全分离或无法确认语义等价时停止人工复核。

## 自动 checker 的能力边界

检查器只读且不执行用户代码、不导入用户模块、不运行求解器或编译器。它检查精确白名单、路径、文件类型、结构、COPY 哈希、静态 Python/import、C/C++ include、有限 CMake 字面路径、静态高置信写入 API、XLSX ZIP/XML 基本结构和敏感信息。

检查器不自动判断正式代码覆盖、绘图/接口职责、原创性、外部相似度、CURATE 语义等价、数学正确性、完整动态导入、动态写入包装、完整 CMake、Excel 数值/公式/格式或提交展示质量；这些由执行证据、Codex 语义审查和人工终审承担。
