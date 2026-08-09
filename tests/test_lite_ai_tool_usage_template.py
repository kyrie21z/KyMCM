from __future__ import annotations

import hashlib
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/kymcm-lite"
TEMPLATE = SKILL / "templates/AI_TOOL_USAGE_DETAILS.template.tex"
MIRROR = ROOT / "docs/lite-v3/AI_TOOL_USAGE_DETAILS.template.tex"
DECLARATION = SKILL / "templates/AI_TOOL_USAGE_DECLARATION.template.tex"
DECLARATION_MIRROR = ROOT / "docs/lite-v3/AI_TOOL_USAGE_DECLARATION.template.tex"
REFERENCE = SKILL / "references/ai_tool_usage_details.md"
REFERENCE_MIRROR = ROOT / "docs/lite-v3/ai_tool_usage_details.md"


PROTECTED_HASHES = {
    "skills/kymcm-lite/templates/START_QN.template.md": "4db5837709686701d1d19fbc797567e34b387751c7998beb5a6717784373fc8e",
    "skills/kymcm-lite/templates/RESULT_QN.template.md": "3794e2b24dedbcb816f09d90e01f400078b5fede85296b1d418dc1a1baa96d45",
    "skills/kymcm-lite/templates/START_PRE.template.md": "f8c30249682de75c5b82af525df8c74fe5bde2338bcdd0c0a198c071ae249d3b",
    "skills/kymcm-lite/templates/RESULT_PRE.template.md": "189595bdb36b5ee33a21363e3dfb3fb4faa65309e6a5bed7b0555931f8f8e4c5",
    "skills/kymcm-lite/templates/SUPPLEMENT_START_QN.template.md": "6056e597253f20ef1d45f4b0b3a14753d6724fa1e37767ac72554b6429099c48",
    "skills/kymcm-lite/templates/SUPPLEMENT_RESULT_QN.template.md": "c25364c2b64339f9c4f50009e0c2e11e536a5c8ec49349d8d5f395cdcb5d80c2",
    "skills/kymcm-lite/templates/HANDOFF_QN.template.md": "2495e222fc350934367956d67c0f74f069cab8c2097f3c06cee4f74c04b11014",
    "skills/kymcm-lite/templates/HANDOFF_PRE.template.md": "b486f30425c74dce973b8d55891b284871161e86a54dbec0836d3801d5c387fb",
    "skills/kymcm-lite/references/final_figure_typography.md": "e6ed88bc2ee3f27588a0f4bc1451f0083b1d5365807da4e0d98c15cb97cc6c79",
}


class LiteAIToolUsageTemplateTests(unittest.TestCase):
    def test_canonical_and_mirror_bytes_match(self):
        for canonical, mirror in (
            (REFERENCE, REFERENCE_MIRROR),
            (TEMPLATE, MIRROR),
            (DECLARATION, DECLARATION_MIRROR),
        ):
            self.assertEqual(canonical.read_bytes(), mirror.read_bytes(), canonical.name)

    def test_pdf_template_has_exact_fixed_structure(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        self.assertIn(r"\documentclass[UTF8,fontset=fandol,12pt,a4paper]{ctexart}", text)
        self.assertIn(r"\title{AI 工具使用详情}", text)
        self.assertIn(r"\author{}", text)
        self.assertIn(r"\date{}", text)
        self.assertEqual(
            re.findall(r"\\section\{([^{}]+)\}", text),
            [
                "AI 工具清单",
                "具体使用目的和环节",
                "主要提示方式与使用过程",
                "AI 输出的采纳、修改与核验情况",
                "总体声明",
            ],
        )
        self.assertNotIn("基本信息", text)

    def test_tool_table_and_fixed_models_are_frozen(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        self.assertEqual(text.count("工具名称 & 版本或模型"), 1)
        for forbidden in ("使用方式", "主要用途", "备注"):
            self.assertNotIn(forbidden, text)
        self.assertIn("ChatGPT & GPT-5.6 Thinking", text)
        self.assertIn("Codex CLI & GPT-5.6 Codex", text)

    def test_fixed_prose_covers_required_categories_and_responsibility(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        for required in (
            "赛题理解", "建模方案讨论", "合理性检查", "程序实现与调试", "结果检查",
            "论文表达优化", "模型选择", "数学假设", "参数设定", "计算执行",
            "结果判断", "最终结论", "自然语言指令", "任务分解", "多轮交互",
            "数据说明", "代码片段", "补充约束", "纠正理解", "要求修改",
            "人工审查", "实际运行和必要测试", "约束检查", "边界检查",
            "数量级和数值合理性", "对照核验", "人工修改和定稿", "承担全部责任",
        ):
            self.assertIn(required, text, required)

    def test_exactly_two_real_screenshot_targets_and_captions(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        self.assertEqual(text.count(r"\includegraphics"), 2)
        self.assertEqual(text.count("figures/chatgpt_example.png"), 2)
        self.assertEqual(text.count("figures/codex_example.png"), 2)
        self.assertIn(r"\captionof{figure}{图 1：ChatGPT 典型交互示例}", text)
        self.assertIn(r"\captionof{figure}{图 2：Codex CLI 典型交互示例}", text)
        self.assertIn("keepaspectratio", text)

    def test_missing_images_fail_closed(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        self.assertEqual(text.count(r"\IfFileExists"), 2)
        self.assertEqual(text.count(r"\PackageError"), 2)
        self.assertIn("缺少必需的真实交互截图", text)

    def test_template_has_no_contest_identity_or_editable_placeholder(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        self.assertIsNone(re.search(r"20\d{2}", text))
        for forbidden in (
            "TODO", "PLACEHOLDER", "占位框", "请在此", "队号", "队伍名称",
            "赛题名称", "参赛日期", "\\texttt{<", "<队",
        ):
            self.assertNotIn(forbidden, text, forbidden)

    def test_declaration_snippet_is_exact_and_non_numbered(self):
        text = DECLARATION.read_text(encoding="utf-8")
        self.assertEqual(text.count(r"\section*{AI 工具使用声明}"), 1)
        self.assertNotIn(r"\section{", text)
        self.assertIn(
            "本参赛队在竞赛过程中使用了 AI 工具，主要用于赛题理解、建模方案讨论、代码实现与调试、结果核验及语言表达优化，详细使用情况见支撑材料。",
            text,
        )

    def test_reference_freezes_process_boundaries_and_output_name(self):
        text = REFERENCE.read_text(encoding="utf-8")
        for required in (
            "2026 年试行", "AI 工具使用详情.pdf", "五节", "基本信息",
            "工具名称", "版本或模型", "ChatGPT", "GPT-5.6 Thinking",
            "Codex CLI", "GPT-5.6 Codex", "只替换两张真实截图",
            "figures/chatgpt_example.png", "figures/codex_example.png",
            "图 1：ChatGPT 典型交互示例", "图 2：Codex CLI 典型交互示例",
            "真实交互", "敏感信息", "xelatex -interaction=nonstopmode -halt-on-error",
            "参考文献之前", "RESULT", "HANDOFF", "Appendix", "figure/",
            "不新增 CLI、checker、diagnostic、state、JSON、manifest 或 approval",
            "工具或模型发生变化时", "不能提交不实材料",
        ):
            self.assertIn(required, text, required)

    def test_no_runtime_api_or_generated_material_was_added(self):
        combined = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (
                SKILL / "SKILL.md", SKILL / "docs/protocol.md", REFERENCE,
                SKILL / "references/machine_contract.md",
            )
        )
        self.assertNotIn("check-ai-usage", combined)
        self.assertNotIn("ai_usage_state", combined)
        self.assertNotIn("AI_TOOL_USAGE_MANIFEST", combined)
        for relative in (
            "AI 工具使用详情.pdf", "AI_TOOL_USAGE_DETAILS.aux", "AI_TOOL_USAGE_DETAILS.log",
            "AI_TOOL_USAGE_DETAILS.out", "AI_TOOL_USAGE_DETAILS.toc",
        ):
            self.assertFalse(any(path.name == relative for path in ROOT.rglob(relative)))

    def test_version_and_protected_lite_surfaces(self):
        self.assertEqual((SKILL / "VERSION").read_bytes(), b"0.9.6\n")
        for relative, expected in PROTECTED_HASHES.items():
            actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            self.assertEqual(actual, expected, relative)
        full_files = list((ROOT / "skills/kymcm-full").rglob("*"))
        self.assertTrue(full_files)
        self.assertFalse(any(path.is_file() and "AI_TOOL_USAGE" in path.name for path in full_files))


if __name__ == "__main__":
    unittest.main()
