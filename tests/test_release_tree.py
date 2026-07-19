from __future__ import annotations

import re
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ReleaseTreeTests(unittest.TestCase):
    def test_skill_identity(self):
        skill = (ROOT / "skills/kymcm-full/SKILL.md").read_text(encoding="utf-8")
        self.assertRegex(skill, r"(?m)^name: kymcm-full$")
        self.assertEqual((ROOT / "skills/kymcm-full/VERSION").read_text(encoding="utf-8"), "1.0.0\n")
        agent = (ROOT / "skills/kymcm-full/agents/openai.yaml").read_text(encoding="utf-8")
        self.assertIn('display_name: "KyMCM Full"', agent)
        self.assertIn("$kymcm-full", agent)

    def test_required_release_paths(self):
        required = (
            ".github/workflows/ci.yml", "docs/installation.md", "docs/full-workflow.md",
            "docs/compatibility.md", "docs/release-checklist.md", "docs/known-limitations.md",
            "skills/kymcm-full/SKILL.md", "CHANGELOG.md", "LICENSE", "NOTICE.md",
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
            for target in link.findall(document.read_text(encoding="utf-8")):
                if "://" in target or target.startswith("#"):
                    continue
                path = target.split("#", 1)[0]
                if path:
                    with self.subTest(document=document.relative_to(ROOT), target=target):
                        self.assertTrue((document.parent / path).resolve().exists())

    def test_no_forbidden_release_paths_caches_or_fonts(self):
        forbidden_roots = {".ai-bridge", "practice", "knowledge_base", "upstream", "prototypes"}
        self.assertFalse(forbidden_roots & {path.name for path in ROOT.iterdir()})
        tracked = subprocess.check_output(["git", "-C", str(ROOT), "ls-files"], text=True).splitlines()
        for relative in tracked:
            path = Path(relative)
            with self.subTest(path=relative):
                self.assertNotIn("__pycache__", path.parts)
                self.assertNotIn(path.suffix.lower(), {".pyc", ".pyo", ".ttf", ".otf", ".woff", ".woff2"})

    def test_synthetic_fixture_has_no_contest_material(self):
        fixture = ROOT / "tests/fixtures/synthetic_contest"
        self.assertTrue((fixture / "README.md").is_file())
        self.assertTrue((fixture / "measurements.csv").is_file())
        text = "\n".join(path.read_text(encoding="utf-8") for path in fixture.iterdir() if path.is_file())
        self.assertIn("invented", text.lower())


if __name__ == "__main__":
    unittest.main()
