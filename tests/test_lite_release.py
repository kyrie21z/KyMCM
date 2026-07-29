from __future__ import annotations

import ast
import hashlib
from pathlib import Path
import re
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/kymcm-lite"
SCRIPTS = SKILL / "scripts"
sys.path.insert(0, str(SCRIPTS))

from kymcm_lite.cli import parser
from kymcm_lite.paths import MARKER_BYTES


class LiteReleaseTests(unittest.TestCase):
    def test_version_is_frozen(self):
        self.assertEqual((SKILL / "VERSION").read_bytes(), b"0.4.0\n")

    def test_release_facing_readmes_have_no_dev_identity(self):
        for relative in (
            "README.md", "skills/kymcm-lite/README.md", "docs/installation.md",
            "docs/compatibility.md", "docs/known-limitations.md",
        ):
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn("0.4.0", text, relative)
            self.assertNotIn("0.4.0-dev", text, relative)

    def test_skill_identity_is_exact(self):
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        agent = (SKILL / "agents/openai.yaml").read_text(encoding="utf-8")
        self.assertRegex(skill, r"(?m)^name: kymcm-lite$")
        self.assertIn('display_name: "KyMCM Lite"', agent)

    def test_public_commands_are_frozen(self):
        subparsers = next(action for action in parser()._actions if hasattr(action, "choices") and action.choices)
        self.assertEqual(set(subparsers.choices), {
            "init", "doctor", "check-start", "check-result",
            "check-appendix-start", "check-appendix-result",
        })
        supporting = {
            name
            for name, command in subparsers.choices.items()
            if any(action.dest == "subproblem" for action in command._actions)
        }
        self.assertEqual(supporting, {"check-start", "check-result"})

    def test_marker_bytes_are_frozen(self):
        self.assertEqual(MARKER_BYTES, b'{"workflow":"kymcm_lite","version":3}\n')

    def test_repository_and_skill_templates_match(self):
        pairs = (
            ("docs/lite-v3/START_QN.template.md", "skills/kymcm-lite/templates/START_QN.template.md"),
            ("docs/lite-v3/RESULT_QN.template.md", "skills/kymcm-lite/templates/RESULT_QN.template.md"),
            ("docs/lite-v3/APPENDIX_START.template.md", "skills/kymcm-lite/templates/APPENDIX_START.template.md"),
            ("docs/lite-v3/APPENDIX_RESULT.template.md", "skills/kymcm-lite/templates/APPENDIX_RESULT.template.md"),
        )
        for repository, standalone in pairs:
            self.assertEqual((ROOT / repository).read_bytes(), (ROOT / standalone).read_bytes(), repository)
        self.assertEqual(
            (ROOT / "docs/lite-v3/appendix_organization.md").read_bytes(),
            (SKILL / "references/appendix_organization.md").read_bytes(),
        )
        self.assertEqual(
            (ROOT / "docs/lite-v3/dependency_review.md").read_bytes(),
            (SKILL / "references/dependency_review.md").read_bytes(),
        )
        self.assertEqual(
            (ROOT / "docs/lite-v3/modeling_plan_design.md").read_bytes(),
            (SKILL / "references/modeling_plan_design.md").read_bytes(),
        )
        self.assertFalse((ROOT / "docs/lite-v3/FROZEN_CONTEXT.template.md").exists())
        self.assertFalse((SKILL / "templates/FROZEN_CONTEXT.template.md").exists())

    def test_modeling_plan_reference_and_start_guidance_are_frozen(self):
        expected_hash = "3c508dc1a48a697efcc8b220cde5187727b8b49ba4b81570ca3ab8750e09120b"
        reference = SKILL / "references/modeling_plan_design.md"
        mirror = ROOT / "docs/lite-v3/modeling_plan_design.md"
        self.assertEqual(hashlib.sha256(reference.read_bytes()).hexdigest(), expected_hash)
        self.assertEqual(hashlib.sha256(mirror.read_bytes()).hexdigest(), expected_hash)

        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        protocol = (SKILL / "docs/protocol.md").read_text(encoding="utf-8")
        template = (SKILL / "templates/START_QN.template.md").read_text(encoding="utf-8")
        self.assertIn("references/modeling_plan_design.md", skill)
        self.assertIn("semantic", protocol)
        self.assertIn("not a workspace contract", protocol)
        for required in ("冒烟测试", "可恢复执行阶段", "L0", "L1", "L2", "嵌套拟合/求解/情景总次数"):
            self.assertIn(required, template)
        self.assertEqual(template.count("**前问依赖：** 无"), 1)

        frozen_hashes = {
            "docs/lite-v3/RESULT_QN.template.md": "3794e2b24dedbcb816f09d90e01f400078b5fede85296b1d418dc1a1baa96d45",
            "docs/lite-v3/APPENDIX_START.template.md": "ab7e0924b9a9188c7008a8df70a51c7e7e4e7c45cd7da6a8c1068c4ebf662f6e",
            "docs/lite-v3/APPENDIX_RESULT.template.md": "448a6fb28afa6132f60729a129fb4b9e0ec6f0210494d0b2810ace7bd540c203",
        }
        for relative, expected in frozen_hashes.items():
            self.assertEqual(hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(), expected, relative)

    def test_standalone_skill_has_no_symlinks(self):
        self.assertFalse(any(path.is_symlink() for path in SKILL.rglob("*")))

    def test_lite_python_imports_are_standard_library_only(self):
        allowed = set(sys.stdlib_module_names) | {"kymcm_lite"}
        for path in SCRIPTS.rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    names = [alias.name.split(".", 1)[0] for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                    names = [node.module.split(".", 1)[0]]
                else:
                    continue
                self.assertTrue(set(names) <= allowed, f"{path}: {names}")

    def test_lite_runtime_is_independent_of_full(self):
        text = "\n".join(path.read_text(encoding="utf-8") for path in SCRIPTS.rglob("*.py"))
        for forbidden in ("kymcm_full", "kymcm-full", "full_checkpoint", "checkpoint_full"):
            self.assertNotIn(forbidden, text)

    def test_runtime_diagnostics_are_documented(self):
        runtime = "\n".join(path.read_text(encoding="utf-8") for path in (SCRIPTS / "kymcm_lite").glob("*.py"))
        catalog = (ROOT / "docs/lite-v3/diagnostics.md").read_text(encoding="utf-8")
        pattern = r"LITE-[A-Z0-9-]+-(?:WARN-)?001"
        self.assertTrue(set(re.findall(pattern, runtime)) <= set(re.findall(pattern, catalog)))

    def test_release_notes_cover_release_contract(self):
        notes = (ROOT / "docs/lite-v3-release-notes.md").read_text(encoding="utf-8")
        for required in (
            "KyMCM Lite 0.4.0", "KyMCM Lite 0.3.1", "KyMCM Lite 0.3.0", "KyMCM Lite 0.2.0", "KyMCM Lite 0.1.0", "Python 3.11", "3.12", "3.13",
            "init", "doctor", "check-start", "check-result", "check-appendix-start",
            "check-appendix-result", '{"workflow":"kymcm_lite","version":3}',
            "Full", "Lite v2", "first standalone Lite v3 release", "not automatically migrated",
            "3c508dc1a48a697efcc8b220cde5187727b8b49ba4b81570ca3ab8750e09120b",
        ):
            self.assertIn(required, notes)

    def test_changelogs_have_dated_release(self):
        for relative in ("CHANGELOG.md", "skills/kymcm-lite/CHANGELOG.md"):
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn("0.4.0 - 2026-07-29", text, relative)
            self.assertIn("0.3.1 - 2026-07-24", text, relative)
            self.assertIn("0.3.0 - 2026-07-23", text, relative)
            self.assertIn("0.2.0 - 2026-07-23", text, relative)
            self.assertIn("0.1.0 - 2026-07-20", text, relative)

    def test_release_candidate_tree_is_clean_of_forbidden_files(self):
        tracked = subprocess.check_output(["git", "-C", str(ROOT), "ls-files"], text=True).splitlines()
        untracked = subprocess.check_output(["git", "-C", str(ROOT), "ls-files", "--others", "--exclude-standard"], text=True).splitlines()
        forbidden_suffixes = {".pyc", ".pyo", ".ttf", ".otf", ".woff", ".woff2"}
        for relative in tracked + untracked:
            if not (ROOT / relative).exists():
                continue
            path = Path(relative)
            self.assertNotIn("__pycache__", path.parts, relative)
            self.assertNotIn(path.suffix.lower(), forbidden_suffixes, relative)
            self.assertFalse(relative.startswith(".ai-bridge/"), relative)
            self.assertLessEqual((ROOT / relative).stat().st_size, 1024 * 1024, relative)

    def test_full_release_identity_is_unchanged(self):
        self.assertEqual((ROOT / "skills/kymcm-full/VERSION").read_bytes(), b"1.0.0\n")
        tag = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "full-v1.0.0"], text=True).strip()
        self.assertEqual(tag, "8de8b146be09c5584cf63d7675d6cc36a3485ec8")


if __name__ == "__main__":
    unittest.main()
