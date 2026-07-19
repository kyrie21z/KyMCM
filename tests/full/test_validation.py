import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "skills/kymcm-full/scripts"))

from checkpoint_full.core import LiteValidationError
from checkpoint_full.validation import validate_prestart_audit, validate_result
from tests.full.helpers import model_spec, result


class ResultValidationTests(unittest.TestCase):
    def test_valid_result_passes(self):
        self.assertTrue(validate_result(model_spec(), result()).passed)

    def test_reports_all_major_contract_failures(self):
        spec = model_spec()
        bad = result(
            spec, problem=2, spec_revision=2, spec_hash="a" * 64,
            direct_answers=({"question": "Q1-1", "answer": "x", "evidence_ids": ("missing",)},),
            validations=({"id": "failed", "name": "blocking", "status": "fail",
                          "summary": "failed", "details": "must fix", "is_key": True,
                          "evidence_ids": ("missing",)},),
            technical_sections=({"title": "x", "analysis": "x", "table_ids": ("missing",),
                                 "figure_ids": ("missing",), "evidence_ids": ("missing",)},),
            evidence={"artifacts": ()},
        )
        report = validate_result(spec, bad)
        codes = {error.code for error in report.errors}
        self.assertTrue({"problem_mismatch", "revision_mismatch", "spec_hash_mismatch",
                         "unknown_table", "unknown_figure", "unknown_evidence",
                         "validation_failed", "missing_evidence"} <= codes)

    def test_result_does_not_depend_on_decision_log(self):
        spec = model_spec()
        record = result(spec)
        self.assertTrue(validate_result(spec, record).passed)

    def test_record_constructor_rejects_nonfinite_key_value(self):
        with self.assertRaises(LiteValidationError):
            result(key_values=({"id": "x", "label": "x", "value": math.inf, "unit": "u"},))

    def test_unknown_and_duplicate_references_fail(self):
        duplicate = result(
            tables=({"id": "table", "title": "T", "source_evidence_id": "summary_csv",
                     "columns": ("name",), "max_rows": 10, "sort": None, "formats": {}},),
            summary_table_ids=("table",),
            technical_sections=({"title": "x", "analysis": "x", "table_ids": ("table",),
                                 "figure_ids": (), "evidence_ids": ()},),
        )
        report = validate_result(model_spec(), duplicate)
        self.assertIn("duplicate_table_reference", {error.code for error in report.errors})

    def test_warning_is_reviewable_with_explanation_but_fail_blocks(self):
        warning = result(validations=({
            "id": "v", "name": "sensitivity", "status": "warning", "summary": "borderline",
            "details": "The rank changes only at an extreme weight.", "is_key": True,
            "evidence_ids": ("summary_csv",),
        },))
        self.assertTrue(validate_result(model_spec(), warning).passed)
        failing = result(validations=({
            "id": "v", "name": "sensitivity", "status": "fail", "summary": "failed",
            "details": "The planned check failed.", "is_key": True,
            "evidence_ids": ("summary_csv",),
        },))
        self.assertIn("validation_failed", {x.code for x in validate_result(model_spec(), failing).errors})

    def test_optional_conclusions_may_be_absent(self):
        record = result(statistical_conclusion=None, operational_conclusion=None)
        self.assertTrue(validate_result(model_spec(), record).passed)


class PrestartAuditValidationTests(unittest.TestCase):
    def codes_and_paths(self, spec):
        return {(error.code, error.path) for error in validate_prestart_audit(spec).errors}

    def semantics(self, audit):
        return {"observation_unit": "one row", "quality_control": "Use reviewed rules.",
                "prestart_audit": audit}

    def test_valid_audit_passes_and_is_bound_by_spec_hash(self):
        first = model_spec()
        changed_semantics = first.payload()["data_semantics"]
        changed_semantics["prestart_audit"] = {
            "scope": "fixture input table",
            "checks": ["structure", "missingness", "range"],
            "findings": [{
                "location": "row 7", "issue": "out-of-range marker",
                "treatment": "treat as missing", "changes_analysis_input": True,
            }],
            "unresolved": [],
        }
        changed = model_spec(data_semantics=changed_semantics)
        self.assertTrue(validate_prestart_audit(first).passed)
        self.assertNotEqual(first.hash, changed.hash)

    def test_missing_audit_fails_without_breaking_model_spec_loading(self):
        spec = model_spec(data_semantics={"observation_unit": "one row"})
        self.assertIn(
            ("missing_prestart_audit", "data_semantics.prestart_audit"),
            self.codes_and_paths(spec),
        )

    def test_scope_checks_and_finding_shape_are_validated(self):
        cases = (
            ({"scope": "", "checks": ["structure"], "findings": [], "unresolved": []},
             "invalid_audit_scope"),
            ({"scope": "table", "checks": [], "findings": [], "unresolved": []},
             "invalid_audit_checks"),
            ({"scope": "table", "checks": ["structure"], "findings": ["bad"], "unresolved": []},
             "invalid_audit_finding"),
            ({"scope": "table", "checks": ["structure"], "findings": [{
                "location": "row 1", "issue": "bad", "changes_analysis_input": True,
            }], "unresolved": []}, "invalid_audit_finding"),
            ({"scope": "table", "checks": ["structure"], "findings": [{
                "location": "row 1", "issue": "bad", "treatment": "drop",
                "changes_analysis_input": 1,
            }], "unresolved": []}, "invalid_audit_finding"),
        )
        for audit, code in cases:
            with self.subTest(code=code):
                self.assertIn(code, {item[0] for item in self.codes_and_paths(
                    model_spec(data_semantics=self.semantics(audit))
                )})

    def test_unresolved_must_be_string_array_and_empty(self):
        invalid = model_spec(data_semantics=self.semantics({
            "scope": "table", "checks": ["structure"], "findings": [],
            "unresolved": "choose duplicate policy",
        }))
        blocked = model_spec(data_semantics=self.semantics({
            "scope": "table", "checks": ["structure"], "findings": [],
            "unresolved": ["choose duplicate policy"],
        }))
        self.assertIn("invalid_audit_unresolved", {x[0] for x in self.codes_and_paths(invalid)})
        self.assertIn("unresolved_data_issue", {x[0] for x in self.codes_and_paths(blocked)})
