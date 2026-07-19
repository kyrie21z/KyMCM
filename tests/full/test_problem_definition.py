import copy
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "skills/kymcm-full/scripts"))

from checkpoint_full.core import LiteValidationError
from checkpoint_full.problem_definition import (
    DefinitionState, ProblemDefinitionStore, ProblemDefinitionWorkflow,
    definition_from_payload, definition_transition,
)
from checkpoint_full.render import render_problem_definition, render_result_document, render_start_document
from tests.full.helpers import model_spec, model_spec_with_alternatives, result


def payload(**changes):
    value = {
        "schema_version": 3, "revision": 1, "title": "Synthetic whole problem", "overall_objective": "Answer two synthetic questions.",
        "source_data": [{"name": "synthetic.csv", "role": "fixture", "scope": "Q1-Q2"}],
        "subproblems": [
            {"problem": 1, "statement": "Rank items.", "objective": "Produce a ranking.", "inputs": ["data"], "outputs": ["ranking"]},
            {"problem": 2, "statement": "Use ranks.", "objective": "Produce a choice.", "inputs": ["ranking"], "outputs": ["choice"]},
        ],
        "shared_semantics": {"item": "one synthetic alternative"},
        "dependencies": {"1": [], "2": [1]},
        "shared_outputs": [{"name": "ranking", "definition": "Q1 output used by Q2"}],
        "ambiguities": [{"issue":"Dependency interpretation", "resolution":"Q2 consumes Q1 ranking", "impact":"Q1 uncertainty propagates"}],
    }
    value.update(changes)
    return value


class ProblemDefinitionTests(unittest.TestCase):
    def test_hash_excludes_revision_and_content_is_immutable(self):
        first = definition_from_payload(payload())
        second = definition_from_payload(payload(revision=2))
        self.assertEqual(first.hash, second.hash)
        with self.assertRaises(TypeError):
            first.dependencies["2"] = ()
        self.assertEqual(first.topological_order, (1, 2))

    def test_dag_guards(self):
        cases = [
            {"1": []}, {"1": [1], "2": []}, {"1": [3], "2": []}, {"1": [2], "2": [1]},
        ]
        for dependencies in cases:
            with self.subTest(dependencies=dependencies), self.assertRaises(LiteValidationError):
                definition_from_payload(payload(dependencies=dependencies))

    def test_review_workflow(self):
        definition = definition_from_payload(payload())
        flow = definition_transition(ProblemDefinitionWorkflow(), "submit", definition=definition, document_hash="a" * 64)
        self.assertEqual(flow.state, DefinitionState.AWAITING_REVIEW)
        with self.assertRaises(LiteValidationError): definition_transition(flow, "accept", user_message=" ")
        accepted = definition_transition(flow, "accept", user_message="I accept.")
        stale = definition_transition(accepted, "mark-stale", reason="semantic change")
        self.assertEqual(definition_transition(stale, "recover").state, DefinitionState.DRAFT)

    def test_deterministic_markdown_and_storage_roundtrip(self):
        definition = definition_from_payload(payload())
        self.assertEqual(render_problem_definition(definition), render_problem_definition(definition_from_payload(copy.deepcopy(payload()))))
        self.assertIn("已冻结的关键建模取舍", render_problem_definition(definition))
        with tempfile.TemporaryDirectory() as temporary:
            store = ProblemDefinitionStore(temporary)
            flow = definition_transition(ProblemDefinitionWorkflow(), "submit", definition=definition, document_hash="c" * 64)
            store.save_workflow(flow)
            self.assertEqual(store.load_workflow(), flow)

    def test_start_and_result_documents_are_deterministic_and_complete(self):
        definition = definition_from_payload(payload())
        spec = model_spec_with_alternatives()
        start = render_start_document(spec, definition, "Use the synthetic model.")
        self.assertEqual(start, render_start_document(spec, definition, "Use the synthetic model."))
        for heading in ("数学符号表", "LaTeX 公式", "诊断、稳健性和敏感性计划", "判定逻辑", "关键取舍与未决问题", "最终采用方案"):
            self.assertIn(heading, start)
        record = result(spec)
        with tempfile.TemporaryDirectory() as temporary:
            rendered = render_result_document(record, temporary)
            self.assertEqual(rendered, render_result_document(record, temporary))
        for heading in ("结果摘要", "技术分析", "完整验证与敏感性分析", "接受或返工建议"):
            self.assertIn(heading, rendered)

    def test_tradeoff_section_is_always_present_and_has_no_ambiguity_fallback(self):
        definition = definition_from_payload(payload(ambiguities=[]))
        definition_md = render_problem_definition(definition)
        start_md = render_start_document(model_spec(), definition, "Proceed.")
        for document in (definition_md, start_md):
            self.assertIn("关键取舍与未决问题", document)
            self.assertIn("本阶段未发现需要用户裁决的关键建模歧义。", document)


if __name__ == "__main__": unittest.main()
