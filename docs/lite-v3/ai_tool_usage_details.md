# AI 工具使用详情

KyMCM Lite 0.9.7 提供本参考文档和固定 LaTeX 模板，用于落实《人工智能工具使用规定（2026 年试行）》对参赛作品支撑材料的要求。该要求适用于 2026 年竞赛试行阶段：凡在竞赛过程中使用 AI 工具，支撑材料应包含一个 PDF，文件名必须精确为 `AI 工具使用详情.pdf`；论文参考文献之前还应放置固定的“AI 工具使用声明”。

## 固定内容

模板正文固定为以下五节，不含“基本信息”节：

1. AI 工具清单；
2. 具体使用目的和环节；
3. 主要提示方式与使用过程；
4. AI 输出的采纳、修改与核验情况；
5. 总体声明。

工具表固定为两列，表头只有“工具名称”和“版本或模型”，当前固定两行为：

| 工具名称 | 版本或模型 |
|---|---|
| ChatGPT | GPT-5.6 Thinking |
| Codex CLI | GPT-5.6 Codex |

固定正文覆盖赛题理解、建模方案讨论和合理性检查、程序实现与调试、结果检查、论文表达优化，并明确模型选择、假设、参数、计算、结果判断和最终结论由参赛队主导。采纳、修改和核验段落只作保守的人工审查、实际运行、必要测试、约束/边界/数量级/数值合理性和对照核验说明，不替参赛队虚构未执行的实验。

## 每场比赛只替换两张真实截图

比赛工作区建议使用以下目录：

```text
reports/ai-usage/
├── AI_TOOL_USAGE_DETAILS.tex
├── figures/
│   ├── chatgpt_example.png
│   └── codex_example.png
└── AI 工具使用详情.pdf
```

从 `skills/kymcm-lite/templates/AI_TOOL_USAGE_DETAILS.template.tex` 复制 `.tex` 后，每场比赛只替换两张真实截图，路径和图注固定为：

| 文件 | 固定图注 |
|---|---|
| `figures/chatgpt_example.png` | 图 1：ChatGPT 典型交互示例 |
| `figures/codex_example.png` | 图 2：Codex CLI 典型交互示例 |

截图必须来自本次比赛的真实交互，能看到具有代表性的提示和 AI 响应上下文；不得使用历史比赛截图、占位图、AI 生成的伪截图或重构文本。可以裁剪或遮盖账号、邮箱、令牌、绝对路径等敏感信息，但不得裁剪掉会改变使用性质的关键上下文。模板在任一图片缺失时通过明确的 LaTeX 错误失败，不会生成占位框或静默跳过。

## 编译和检查

XeLaTeX/TeX Live 是最终合规材料的可选构建依赖，不是 Lite Python runtime 的依赖。模板使用 `ctexart`、A4、12pt、`fontset=fandol`，不下载网络资源，也不打包字体文件。推荐执行：

```bash
mkdir -p reports/ai-usage/figures
cp skills/kymcm-lite/templates/AI_TOOL_USAGE_DETAILS.template.tex \
  reports/ai-usage/AI_TOOL_USAGE_DETAILS.tex

# 放入两张本次比赛的真实截图，不要使用合成图或占位图。
# reports/ai-usage/figures/chatgpt_example.png
# reports/ai-usage/figures/codex_example.png

cd reports/ai-usage
xelatex -interaction=nonstopmode -halt-on-error \
  -jobname="AI 工具使用详情" AI_TOOL_USAGE_DETAILS.tex
xelatex -interaction=nonstopmode -halt-on-error \
  -jobname="AI 工具使用详情" AI_TOOL_USAGE_DETAILS.tex
```

必须确认输出文件精确为 `reports/ai-usage/AI 工具使用详情.pdf`。用可用的 PDF 文本和渲染工具检查五个节标题、两项工具、两张图和声明内容，确认没有裁切、越界、黑块、乱码或重叠。最终支撑材料通常只提交该 PDF；`.aux`、`.log`、`.out`、`.toc` 等 LaTeX 中间文件不应提交，除非竞赛另有要求。

论文正文在参考文献之前直接插入 `skills/kymcm-lite/templates/AI_TOOL_USAGE_DECLARATION.template.tex` 的非编号节。该片段只提供固定声明和位置，不自动修改 `paper/`，不绑定 Full renderer，也不新增论文生成命令。

## 边界、真实性和版本更新

AI 工具使用详情是最终提交合规材料阶段，顺序上位于正式 RESULT/Supplement 已完成并接受、必要 HANDOFF 完成、Appendix 稳定之后。它不是数学建模执行、RESULT、HANDOFF、Appendix 计算核心、`figure/` final figure 工作区、evidence 或后续问题依赖；`reports/ai-usage/` 不进入 Appendix whitelist、RESULT evidence 或 root `code/`。

使用 KyMCM Lite 本身属于 AI 工具使用，因此应按实际情况准备声明和 PDF。但 Lite runtime 不读取截图或聊天记录，不自动生成 PDF，不判断声明真实性，不从 RESULT、HANDOFF 或历史对话推断内容，也不新增 CLI、checker、diagnostic、state、JSON、manifest 或 approval。模板正文由文档和 release tests 冻结，LaTeX 编译与视觉验收由执行者负责。

当前固定正文绑定 ChatGPT/GPT-5.6 Thinking 与 Codex CLI/GPT-5.6 Codex。工具或模型发生变化时，必须在新的 KyMCM Lite 版本中集中更新 canonical template 和 mirror；不得在比赛工作区临时改写固定正文。固定正文仍必须与实际使用过程一致；若真实过程偏离固定声明，应停止套用模板，由用户决定是否修改产品级模板，不能提交不实材料。真实性、截图代表性、隐私遮盖和最终合规性始终需要参赛队人工审查。
