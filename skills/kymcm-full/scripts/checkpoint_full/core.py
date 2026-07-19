"""Small immutable artifacts for the standalone Checkpoint Lite MVP."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from types import MappingProxyType
from typing import Any, Mapping


class LiteValidationError(ValueError):
    """An artifact violates the Checkpoint Lite contract."""


_IMPLEMENTATION_KEYS = {
    "api", "api_name", "cache", "cache_config", "callable", "function",
    "function_name", "python_api",
}


def _freeze_json(value: Any) -> Any:
    """Recursively detach and freeze a JSON-like value."""
    if isinstance(value, Mapping):
        return MappingProxyType({key: _freeze_json(child) for key, child in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze_json(child) for child in value)
    return value


def _thaw_json(value: Any) -> Any:
    """Return a detached ordinary JSON-compatible copy."""
    if isinstance(value, Mapping):
        return {key: _thaw_json(child) for key, child in value.items()}
    if isinstance(value, (list, tuple)):
        return [_thaw_json(child) for child in value]
    return value


def _require_positive_int(value: Any, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise LiteValidationError(f"{name} must be a positive integer")


def _require_text(value: Any, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise LiteValidationError(f"{name} must be a non-empty string")


def ensure_json_value(value: Any, path: str = "value") -> None:
    """Reject non-JSON values and non-finite numbers recursively."""
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise LiteValidationError(f"{path} must contain finite numbers")
        return
    if isinstance(value, Mapping):
        for key, child in value.items():
            if not isinstance(key, str):
                raise LiteValidationError(f"{path} object keys must be strings")
            ensure_json_value(child, f"{path}.{key}")
        return
    if isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            ensure_json_value(child, f"{path}[{index}]")
        return
    raise LiteValidationError(f"{path} contains unsupported value {type(value).__name__}")


def _reject_implementation_details(value: Any, path: str) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if key.lower() in _IMPLEMENTATION_KEYS:
                raise LiteValidationError(f"{path}.{key} is an implementation detail, not mathematics")
            _reject_implementation_details(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_implementation_details(child, f"{path}[{index}]")


@dataclass(frozen=True)
class ModelSpec:
    schema_version: int
    problem: int
    revision: int
    objective: str
    data_semantics: Mapping[str, Any]
    assumptions: tuple[str, ...]
    model: Mapping[str, Any]
    decision_rules: tuple[Mapping[str, Any], ...]
    required_outputs: tuple[Mapping[str, Any], ...]

    def __post_init__(self) -> None:
        if self.schema_version != 3:
            raise LiteValidationError("Model Spec schema_version must be 3")
        _require_positive_int(self.problem, "problem")
        _require_positive_int(self.revision, "revision")
        _require_text(self.objective, "objective")
        ensure_json_value(self.payload())
        observation_unit = self.data_semantics.get("observation_unit")
        _require_text(observation_unit, "data_semantics.observation_unit")
        _require_text(self.model.get("method"), "model.method")
        _require_text(self.model.get("formal_definition"), "model.formal_definition")
        self._validate_structured_model()
        for field_name in ("data_semantics", "model", "decision_rules", "required_outputs"):
            _reject_implementation_details(getattr(self, field_name), field_name)
        for index, assumption in enumerate(self.assumptions):
            _require_text(assumption, f"assumptions[{index}]")
        for index, rule in enumerate(self.decision_rules):
            _require_text(rule.get("metric"), f"decision_rules[{index}].metric")
            _require_text(rule.get("rule"), f"decision_rules[{index}].rule")
        if not self.required_outputs:
            raise LiteValidationError("required_outputs must not be empty")
        names = []
        for index, output in enumerate(self.required_outputs):
            for field in ("name", "definition", "unit"):
                _require_text(output.get(field), f"required_outputs[{index}].{field}")
            _reject_implementation_details(output, f"required_outputs[{index}]")
            names.append(output["name"])
        if len(names) != len(set(names)):
            raise LiteValidationError("required output names must be unique")
        for field_name in (
            "data_semantics", "assumptions", "model", "decision_rules",
            "required_outputs",
        ):
            object.__setattr__(self, field_name, _freeze_json(getattr(self, field_name)))

    def _validate_structured_model(self) -> None:
        required_sequences = ("symbols", "formulas", "procedures", "diagnostics")
        for key in required_sequences:
            value = self.model.get(key)
            if not isinstance(value, (list, tuple)) or not value:
                raise LiteValidationError(f"model.{key} must be a non-empty array")
        hypotheses = self.model.get("hypotheses")
        if not isinstance(hypotheses, (list, tuple)):
            raise LiteValidationError("model.hypotheses must be an array")
        if not isinstance(self.model.get("decision_logic"), (list, tuple)) or not self.model["decision_logic"]:
            raise LiteValidationError("model.decision_logic must be a non-empty array")
        fields = {
            "symbols": ("symbol", "meaning"),
            "formulas": ("name", "latex", "meaning"),
            "hypotheses": ("name", "null", "alternative", "scope"),
            "procedures": ("step", "mathematical_action", "output"),
            "diagnostics": ("target", "method", "pass_rule", "failure_action"),
        }
        for key, required in fields.items():
            for index, item in enumerate(self.model[key]):
                if not isinstance(item, Mapping):
                    raise LiteValidationError(f"model.{key}[{index}] must be an object")
                for field in required:
                    _require_text(item.get(field), f"model.{key}[{index}].{field}")
        for index, rule in enumerate(self.model["decision_logic"]):
            if isinstance(rule, str):
                _require_text(rule, f"model.decision_logic[{index}]")
            elif isinstance(rule, Mapping):
                _require_text(rule.get("condition"), f"model.decision_logic[{index}].condition")
                _require_text(rule.get("conclusion"), f"model.decision_logic[{index}].conclusion")
            else:
                raise LiteValidationError(f"model.decision_logic[{index}] must be text or an object")
        alternatives = self.model.get("alternatives", ())
        if not isinstance(alternatives, (list, tuple)):
            raise LiteValidationError("model.alternatives must be an array")
        names: list[str] = []
        for index, item in enumerate(alternatives):
            if not isinstance(item, Mapping):
                raise LiteValidationError(f"model.alternatives[{index}] must be an object")
            for field in ("option", "mathematical_meaning", "applicability", "advantages", "disadvantages", "result_impact"):
                _require_text(item.get(field), f"model.alternatives[{index}].{field}")
            names.append(item["option"])
        if len(names) != len(set(names)):
            raise LiteValidationError("model.alternatives names must be unique")
        recommendation = self.model.get("recommendation")
        rationale = self.model.get("selection_rationale")
        if alternatives:
            if not isinstance(recommendation, Mapping):
                raise LiteValidationError("model.recommendation must be an object when alternatives exist")
            _require_text(recommendation.get("option"), "model.recommendation.option")
            _require_text(recommendation.get("reason"), "model.recommendation.reason")
            if recommendation["option"] not in names:
                raise LiteValidationError("model.recommendation must reference an alternative")
            _require_text(rationale, "model.selection_rationale")
        elif recommendation not in (None, {}) or rationale not in (None, ""):
            raise LiteValidationError("recommendation and selection_rationale require alternatives")

    def payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "problem": self.problem,
            "revision": self.revision,
            "objective": self.objective,
            "data_semantics": _thaw_json(self.data_semantics),
            "assumptions": _thaw_json(self.assumptions),
            "model": _thaw_json(self.model),
            "decision_rules": _thaw_json(self.decision_rules),
            "required_outputs": _thaw_json(self.required_outputs),
        }
    def semantic_payload(self) -> dict[str, Any]:
        """Return the mathematical content, excluding revision metadata."""
        payload = self.payload()
        del payload["revision"]
        return payload

    @property
    def hash(self) -> str:
        return spec_hash(self)


def spec_hash(spec: ModelSpec | Mapping[str, Any]) -> str:
    """Hash semantic content; full Model Spec mappings ignore top-level revision."""
    payload = spec.semantic_payload() if isinstance(spec, ModelSpec) else _thaw_json(spec)
    semantic_fields = {
        "problem", "objective", "data_semantics", "assumptions", "model",
        "decision_rules", "required_outputs",
    }
    if isinstance(payload, dict) and semantic_fields <= payload.keys():
        payload.pop("revision", None)
    ensure_json_value(payload)
    encoded = json.dumps(
        payload, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class ResultRecord:
    schema_version: int
    problem: int
    spec_revision: int
    spec_hash: str
    summary: Mapping[str, Any]
    direct_answers: tuple[Mapping[str, Any], ...]
    statistical_conclusion: Mapping[str, Any] | None
    operational_conclusion: Mapping[str, Any] | None
    key_values: tuple[Mapping[str, Any], ...]
    evidence_strength: Mapping[str, Any]
    recommendation: Mapping[str, Any]
    summary_table_ids: tuple[str, ...]
    tables: tuple[Mapping[str, Any], ...]
    figures: tuple[Mapping[str, Any], ...]
    technical_sections: tuple[Mapping[str, Any], ...]
    validations: tuple[Mapping[str, Any], ...]
    limitations: tuple[Mapping[str, Any], ...]
    evidence: Mapping[str, Any]

    def __post_init__(self) -> None:
        if self.schema_version != 2:
            raise LiteValidationError("ResultRecord schema_version must be 2")
        _require_positive_int(self.problem, "problem")
        _require_positive_int(self.spec_revision, "spec_revision")
        self._require_sha256(self.spec_hash, "spec_hash")
        ensure_json_value(self.payload())
        self._validate_summary()
        self._validate_answers_and_conclusions()
        self._validate_key_values()
        self._validate_review_fields()
        self._validate_tables_and_figures()
        self._validate_analysis()
        self._validate_evidence()
        for field_name in (
            "summary", "direct_answers", "statistical_conclusion", "operational_conclusion",
            "key_values", "evidence_strength", "recommendation", "summary_table_ids",
            "tables", "figures", "technical_sections", "validations", "limitations", "evidence",
        ):
            object.__setattr__(self, field_name, _freeze_json(getattr(self, field_name)))

    @staticmethod
    def _require_sha256(value: Any, name: str) -> None:
        if not isinstance(value, str) or len(value) != 64:
            raise LiteValidationError(f"{name} must be a SHA-256 hex digest")
        try:
            int(value, 16)
        except ValueError as exc:
            raise LiteValidationError(f"{name} must be a SHA-256 hex digest") from exc

    @staticmethod
    def _require_text_array(value: Any, name: str) -> None:
        if not isinstance(value, (list, tuple)):
            raise LiteValidationError(f"{name} must be an array")
        for index, item in enumerate(value):
            _require_text(item, f"{name}[{index}]")

    @staticmethod
    def _require_bool(value: Any, name: str) -> None:
        if type(value) is not bool:
            raise LiteValidationError(f"{name} must be boolean")

    @staticmethod
    def _validate_format(value: Any, name: str) -> None:
        if value is None:
            return
        if not isinstance(value, Mapping):
            raise LiteValidationError(f"{name} must be an object")
        unknown = set(value) - {"decimals", "scale"}
        if unknown:
            raise LiteValidationError(f"{name} contains unsupported rules")
        if "decimals" in value:
            decimals = value["decimals"]
            if isinstance(decimals, bool) or not isinstance(decimals, int) or not 0 <= decimals <= 15:
                raise LiteValidationError(f"{name}.decimals must be an integer from 0 to 15")
        if "scale" in value:
            scale = value["scale"]
            if isinstance(scale, bool) or not isinstance(scale, (int, float)) or not math.isfinite(scale):
                raise LiteValidationError(f"{name}.scale must be a finite number")

    @staticmethod
    def _unique_ids(items: Any, name: str) -> set[str]:
        if not isinstance(items, (list, tuple)):
            raise LiteValidationError(f"{name} must be an array")
        ids: list[str] = []
        for index, item in enumerate(items):
            if not isinstance(item, Mapping):
                raise LiteValidationError(f"{name}[{index}] must be an object")
            _require_text(item.get("id"), f"{name}[{index}].id")
            ids.append(item["id"])
        if len(ids) != len(set(ids)):
            raise LiteValidationError(f"{name} ids must be unique")
        return set(ids)

    def _validate_summary(self) -> None:
        if not isinstance(self.summary, Mapping):
            raise LiteValidationError("summary must be an object")
        for field in ("problem", "method", "decision_basis"):
            _require_text(self.summary.get(field), f"summary.{field}")

    def _validate_answers_and_conclusions(self) -> None:
        if not isinstance(self.direct_answers, (list, tuple)) or not self.direct_answers:
            raise LiteValidationError("direct_answers must contain at least one answer")
        questions: list[str] = []
        for index, answer in enumerate(self.direct_answers):
            if not isinstance(answer, Mapping):
                raise LiteValidationError(f"direct_answers[{index}] must be an object")
            for field in ("question", "answer"):
                _require_text(answer.get(field), f"direct_answers[{index}].{field}")
            self._require_text_array(answer.get("evidence_ids", ()), f"direct_answers[{index}].evidence_ids")
            questions.append(answer["question"])
        if len(questions) != len(set(questions)):
            raise LiteValidationError("direct answer questions must be unique")
        for name, conclusion in (
            ("statistical_conclusion", self.statistical_conclusion),
            ("operational_conclusion", self.operational_conclusion),
        ):
            if conclusion is None:
                continue
            if not isinstance(conclusion, Mapping):
                raise LiteValidationError(f"{name} must be an object or null")
            _require_text(conclusion.get("text"), f"{name}.text")
            self._require_text_array(conclusion.get("evidence_ids", ()), f"{name}.evidence_ids")

    def _validate_key_values(self) -> None:
        self._unique_ids(self.key_values, "key_values")
        for index, item in enumerate(self.key_values):
            _require_text(item.get("label"), f"key_values[{index}].label")
            value = item.get("value")
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise LiteValidationError(f"key_values[{index}].value must be a finite number")
            if not isinstance(item.get("unit", ""), str):
                raise LiteValidationError(f"key_values[{index}].unit must be text")
            self._validate_format(item.get("format"), f"key_values[{index}].format")

    def _validate_review_fields(self) -> None:
        if not isinstance(self.evidence_strength, Mapping):
            raise LiteValidationError("evidence_strength must be an object")
        if self.evidence_strength.get("level") not in {
            "strong", "moderate", "limited", "insufficient", "not_applicable",
        }:
            raise LiteValidationError("evidence_strength.level is invalid")
        _require_text(self.evidence_strength.get("explanation"), "evidence_strength.explanation")
        if not isinstance(self.recommendation, Mapping):
            raise LiteValidationError("recommendation must be an object")
        if self.recommendation.get("status") not in {"accept", "revise", "reject"}:
            raise LiteValidationError("recommendation.status is invalid")
        _require_text(self.recommendation.get("reason"), "recommendation.reason")
        actions = self.recommendation.get("required_actions", ())
        self._require_text_array(actions, "recommendation.required_actions")
        if self.recommendation["status"] == "revise" and not actions:
            raise LiteValidationError("revise recommendation requires at least one action")

    def _validate_tables_and_figures(self) -> None:
        self._require_text_array(self.summary_table_ids, "summary_table_ids")
        self._unique_ids(self.tables, "tables")
        for index, table in enumerate(self.tables):
            for field in ("title", "source_evidence_id"):
                _require_text(table.get(field), f"tables[{index}].{field}")
            self._require_text_array(table.get("columns"), f"tables[{index}].columns")
            if not table["columns"]:
                raise LiteValidationError(f"tables[{index}].columns must not be empty")
            _require_positive_int(table.get("max_rows"), f"tables[{index}].max_rows")
            sort = table.get("sort")
            if sort is not None:
                if not isinstance(sort, Mapping):
                    raise LiteValidationError(f"tables[{index}].sort must be an object or null")
                _require_text(sort.get("column"), f"tables[{index}].sort.column")
                self._require_bool(sort.get("descending", False), f"tables[{index}].sort.descending")
            formats = table.get("formats", {})
            if not isinstance(formats, Mapping):
                raise LiteValidationError(f"tables[{index}].formats must be an object")
            for column, rule in formats.items():
                if column not in table["columns"]:
                    raise LiteValidationError(f"tables[{index}].formats references an unknown column")
                self._validate_format(rule, f"tables[{index}].formats.{column}")
        self._unique_ids(self.figures, "figures")
        for index, figure in enumerate(self.figures):
            for field in ("source_evidence_id", "caption", "interpretation"):
                _require_text(figure.get(field), f"figures[{index}].{field}")

    def _validate_analysis(self) -> None:
        if not isinstance(self.technical_sections, (list, tuple)):
            raise LiteValidationError("technical_sections must be an array")
        for index, section in enumerate(self.technical_sections):
            if not isinstance(section, Mapping):
                raise LiteValidationError(f"technical_sections[{index}] must be an object")
            for field in ("title", "analysis"):
                _require_text(section.get(field), f"technical_sections[{index}].{field}")
            for field in ("table_ids", "figure_ids", "evidence_ids"):
                self._require_text_array(section.get(field, ()), f"technical_sections[{index}].{field}")
        self._unique_ids(self.validations, "validations")
        for index, validation in enumerate(self.validations):
            for field in ("name", "summary"):
                _require_text(validation.get(field), f"validations[{index}].{field}")
            if validation.get("status") not in {"pass", "warning", "fail", "not_applicable"}:
                raise LiteValidationError(f"validations[{index}].status is invalid")
            details = validation.get("details", "")
            if not isinstance(details, str):
                raise LiteValidationError(f"validations[{index}].details must be text")
            if validation["status"] == "warning" and not details.strip():
                raise LiteValidationError(f"validations[{index}].details must explain a warning")
            self._require_bool(validation.get("is_key"), f"validations[{index}].is_key")
            self._require_text_array(validation.get("evidence_ids", ()), f"validations[{index}].evidence_ids")
        self._unique_ids(self.limitations, "limitations")
        for index, limitation in enumerate(self.limitations):
            for field in ("summary", "impact"):
                _require_text(limitation.get(field), f"limitations[{index}].{field}")
            self._require_bool(limitation.get("is_key"), f"limitations[{index}].is_key")

    def _validate_evidence(self) -> None:
        if not isinstance(self.evidence, Mapping):
            raise LiteValidationError("evidence must be an object")
        artifacts = self.evidence.get("artifacts")
        self._unique_ids(artifacts, "evidence.artifacts")
        for index, artifact in enumerate(artifacts):
            for field in ("path", "kind", "purpose"):
                _require_text(artifact.get(field), f"evidence.artifacts[{index}].{field}")

    def payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "problem": self.problem,
            "spec_revision": self.spec_revision,
            "spec_hash": self.spec_hash,
            "summary": _thaw_json(self.summary),
            "direct_answers": _thaw_json(self.direct_answers),
            "statistical_conclusion": _thaw_json(self.statistical_conclusion),
            "operational_conclusion": _thaw_json(self.operational_conclusion),
            "key_values": _thaw_json(self.key_values),
            "evidence_strength": _thaw_json(self.evidence_strength),
            "recommendation": _thaw_json(self.recommendation),
            "summary_table_ids": _thaw_json(self.summary_table_ids),
            "tables": _thaw_json(self.tables),
            "figures": _thaw_json(self.figures),
            "technical_sections": _thaw_json(self.technical_sections),
            "validations": _thaw_json(self.validations),
            "limitations": _thaw_json(self.limitations),
            "evidence": _thaw_json(self.evidence),
        }
