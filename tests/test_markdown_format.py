from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "kymcm-full" / "SKILL.md"
REFERENCE = ROOT / "skills" / "kymcm-full" / "references" / "markdown_format.md"


class MarkdownFormatReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL.read_text(encoding="utf-8")
        cls.reference = REFERENCE.read_text(encoding="utf-8")

    def test_skill_routes_all_contest_markdown_to_reference(self):
        self.assertTrue(REFERENCE.is_file())
        self.assertIn("references/markdown_format.md", self.skill)
        for artifact in ("Problem Definition", "Start", "Result", "notes", "reports"):
            with self.subTest(artifact=artifact):
                self.assertIn(artifact, self.skill)

    def test_reference_defines_math_delimiters_and_code_boundary(self):
        for required in (
            "inline delimiters `$...$`",
            "display equation in `$$...$$`",
            "Bare LaTeX commands are forbidden",
            "Do not put mathematics that should render in backticks",
            "The significance level is $\\alpha=0.05$.",
            "$G=\\sigma_p^2/\\sigma_e^2$",
            "\\begin{aligned}",
        ):
            with self.subTest(required=required):
                self.assertIn(required, self.reference)

    def test_reference_covers_contest_markdown_and_table_safety(self):
        for heading in (
            "## Headings, paragraphs, and lists",
            "## Tables",
            "## Code, paths, and field names",
            "## Images and links",
            "## Pre-output check",
        ):
            with self.subTest(heading=heading):
                self.assertIn(heading, self.reference)
        self.assertIn("`\\mid`", self.reference)
        self.assertIn("bare `|`", self.reference)

    def test_reference_excludes_obsidian_specific_features(self):
        self.assertIn("## Excluded Obsidian features", self.reference)
        for excluded in ("frontmatter", "wikilinks", "note embeds", "callouts", "Obsidian CLI"):
            with self.subTest(excluded=excluded):
                self.assertIn(excluded, self.reference)
        self.assertIn("Do not use wikilinks", self.reference)
        self.assertIn("Mermaid is outside this reference", self.reference)


if __name__ == "__main__":
    unittest.main()
