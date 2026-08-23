from __future__ import annotations

import re
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]


def is_tracked_ai_bridge_path(relative: str) -> bool:
    """Return whether a tracked path would expose local coordination files."""
    return relative == ".ai-bridge" or relative.startswith(".ai-bridge/")


class ReleaseTreeTests(unittest.TestCase):
    def test_skill_identity(self):
        products = (("kymcm-full", "1.0.0", "KyMCM Full"), ("kymcm-lite", "0.10.1", "KyMCM Lite"))
        for name, version, display in products:
            with self.subTest(skill=name):
                root = ROOT / "skills" / name
                skill = (root / "SKILL.md").read_text(encoding="utf-8")
                self.assertRegex(skill, rf"(?m)^name: {re.escape(name)}$")
                self.assertEqual((root / "VERSION").read_text(encoding="utf-8"), f"{version}\n")
                agent = (root / "agents/openai.yaml").read_text(encoding="utf-8")
                self.assertIn(f'display_name: "{display}"', agent)
                self.assertIn(f"${name}", agent)
                for required in ("README.md", "SKILL.md", "LICENSE", "VERSION", "agents/openai.yaml"):
                    self.assertTrue((root / required).is_file(), required)

    def test_lite_skill_is_standalone_and_has_no_symlinks(self):
        root = ROOT / "skills/kymcm-lite"
        for path in root.rglob("*"):
            self.assertFalse(path.is_symlink(), str(path))
            if path.is_file() and path.suffix in {".py", ".md"}:
                text = path.read_text(encoding="utf-8")
                self.assertNotIn("checkpoint_full", text, str(path))
                self.assertNotIn("skills/kymcm-full", text, str(path))

    def test_required_release_paths(self):
        required = (
            ".github/workflows/ci.yml", "docs/installation.md", "docs/full-workflow.md",
            "docs/compatibility.md", "docs/release-checklist.md", "docs/known-limitations.md",
            "skills/kymcm-full/SKILL.md", "CHANGELOG.md", "LICENSE", "NOTICE.md",
            "skills/kymcm-lite/SKILL.md", "skills/kymcm-lite/scripts/lite.py",
            "skills/kymcm-lite/references/modeling_plan_design.md",
            "docs/lite-v3/modeling_plan_design.md",
            "skills/kymcm-lite/references/technical_handoff.md",
            "docs/lite-v3/technical_handoff.md",
            "skills/kymcm-lite/templates/HANDOFF_QN.template.md",
            "docs/lite-v3/HANDOFF_QN.template.md",
            "skills/kymcm-lite/templates/SUPPLEMENT_START_QN.template.md",
            "docs/lite-v3/SUPPLEMENT_START_QN.template.md",
            "skills/kymcm-lite/templates/SUPPLEMENT_RESULT_QN.template.md",
            "docs/lite-v3/SUPPLEMENT_RESULT_QN.template.md",
            "skills/kymcm-lite/references/supplement_work.md",
            "docs/lite-v3/supplement_work.md",
            "skills/kymcm-lite/references/explore_work.md",
            "docs/lite-v3/explore_work.md",
            "skills/kymcm-lite/templates/EXPLORE_QN.template.md",
            "docs/lite-v3/EXPLORE_QN.template.md",
            "skills/kymcm-lite/references/machine_contract.md",
            "docs/lite-v3/machine_contract.md",
            "skills/kymcm-lite/references/final_figure_typography.md",
            "docs/lite-v3/final_figure_typography.md",
            "skills/kymcm-lite/references/final_figure_core_rules.md",
            "docs/lite-v3/final_figure_core_rules.md",
            "skills/kymcm-lite/references/final_figure_execution.md",
            "docs/lite-v3/final_figure_execution.md",
            "skills/kymcm-lite/references/final_figure_selection.md",
            "docs/lite-v3/final_figure_selection.md",
            "skills/kymcm-lite/references/kymcm-flowchart-selection-v1.md",
            "docs/lite-v3/kymcm-flowchart-selection-v1.md",
            "skills/kymcm-lite/references/kymcm-flowchart-content-v1.md",
            "docs/lite-v3/kymcm-flowchart-content-v1.md",
            "skills/kymcm-lite/references/final_figure_style.md",
            "docs/lite-v3/final_figure_style.md",
            "skills/kymcm-lite/references/final_figure_color.md",
            "docs/lite-v3/final_figure_color.md",
            "skills/kymcm-lite/references/ai_tool_usage_details.md",
            "docs/lite-v3/ai_tool_usage_details.md",
            "skills/kymcm-lite/templates/AI_TOOL_USAGE_DETAILS.template.tex",
            "docs/lite-v3/AI_TOOL_USAGE_DETAILS.template.tex",
            "skills/kymcm-lite/templates/AI_TOOL_USAGE_DECLARATION.template.tex",
            "docs/lite-v3/AI_TOOL_USAGE_DECLARATION.template.tex",
            "scripts/export_kymcm_lite_full_spec.py",
            "docs/lite-v3/KyMCM_Lite_FULL_SPEC.md",
            "skills/kymcm-lite/references/preprocess_stage.md",
            "docs/lite-v3/preprocess_stage.md",
            "skills/kymcm-lite/templates/START_PRE.template.md",
            "docs/lite-v3/START_PRE.template.md",
            "skills/kymcm-lite/templates/RESULT_PRE.template.md",
            "docs/lite-v3/RESULT_PRE.template.md",
            "skills/kymcm-lite/templates/HANDOFF_PRE.template.md",
            "docs/lite-v3/HANDOFF_PRE.template.md",
            "skills/kymcm-lite/figure_exec.py", "skills/kymcm-lite/requirements-figure.txt",
            "README.md", "requirements.txt", "requirements-optional.txt", "SECURITY.md",
        )
        for relative in required:
            with self.subTest(relative=relative):
                self.assertTrue((ROOT / relative).is_file())

    def test_relative_markdown_links_resolve(self):
        link = re.compile(r"(?<!!)\[[^]]+\]\(([^)]+)\)")
        for document in ROOT.rglob("*.md"):
            if ".git" in document.parts:
                continue
            if document == ROOT / "docs/lite-v3/KyMCM_Lite_FULL_SPEC.md":
                # The generated document deliberately preserves source Markdown
                # verbatim; its embedded relative links retain the source file's
                # original base rather than pretending the export is a website.
                continue
            for target in link.findall(document.read_text(encoding="utf-8")):
                if "://" in target or target.startswith("#"):
                    continue
                path = target.split("#", 1)[0]
                if path:
                    with self.subTest(document=document.relative_to(ROOT), target=target):
                        self.assertTrue((document.parent / path).resolve().exists())

    def test_no_forbidden_release_paths_caches_or_fonts(self):
        forbidden_roots = {"practice", "knowledge_base", "upstream", "prototypes"}
        self.assertFalse(forbidden_roots & {path.name for path in ROOT.iterdir()})
        tracked = subprocess.check_output(["git", "-C", str(ROOT), "ls-files"], text=True).splitlines()
        for relative in tracked:
            path = Path(relative)
            with self.subTest(path=relative):
                self.assertFalse(is_tracked_ai_bridge_path(relative))
                self.assertNotIn("__pycache__", path.parts)
                self.assertNotIn(path.suffix.lower(), {".pyc", ".pyo", ".ttf", ".otf", ".woff", ".woff2"})

    def test_untracked_ai_bridge_is_ignored_but_tracked_paths_are_forbidden(self):
        bridge_file = ROOT / ".ai-bridge/current-plan.md"
        ignored = subprocess.run(
            ["git", "-C", str(ROOT), "check-ignore", "--quiet", str(bridge_file)],
            check=False,
        )
        self.assertEqual(ignored.returncode, 0)
        self.assertTrue(is_tracked_ai_bridge_path(".ai-bridge"))
        self.assertTrue(is_tracked_ai_bridge_path(".ai-bridge/current-plan.md"))
        self.assertFalse(is_tracked_ai_bridge_path(".ai-bridge-notes/example.md"))

    def test_synthetic_fixture_has_no_contest_material(self):
        fixture = ROOT / "tests/fixtures/synthetic_contest"
        self.assertTrue((fixture / "README.md").is_file())
        self.assertTrue((fixture / "measurements.csv").is_file())
        text = "\n".join(path.read_text(encoding="utf-8") for path in fixture.iterdir() if path.is_file())
        self.assertIn("invented", text.lower())


if __name__ == "__main__":
    unittest.main()
