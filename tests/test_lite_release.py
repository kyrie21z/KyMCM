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
from kymcm_lite.appendix_contracts import SOURCE_ROOTS
from kymcm_lite.paths import LEGACY_IGNORED_ROOTS, MANAGED_ROOTS, MARKER_BYTES


class LiteReleaseTests(unittest.TestCase):
    def test_version_is_frozen(self):
        self.assertEqual((SKILL / "VERSION").read_bytes(), b"0.7.0\n")

    def test_release_facing_readmes_have_no_dev_identity(self):
        for relative in (
            "README.md", "skills/kymcm-lite/README.md", "docs/installation.md",
            "docs/compatibility.md", "docs/known-limitations.md",
        ):
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn("0.7.0", text, relative)
            self.assertNotIn("0.7.0-dev", text, relative)

    def test_skill_identity_is_exact(self):
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        agent = (SKILL / "agents/openai.yaml").read_text(encoding="utf-8")
        self.assertRegex(skill, r"(?m)^name: kymcm-lite$")
        self.assertIn('display_name: "KyMCM Lite"', agent)

    def test_public_commands_are_frozen(self):
        subparsers = next(action for action in parser()._actions if hasattr(action, "choices") and action.choices)
        self.assertEqual(set(subparsers.choices), {
            "init", "doctor", "check-start", "check-result",
            "check-preprocess-start", "check-preprocess-result",
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

    def test_legacy_paper_root_is_outside_runtime_scope(self):
        self.assertEqual(MANAGED_ROOTS, (".kymcm", "input", "reports", "problems"))
        self.assertIn("paper", LEGACY_IGNORED_ROOTS)
        self.assertEqual(SOURCE_ROOTS, ("problems/", "input/"))

    def test_repository_and_skill_templates_match(self):
        pairs = (
            ("docs/lite-v3/START_QN.template.md", "skills/kymcm-lite/templates/START_QN.template.md"),
            ("docs/lite-v3/RESULT_QN.template.md", "skills/kymcm-lite/templates/RESULT_QN.template.md"),
            ("docs/lite-v3/HANDOFF_QN.template.md", "skills/kymcm-lite/templates/HANDOFF_QN.template.md"),
            ("docs/lite-v3/START_PRE.template.md", "skills/kymcm-lite/templates/START_PRE.template.md"),
            ("docs/lite-v3/RESULT_PRE.template.md", "skills/kymcm-lite/templates/RESULT_PRE.template.md"),
            ("docs/lite-v3/HANDOFF_PRE.template.md", "skills/kymcm-lite/templates/HANDOFF_PRE.template.md"),
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
            (ROOT / "docs/lite-v3/preprocess_stage.md").read_bytes(),
            (SKILL / "references/preprocess_stage.md").read_bytes(),
        )
        self.assertEqual(
            (ROOT / "docs/lite-v3/modeling_plan_design.md").read_bytes(),
            (SKILL / "references/modeling_plan_design.md").read_bytes(),
        )
        self.assertEqual(
            (ROOT / "docs/lite-v3/technical_handoff.md").read_bytes(),
            (SKILL / "references/technical_handoff.md").read_bytes(),
        )
        self.assertFalse((ROOT / "docs/lite-v3/paper_handoff.md").exists())
        self.assertFalse((SKILL / "references/paper_handoff.md").exists())
        self.assertFalse((ROOT / "docs/lite-v3/FROZEN_CONTEXT.template.md").exists())
        self.assertFalse((SKILL / "templates/FROZEN_CONTEXT.template.md").exists())

    def test_modeling_plan_reference_and_start_guidance_are_frozen(self):
        expected_hash = "a3f77a7528c0d5829bdee7dbde4c4686d34cb7b1f7413418ea1c64df4769ee64"
        reference = SKILL / "references/modeling_plan_design.md"
        mirror = ROOT / "docs/lite-v3/modeling_plan_design.md"
        self.assertEqual(hashlib.sha256(reference.read_bytes()).hexdigest(), expected_hash)
        self.assertEqual(hashlib.sha256(mirror.read_bytes()).hexdigest(), expected_hash)

        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        protocol = (SKILL / "docs/protocol.md").read_text(encoding="utf-8")
        template = (SKILL / "templates/START_QN.template.md").read_text(encoding="utf-8")
        self.assertIn("references/modeling_plan_design.md", skill)
        self.assertIn("semantic", protocol)
        self.assertIn("semantic standard", protocol)
        for required in ("冒烟测试", "可恢复执行阶段", "L0", "L1", "L2", "嵌套拟合/求解/情景总次数"):
            self.assertIn(required, template)
        self.assertEqual(template.count("**前问依赖：** 无"), 1)

        frozen_hashes = {
            "docs/lite-v3/START_QN.template.md": "b60c0b09ed6a904b99e16eecd43b2ce9e059188847360a0d286d4d4b0720426a",
            "docs/lite-v3/RESULT_QN.template.md": "3794e2b24dedbcb816f09d90e01f400078b5fede85296b1d418dc1a1baa96d45",
            "docs/lite-v3/HANDOFF_QN.template.md": "623fe163eb6c5658695a5bac0b832c6a8326aaab96d10ba04f21cd42caab8574",
        }
        for relative, expected in frozen_hashes.items():
            self.assertEqual(hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(), expected, relative)

    def test_preprocess_contracts_and_semantic_boundaries(self):
        hashes = {
            "START_PRE.template.md": "8f60850084a4ca814654107838366660c4ce384c07130f2eda9cd677ce8c7539",
            "RESULT_PRE.template.md": "189595bdb36b5ee33a21363e3dfb3fb4faa65309e6a5bed7b0555931f8f8e4c5",
            "HANDOFF_PRE.template.md": "e5198504045d2243f174c43656082dd21c2373deb0812de95225f43bbf1893e9",
        }
        for name, expected in hashes.items():
            self.assertEqual(hashlib.sha256((SKILL / "templates" / name).read_bytes()).hexdigest(), expected)
        reference = (SKILL / "references/preprocess_stage.md").read_text(encoding="utf-8")
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        for required in ("样本 accounting", "L0", "L1", "L2", "因果", "下游"):
            self.assertIn(required, reference)
        for required in (
            "templates/START_PRE.template.md", "templates/RESULT_PRE.template.md",
            "templates/HANDOFF_PRE.template.md", "check-preprocess-result",
            "no Python checker", "content JSON",
        ):
            self.assertIn(required, skill)

    def test_appendix_code_scope_policy_and_templates(self):
        reference = (SKILL / "references/appendix_organization.md").read_text(encoding="utf-8")
        start = (SKILL / "templates/APPENDIX_START.template.md").read_text(encoding="utf-8")
        result = (SKILL / "templates/APPENDIX_RESULT.template.md").read_text(encoding="utf-8")
        protocol = (SKILL / "docs/protocol.md").read_text(encoding="utf-8")
        for required in (
            "完整正式求解代码", "绘图代码排除", "代表性真实实现",
            "调度", "恢复", "审计", "禁止复制", "混淆", "垃圾",
            "外部相似度",
        ):
            self.assertIn(required, reference)
        for required in ("完整正式求解代码", "代表性", "绘图", "相似度"):
            self.assertIn(required, start)
        for required in ("完整正式入口", "调度/恢复路径", "根 code 来源真实性"):
            self.assertIn(required, result)
        for required in (
            "complete formal solve code package", "authentic representative",
            "scheduling", "recovery", "external similarity",
        ):
            self.assertIn(required, protocol)

    def test_technical_handoff_reference_template_and_semantic_boundaries(self):
        reference = SKILL / "references/technical_handoff.md"
        template = SKILL / "templates/HANDOFF_QN.template.md"
        self.assertEqual(
            hashlib.sha256(reference.read_bytes()).hexdigest(),
            "4097cf896c21bc3049fbeecb9879f7d82d4e7efce1459835666861085aac1564",
        )
        self.assertEqual(
            hashlib.sha256(template.read_bytes()).hexdigest(),
            "623fe163eb6c5658695a5bac0b832c6a8326aaab96d10ba04f21cd42caab8574",
        )
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        protocol = (SKILL / "docs/protocol.md").read_text(encoding="utf-8")
        reference_text = reference.read_text(encoding="utf-8")
        self.assertIn("references/technical_handoff.md", skill)
        for required in (
            "neutral complete technical transfer", "RESULT remains the concise formal boundary",
            "Never use HANDOFF as a later modeling dependency", "cannot be copied",
        ):
            self.assertIn(required, skill)
        for required in (
            "HANDOFF_QN_K.md", "split mode has no aggregate", "formal", "auxiliary",
            "check-result", "no command",
        ):
            self.assertIn(required, protocol)
        for required in (
            "Machine evidence", "formal plus selected auxiliary", "Evidence and asset mapping",
            "causal", "extrapolation",
        ):
            self.assertIn(required, reference_text)

    def test_current_product_surface_has_no_writing_behavior(self):
        surfaces = [
            SKILL / "SKILL.md",
            SKILL / "README.md",
            SKILL / "agents/openai.yaml",
            SKILL / "docs/protocol.md",
            *sorted((SKILL / "references").glob("*.md")),
            *sorted((SKILL / "templates").glob("*.md")),
        ]
        forbidden = (
            "paper-writing", "paper writer", "paper-ready", "论文定位",
            "推荐论文表述", "摘要、正文或附录", "论文手", "论文说服力",
        )
        text = "\n".join(path.read_text(encoding="utf-8") for path in surfaces)
        for phrase in forbidden:
            self.assertNotIn(phrase, text, phrase)

    def test_check_result_does_not_require_handoff(self):
        workspace = ROOT / "tests/fixtures/lite_synthetic_handoff"
        self.assertFalse(any(workspace.rglob("HANDOFF_Q*.md")))
        completed = subprocess.run(
            [
                sys.executable, str(SKILL / "scripts/lite.py"), "check-result",
                "--workspace", str(workspace), "--problem", "1",
            ],
            text=True, capture_output=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

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
            "KyMCM Lite 0.7.0", "0.6.0", "0.5.1", "0.5.0", "0.4.0", "0.3.1", "0.3.0", "0.2.0", "0.1.0", "Python 3.11", "3.12", "3.13",
            "init", "doctor", "check-start", "check-result", "check-appendix-start",
            "check-appendix-result", "check-preprocess-start", "check-preprocess-result",
            '{"workflow":"kymcm_lite","version":3}',
            "Full", "Lite v2", "not automatically migrated",
            "technical_handoff.md", "HANDOFF", "formal", "auxiliary",
            "complete formal solve code package", "authentic representative",
        ):
            self.assertIn(required, notes)

    def test_changelogs_have_dated_release(self):
        for relative in ("CHANGELOG.md", "skills/kymcm-lite/CHANGELOG.md"):
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn("0.7.0 - 2026-07-30", text, relative)
            self.assertIn("0.6.0 - 2026-07-29", text, relative)
            self.assertIn("0.5.1 - 2026-07-29", text, relative)
            self.assertIn("0.5.0 - 2026-07-29", text, relative)
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
