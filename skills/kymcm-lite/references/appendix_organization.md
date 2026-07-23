# KyMCM Lite 附录整理规范

附录整理是建模完成后的可选独立阶段。`appendix/` 是随作品提交的最小复现与正式结果附件，根 `code/` 是论文正文后的精简核心算法附录；二者用途不同、互不替代。唯一正式计划是 `reports/appendix/APPENDIX_START.md`，唯一执行报告是 `reports/appendix/APPENDIX_RESULT.md`。

The modeling workflow has no FROZEN_CONTEXT surface. Appendix organization may reference START and RESULT only.

## 基本原则

1. 先冻结结构和白名单，再从白名单正向构造，禁止先复制整个工程再反向删除。
2. 只保留审稿验证所需的最小充分集合；依赖闭包优先于表面文件数最少。
3. `problems/`、`input/`、`paper/` 以及正式 START/RESULT 始终只读；复制、裁剪、重命名和机械清理仅发生在 `appendix/`、`code/` 与 `reports/appendix/evidence/`。
4. 建模工作流没有 FROZEN_CONTEXT surface；START_QN 和 RESULT_QN 只能作为上下文参考，不能授权或扩展最终包。
5. 不引入附录状态机、审批对象、事件日志、哈希对象、内容 JSON 或持久化清单。

## `appendix/`

`appendix/problems/qN/` 只能有 `code/` 和 `result/` 后代。代码保留正式入口和传递运行/构建依赖，排除测试、缓存、历史实现、调试、资源监控及内部桥接代码。结果只保留最终策略、代表性或最坏轨迹、核心汇总表和必要证书，排除 RESULT Markdown、日志、manifest、checkpoint、阶段账本、内部审计报告和可重建中间文件。

每项结论只保留一个正式结果版本，禁止重复 Excel 或结果副本。比赛强制的 `Result.xlsx`（如适用）只能在 `appendix/Result.xlsx` 出现一次，沿用官方模板、数值一致，并接受 COPY 哈希和基本可打开性检查。

`appendix/environment/` 只能包含 `README.md`、`requirements.txt` 与 `system_info.txt`。`appendix/input/` 仅在确实使用了审稿人无法取得且验证必需的非标准外部资料时存在，绝不创建空目录。

## 根 `code/`

根 `code/` 只含直接位于该目录的精简核心算法文件。不得包含 README、结果、环境文件、调度、日志、绘图、数据导出、测试、后端或完整源码树。核心代码不得硬编码最终数值答案，也不得改变模型语义、计算顺序、平局规则或认证边界。

## 验证与表述

所有输出不得含绝对本地路径、用户名路径、凭据、令牌或敏感机器信息。部分验证、有限策略类、受限状态覆盖或有限时域偏离分析不得被表述为全局最优或完整均衡认证。

检查器只读且不执行用户代码、不导入用户模块、不运行求解器或编译器。它可计算哈希、静态解析 Python/import、C/C++ include 与有限的 CMake 字面路径，并检查 XLSX ZIP/XML 基本结构。实际编译、构建、依赖准确性、工作簿数值/格式和数学正确性由 Codex 执行证据与人工终审承担。

语义等价、数学正确性、完整动态导入解析、完整 CMake 解释、Excel 公式/值/合并单元格/格式语义验证均不在自动检查范围。
