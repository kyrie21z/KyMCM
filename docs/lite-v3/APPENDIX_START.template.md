# APPENDIX START

## 1. 提交范围与比赛要求

<!-- 说明正式提交要求、附件限制以及 appendix/ 与 code/ 的不同用途。 -->

## 2. 论文引用、正式结果与认证边界

<!-- 列出论文实际引用的结果、唯一正式版本，以及有限策略类或有限时域等认证边界。 -->

## 3. appendix 目标结构

<!-- 冻结 appendix/ 和 code/ 的最终目录结构；不要先复制整个工程。 -->

## 4. appendix 文件白名单

<!-- 每个目标一行；示例仅供格式参考：
- A001 — COPY — `problems/q1/code/solve.py` → `appendix/problems/q1/code/solve.py` — 正式入口
- A002 — CURATE — `problems/q1/code/solve.py`; `problems/q1/code/model.py` → `appendix/problems/q1/code/core.py` — 机械整理
-->
- A090 — GENERATE — `appendix/environment/README.md` — 复现入口说明
- A091 — GENERATE — `appendix/environment/requirements.txt` — 最小依赖清单
- A092 — GENERATE — `appendix/environment/system_info.txt` — 非敏感版本信息

## 5. code 文件白名单

<!-- 每个目标一行；示例仅供格式参考：
- C001 — COPY — `problems/q1/code/core.py` → `code/q1_core_algorithm.py` — 论文后的核心算法
-->

## 6. 依赖闭包与机械裁剪规则

<!-- 说明入口、传递依赖、静态导入/include/CMake 闭包，以及 CURATE 不改变数学语义的边界。 -->

## 7. 环境、外部资料与强制结果文件

外部资料：无

强制结果文件：无

<!-- 如声明 appendix/input，请补充资料来源、用途及不可替代性。 -->

## 8. 验收方法与停止规则

<!-- 说明编译、构建、工作簿、哈希、敏感信息和人工复核方法。 -->

## 9. 未决问题

无
