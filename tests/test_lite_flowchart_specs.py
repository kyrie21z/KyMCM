from __future__ import annotations

from pathlib import Path
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

    def test_selection_contract_is_complete(self):
        for required in (
            "kymcm-flowchart-selection-v1", "73 strict CUMCM", "Macro 40", "Algorithm 33",
            "M1", "线性/阶段链", "M2", "多源/多支路汇聚", "M3", "分层分支-汇合",
            "M4", "阶段分组模块化", "M5", "双通道/对称", "M6", "反馈/循环系统",
            "A1", "线性顺序", "A2", "单循环迭代", "A3", "嵌套循环/多判定迭代",
            "A4", "分支/搜索", "A5", "并行子算法", "A6", "密集判定/调度网络",
            "minimum sufficient complexity", "low-evidence", "does not bind left-to-right",
            "does not support default algorithm serpentine", "human author", "manually judged and drawn",
        ):
            self.assertIn(required.lower(), self.selection.lower(), required)

    def test_content_contract_and_high_value_profiles_are_complete(self):
        for required in (
            "kymcm-flowchart-content-v1", "73 strict flowcharts", "747 ordinary flow nodes",
            "18 container titles", "726 ordinary nodes", "Typical Range = Q1–Q3",
            "N > type_Q3", "no universal Hard Max", "prefer 1–2 text lines",
            "Strong Overload requires both", "LOW EVIDENCE, descriptive only",
            "real functional or semantic boundary", "real encapsulatable process",
            "Final spatial layout and manual drawing are owned",
            "| M4 | 8 | 12 / 14 / 19 / 22.3 / 30 | 100; 2 / 3 / 6 / 15 |",
            "| A2 | 10 | 7 / 7.5 / 9 / 10 / 10 | 52; 5 / 7 / 12 / 18.9 | 15; 7 / 7 / 10.5 / 12.2 |",
            "| A3 | 9 | 11 / 12 / 13 / 15 / 15 | 56; 3 / 8.5 / 13.5 / 24.5 | 26; 7 / 8 / 10 / 14 |",
            "| A4 | 4 | 8.5 / 9.5 / 11.75 / 14.9 / 17 | 23; 7.5 / 9 / 11 / 12.8 | 9; 4 / 6 / 8 / 12.8 |",
            "| A5 | 1 — LOW EVIDENCE, descriptive only |",
            "| A6 | 3 — LOW EVIDENCE, descriptive only |",
        ):
            self.assertIn(required, self.content, required)

    def test_current_active_surfaces_retire_stale_flowchart_rules(self):
        active_paths = (
            SKILL / "SKILL.md", SKILL / "README.md", SKILL / "docs/protocol.md",
            SKILL / "agents/openai.yaml", REFERENCES / "final_figure_core_rules.md",
            REFERENCES / "final_figure_selection.md", ROOT / "README.md",
            ROOT / "docs/compatibility.md", ROOT / "docs/installation.md",
            ROOT / "docs/known-limitations.md", ROOT / "docs/release-checklist.md",
        )
        active = "\n".join(path.read_text(encoding="utf-8") for path in active_paths)
        for forbidden in (
            "fixed **4 columns × 3 rows**", "Use a two-row serpentine layout by default",
            "flowcharts follow only the frozen Pt1 flowchart rules",
            "Do not introduce additional flowchart symbol families.",
        ):
            self.assertNotIn(forbidden, active, forbidden)

        core = (REFERENCES / "final_figure_core_rules.md").read_text(encoding="utf-8")
        for required in (
            "kymcm-flowchart-selection-v1.md", "kymcm-flowchart-content-v1.md",
            "Stop before final spatial layout", "user/human author owns final layout",
        ):
            self.assertIn(required, core, required)

    def test_skill_agent_and_protocol_route_and_stop_before_layout(self):
        surfaces = {
            "SKILL.md": SKILL / "SKILL.md",
            "protocol.md": SKILL / "docs/protocol.md",
            "openai.yaml": SKILL / "agents/openai.yaml",
        }
        for name, path in surfaces.items():
            text = path.read_text(encoding="utf-8")
            for required in (
                "kymcm-flowchart-selection-v1.md", "kymcm-flowchart-content-v1.md",
                "stop before", "human-owned",
            ):
                self.assertIn(required.lower(), text.lower(), f"{name}: {required}")
        combined = "\n".join(path.read_text(encoding="utf-8") for path in surfaces.values())
        self.assertIn("Do not call `figure_exec.py`", combined)
        self.assertNotIn("figure_exec.py is a flowchart executor", combined)


if __name__ == "__main__":
    unittest.main()
