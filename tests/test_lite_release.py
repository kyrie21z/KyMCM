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
        self.assertEqual((SKILL / "VERSION").read_bytes(), b"0.10.2\n")
        protocol = (SKILL / "docs/protocol.md").read_text(encoding="utf-8")
        self.assertIn("KyMCM Lite 0.10.2 is a programming-side", protocol)

    def test_release_facing_readmes_have_no_dev_identity(self):
        for relative in (
            "README.md", "skills/kymcm-lite/README.md", "docs/installation.md",
            "docs/compatibility.md", "docs/known-limitations.md",
        ):
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn("0.10.2", text, relative)
            self.assertNotIn("0.10.2-dev", text, relative)

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
            ("docs/lite-v3/EXPLORE_QN.template.md", "skills/kymcm-lite/templates/EXPLORE_QN.template.md"),
            ("docs/lite-v3/START_PRE.template.md", "skills/kymcm-lite/templates/START_PRE.template.md"),
            ("docs/lite-v3/RESULT_PRE.template.md", "skills/kymcm-lite/templates/RESULT_PRE.template.md"),
            ("docs/lite-v3/HANDOFF_PRE.template.md", "skills/kymcm-lite/templates/HANDOFF_PRE.template.md"),
            ("docs/lite-v3/APPENDIX_START.template.md", "skills/kymcm-lite/templates/APPENDIX_START.template.md"),
            ("docs/lite-v3/APPENDIX_RESULT.template.md", "skills/kymcm-lite/templates/APPENDIX_RESULT.template.md"),
            ("docs/lite-v3/final_figure_core_rules.md", "skills/kymcm-lite/references/final_figure_core_rules.md"),
            ("docs/lite-v3/final_figure_execution.md", "skills/kymcm-lite/references/final_figure_execution.md"),
            ("docs/lite-v3/final_figure_selection.md", "skills/kymcm-lite/references/final_figure_selection.md"),
            ("docs/lite-v3/kymcm-flowchart-selection-v1.md", "skills/kymcm-lite/references/kymcm-flowchart-selection-v1.md"),
            ("docs/lite-v3/kymcm-flowchart-content-v1.md", "skills/kymcm-lite/references/kymcm-flowchart-content-v1.md"),
            ("docs/lite-v3/final_figure_style.md", "skills/kymcm-lite/references/final_figure_style.md"),
            ("docs/lite-v3/final_figure_color.md", "skills/kymcm-lite/references/final_figure_color.md"),
            ("docs/lite-v3/final_figure_3d.md", "skills/kymcm-lite/references/final_figure_3d.md"),
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
            (ROOT / "docs/lite-v3/explore_work.md").read_bytes(),
            (SKILL / "references/explore_work.md").read_bytes(),
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
        expected_hash = "11564c431950b7bf8de34749103edf2f9c7829262674b9be8b2b134f7e4a82d2"
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
        guidance = reference.read_text(encoding="utf-8")
        for required in (
            "核心 Claim", "failure mode", "直接证据",
            "L0：Claim-required / 必需证据",
            "L1：Risk-triggered / 风险触发",
            "L2：Evidence-strengthening / 证据强化",
            "验证方法名称不决定等级",
            "成本也不决定等级",
            "样本外验证/回测 + 预测误差 + 简单且有意义的基准",
            "可行性/约束审计 + 目标值独立复算",
            "收敛曲线、敏感性分析或单次良好运行都不能证明全局最优",
            "不得仅为论文完整性安排敏感性分析",
            "模型评价", "不是 validation evidence",
            "每条核心正式 Claim 至少有一项适合该 Claim 的直接证据",
            "已经得到检验或被显式披露为限制",
            "剩余候选实验主要重复既有证据",
        ):
            self.assertIn(required, guidance)
        self.assertFalse((SKILL / "references/validation_strength.md").exists())
        self.assertFalse((ROOT / "docs/lite-v3/validation_strength.md").exists())
        self.assertNotIn("check-validation", guidance)
        self.assertNotIn("收敛曲线可以证明全局最优", guidance)
        self.assertNotIn("所有问题必须执行敏感性分析", guidance)
        self.assertNotIn("所有随机算法必须执行多种子", guidance)
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
            "计算核心", "独立正式结果", "绘图、显示和接口代码排除",
            "输入、特征/参数", "优化", "统计", "预测", "约束", "审计",
            "第一层：文件写入与持久化副作用",
            "第二层：结果与文档构造",
            "第三层：展示/导出入口与孤儿代码清理",
            "每个 `CURATE` 条目都必须记录",
            "禁止复制", "混淆", "垃圾", "外部相似度",
        ):
            self.assertIn(required, reference)
        self.assertNotIn("代码层/文档层/流程层", reference)
        for required in (
            "计算核心", "独立正式结果", "代表性", "绘图", "相似度",
            "每个 CURATE 条目必须记录", "第一层", "第二层", "第三层",
            "孤儿", "数学、数据和执行语义",
        ):
            self.assertIn(required, start)
        for required in (
            "计算核心", "独立正式结果", "静态副作用", "根 code/ 选择理由",
            "三层删除", "第一层", "第二层", "第三层", "孤儿代码",
        ):
            self.assertIn(required, result)
        machine = (SKILL / "references/machine_contract.md").read_text(encoding="utf-8")
        self.assertIn("They also reject CSV,", machine)
        self.assertIn("Markdown, and XLSX result-like files in code targets", machine)
        self.assertNotIn("They do not reject\nCSV, Markdown, or XLSX", machine)
        for required in (
            "auditable computation core", "authentic representative computation-core",
            "COPY-only independent submission attachments", "code-side effects",
            "human-owned",
        ):
            self.assertIn(required, protocol)

    def test_submission_root_assets_and_legacy_boundary_are_frozen(self):
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        protocol = (SKILL / "docs/protocol.md").read_text(encoding="utf-8")
        machine = (SKILL / "references/machine_contract.md").read_text(encoding="utf-8")
        appendix = (SKILL / "references/appendix_organization.md").read_text(encoding="utf-8")
        start = (SKILL / "templates/APPENDIX_START.template.md").read_text(encoding="utf-8")
        result = (SKILL / "templates/APPENDIX_RESULT.template.md").read_text(encoding="utf-8")
        for current in (skill, protocol):
            self.assertLess(
                current.index("## Final submission AI tool usage details"),
                current.index("## Optional submission appendix organization"),
            )
        self.assertEqual(start.count("AI 工具使用详情：`appendix/AI 工具使用详情.pdf`"), 1)
        self.assertEqual(
            start.count(
                "- A093 — COPY — `reports/ai-usage/AI 工具使用详情.pdf` → "
                "`appendix/AI 工具使用详情.pdf`"
            ),
            1,
        )
        for required in (
            "legacy contract shape", "without automatic migration", "COPY-only",
            "reports/ai-usage/AI 工具使用详情.pdf", "appendix/AI 工具使用详情.pdf",
            ".xlsx", ".csv", ".txt", "one authoritative root copy",
        ):
            self.assertIn(required, machine, required)
        for required in (
            "appendix root submission asset", "普通审计/复现结果", "一个权威根副本",
            "appendix/problems/qN/result/", "appendix/Result.xlsx",
        ):
            self.assertIn(required, appendix, required)
        for required in ("人工视觉复核", "COPY/SHA-256", "XLSX/文本基本可读性"):
            self.assertIn(required, result, required)
        self.assertNotIn("所有结果都移到", appendix)
        self.assertNotIn("Result.xlsx 是唯一", appendix)

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
        self.assertEqual(hashlib.sha256(reference.read_bytes()).hexdigest(), "15cd5504622803ae06246f5aa7ee207bdaab7fe3d170fde93358b9466bfe483b")
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

    def test_normal_figure_authority_and_optional_specialist_boundary(self):
        active_paths = (
            SKILL / "SKILL.md", SKILL / "README.md", SKILL / "docs/protocol.md",
            SKILL / "agents/openai.yaml", SKILL / "references/final_figure_execution.md",
            SKILL / "references/final_figure_typography.md", ROOT / "README.md",
            ROOT / "docs/installation.md", ROOT / "docs/known-limitations.md",
            ROOT / "docs/release-checklist.md", ROOT / "docs/system-dependencies.md",
        )
        active = "\n".join(path.read_text(encoding="utf-8") for path in active_paths)
        for required in (
            "figure_exec.py", "ChatGPT/user", "semantic and visual", "optional",
            "explicit", "read-only", "advisory", "rerender", "restyle", "export",
            "overwrite", "recommendations return to Codex", "hard audit again",
        ):
            self.assertIn(required.lower(), active.lower(), required)
        for forbidden in (
            "before calling the external `nature-figure` Skill",
            "use `nature-figure` for semantic",
            "final figures require an explicit user request and the separately installed `nature-figure` Skill",
            "install the separate `nature-figure` Skill for semantic and visual audit",
            "`nature-figure` remains responsible for complex mixed-text routing",
        ):
            self.assertNotIn(forbidden, active, forbidden)
        executor = (SKILL / "figure_exec.py").read_text(encoding="utf-8")
        self.assertNotIn("nature-figure", executor)
        self.assertNotIn("nature_figure", executor)
        self.assertFalse((SKILL / "skills/nature-figure").exists())

    def test_final_figure_typography_contract_is_exact_and_fail_closed(self):
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
            "ASCII punctuation", "Math formulas", "Mixed titles", "script-aware helper",
            "stop the formal final-figure task", "silent fallback", "download a font",
            "copy it from another directory", "font binary", "preview/non-final",
            "nature-figure", "core CLI/runtime does not render figures", "injected resolver seam",
            "minimum routing probe", "PDF and PNG", "user-requested different font",
            "font_kwargs(role, script=\"mixed\")", "declared-family audit",
            "does not prove the exact physical font file", "read-only specialist",
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

    def test_frozen_final_figure_rules_and_optional_executor_are_documented(self):
        core = (SKILL / "references/final_figure_core_rules.md").read_text(encoding="utf-8")
        selection = (SKILL / "references/final_figure_selection.md").read_text(encoding="utf-8")
        style = (SKILL / "references/final_figure_style.md").read_text(encoding="utf-8")
        color = (SKILL / "references/final_figure_color.md").read_text(encoding="utf-8")
        execution = (SKILL / "references/final_figure_execution.md").read_text(encoding="utf-8")
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        protocol = (SKILL / "docs/protocol.md").read_text(encoding="utf-8")
        agent = (SKILL / "agents/openai.yaml").read_text(encoding="utf-8")
        checklist = (ROOT / "docs/release-checklist.md").read_text(encoding="utf-8")

        for name in (
            "final_figure_core_rules.md", "final_figure_selection.md", "final_figure_style.md",
            "final_figure_color.md", "final_figure_typography.md", "final_figure_execution.md",
            "final_figure_3d.md",
        ):
            self.assertIn(name, skill)
            self.assertIn(name, protocol)
            self.assertIn(name, agent)

        for required in (
            "no figure title", "PDF + PNG + PY + TXT", "kymcm-flowchart-selection-v1.md",
            "kymcm-flowchart-content-v1.md", "human author owns final layout",
        ):
            self.assertIn(required, core, required)
        for required in (
            "160 × 60 mm", "160 × 80 mm", "160 × 105 mm", "128 × 80 mm",
            "9.5 pt", "8.5 pt", "8 pt", "FIGURE_STYLE_V1", "600 dpi",
            'bbox_inches="tight"', "showfliers=False", "rasterized=True",
        ):
            self.assertIn(required, style, required)
        for required in (
            "#264653", "#E76F51", "#A61B29", "#D9D9D9",
            "KY_MCM_QUALITATIVE_V1", "batlow", "vik", "TwoSlopeNorm",
            "qualitative_colors(n)", "semantic_color(role)",
        ):
            self.assertIn(required, color, required)

        for required in (
            "kymcm-figure-exec-v1", "configure_matplotlib()", "apply_axis_style()",
            "save_formal_figure()", "Machine-enforced rules", "Semantic and visual review",
            "eight commands", "standard-library-only",
        ):
            self.assertIn(required, execution, required)
        for required in (
            "ChatGPT/user performs semantic and visual review", "nature-figure` is not required",
            "read-only", "advisory only", "Recommendations return to Codex",
        ):
            self.assertIn(required, execution, required)

        runtime = "\n".join(path.read_text(encoding="utf-8") for path in SCRIPTS.rglob("*.py"))
        for forbidden in ("matplotlib", "cmcrameri", "FIGURE_STYLE_V1", "KY_MCM_FIGURE_COLOR_V1"):
            self.assertNotIn(forbidden, runtime, forbidden)
        self.assertNotIn("FIGURE_SELECTION_V1", runtime)
        self.assertNotIn("kymcm-figure-selection-v1", runtime)

        for required in (
            "kymcm-figure-selection-v1", "FIGURE_SELECTION_V1",
            "levels = [L0, L1, L2, L3]", "L0 — prose or table",
            "L1 — base chart", "L2 — enhanced chart", "L3 — Figure Group",
            "comparison", "model_relation", "distribution", "uncertainty",
            "density_or_spatial_structure", "extra_continuous_dimension",
            "diagnostic", "crowding",
            "branches = [trend, category_comparison, bivariate_relation, distribution",
            "matrix, spatial, sensitivity, forecasting, diagnostics]",
            "multi_line | small_multiples | conditional_surface_or_contour",
            "sorted_horizontal_bar | grouped_bar | boxplot",
            "relation_overlay | redundant_category_encoding | facets | density_representation",
            "histogram_plus_KDE | KDE_or_faceted_density | boxplot",
            "heatmap | annotated_heatmap | shared_scale_heatmap_group",
            "categorized_scatter | density_map | same_basemap_small_multiples",
            "multi_line | small_multiples | conditional_response_or_feasible_region",
            "prediction_line | interval_band | small_multiples_or_facets",
            "residual_diagnostic | conditional_QQ | conditional_residual_vs_fitted",
            "### Spatial data", "L1 map + points", "L2 categorized spatial scatter",
            "L2 heat/density map", "L3 same-basemap small multiples",
            "conditional L2 2D density or 3D density surface",
            "violin plot", "raincloud plot", "ECDF", "forest plot", "Pareto front",
            "PR curve", "calibration curve", "classification-evaluation hierarchy", "ridgeline",
            "visual complexity != information value", "WHAT / WHEN", "HOW",
        ):
            self.assertIn(required, selection, required)

        self.assertIn("references/final_figure_selection.md", skill)
        self.assertIn("references/final_figure_style.md", protocol)
        self.assertIn("final_figure_selection.md", agent)
        self.assertIn("tool-routing design", core)
        self.assertIn("human author owns final layout", core)
        for required in (
            "For spatial data, selection-v1 governs WHAT/WHEN expression-level choice",
            "map + points", "categorized spatial views", "density views",
            "same-basemap small multiples", "conditional density surfaces",
            "does not choose a mapping library", "dedicated PyVista executor",
            "Ordinary Cartesian Pt2 geometry does not silently govern map or VTK geometry",
            "flowcharts use `kymcm-flowchart-selection-v1.md` followed by `kymcm-flowchart-content-v1.md`",
            "Manually edited structural illustrations remain outside automatic data-chart selection",
        ):
            self.assertIn(required, core, required)
        self.assertNotIn(
            "selection/style/color contracts do not silently govern flowcharts, maps",
            core,
        )

        for surface in (protocol, checklist):
            normalized = surface.lower()
            for required in (
                "lowest adequate level from the actual information need",
                "l0 and l1 require no enhancement trigger",
                "an l2 upgrade requires an applicable named selection-v1 trigger",
                "l3 requires a coherent shared conclusion and complementary evidence",
                "enhanced panel retains its applicable trigger rationale",
            ):
                self.assertIn(required, normalized, required)
            for stale in (
                "choose what/when at l0/l1/l2/l3 from a named enhancement trigger",
                "choose l0/l1/l2/l3 from a real enhancement trigger",
                "choose l0/l1/l2/l3 from one of eight evidence triggers",
            ):
                self.assertNotIn(stale, normalized, stale)
        normalized_agent = agent.lower()
        for required in (
            "lowest adequate level from the actual information need",
            "l0/l1 need no trigger", "l2 needs one of the existing eight triggers",
            "l3 needs coherent complementary evidence",
        ):
            self.assertIn(required, normalized_agent, required)

        notes = (ROOT / "docs/lite-v3-release-notes.md").read_text(encoding="utf-8")
        current_notes = notes.split("# KyMCM Lite 0.9.12", 1)[0]
        for required in (
            "same-stem four-file bundle", "PyVista/VTK", "SSAA",
            "not decorative", "mplot3d", "flowchart",
        ):
            self.assertIn(required.lower(), current_notes.lower())

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

    def test_0913_bundle_and_intrinsic_3d_contract_is_scoped(self):
        bundle = (SKILL / "figure_bundle.py").read_text(encoding="utf-8")
        executor = (SKILL / "figure_3d_exec.py").read_text(encoding="utf-8")
        selection = (SKILL / "references/final_figure_selection.md").read_text(encoding="utf-8")
        three_d = (SKILL / "references/final_figure_3d.md").read_text(encoding="utf-8")
        core = (SKILL / "references/final_figure_core_rules.md").read_text(encoding="utf-8")
        requirements = (SKILL / "requirements-figure-3d.txt").read_text(encoding="utf-8")
        active = "\n".join((
            (SKILL / "SKILL.md").read_text(encoding="utf-8"),
            (SKILL / "docs/protocol.md").read_text(encoding="utf-8"),
            (SKILL / "agents/openai.yaml").read_text(encoding="utf-8"),
            core, selection, three_d,
        ))

        self.assertIn('BUNDLE_ID = "kymcm-figure-bundle-v1"', bundle)
        self.assertIn('EXECUTION_3D_ID = "kymcm-figure-3d-exec-v1"', executor)
        self.assertEqual(requirements, (
            "-r requirements-figure.txt\n"
            "pyvista>=0.48,<0.49\n"
            "vtk>=9.5,<9.6\n"
        ))
        for required in (
            "PDF/PNG/PY/TXT", "same-stem", "图题：", "图注：",
            "figure_bundle.py", "figure_3d_exec.py", "PyVista", "intrinsic-3D",
            "off-screen", "SSAA", "explicit camera", "raster", "mplot3d",
            "human-owned", "eight commands",
        ):
            self.assertIn(required.lower(), active.lower(), required)
        self.assertIn("not a ninth enhancement trigger", selection)
        self.assertIn("3D bars", selection)
        self.assertIn("contour, aligned slices, heatmap, or small multiples", selection)
        trigger_block = selection.split("The only automatic v1 trigger vocabulary is:", 1)[1].split("```", 2)[1]
        trigger_lines = [line for line in trigger_block.splitlines() if line.strip() and line.strip() != "text"]
        self.assertEqual(len(trigger_lines), 8)
        self.assertNotIn("\n3d\n", trigger_block.lower())
        self.assertIn("outside the four-file programmatic bundle requirement", core)
        self.assertNotIn("mplot3d", executor.lower())
        self.assertNotIn('projection="3d"', executor)
        self.assertNotIn("chart-template", bundle.lower())
        self.assertNotIn("json", bundle.split("class FigureBundleError", 1)[0].lower())

        runtime = "\n".join(path.read_text(encoding="utf-8") for path in SCRIPTS.rglob("*.py"))
        for forbidden in ("figure_bundle", "figure_3d_exec", "pyvista", "vtk"):
            self.assertNotIn(forbidden, runtime)
        self.assertEqual(
            hashlib.sha256((SKILL / "figure_exec.py").read_bytes()).hexdigest(),
            "ce9c984d09d15a07d19d6ac22d8c99dd8aefbf0cb0f155fd25f727d119bb47ab",
        )

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
        self.assertIn("KyMCM Lite 0.10.2", notes)
        for required in (
            "KyMCM Lite 0.9.11", "KyMCM Lite 0.9.10", "KyMCM Lite 0.9.9", "KyMCM Lite 0.9.8", "KyMCM Lite 0.9.7", "KyMCM Lite 0.9.6", "KyMCM Lite 0.9.5", "KyMCM Lite 0.9.4", "KyMCM Lite 0.9.3", "KyMCM Lite 0.9.2", "KyMCM Lite 0.9.1", "KyMCM Lite 0.9.0", "0.8.1", "0.8.0", "0.7.0", "0.6.0", "0.5.1", "0.5.0", "0.4.0", "0.3.1", "0.3.0", "0.2.0", "0.1.0", "Python 3.11", "3.12", "3.13",
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
            "kymcm-figure-selection-v1", "kymcm-figure-exec-v1", "kymcm-figure-style-v1", "kymcm-figure-color-v1", "PDF/PNG-only",
            "kymcm-figure-3d-v1", "kymcm-figure-3d-exec-v1", "same-stem four-file bundle",
            "PyVista/VTK", "SSAA", "mplot3d", "rasterized scene content",
        ):
            self.assertIn(required, notes)

    def test_changelogs_have_dated_release(self):
        for relative in ("CHANGELOG.md", "skills/kymcm-lite/CHANGELOG.md"):
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn("0.10.2 - 2026-09-06", text, relative)
            self.assertIn("0.10.1 - 2026-08-23", text, relative)
            self.assertIn("0.10.0 - 2026-08-22", text, relative)
            self.assertIn("0.9.14 - 2026-08-19", text, relative)
            self.assertIn("0.9.13 - 2026-08-19", text, relative)
            self.assertIn("0.9.12 - 2026-08-16", text, relative)
            self.assertIn("0.9.11 - 2026-08-16", text, relative)
            self.assertIn("0.9.10 - 2026-08-12", text, relative)
            self.assertIn("0.9.9 - 2026-08-12", text, relative)
            self.assertIn("0.9.8 - 2026-08-10", text, relative)
            self.assertIn("0.9.7 - 2026-08-09", text, relative)
            self.assertIn("0.9.5 - 2026-08-04", text, relative)
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
