"""Structured semantic validation for Checkpoint Lite."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Mapping

from .core import ModelSpec, ResultRecord


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    path: str
    message: str


@dataclass(frozen=True)
class ValidationReport:
    passed: bool
    errors: tuple[ValidationIssue, ...]


def validate_prestart_audit(spec: ModelSpec) -> ValidationReport:
    """Validate the resolved problem-scoped audit required by Start review."""
    errors: list[ValidationIssue] = []
    base = "data_semantics.prestart_audit"
    audit = spec.data_semantics.get("prestart_audit")

    def issue(code: str, path: str, message: str) -> None:
        errors.append(ValidationIssue(code, path, message))

    if not isinstance(audit, Mapping):
        issue("missing_prestart_audit", base, "Start requires a pre-start data audit summary")
        return ValidationReport(False, tuple(errors))

    scope = audit.get("scope")
    if not isinstance(scope, str) or not scope.strip():
        issue("invalid_audit_scope", f"{base}.scope", "audit scope must be non-empty text")

    checks = audit.get("checks")
    if (not isinstance(checks, (list, tuple)) or not checks or
            any(not isinstance(item, str) or not item.strip() for item in checks)):
        issue("invalid_audit_checks", f"{base}.checks", "audit checks must be a non-empty text array")

    findings = audit.get("findings")
    if not isinstance(findings, (list, tuple)):
        issue("invalid_audit_finding", f"{base}.findings", "audit findings must be an array")
    else:
        for index, finding in enumerate(findings):
            path = f"{base}.findings[{index}]"
            if not isinstance(finding, Mapping):
                issue("invalid_audit_finding", path, "each audit finding must be an object")
                continue
            invalid_text = any(
                not isinstance(finding.get(field), str) or not finding[field].strip()
                for field in ("location", "issue", "treatment")
            )
            if invalid_text or type(finding.get("changes_analysis_input")) is not bool:
                issue(
                    "invalid_audit_finding", path,
                    "finding requires location, issue, treatment, and boolean changes_analysis_input",
                )

    unresolved = audit.get("unresolved")
    if (not isinstance(unresolved, (list, tuple)) or
            any(not isinstance(item, str) or not item.strip() for item in unresolved)):
        issue(
            "invalid_audit_unresolved", f"{base}.unresolved",
            "unresolved must be a text array",
        )
    elif unresolved:
        issue(
            "unresolved_data_issue", f"{base}.unresolved",
            "all data issues must be resolved before Start review",
        )
    return ValidationReport(not errors, tuple(errors))


def _finite_values(value: Any, path: str, errors: list[ValidationIssue]) -> None:
    if isinstance(value, float) and not math.isfinite(value):
        errors.append(ValidationIssue("nonfinite_value", path, "conclusion values must be finite"))
    elif isinstance(value, Mapping):
        for key, child in value.items():
            _finite_values(child, f"{path}.{key}", errors)
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _finite_values(child, f"{path}[{index}]", errors)


def validate_result(
    spec: ModelSpec,
    result: ResultRecord,
) -> ValidationReport:
    errors: list[ValidationIssue] = []

    def issue(code: str, path: str, message: str) -> None:
        errors.append(ValidationIssue(code, path, message))

    if result.problem != spec.problem:
        issue("problem_mismatch", "problem", "result problem does not match Model Spec")
    if result.spec_revision != spec.revision:
        issue("revision_mismatch", "spec_revision", "result revision does not match Model Spec")
    if result.spec_hash != spec.hash:
        issue("spec_hash_mismatch", "spec_hash", "result does not match the active Model Spec")

    artifacts = {
        item["id"]: item for item in result.evidence.get("artifacts", ())
        if isinstance(item, Mapping) and isinstance(item.get("id"), str)
    }
    evidence_ids = set(artifacts)

    def check_evidence_refs(values: Any, path: str) -> None:
        if not isinstance(values, (list, tuple)):
            return
        for index, evidence_id in enumerate(values):
            if evidence_id not in evidence_ids:
                issue("unknown_evidence", f"{path}[{index}]", "reference names unknown evidence")

    for index, answer in enumerate(result.direct_answers):
        check_evidence_refs(answer.get("evidence_ids", ()), f"direct_answers[{index}].evidence_ids")
    for name, conclusion in (
        ("statistical_conclusion", result.statistical_conclusion),
        ("operational_conclusion", result.operational_conclusion),
    ):
        if conclusion is not None:
            check_evidence_refs(conclusion.get("evidence_ids", ()), f"{name}.evidence_ids")
    for index, validation in enumerate(result.validations):
        check_evidence_refs(validation.get("evidence_ids", ()), f"validations[{index}].evidence_ids")
        if validation.get("status") == "fail":
            issue("validation_failed", f"validations[{index}].status",
                  "failed validation blocks formal result review")
    for index, section in enumerate(result.technical_sections):
        check_evidence_refs(section.get("evidence_ids", ()), f"technical_sections[{index}].evidence_ids")

    table_ids = {table["id"] for table in result.tables}
    figure_ids = {figure["id"] for figure in result.figures}
    table_references = list(result.summary_table_ids)
    figure_references: list[str] = []
    for index, section in enumerate(result.technical_sections):
        for table_id in section.get("table_ids", ()):
            if table_id not in table_ids:
                issue("unknown_table", f"technical_sections[{index}].table_ids",
                      "technical section references an unknown table")
            table_references.append(table_id)
        for figure_id in section.get("figure_ids", ()):
            if figure_id not in figure_ids:
                issue("unknown_figure", f"technical_sections[{index}].figure_ids",
                      "technical section references an unknown figure")
            figure_references.append(figure_id)
    for table_id in result.summary_table_ids:
        if table_id not in table_ids:
            issue("unknown_table", "summary_table_ids", "summary references an unknown table")
    for table_id in table_ids:
        count = table_references.count(table_id)
        if count == 0:
            issue("unused_table", "tables", f"table {table_id} is never rendered")
        elif count > 1:
            issue("duplicate_table_reference", "tables", f"table {table_id} is rendered more than once")
    for figure_id in figure_ids:
        count = figure_references.count(figure_id)
        if count == 0:
            issue("unused_figure", "figures", f"figure {figure_id} is never rendered")
        elif count > 1:
            issue("duplicate_figure_reference", "figures", f"figure {figure_id} is rendered more than once")

    for index, table in enumerate(result.tables):
        evidence_id = table["source_evidence_id"]
        artifact = artifacts.get(evidence_id)
        if artifact is None:
            issue("unknown_evidence", f"tables[{index}].source_evidence_id", "table source is unknown")
        elif artifact.get("kind") != "csv":
            issue("invalid_table_evidence", f"tables[{index}].source_evidence_id",
                  "table source evidence must be CSV")
    for index, figure in enumerate(result.figures):
        evidence_id = figure["source_evidence_id"]
        artifact = artifacts.get(evidence_id)
        if artifact is None:
            issue("unknown_evidence", f"figures[{index}].source_evidence_id", "figure source is unknown")
        elif artifact.get("kind") != "png":
            issue("invalid_figure_evidence", f"figures[{index}].source_evidence_id",
                  "figure source evidence must be PNG")

    _finite_values(result.key_values, "key_values", errors)
    for field in ("input_hash", "code_revision", "result_hash"):
        value = result.evidence.get(field)
        if not isinstance(value, str) or not value.strip():
            issue("missing_evidence", f"evidence.{field}", f"evidence requires {field}")
    return ValidationReport(not errors, tuple(errors))
