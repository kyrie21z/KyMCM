from __future__ import annotations

import hashlib
from pathlib import Path
import re
import shutil
import struct
import subprocess
import tempfile
import zlib
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
    "skills/kymcm-lite/references/final_figure_typography.md": "7399a5545ded173ad12543b6d155ceb9ee233ce42c0c76e7c3bec03c5e48ee21",
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

    def test_editable_facts_and_scoped_tool_table(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        table = text.split(r"\begin{tabular}", 1)[1].split(r"\end{tabular}", 1)[0]
        rows = [line for line in table.splitlines() if "&" in line]
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(line.count("&") == 1 for line in rows))
        self.assertIn("【待填：实际工具】", table)
        self.assertNotIn("GPT-", table)
        body = text.split(r"\begin{document}", 1)[1]
        for field in ("使用工具及具体目的", "参赛队承担的关键判断", "案例 A", "案例 B",
                      "采纳范围与具体修改/未采纳理由", "核验方式及结果", "剩余限制"):
            self.assertIn(field, body)
        active = "\n".join(line for line in body.splitlines() if not line.startswith("%"))
        self.assertEqual(active.count(r"\AIUsageScreenshot{"), 3)
        self.assertNotIn(r"\includegraphics", active)
        self.assertNotIn(r"\clearpage", active)

    def test_declaration_keeps_official_frame_and_editable_purpose(self):
        text = DECLARATION.read_text(encoding="utf-8")
        self.assertEqual(text.count(r"\section*{AI 工具使用声明}"), 1)
        self.assertNotIn(r"\section{", text)
        self.assertRegex(text, r"本参赛队在竞赛过程中使用了 AI 工具，主要用于【待填：[^】]+】，详细使用情况见支撑材料。")

    def test_reference_preserves_factual_and_submission_boundaries(self):
        text = REFERENCE.read_text(encoding="utf-8")
        for required in (
            "五节", "工具名称", "版本或模型", "概述", "原记录", "AI 首先提出",
            "不能单凭最终成果", "比赛前后", "最多 5 张", "不是官方配额",
            "人工", "不替代", "必要核验", "参考文献之前", "COPY",
            "reports/ai-usage/AI 工具使用详情.pdf", "appendix/AI 工具使用详情.pdf",
            "xelatex -interaction=nonstopmode -halt-on-error", "无需新的 Skill 版本",
        ):
            self.assertIn(required, text)
        for obsolete in ("只替换两张真实截图", "GPT-5.6", "正文不可改"):
            self.assertNotIn(obsolete, text)

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

    def test_ai_usage_precedes_appendix_and_only_frozen_pdf_is_copyable(self):
        skill_text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        protocol = (SKILL / "docs/protocol.md").read_text(encoding="utf-8")
        machine = (SKILL / "references/machine_contract.md").read_text(encoding="utf-8")
        appendix_start = (SKILL / "templates/APPENDIX_START.template.md").read_text(
            encoding="utf-8"
        )
        for text in (skill_text, protocol):
            self.assertLess(
                text.index("## Final submission AI tool usage details"),
                text.index("## Optional submission appendix organization"),
            )
            self.assertNotIn("Appendix organization is stable", text)
            self.assertNotIn("Appendix 稳定之后", text)
        for required in (
            "reports/ai-usage/AI 工具使用详情.pdf",
            "appendix/AI 工具使用详情.pdf",
            "sole\nreports exception",
            "COPY-only",
            ".xlsx", ".csv", ".txt",
            "legacy contract shape",
        ):
            self.assertIn(required, machine, required)
        self.assertIn(
            "AI 工具使用详情：`appendix/AI 工具使用详情.pdf`", appendix_start
        )
        self.assertIn("- A093 — COPY — `reports/ai-usage/AI 工具使用详情.pdf`", appendix_start)
        self.assertNotIn("A093 — CURATE", appendix_start)
        self.assertNotIn("A093 — GENERATE", appendix_start)

    def test_version_and_protected_lite_surfaces(self):
        self.assertEqual((SKILL / "VERSION").read_bytes(), b"1.0.0\n")
        for relative, expected in PROTECTED_HASHES.items():
            actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            self.assertEqual(actual, expected, relative)
        full_files = list((ROOT / "skills/kymcm-full").rglob("*"))
        self.assertTrue(full_files)
        self.assertFalse(any(path.is_file() and "AI_TOOL_USAGE" in path.name for path in full_files))


def write_test_image(path, portrait=False):
    """Dependency-free PNG with visibly synthetic TEST ONLY text, never a chat UI."""
    width, height = (600, 800) if portrait else (1000, 400)
    glyphs = {
        "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
        "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
        "S": ("11111", "10000", "10000", "11111", "00001", "00001", "11111"),
        "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
        "N": ("10001", "11001", "11001", "10101", "10011", "10011", "10001"),
        "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
        "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
        " ": ("00000",) * 7,
    }
    scale = 8
    pixels = bytearray(b"\xf2\xf5\xf8" * width * height)
    for top in range(30, height - 60, 100):
        for index, char in enumerate("TEST ONLY"):
            for y, row in enumerate(glyphs[char]):
                for x, bit in enumerate(row):
                    if bit == "1":
                        for dy in range(scale):
                            for dx in range(scale):
                                pos = ((top + y * scale + dy) * width + 30 + index * 6 * scale + x * scale + dx) * 3
                                pixels[pos:pos + 3] = b"\x20\x35\x50"
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
    raw = b"".join(b"\0" + pixels[y * width * 3:(y + 1) * width * 3] for y in range(height))
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">2I5B", width, height, 8, 2, 0, 0, 0))
                     + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


def prepare_build_fixture(directory, count):
    """Fill the actual template with explicitly synthetic layout-test data."""
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "figures").mkdir(exist_ok=True)
    text = TEMPLATE.read_text(encoding="utf-8")
    text = re.sub(r"【待填：[^】]*】", "仅用于排版测试：此处为合成测试数据，不是参赛事实。", text)
    text = text.replace("仅用于排版测试：此处为合成测试数据，不是参赛事实。 & 仅用于排版测试：此处为合成测试数据，不是参赛事实。",
                        "Test Tool & Model Z 42", 1)
    # Exercise long wrapping Chinese cells without altering the table structure.
    text = text.replace("仅用于排版测试：此处为合成测试数据，不是参赛事实。",
                        "仅用于排版测试：使用合成数据检查较长中文说明的自动换行、表格边界及编号；这不是实际比赛记录。")
    if count == 2:
        text = re.sub(r"^\\AIUsageScreenshot\{figures/interaction_03.png\}.*\n", "", text, flags=re.M)
        text = text.replace("、图~\\ref{fig:ai-3}", "")
    if count > 3:
        extra = "\n".join(
            rf"\AIUsageScreenshot{{figures/interaction_{i:02d}.png}}{{案例 B：TEST ONLY 补充版面测试 {i}}}"
            rf"见图~\ref{{fig:ai-{i}}}。"
            for i in range(4, count + 1)
        )
        text = text.replace(r"\section{AI 输出的采纳、修改与核验情况}",
                            extra + "\n" + r"\section{AI 输出的采纳、修改与核验情况}")
    for i in range(1, count + 1):
        write_test_image(directory / f"figures/interaction_{i:02d}.png", portrait=i % 2 == 0)
    (directory / "AI_TOOL_USAGE_DETAILS.tex").write_text(text, encoding="utf-8")
    return text


def compile_fixture(directory):
    return subprocess.run(
        ["xelatex", "-interaction=nonstopmode", "-halt-on-error",
         "-jobname=AI 工具使用详情", "AI_TOOL_USAGE_DETAILS.tex"],
        cwd=directory, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=90,
    )


@unittest.skipUnless(shutil.which("xelatex"), "optional XeLaTeX build dependency unavailable")
class LiteAIUsageLatexBuildTests(unittest.TestCase):
    def test_two_three_five_images_and_resolved_references(self):
        for count in (2, 3, 5):
            with self.subTest(count=count), tempfile.TemporaryDirectory(prefix="kymcm-ai-usage-") as tmp:
                directory = Path(tmp)
                prepare_build_fixture(directory, count)
                for _ in range(2):
                    result = compile_fixture(directory)
                    self.assertEqual(result.returncode, 0, result.stdout[-6000:])
                self.assertTrue((directory / "AI 工具使用详情.pdf").is_file())
                self.assertNotIn("undefined", result.stdout)
                self.assertNotIn("Overfull", result.stdout)
                aux = (directory / "AI 工具使用详情.aux").read_text(encoding="utf-8")
                for i in range(1, count + 1):
                    self.assertIn(rf"\newlabel{{fig:ai-{i}}}{{{{{i}}}", aux)
                if shutil.which("pdftotext"):
                    extracted = subprocess.check_output(
                        ["pdftotext", "AI 工具使用详情.pdf", "-"], cwd=directory, text=True
                    )
                    self.assertNotIn("待填", extracted)
                    self.assertNotIn("??", extracted)
                    self.assertIn("Model Z 42", extracted)
                    self.assertIn("总体声明", extracted)

    def test_sixth_image_missing_image_and_empty_caption_fail(self):
        for failure, expected in (
            ("sixth", "At most 5 screenshots allowed"),
            ("missing", "Missing screenshot"),
            ("caption", "Empty screenshot caption"),
        ):
            with self.subTest(failure=failure), tempfile.TemporaryDirectory(prefix="kymcm-ai-usage-") as tmp:
                directory = Path(tmp)
                text = prepare_build_fixture(directory, 6 if failure == "sixth" else 2)
                if failure == "missing":
                    (directory / "figures/interaction_01.png").unlink()
                elif failure == "caption":
                    text = re.sub(r"(\\AIUsageScreenshot\{figures/interaction_01.png\})\{[^}]*\}",
                                  r"\1{}", text)
                    (directory / "AI_TOOL_USAGE_DETAILS.tex").write_text(text, encoding="utf-8")
                result = compile_fixture(directory)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected, result.stdout)


if __name__ == "__main__":
    unittest.main()
