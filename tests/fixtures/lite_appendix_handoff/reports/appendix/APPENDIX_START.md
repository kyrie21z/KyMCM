# APPENDIX START

## 1. 提交范围与比赛要求

提交最小复现附件和论文后的核心算法。

## 2. 论文引用、正式结果与认证边界

q1 的 formal.csv 是唯一正式结果；结论仅覆盖有限策略类。

## 3. appendix 目标结构

按白名单构造 q1 Python、q2 C++、正式结果和最小环境。

## 4. appendix 文件白名单

- A001 — COPY — `problems/q1/code/solve.py` → `appendix/problems/q1/code/solve.py` — Python 正式入口
- A002 — COPY — `problems/q1/code/helper.py` → `appendix/problems/q1/code/helper.py` — Python 本地依赖
- A003 — COPY — `problems/q1/outputs/formal.csv` → `appendix/problems/q1/result/formal.csv` — 唯一正式结果
- A004 — COPY — `problems/q2/code/solver.cpp` → `appendix/problems/q2/code/solver.cpp` — C++ 正式入口
- A005 — COPY — `problems/q2/code/solver.hpp` → `appendix/problems/q2/code/solver.hpp` — C++ 本地头文件
- A090 — GENERATE — `appendix/environment/README.md` — 复现入口说明
- A091 — GENERATE — `appendix/environment/requirements.txt` — 最小依赖清单
- A092 — GENERATE — `appendix/environment/system_info.txt` — 非敏感版本信息

## 5. code 文件白名单

- C001 — COPY — `problems/q1/code/core.py` → `code/q1_core_algorithm.py` — q1 核心算法
- C002 — COPY — `problems/q2/code/solver.cpp` → `code/q2_core_algorithm.cpp` — q2 核心算法实现
- C003 — COPY — `problems/q2/code/solver.hpp` → `code/solver.hpp` — q2 核心算法头文件

## 6. 依赖闭包与机械裁剪规则

保留 Python 本地模块与 C++ 引用头文件；不改变计算顺序、规则或认证边界。

## 7. 环境、外部资料与强制结果文件

外部资料：无

强制结果文件：无

## 8. 验收方法与停止规则

执行静态语法、编译、COPY 哈希、敏感信息和源文件完整性验证；歧义交人工复核。

## 9. 未决问题

无
