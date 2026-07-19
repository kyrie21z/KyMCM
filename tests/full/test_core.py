import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "skills/kymcm-full/scripts"))

from checkpoint_full.core import LiteValidationError, ModelSpec, spec_hash
from tests.full.helpers import model_spec, model_spec_with_alternatives, result


class ModelSpecTests(unittest.TestCase):
    def test_hash_is_stable_across_mapping_key_order(self):
        first = model_spec(data_semantics={"observation_unit": "row", "response": "y"})
        second = model_spec(data_semantics={"response": "y", "observation_unit": "row"})
        self.assertEqual(first.hash, second.hash)
        self.assertEqual(len(first.hash), 64)

    def test_hash_excludes_revision_but_payload_keeps_it(self):
        first = model_spec(revision=1)
        second = model_spec(revision=2)
        self.assertEqual(first.hash, second.hash)
        self.assertEqual(first.hash, spec_hash(first.payload()))
        self.assertEqual(first.payload()["revision"], 1)
        self.assertNotIn("revision", first.semantic_payload())

    def test_hash_changes_only_for_mathematical_content(self):
        baseline = model_spec()
        candidates = (
            model_spec(objective="Minimize loss."),
            model_spec(model={"method": "robust score", "formal_definition": "min_w S(w)"}),
            model_spec(decision_rules=({"metric": "loss", "rule": "smaller is better"},)),
        )
        for candidate in candidates:
            with self.subTest(candidate=candidate):
                self.assertNotEqual(baseline.hash, candidate.hash)

    def test_list_order_is_semantic(self):
        first = model_spec(assumptions=("A", "B"))
        second = model_spec(assumptions=("B", "A"))
        self.assertNotEqual(first.hash, second.hash)

    def test_rejects_invalid_structure_and_nonfinite_number(self):
        cases = [
            {"problem": 0},
            {"data_semantics": {}},
            {"schema_version": 1},
            {"decision_rules": ({"metric": "m"},)},
            {"required_outputs": ()},
            {"required_outputs": (
                {"name": "x", "definition": "x", "unit": "m"},
                {"name": "x", "definition": "x2", "unit": "m"},
            )},
            {"data_semantics": {"observation_unit": "row", "bad": math.nan}},
            {"model": {"method": "M", "formal_definition": "x", "python_api": "solve"}},
        ]
        for changes in cases:
            with self.subTest(changes=changes), self.assertRaises(LiteValidationError):
                model_spec(**changes)

    def test_mapping_hash_rejects_infinity(self):
        with self.assertRaises(LiteValidationError):
            spec_hash({"x": math.inf})

    def test_v3_requires_complete_structured_mathematics_but_not_alternatives(self):
        baseline = model_spec().payload()
        self.assertNotIn("alternatives", baseline["model"])
        for field in ("symbols", "formulas", "procedures", "diagnostics", "decision_logic"):
            payload = baseline.copy(); payload["model"] = dict(baseline["model"]); payload["model"][field] = []
            with self.subTest(field=field), self.assertRaises(LiteValidationError):
                ModelSpec(**{**payload, "assumptions": tuple(payload["assumptions"]), "decision_rules": tuple(payload["decision_rules"]), "required_outputs": tuple(payload["required_outputs"])})
        payload = baseline.copy(); payload["model"] = dict(baseline["model"]); payload["model"]["formulas"] = [{"name":"bad","latex":"","meaning":"empty"}]
        with self.assertRaises(LiteValidationError):
            ModelSpec(**{**payload, "assumptions": tuple(payload["assumptions"]), "decision_rules": tuple(payload["decision_rules"]), "required_outputs": tuple(payload["required_outputs"])})

    def test_optional_alternatives_require_a_valid_recommendation_and_rationale(self):
        self.assertEqual(len(model_spec_with_alternatives().model["alternatives"]), 2)
        with self.assertRaises(LiteValidationError):
            model_spec(model={"alternatives": ({"option": "x"},)})
        with self.assertRaises(LiteValidationError):
            model_spec(model={"recommendation": {"option": "x", "reason": "r"}})

    def test_nested_artifact_is_immutable_and_detached_from_input(self):
        model = {"method": "M", "formal_definition": "x", "nested": {"weights": [1, 2]}}
        semantics = {"observation_unit": "row", "nested": {"labels": ["a"]}}
        rules = [{"metric": "m", "rule": "larger", "nested": {"cutoffs": [1]}}]
        outputs = [{"name": "x", "definition": "answer", "unit": "m", "shape": [1, 2]}]
        spec = model_spec(data_semantics=semantics, model=model,
                          decision_rules=tuple(rules), required_outputs=tuple(outputs))
        original_hash = spec.hash
        with self.assertRaises(TypeError):
            spec.model["method"] = "changed"
        with self.assertRaises(TypeError):
            spec.data_semantics["nested"]["labels"] = ()
        with self.assertRaises(TypeError):
            spec.decision_rules[0]["rule"] = "smaller"
        with self.assertRaises(TypeError):
            spec.required_outputs[0]["unit"] = "kg"
        model["nested"]["weights"].append(3)
        semantics["nested"]["labels"].append("b")
        rules[0]["nested"]["cutoffs"].append(2)
        outputs[0]["shape"].append(3)
        self.assertEqual(spec.hash, original_hash)

    def test_payload_is_a_deep_mutable_copy(self):
        spec = model_spec(model={"method": "M", "formal_definition": "x", "nested": {"a": [1]}})
        payload = spec.payload()
        payload["model"]["nested"]["a"].append(2)
        self.assertEqual(spec.model["nested"]["a"], (1,))

    def test_rejects_implementation_keys_in_all_semantic_mappings(self):
        for changes in (
            {"data_semantics": {"observation_unit": "row", "python_api": "load"}},
            {"decision_rules": ({"metric": "m", "rule": "r", "function_name": "score"},)},
        ):
            with self.subTest(changes=changes), self.assertRaises(LiteValidationError):
                model_spec(**changes)


class ResultImmutabilityTests(unittest.TestCase):
    def test_v2_is_the_only_supported_result_schema(self):
        self.assertEqual(result().schema_version, 2)
        payload = result().payload()
        payload["schema_version"] = 1
        with self.assertRaises(LiteValidationError):
            result(schema_version=1)
        with self.assertRaises(TypeError):
            from checkpoint_full.core import ResultRecord
            ResultRecord(problem=1, spec_revision=1, spec_hash="a" * 64,
                         claims=(), outputs=(), validation={}, evidence={})

    def test_result_enums_required_text_ids_and_formats_are_validated(self):
        cases = (
            {"direct_answers": ()},
            {"evidence_strength": {"level": "high", "explanation": "x"}},
            {"recommendation": {"status": "maybe", "reason": "x", "required_actions": ()}},
            {"recommendation": {"status": "revise", "reason": "x", "required_actions": ()}},
            {"validations": ({"id": "v", "name": "v", "status": "unknown", "summary": "x",
                               "details": "x", "is_key": True, "evidence_ids": ()},)},
            {"key_values": ({"id": "x", "label": "x", "value": math.inf, "unit": "u"},)},
            {"key_values": ({"id": "x", "label": "x", "value": 1, "unit": "u",
                              "format": {"decimals": -1}},)},
            {"limitations": ({"id": "same", "summary": "x", "impact": "x", "is_key": True},
                              {"id": "same", "summary": "y", "impact": "y", "is_key": False})},
        )
        for changes in cases:
            with self.subTest(changes=changes), self.assertRaises(LiteValidationError):
                result(**changes)

    def test_result_is_deeply_immutable_and_payload_is_detached(self):
        source_answer = {"question": "Q1-1", "answer": "A", "evidence_ids": ["summary_csv"]}
        source_validation = {"id": "v", "name": "check", "status": "pass",
                             "summary": "ok", "details": "ok", "is_key": True,
                             "evidence_ids": ["summary_csv"]}
        record = result(direct_answers=(source_answer,), validations=(source_validation,))
        with self.assertRaises(TypeError):
            record.direct_answers[0]["answer"] = "changed"
        with self.assertRaises(TypeError):
            record.summary["problem"] = "changed"
        with self.assertRaises(TypeError):
            record.validations[0]["status"] = "fail"
        with self.assertRaises(TypeError):
            record.evidence["input_hash"] = "changed"
        source_answer["evidence_ids"].append("other")
        source_validation["status"] = "fail"
        payload = record.payload()
        payload["direct_answers"][0]["evidence_ids"].append("third")
        payload["validations"][0]["status"] = "fail"
        self.assertEqual(record.direct_answers[0]["evidence_ids"], ("summary_csv",))
        self.assertEqual(record.validations[0]["status"], "pass")


if __name__ == "__main__":
    unittest.main()
