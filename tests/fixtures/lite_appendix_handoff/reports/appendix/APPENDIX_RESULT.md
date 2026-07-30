# APPENDIX RESULT

## 1. 最终交付结构

appendix/ 包含两题复现代码、q1 正式结果和环境文件；code/ 包含两题核心算法。

## 2. 实际整理方案与 APPENDIX_START 偏差

无偏差

## 3. 白名单执行结果

A001、A002、A003、A004、A005、A090、A091、A092、C001、C002、C003 均已按计划完成。

## 4. 依赖闭包与编译构建验证

Python 静态编译和 C++ 构建均通过，本地依赖闭包完整。

## 5. 正式结果一致性

formal.csv 是唯一正式结果附件，结论限于有限策略类。

## 6. 强制结果文件核验

不适用；比赛不要求根 Result.xlsx。

## 7. 排除项与敏感信息扫描

未发现缓存、日志、重复结果、绝对路径或凭据。

## 8. 原始工程只读验证

source_integrity.csv 记录整理前后源文件哈希相同；该记录由执行方提供，不是独立密码学时间戳。

## 9. 证据索引

- E1 — `reports/appendix/evidence/source_integrity.csv` — 原始工程前后 SHA-256 完整性记录
- E2 — `reports/appendix/evidence/python_compile.txt` — Python 编译验证
- E3 — `reports/appendix/evidence/native_build.txt` — C++ 构建验证

## 10. 局限性与人工复核事项

数学正确性、不同结果的语义等价和动态依赖仍需人工终审。
