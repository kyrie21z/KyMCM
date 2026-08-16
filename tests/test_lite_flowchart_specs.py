from __future__ import annotations

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/kymcm-lite"
REFERENCES = SKILL / "references"
MIRRORS = ROOT / "docs/lite-v3"


class LiteFlowchartSpecTests(unittest.TestCase):
    def setUp(self):
        self.selection = (REFERENCES / "kymcm-flowchart-selection-v1.md").read_text(encoding="utf-8")
        self.content = (REFERENCES / "kymcm-flowchart-content-v1.md").read_text(encoding="utf-8")

    def test_canonical_mirrors_are_byte_identical(self):
        for name in ("kymcm-flowchart-selection-v1.md", "kymcm-flowchart-content-v1.md"):
            self.assertEqual((REFERENCES / name).read_bytes(), (MIRRORS / name).read_bytes(), name)

    def test_corrected_global_line_census_is_frozen(self):
        for required in ("68.0%", "19.6%", "12.4%", "median = 1", "Q3 = 2", "P90 = 3"):
            self.assertIn(required, self.content, required)
        for superseded in ("63.5%", "24.7%", "11.8%"):
            self.assertNotIn(superseded, self.content, superseded)
        self.assertIn("普通节点优先 1–2 行", self.content)
        self.assertIn("multiline-density-review", self.content)

    def test_selection_is_complete_long_form(self):
        self.assertGreaterEqual(len(self.selection.splitlines()), 900)
        for heading in (
            "## 0. 规范依据与证据边界",
            "# 1. 规范目标",
            "# 2. 核心原则：最低充分结构复杂度",
            "# 3. 流程图资格门槛",
            "# 4. 第一层选择：Macro vs Algorithm",
            "# 5. Macro 类型体系 M1–M6",
            "# 6. Algorithm 类型体系 A1–A6",
            "# 7. 规范化选择决策树",
            "# 8. 类型冲突时的优先级规则",
            "# 9. 类型升级 / 降级规则",
            "# 10. 类型与 Layout 必须解耦",
            "# 11. 当前不冻结的内容与 human-owned 边界",
            "# 12. Agent 选择输出格式",
            "# 13. 验收清单",
            "# 14. Evidence Summary",
            "# 15. v1 冻结结论",
        ):
            self.assertIn(heading, self.selection, heading)
        self.assertEqual(len(re.findall(r"(?m)^## M[1-6]\b", self.selection)), 6)
        self.assertEqual(len(re.findall(r"(?m)^## A[1-6]\b", self.selection)), 6)

    def test_selection_evidence_conflicts_and_transitions_are_frozen(self):
        for required in (
            "Macro / 宏观、高层过程：**40 幅**",
            "Algorithm / 算法、可执行过程：**33 幅**",
            "并行结构：**30/40 = 75.0%**",
            "汇聚：**33/40 = 82.5%**",
            "主阅读方向为 TB（Top-to-Bottom）：**25/33 = 75.8%**",
            "判定：**27/33 = 81.8%**",
            "循环/回边：**24/33 = 72.7%**",
            "仅有 **2 幅明显 serpentine**",
            "## 8.1 Macro 冲突",
            "## 8.2 Algorithm 冲突",
            "## 9.1 升级",
            "## 9.2 降级",
            "layout_status: human-owned / pending-human",
            "ChatGPT/Codex 在产出语义节点、边、分支和内容计划后停止",
        ):
            self.assertIn(required, self.selection, required)
        for required in ("A5 并行子算法：**1 幅**", "A6 密集判定/调度网络：**3 幅**"):
            self.assertIn(required, self.selection, required)

    def test_content_is_complete_long_form(self):
        self.assertGreaterEqual(len(self.content.splitlines()), 550)
        for heading in (
            "# 0. 职责边界",
            "# 1. Evidence Base",
            "# 2. 规范语言",
            "# 3. Evidence Strength",
            "# 4. 核心原则",
            "# 5. 字数与行数口径",
            "# 6. 跨类型节点角色规范",
            "# 7. 类型统计总表",
            "# 8. Type-Specific Profiles",
            "# 9. Overload Detection",
            "# 10. 过载重构决策树",
            "# 11. Stage / Subprocess / 拆图准入",
            "# 12. Agent Content Contract",
            "# 13. 验收清单",
            "# 14. Machine-Safe Policy Object",
            "# 15. 不设置统一 Hard Max",
            "# 16. 与 human-owned 最终布局 / 绘制的接口",
            "# 17. v1 冻结结论",
        ):
            self.assertIn(heading, self.content, heading)
        self.assertEqual(len(re.findall(r"(?m)^## M[1-6]\b", self.content)), 6)
        self.assertEqual(len(re.findall(r"(?m)^## A[1-6]\b", self.content)), 6)

    def test_content_evidence_language_and_pooled_statistics_are_frozen(self):
        for required in (
            "固定样本：73 幅",
            "普通节点：747",
            "Container title：18",
            "可测文本节点：726",
            "21 个节点因无标签或无法可靠辨认",
            "high 58 / medium 13 / low 2",
            "High   : 同类型 >= 6 幅图",
            "Medium : 同类型 4–5 幅图",
            "Low    : 同类型 <= 3 幅图",
            "Macro pooled process（n=312）：Q1/median/Q3/P90 = 3/5/9/16",
            "Algorithm A2–A4 process（n=131）：Q1/median/Q3/P90 = 5/8/12/23",
            "A2–A4 decision（n=50）：Q1/median/Q3/P90 = 6/8/10/13",
            "Terminal（n=39）：Q1/median/Q3 = 2/2/2",
            "Container title（n=18）：Q1/median/Q3/P90/max = 6/6.5/8/8/12",
        ):
            self.assertIn(required, self.content, required)

    def test_content_profiles_overload_and_low_evidence_guards_are_frozen(self):
        for required in (
            "| M4 阶段分组模块化 | 8 | High | 12–19 | 2–6 (n=100)",
            "| A2 单循环迭代 | 10 | High | 7–9 | 5–12 (n=52) | 7–10.5 (n=15)",
            "| A3 嵌套循环/多判定迭代 | 9 | High | 11–13 | 3–13.5 (n=56) | 7–10 (n=26)",
            "| A4 分支/搜索 | 4 | Medium | 8.5–11.8 | 7.5–11 (n=23) | 4–8 (n=9)",
            "**图级证据：1 幅；Evidence=Low。**",
            "**图级证据：3 幅；Evidence=Low。**",
            "Strong overload 进入重构决策，不自动失败",
            '"hard_max_node_count": None',
            '"hard_max_chars": None',
            "A5/A6 只报告观察值，不执行稳定 type-specific 自动阈值",
            "layout_status: human-owned / pending-human",
        ):
            self.assertIn(required, self.content, required)

    def test_current_active_surfaces_route_and_stop_before_human_layout(self):
        active_paths = (
            SKILL / "SKILL.md", SKILL / "README.md", SKILL / "docs/protocol.md",
            SKILL / "agents/openai.yaml", REFERENCES / "final_figure_core_rules.md",
            REFERENCES / "final_figure_selection.md", ROOT / "README.md",
            ROOT / "docs/compatibility.md", ROOT / "docs/installation.md",
            ROOT / "docs/known-limitations.md", ROOT / "docs/release-checklist.md",
        )
        active = "\n".join(path.read_text(encoding="utf-8") for path in active_paths)
        for forbidden in (
            "fixed **4 columns × 3 rows**",
            "Use a two-row serpentine layout by default",
            "flowcharts follow only the frozen Pt1 flowchart rules",
            "Do not introduce additional flowchart symbol families.",
            "figure_exec.py is a flowchart executor",
        ):
            self.assertNotIn(forbidden, active, forbidden)

        for name, text in (("selection", self.selection), ("content", self.content)):
            self.assertIn("human-owned", text, name)
            self.assertIn("pending-human", text, name)
        for path in (SKILL / "SKILL.md", SKILL / "docs/protocol.md", SKILL / "agents/openai.yaml"):
            text = path.read_text(encoding="utf-8")
            for required in (
                "kymcm-flowchart-selection-v1.md",
                "kymcm-flowchart-content-v1.md",
                "stop before",
                "human-owned",
            ):
                self.assertIn(required.lower(), text.lower(), f"{path.name}: {required}")

        core = (REFERENCES / "final_figure_core_rules.md").read_text(encoding="utf-8")
        for required in (
            "Stop before final spatial layout",
            "user/human author owns final layout",
            "no fixed macro grid",
            "automatic layout engine",
        ):
            self.assertIn(required, core, required)
        combined = "\n".join(path.read_text(encoding="utf-8") for path in active_paths)
        self.assertIn("Do not call `figure_exec.py`", combined)


if __name__ == "__main__":
    unittest.main()
