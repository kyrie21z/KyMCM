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
from kymcm_lite.paths import (
    EVIDENCE_DIRS, LEGACY_IGNORED_ROOTS, MANAGED_ROOTS, MARKER_BYTES,
    OPTIONAL_ROOTS,
)


class LiteReleaseTests(unittest.TestCase):
    def test_version_is_frozen(self):
        self.assertEqual((SKILL / "VERSION").read_bytes(), b"0.9.4\n")

    def test_release_facing_readmes_have_no_dev_identity(self):
        for relative in (
            "README.md", "skills/kymcm-lite/README.md", "docs/installation.md",
            "docs/compatibility.md", "docs/known-limitations.md",
        ):
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn("0.9.4", text, relative)
            self.assertNotIn("0.9.4-dev", text, relative)

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

    def test_optional_figure_and_legacy_paper_are_outside_runtime_scope(self):
        self.assertEqual(MANAGED_ROOTS, (".kymcm", "input", "reports", "problems"))
        self.assertEqual(OPTIONAL_ROOTS, ("figure",))
        self.assertIn("paper", LEGACY_IGNORED_ROOTS)
        self.assertNotIn("figure", EVIDENCE_DIRS)
        self.assertEqual(SOURCE_ROOTS, ("problems/", "input/"))

    def test_repository_and_skill_templates_match(self):
        pairs = (
            ("docs/lite-v3/START_QN.template.md", "skills/kymcm-lite/templates/START_QN.template.md"),
            ("docs/lite-v3/RESULT_QN.template.md", "skills/kymcm-lite/templates/RESULT_QN.template.md"),
            ("docs/lite-v3/HANDOFF_QN.template.md", "skills/kymcm-lite/templates/HANDOFF_QN.template.md"),
            ("docs/lite-v3/SUPPLEMENT_START_QN.template.md", "skills/kymcm-lite/templates/SUPPLEMENT_START_QN.template.md"),
            ("docs/lite-v3/SUPPLEMENT_RESULT_QN.template.md", "skills/kymcm-lite/templates/SUPPLEMENT_RESULT_QN.template.md"),
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
        self.assertEqual(
            (ROOT / "docs/lite-v3/supplement_work.md").read_bytes(),
            (SKILL / "references/supplement_work.md").read_bytes(),
        )
        self.assertEqual(
            (ROOT / "docs/lite-v3/machine_contract.md").read_bytes(),
            (SKILL / "references/machine_contract.md").read_bytes(),
        )
        self.assertEqual(
            (ROOT / "docs/lite-v3/final_figure_typography.md").read_bytes(),
            (SKILL / "references/final_figure_typography.md").read_bytes(),
        )
        self.assertFalse((ROOT / "docs/lite-v3/paper_handoff.md").exists())
        self.assertFalse((SKILL / "references/paper_handoff.md").exists())
        self.assertFalse((ROOT / "docs/lite-v3/FROZEN_CONTEXT.template.md").exists())
        self.assertFalse((SKILL / "templates/FROZEN_CONTEXT.template.md").exists())

    def test_modeling_plan_reference_and_start_guidance_are_frozen(self):
        expected_hash = "b90c4689fc87e75c7a853441e39b620c3cbc4676ad185bd38a6ac06cee4ae2ed"
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
            "docs/lite-v3/START_QN.template.md": "4db5837709686701d1d19fbc797567e34b387751c7998beb5a6717784373fc8e",
            "docs/lite-v3/RESULT_QN.template.md": "3794e2b24dedbcb816f09d90e01f400078b5fede85296b1d418dc1a1baa96d45",
            "docs/lite-v3/HANDOFF_QN.template.md": "2495e222fc350934367956d67c0f74f069cab8c2097f3c06cee4f74c04b11014",
        }
        for relative, expected in frozen_hashes.items():
            self.assertEqual(hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(), expected, relative)

    def test_preprocess_contracts_and_semantic_boundaries(self):
        hashes = {
            "START_PRE.template.md": "f8c30249682de75c5b82af525df8c74fe5bde2338bcdd0c0a198c071ae249d3b",
            "RESULT_PRE.template.md": "189595bdb36b5ee33a21363e3dfb3fb4faa65309e6a5bed7b0555931f8f8e4c5",
            "HANDOFF_PRE.template.md": "b486f30425c74dce973b8d55891b284871161e86a54dbec0836d3801d5c387fb",
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
            "2d5f3450a86f4a6936ddbf0ebfd8beb629fec24c10eba34be8baf58ebf954419",
        )
        self.assertEqual(
            hashlib.sha256(template.read_bytes()).hexdigest(),
            "2495e222fc350934367956d67c0f74f069cab8c2097f3c06cee4f74c04b11014",
        )
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        protocol = (SKILL / "docs/protocol.md").read_text(encoding="utf-8")
        reference_text = reference.read_text(encoding="utf-8")
        self.assertIn("references/technical_handoff.md", skill)
        for required in (
            "neutral complete technical transfer", "exact base RESULT units",
            "Never use HANDOFF as a later modeling dependency", "cannot be copied",
        ):
            self.assertIn(required, skill)
        for required in (
            "one current problem-level `HANDOFF_QN.md`", "Partial split RESULT completion",
            "Never create a new suffixed `HANDOFF_QN_K.md`", "aggregate RESULT",
            "formal", "auxiliary", "check-result", "no command",
        ):
            self.assertIn(required, protocol)
        for required in (
            "Machine evidence", "formal plus selected auxiliary", "Evidence and asset mapping",
            "causal", "extrapolation", "every contiguous `START_QN_K.md`",
            "ordinary legacy notes",
        ):
            self.assertIn(required, reference_text)
        template_text = template.read_text(encoding="utf-8")
        self.assertIn("每题只创建这一份问题级 HANDOFF", template_text)
        self.assertIn("拆分模式全部 RESULT_QN_K.md", template_text)
        self.assertIn("SUPPLEMENT_RESULT_QN.md", template_text)
        self.assertNotIn("HANDOFF_QN_K.md", template_text)

    def test_question_scoped_handoff_identity_and_compatibility(self):
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        protocol = (SKILL / "docs/protocol.md").read_text(encoding="utf-8")
        reference = (SKILL / "references/technical_handoff.md").read_text(encoding="utf-8")
        combined = "\n".join((skill, protocol, reference))
        for required in (
            "problem-level `HANDOFF_QN.md`", "single and split modes",
            "every contiguous START unit has a matching RESULT",
            "Partial split completion", "exact base RESULT units",
            "Never create a new `HANDOFF_QN_K.md`",
            "without deletion, renaming, merging",
        ):
            self.assertIn(required, combined)
        for forbidden in (
            "split `HANDOFF_QN_K.md`, never an unsuffixed aggregate",
            "Single and split HANDOFF identities cannot mix",
            "Identity must match an existing RESULT exactly",
        ):
            self.assertNotIn(forbidden, combined)
        self.assertNotIn("SUPPLEMENT_QN.md", combined)
        self.assertIn("Add no Supplement checker", combined)
        self.assertIn("followups/", combined)

    def test_result_acceptance_gate_is_explicit_and_two_stage(self):
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        protocol = (SKILL / "docs/protocol.md").read_text(encoding="utf-8")
        agent = (SKILL / "agents/openai.yaml").read_text(encoding="utf-8")
        handoff = (SKILL / "references/technical_handoff.md").read_text(encoding="utf-8")
        supplement = (SKILL / "references/supplement_work.md").read_text(encoding="utf-8")
        preprocess = (SKILL / "references/preprocess_stage.md").read_text(encoding="utf-8")
        machine = (SKILL / "references/machine_contract.md").read_text(encoding="utf-8")
        qn_template = (SKILL / "templates/HANDOFF_QN.template.md").read_text(encoding="utf-8")
        pre_template = (SKILL / "templates/HANDOFF_PRE.template.md").read_text(encoding="utf-8")
        self.assertIn("execution terminal point", skill)
        self.assertIn("never authorizes HANDOFF", skill)
        self.assertIn("separate explicit HANDOFF task", protocol)
        self.assertIn("explicit user/ChatGPT semantic acceptance", agent)
        self.assertIn("new independent HANDOFF task", handoff)
        self.assertIn("read-only phase", handoff)
        self.assertIn("stop for explicit user/ChatGPT semantic acceptance", supplement)
        self.assertIn("不要创建或更新 HANDOFF_PRE", preprocess)
        self.assertIn("human semantic acceptance of RESULT_PRE", machine)
        self.assertIn("HANDOFF refresh alone does not adopt", machine)
        for template in (qn_template, pre_template):
            self.assertIn("明确验收通过", template)
            self.assertIn("只读", template)
            self.assertIn("不构成授权", template)

    def test_question_level_supplement_contracts_and_semantics(self):
        start = SKILL / "templates/SUPPLEMENT_START_QN.template.md"
        result = SKILL / "templates/SUPPLEMENT_RESULT_QN.template.md"
        reference = SKILL / "references/supplement_work.md"
        self.assertEqual(hashlib.sha256(start.read_bytes()).hexdigest(), "6056e597253f20ef1d45f4b0b3a14753d6724fa1e37767ac72554b6429099c48")
        self.assertEqual(hashlib.sha256(result.read_bytes()).hexdigest(), "c25364c2b64339f9c4f50009e0c2e11e536a5c8ec49349d8d5f395cdcb5d80c2")
        self.assertEqual(hashlib.sha256(reference.read_bytes()).hexdigest(), "ad120b1bc2ba0702e3b267806c56817fcf5633ab5f99a29de2a08d511008187f")
        self.assertEqual(start.read_text(encoding="utf-8").splitlines()[0], "# SUPPLEMENT START QN")
        self.assertEqual(result.read_text(encoding="utf-8").splitlines()[0], "# SUPPLEMENT RESULT QN")
        combined = "\n".join(
            (SKILL / relative).read_text(encoding="utf-8")
            for relative in ("SKILL.md", "docs/protocol.md", "references/supplement_work.md")
        )
        for required in (
            "SUPPLEMENT_START_QN.md", "SUPPLEMENT_RESULT_QN.md", "补充验证",
            "方案修订", "实现修复", "追加证据", "局部替代", "完全替代",
            "不改变正式状态", "S1, S2", "plan-before-execution",
            "base RESULT", "HANDOFF_QN.md", "dependency token",
            "PRE Supplement", "latest unadopted", "adopted", "invalidates",
            "downstream use", "overwrite/rebuild",
        ):
            self.assertIn(required, combined)

        self.assertIn("最新且尚未被采用的 Sx 可以原位修改", start.read_text(encoding="utf-8"))
        self.assertIn("已有后续 Sy 的 Sx 冻结", start.read_text(encoding="utf-8"))
        self.assertIn("实质修改 Start 后，必须先移除/替换旧 Result", start.read_text(encoding="utf-8"))
        self.assertIn("最新且尚未被采用的 Sx 可以先删除/替换同编号 Result", result.read_text(encoding="utf-8"))
        self.assertIn("新 Start 与旧 Result 不得并存", result.read_text(encoding="utf-8"))
        self.assertIn("alone does not freeze", combined)
        self.assertIn("HANDOFF alone", combined)

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

    def test_nonvisual_default_and_optional_figure_boundaries(self):
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        protocol = (SKILL / "docs/protocol.md").read_text(encoding="utf-8")
        agent = (SKILL / "agents/openai.yaml").read_text(encoding="utf-8")
        combined = "\n".join((skill, protocol))
        for required in (
            "non-visual by default", "structured evidence", "named risk",
            "stopping condition", "figure/", "nature-figure",
            "explicit user request", "appendix source",
        ):
            self.assertIn(required, combined)
        self.assertIn("nature-figure", agent)
        self.assertFalse((SKILL / "skills/nature-figure").exists())
        runtime = "\n".join(path.read_text(encoding="utf-8") for path in SCRIPTS.rglob("*.py"))
        self.assertNotIn("nature-figure", runtime)
        self.assertNotIn("nature_figure", runtime)

    def test_final_figure_typography_contract_is_exact_and_external(self):
        reference = (SKILL / "references/final_figure_typography.md").read_text(encoding="utf-8")
        mirror = ROOT / "docs/lite-v3/final_figure_typography.md"
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        protocol = (SKILL / "docs/protocol.md").read_text(encoding="utf-8")
        agent = (SKILL / "agents/openai.yaml").read_text(encoding="utf-8")
        self.assertEqual((SKILL / "references/final_figure_typography.md").read_bytes(), mirror.read_bytes())
        for exact in ("Noto Serif CJK SC", "Tinos", "STIX mathtext", "mathtext.fontset = stix"):
            self.assertIn(exact, reference)
            self.assertIn(exact, skill + protocol + agent)
        for required in (
            "Chinese full-width punctuation", "Latin letters", "Arabic numerals",
            "ASCII punctuation", "Math formulas", "Mixed titles", "font properties",
            "stop the formal final-figure task", "silent fallback", "download a font",
            "copy it from another directory", "font binary", "preview/non-final",
            "nature-figure", "does not render figures", "CI does not need these fonts",
            "minimum routing probe", "PDF/SVG", "user-requested different font",
        ):
            self.assertIn(required, reference, required)
        self.assertIn("references/final_figure_typography.md", skill)
        self.assertIn("references/final_figure_typography.md", protocol)
        self.assertIn("Noto Serif CJK SC", agent)
        self.assertIn("Tinos", agent)
        self.assertIn("STIX mathtext", agent)
        runtime = "\n".join(path.read_text(encoding="utf-8") for path in SCRIPTS.rglob("*.py"))
        self.assertNotIn("matplotlib", runtime)
        self.assertNotIn("fonttools", runtime)
        self.assertNotIn("nature-figure", runtime)
        self.assertNotIn("check-figure-fonts", runtime)
        for template in (SKILL / "templates").glob("*.md"):
            if template.name in {
                "START_QN.template.md", "RESULT_QN.template.md", "START_PRE.template.md",
                "RESULT_PRE.template.md", "SUPPLEMENT_START_QN.template.md",
                "SUPPLEMENT_RESULT_QN.template.md", "HANDOFF_QN.template.md",
                "HANDOFF_PRE.template.md", "APPENDIX_START.template.md",
                "APPENDIX_RESULT.template.md",
            }:
                text = template.read_text(encoding="utf-8")
                self.assertNotIn("Noto Serif CJK SC", text, template.name)
                self.assertNotIn("Tinos", text, template.name)
                self.assertNotIn("STIX mathtext", text, template.name)

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
            "KyMCM Lite 0.9.4", "KyMCM Lite 0.9.3", "KyMCM Lite 0.9.2", "KyMCM Lite 0.9.1", "KyMCM Lite 0.9.0", "0.8.1", "0.8.0", "0.7.0", "0.6.0", "0.5.1", "0.5.0", "0.4.0", "0.3.1", "0.3.0", "0.2.0", "0.1.0", "Python 3.11", "3.12", "3.13",
            "init", "doctor", "check-start", "check-result", "check-appendix-start",
            "check-appendix-result", "check-preprocess-start", "check-preprocess-result",
            '{"workflow":"kymcm_lite","version":3}',
            "Full", "Lite v2", "not automatically migrated",
            "supplement_work.md", "technical_handoff.md", "HANDOFF", "formal", "auxiliary",
            "complete formal solve code package", "authentic representative",
            "figure/", "nature-figure", "known optional root", "Noto Serif CJK SC", "Tinos", "STIX mathtext", "mathtext.fontset = stix", "silent fallback",
            "HANDOFF_QN.md", "HANDOFF_QN_K.md", "exact tokens",
            "SUPPLEMENT_START_QN.md", "SUPPLEMENT_RESULT_QN.md",
            "KyMCM_Lite_FULL_SPEC.md", "export_kymcm_lite_full_spec.py", "--check",
            "latest unadopted", "adopted", "invalidates", "HANDOFF", "explicit", "accepted", "read-only",
        ):
            self.assertIn(required, notes)

    def test_changelogs_have_dated_release(self):
        for relative in ("CHANGELOG.md", "skills/kymcm-lite/CHANGELOG.md"):
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn("0.9.4 - 2026-08-04", text, relative)
            self.assertIn("0.9.3 - 2026-08-04", text, relative)
            self.assertIn("0.9.2 - 2026-08-04", text, relative)
            self.assertIn("0.9.1 - 2026-07-31", text, relative)
            self.assertIn("0.9.0 - 2026-07-30", text, relative)
            self.assertIn("0.8.1 - 2026-07-30", text, relative)
            self.assertIn("0.8.0 - 2026-07-30", text, relative)
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
