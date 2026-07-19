"""Six-state review workflow for Checkpoint Lite."""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Any, Mapping

from .core import ModelSpec, ResultRecord
from .validation import validate_prestart_audit, validate_result


class WorkflowError(ValueError):
    pass


class WorkflowState(str, Enum):
    EXPLORING = "exploring"
    AWAITING_START_REVIEW = "awaiting_start_review"
    RUNNING = "running"
    AWAITING_RESULT_REVIEW = "awaiting_result_review"
    COMPLETED = "completed"
    STALE = "stale"


class StaleReason(str, Enum):
    RERUN_REQUIRED = "rerun_required"
    REPLAN_REQUIRED = "replan_required"


_ACTION_SOURCES = {
    "submit_start": frozenset({WorkflowState.EXPLORING}),
    "accept_start": frozenset({WorkflowState.AWAITING_START_REVIEW}),
    "replan": frozenset({WorkflowState.AWAITING_START_REVIEW, WorkflowState.AWAITING_RESULT_REVIEW}),
    "submit_result": frozenset({WorkflowState.RUNNING}),
    "accept_result": frozenset({WorkflowState.AWAITING_RESULT_REVIEW}),
    "repair": frozenset({WorkflowState.AWAITING_RESULT_REVIEW}),
    "recover": frozenset({WorkflowState.STALE}),
}

_STALE_SOURCES = {
    StaleReason.RERUN_REQUIRED: frozenset({
        WorkflowState.RUNNING, WorkflowState.AWAITING_RESULT_REVIEW, WorkflowState.COMPLETED,
    }),
    StaleReason.REPLAN_REQUIRED: frozenset({
        WorkflowState.AWAITING_START_REVIEW, WorkflowState.RUNNING,
        WorkflowState.AWAITING_RESULT_REVIEW, WorkflowState.COMPLETED,
    }),
}


@dataclass(frozen=True)
class Workflow:
    problem: int
    state: WorkflowState = WorkflowState.EXPLORING
    spec_revision: int | None = None
    spec_hash: str | None = None
    stale_reason: StaleReason | None = None
    stale_source: str | None = None
    review_result_hash: str | None = None
    review_document_hash: str | None = None

    def __post_init__(self) -> None:
        if isinstance(self.problem, bool) or not isinstance(self.problem, int) or self.problem < 1:
            raise WorkflowError("problem must be a positive integer")
        if (self.spec_revision is None) != (self.spec_hash is None):
            raise WorkflowError("spec revision and hash must be present together")
        if self.spec_revision is not None and (
            isinstance(self.spec_revision, bool) or not isinstance(self.spec_revision, int) or self.spec_revision < 1
        ):
            raise WorkflowError("spec revision must be a positive integer")
        if self.spec_hash is not None and not _valid_sha256(self.spec_hash):
            raise WorkflowError("spec hash must be a lowercase SHA-256 digest")
        spec_required = self.state in {
            WorkflowState.AWAITING_START_REVIEW, WorkflowState.RUNNING,
            WorkflowState.AWAITING_RESULT_REVIEW, WorkflowState.COMPLETED,
        }
        if spec_required and self.spec_revision is None:
            raise WorkflowError(f"{self.state.value} requires an active Model Spec")
        if self.state is WorkflowState.STALE:
            if self.stale_reason is None or not self.stale_source:
                raise WorkflowError("stale work requires reason and source")
            if self.stale_reason is StaleReason.RERUN_REQUIRED and self.spec_revision is None:
                raise WorkflowError("rerun recovery requires an active Model Spec")
        elif self.stale_reason is not None or self.stale_source is not None:
            raise WorkflowError("stale metadata is only valid for stale work")
        if self.state is WorkflowState.AWAITING_RESULT_REVIEW:
            if not _valid_sha256(self.review_result_hash):
                raise WorkflowError("result review requires a lowercase SHA-256 result hash")
        elif self.review_result_hash is not None:
            raise WorkflowError("result review hash is only valid while awaiting result review")
        review_required = self.state in {WorkflowState.AWAITING_START_REVIEW, WorkflowState.AWAITING_RESULT_REVIEW}
        if review_required and not _valid_sha256(self.review_document_hash):
            raise WorkflowError("review state requires a lowercase SHA-256 document hash")
        if not review_required and self.review_document_hash is not None:
            raise WorkflowError("review document hash is only valid while awaiting review")

    def payload(self) -> dict[str, Any]:
        return {
            "problem": self.problem,
            "state": self.state.value,
            "spec_revision": self.spec_revision,
            "spec_hash": self.spec_hash,
            "stale_reason": self.stale_reason.value if self.stale_reason else None,
            "stale_source": self.stale_source,
            "review_result_hash": self.review_result_hash,
            "review_document_hash": self.review_document_hash,
        }


def _require(context: Mapping[str, Any], key: str) -> Any:
    if key not in context:
        raise WorkflowError(f"action requires {key}")
    return context[key]


def _valid_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and value == value.lower() and all(c in "0123456789abcdef" for c in value)


def _require_action_source(action: str, state: WorkflowState) -> None:
    if action not in _ACTION_SOURCES:
        raise WorkflowError(f"unknown action: {action!r}")
    if state not in _ACTION_SOURCES[action]:
        raise WorkflowError(f"action {action!r} is invalid from {state.value}")


def _result_hash(result: ResultRecord) -> str:
    value = result.evidence.get("result_hash")
    if not _valid_sha256(value):
        raise WorkflowError("Result Record requires a lowercase SHA-256 result hash")
    return value


def _require_active_spec(workflow: Workflow, context: Mapping[str, Any]) -> ModelSpec:
    spec = _require(context, "spec")
    if not isinstance(spec, ModelSpec) or spec.problem != workflow.problem:
        raise WorkflowError("action requires the active Model Spec")
    if spec.revision != workflow.spec_revision or spec.hash != workflow.spec_hash:
        raise WorkflowError("Model Spec does not match the active workflow")
    return spec


def _require_start_candidate(workflow: Workflow, context: Mapping[str, Any]) -> ModelSpec:
    spec = _require(context, "spec")
    if not isinstance(spec, ModelSpec) or spec.problem != workflow.problem:
        raise WorkflowError("submit_start requires a matching Model Spec")
    if workflow.spec_revision is not None:
        if spec.revision <= workflow.spec_revision:
            raise WorkflowError("revised Model Spec must increase revision")
        if spec.hash == workflow.spec_hash:
            raise WorkflowError("revised Model Spec must change mathematical semantics")
    return spec


def _require_resolved_prestart_audit(spec: ModelSpec) -> None:
    report = validate_prestart_audit(spec)
    if not report.passed:
        details = ", ".join(f"{error.code}@{error.path}" for error in report.errors)
        raise WorkflowError(f"pre-start data audit validation failed: {details}")


def transition(workflow: Workflow, action: str, context: Mapping[str, Any] | None = None) -> Workflow:
    """Return a new state or fail without mutating the frozen input."""
    context = context or {}
    if not isinstance(context, Mapping):
        raise WorkflowError("transition context must be a mapping")
    state = workflow.state
    if action == "mark_stale":
        try:
            reason = StaleReason(_require(context, "reason"))
        except ValueError as exc:
            raise WorkflowError("unknown stale reason") from exc
        if state not in _STALE_SOURCES[reason]:
            raise WorkflowError(f"{reason.value} is invalid from {state.value}")
        source = _require(context, "source")
        if not isinstance(source, str) or not source.strip():
            raise WorkflowError("stale source must be non-empty")
        return replace(workflow, state=WorkflowState.STALE, stale_reason=reason, stale_source=source,
                       review_result_hash=None, review_document_hash=None)

    _require_action_source(action, state)
    if action == "recover":
        target = WorkflowState.RUNNING if workflow.stale_reason is StaleReason.RERUN_REQUIRED else WorkflowState.EXPLORING
        return replace(workflow, state=target, stale_reason=None, stale_source=None)
    if action == "submit_start":
        spec = _require_start_candidate(workflow, context)
        _require_resolved_prestart_audit(spec)
        return replace(workflow, state=WorkflowState.AWAITING_START_REVIEW,
                       spec_revision=spec.revision, spec_hash=spec.hash,
                       review_document_hash=context.get("review_document_hash", spec.hash))
    if action == "accept_start":
        spec = _require_active_spec(workflow, context)
        _require_resolved_prestart_audit(spec)
        return replace(workflow, state=WorkflowState.RUNNING, review_document_hash=None)
    if action == "replan":
        return replace(workflow, state=WorkflowState.EXPLORING,
                       review_result_hash=None, review_document_hash=None)
    if action == "repair":
        return replace(workflow, state=WorkflowState.RUNNING,
                       review_result_hash=None, review_document_hash=None)
    if action == "submit_result":
        spec = _require_active_spec(workflow, context)
        result = _require(context, "result")
        if not isinstance(result, ResultRecord):
            raise WorkflowError("submit_result requires a Result Record")
        report = validate_result(spec, result)
        if not report.passed:
            raise WorkflowError("result validation failed: " + ", ".join(error.code for error in report.errors))
        return replace(workflow, state=WorkflowState.AWAITING_RESULT_REVIEW,
                       review_result_hash=_result_hash(result),
                       review_document_hash=context.get("review_document_hash", _result_hash(result)))
    if action == "accept_result":
        spec = _require_active_spec(workflow, context)
        result = _require(context, "result")
        if not isinstance(result, ResultRecord):
            raise WorkflowError("accept_result requires a Result Record")
        if _result_hash(result) != workflow.review_result_hash:
            raise WorkflowError("Result Record does not match the result submitted for review")
        report = validate_result(spec, result)
        if not report.passed:
            raise WorkflowError("result validation failed: " + ", ".join(error.code for error in report.errors))
        return replace(workflow, state=WorkflowState.COMPLETED,
                       review_result_hash=None, review_document_hash=None)
    raise WorkflowError(f"action {action!r} is invalid from {state.value}")
