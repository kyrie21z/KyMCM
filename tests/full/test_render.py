from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "skills/kymcm-full/scripts"))

from checkpoint_full.render import (
    public_status, render_result_brief, render_start_brief, render_start_document,
)
from checkpoint_full.problem_definition import definition_from_payload
from checkpoint_full.workflow import StaleReason, Workflow, WorkflowState
from tests.full.helpers import model_spec, result
from tests.full.test_problem_definition import payload as definition_payload


FORBIDDEN = (
    "exploring", "awaiting_start_review", "running", "waiting_decision",
    "awaiting_result_review", "completed", "stale", "spec_hash", "revision id",
    "decision id", "json schema", ".json", "/", "transition", "render_",
)


class RenderTests(unittest.TestCase):
    def assertPublic(self, text):
        lowered = text.lower()
        for token in FORBIDDEN:
            with self.subTest(token=token):
                self.assertNotIn(token, lowered)

    def test_briefs_have_required_sections_and_no_leaks(self):
        start = render_start_brief(model_spec(), "按加权评分开始")
        outcome = render_result_brief(result())
        for text, phrases in (
            (start, ("我对问题的理解", "建议采用的方法", "我的建议")),
            (outcome, ("直接答案", "关键数值", "证据强度", "建议")),
        ):
            self.assertTrue(all(phrase in text for phrase in phrases))
            self.assertPublic(text)

    def test_every_public_status_is_natural_language(self):
        spec = model_spec()
        for state in WorkflowState:
            if state is WorkflowState.STALE:
                flow = Workflow(1, state=state, spec_revision=spec.revision, spec_hash=spec.hash,
                                stale_reason=StaleReason.RERUN_REQUIRED, stale_source="code change")
            elif state in {WorkflowState.AWAITING_START_REVIEW, WorkflowState.RUNNING,
                           WorkflowState.AWAITING_RESULT_REVIEW, WorkflowState.COMPLETED}:
                flow = Workflow(
                    1, state=state, spec_revision=spec.revision, spec_hash=spec.hash,
                    review_result_hash="b" * 64 if state is WorkflowState.AWAITING_RESULT_REVIEW else None,
                    review_document_hash="c" * 64 if state in {WorkflowState.AWAITING_START_REVIEW, WorkflowState.AWAITING_RESULT_REVIEW} else None,
                )
            else:
                flow = Workflow(1, state=state)
            self.assertPublic(public_status(flow))

    def test_start_document_displays_prestart_audit_and_treatment(self):
        semantics = model_spec().payload()["data_semantics"]
        semantics["prestart_audit"] = {
            "scope": "附件一评分表的样本编号与评分列",
            "checks": ["结构与标识", "主键与配对", "合法范围"],
            "findings": [{
                "location": "样本 7 的评分列", "issue": "存在越界值",
                "treatment": "按缺失值处理并保留样本", "changes_analysis_input": True,
            }],
            "unresolved": [],
        }
        text = render_start_document(
            model_spec(data_semantics=semantics),
            definition_from_payload(definition_payload()), "采用该方案",
        )
        for phrase in (
            "Start 前数据审计与处理规则", "附件一评分表", "结构与标识",
            "样本 7", "存在越界值", "会改变分析输入", "按缺失值处理",
            "**未决问题**：无",
        ):
            self.assertIn(phrase, text)

    def test_start_document_handles_no_findings_and_exposes_unresolved(self):
        clean = render_start_document(
            model_spec(), definition_from_payload(definition_payload()), "采用该方案",
        )
        self.assertIn("未发现需要单独处理的数据异常", clean)
        semantics = model_spec().payload()["data_semantics"]
        semantics["prestart_audit"]["unresolved"] = ["重复样本保留规则待确认"]
        unresolved = render_start_document(
            model_spec(data_semantics=semantics),
            definition_from_payload(definition_payload()), "暂不开始",
        )
        self.assertIn("重复样本保留规则待确认", unresolved)

    def test_missing_audit_renders_predictably_for_legacy_spec(self):
        text = render_start_document(
            model_spec(data_semantics={"observation_unit": "one row"}),
            definition_from_payload(definition_payload()), "不得提交",
        )
        self.assertIn("尚未提供 Start 前数据审计摘要", text)

    def test_result_document_has_two_layers_formatted_values_and_no_duplication(self):
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            output = workspace / "problems/q1/outputs"
            output.mkdir(parents=True)
            (output / "summary.csv").write_text("对象,结果\nA,-2.563978\nB,0.89931\n", encoding="utf-8")
            (output / "detail.csv").write_text("对象,得分\nA,0.89931\nB,0.70001\n", encoding="utf-8")
            (output / "comparison.png").write_bytes(b"png")
            record = result(
                key_values=(
                    {"id": "difference", "label": "平均得分差", "value": -2.563978,
                     "unit": "分", "format": {"decimals": 2}},
                    {"id": "rate", "label": "覆盖率", "value": 0.89931,
                     "unit": "%", "format": {"scale": 100, "decimals": 1}},
                ),
                summary_table_ids=("summary",),
                tables=(
                    {"id": "summary", "title": "关键结果汇总", "source_evidence_id": "summary_csv",
                     "columns": ("对象", "结果"), "max_rows": 1, "sort": None,
                     "formats": {"结果": {"decimals": 2}}},
                    {"id": "detail", "title": "详细结果", "source_evidence_id": "detail_csv",
                     "columns": ("对象", "得分"), "max_rows": 20,
                     "sort": {"column": "得分", "descending": True},
                     "formats": {"得分": {"decimals": 3}}},
                ),
                figures=({"id": "comparison", "source_evidence_id": "comparison_png",
                          "caption": "两组结果比较", "interpretation": "图中差异支持直接答案。"},),
                technical_sections=({"title": "核心证据", "analysis": "详细结果说明排序稳定。",
                                     "table_ids": ("detail",), "figure_ids": ("comparison",),
                                     "evidence_ids": ("detail_csv",)},),
                validations=(
                    {"id": "primary_check", "name": "主要完整性检验", "status": "pass",
                     "summary": "主要结果完整。", "details": "所有关键结果均已生成。",
                     "is_key": True, "evidence_ids": ("summary_csv",)},
                    {"id": "secondary_check", "name": "次要稳健性检验", "status": "pass",
                     "summary": "结论保持不变。", "details": "", "is_key": False,
                     "evidence_ids": ("detail_csv",)},
                    {"id": "no_evidence_check", "name": "无需证据检验", "status": "not_applicable",
                     "summary": "本结果不适用。", "details": "", "is_key": False,
                     "evidence_ids": ()},
                ),
                evidence={"input_hash": "a" * 64, "code_revision": "abc123", "result_hash": "b" * 64,
                          "artifacts": (
                              {"id": "summary_csv", "path": "problems/q1/outputs/summary.csv", "kind": "csv", "purpose": "摘要表"},
                              {"id": "detail_csv", "path": "problems/q1/outputs/detail.csv", "kind": "csv", "purpose": "详细表"},
                              {"id": "comparison_png", "path": "problems/q1/outputs/comparison.png", "kind": "png", "purpose": "比较图"},
                          )},
            )
            from checkpoint_full.render import render_result_document
            text = render_result_document(record, workspace)
        headings = (
            "## 1. 内容导航", "## 2. 结果摘要", "## 3. 技术分析",
            "## 4. 完整验证与敏感性分析", "## 5. 局限与适用范围",
            "## 6. 证据索引", "## 7. 审阅信息",
        )
        self.assertTrue(all(heading in text for heading in headings))
        self.assertEqual(text.count("### 直接答案"), 1)
        self.assertIn("> **Q1-1：** Alternative A ranks first. [E1]", text)
        self.assertIn("- **平均得分差**：-2.56 分", text)
        self.assertIn("- **覆盖率**：89.9%", text)
        self.assertNotIn("-2.563978", text)
        self.assertEqual(text.count("### 关键结果汇总"), 1)
        self.assertEqual(text.count("### 详细结果"), 1)
        self.assertEqual(text.count("![两组结果比较]"), 1)
        self.assertIn("| 验证项 | 状态 | 核心结果 | 证据 |", text)
        self.assertIn("| 次要稳健性检验 | 通过 | 结论保持不变。 | [E2] |", text)
        self.assertIn("| 无需证据检验 | 不适用 | 本结果不适用。 | — |", text)
        self.assertNotIn("### 次要稳健性检验", text)
        self.assertNotIn("<details>", text)
        self.assertNotIn("summary_csv", text)
        self.assertNotIn("detail_csv", text)

    def test_optional_conclusion_headings_are_omitted(self):
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            (workspace / "problems/q1/outputs").mkdir(parents=True)
            record = result(statistical_conclusion=None, operational_conclusion=None)
            text = __import__("checkpoint_full.render", fromlist=["render_result_document"]).render_result_document(record, workspace)
        self.assertNotIn("### 统计结论", text)
        self.assertNotIn("### 操作性结论", text)

    def test_validation_table_rejects_unknown_evidence(self):
        record = result(validations=({
            "id": "unknown_evidence_check", "name": "未知证据检验", "status": "pass",
            "summary": "不应静默渲染。", "details": "", "is_key": False,
            "evidence_ids": ("missing_evidence",),
        },))
        with tempfile.TemporaryDirectory() as temporary, self.assertRaises(ValueError):
            __import__(
                "checkpoint_full.render", fromlist=["render_result_document"],
            ).render_result_document(record, temporary)
