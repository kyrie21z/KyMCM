# APPENDIX START

## 1. 提交范围与比赛要求

<!-- 说明当届比赛提交要求、容量和附件限制。根 code/ 为真实代码选录，不要求独立运行；appendix/ 保留最小完整运行包和冻结结果。展示规则不是完整提交合规结论，最终覆盖范围按明确要求核对。 -->

## 2. 正式结果与认证边界

<!-- 按顺序列出基础 RESULT、已接受 Supplement Result、当前 HANDOFF、有效数据产品、机器证据和独立正式结果附件及认证边界。内部合同只作上下文，不复制；AI PDF 在 Appendix 前完成并冻结。 -->

## 3. appendix 目标结构

<!-- 冻结 appendix/problems/{preprocess,qN}/{code,result}/、现有 environment/、按需 input/ 与根 code/ 代表性直接文件。白名单正向构造，保留必要相对结构；运行从临时副本进行，本次结果只写独立工作目录。 -->

## 4. appendix 文件白名单

<!-- 覆盖正式路线实际需要的预处理、模型、求解、约束核验、Python 调度、C/C++ 源码/头文件/构建配置、输入解析和科学结果导出。必要 CSV/XLSX writer、受控输出和 checkpoint API 不因写入被删除；实际缓存是否打包按输入起点判断。排除 Explore、废弃历史、无关内部报告、凭据和重复正式结果。示例仅供格式参考：
- A001 — COPY — `problems/q1/code/solve.py` → `appendix/problems/q1/code/solve.py` — 真实求解、调度和科学结果导出入口
- A002 — COPY — `problems/q1/outputs/formal.csv` → `appendix/problems/q1/result/formal.csv` — 已接受比较基准，只读且不被本次运行覆盖
- A003 — CURATE — `problems/q1/code/model.py` → `appendix/problems/q1/code/model.py` — 披露必要相对路径调整，数学语义不变并复验
PRE code 来自 `problems/preprocess/code/`；result 可来自允许的 data/derived、outputs 和非合同 notes。声明的根结果保持唯一根副本，不再重复嵌套。科学配置/数据与工作流 state/manifest JSON 区分；映射缺口先报告，不开放任意路径。 -->
- A093 — COPY — `reports/ai-usage/AI 工具使用详情.pdf` → `appendix/AI 工具使用详情.pdf` — 已完成并人工验收的 AI 工具使用详情提交附件
- A090 — GENERATE — `appendix/environment/README.md` — 复现入口说明
- A091 — GENERATE — `appendix/environment/requirements.txt` — 最小依赖清单
- A092 — GENERATE — `appendix/environment/system_info.txt` — 非敏感版本信息

## 5. code 文件白名单

<!-- 选取本队当前有效正式源码中的状态、目标/约束、候选构造、剪枝、阶段控制、融合与核验等代表性真实代码。调度按职责选择，不强制零写入、最短或每问配额。每项写明源文件、函数/行范围、职责、展示理由、COPY/CURATE 与省略范围，不另写附录版算法、不为相似度混淆变量。示例：
- C001 — CURATE — `problems/q1/code/model.py` → `code/q1_model_core.py` — 完整函数 solve 的忠实选录；省略 import 和 CLI，不宣称独立运行
 -->

## 6. 依赖闭包与机械裁剪规则

<!-- A 类要求必要依赖和完整执行链；C 类展示选录不要求独立语法、依赖闭包、编译或运行，非连续片段分别标明。每个 CURATE 条目必须记录来源/范围、保留职责、具体省略或路径/入口适配、保持不变的数学、数据和执行语义。必要写入保留，无关绘图/文案分离；涉及算法、执行顺序、随机性、平局规则或成功标准的变化先回正式流程。论文排版直接引用选录文件，不手工另维一套源码。 -->

## 7. 环境、外部资料与强制结果文件

AI 工具使用详情：`appendix/AI 工具使用详情.pdf`

外部资料：无

强制结果文件：无

<!-- 环境 README 写清运行顺序、精确输入身份及获取/放置方式、依赖/编译器、构建/入口命令、独立输出目录、复现起点、预计预算和比较标准。官方输入可依规则不重复打包；appendix/input 的既有外部资料声明补充来源、用途及不可替代性。冻结候选/权重或上游结果若作为输入，标明其身份及生成路线，不把固定产物复算称为从原始输入求解。强制结果文件可声明一个或多个以英文逗号加空格分隔的根目标，例如 `appendix/Result.xlsx`, `appendix/Q2_result.csv`；每项须有唯一 COPY 条目。 -->

## 8. 验收方法与停止规则

<!-- 执行前写清：起点/输入 → 命令与范围 → 预算 → 预期关键结果和容差 → 停止条件。正常成本默认完整复跑一次；高成本可事先约定完整构建＋真实入口短程运行＋冻结候选/模型的正式精度结果复算，分别记录，完整搜索/训练未重跑不得称完整端到端通过。拟提交包从隔离副本构建运行，清除项目 PYTHONPATH 等未声明依赖；Python+C++ 必须实际构建和调用，不只语法检查。只写指定工作目录，原始源、输入和冻结附件保持只读并核对完整性；临时目录不是操作系统安全沙箱。COPY 用哈希，重新运行按预先标准比较 ID/数量、数值容差、约束/排序和 CSV/XLSX 字段/公式/格式；不看结果后放宽。纯打包问题最小修复并重跑，计算/约束/版本/算法问题回 START/Supplement；必需验收预算不足即未完成。完成约定范围与比较、无未声明依赖且源/基准未变即停止。证据复用 reports/appendix/evidence/，不新建复现合同或状态。 -->

## 9. 未决问题

无
