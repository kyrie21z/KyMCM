"""Whole-problem semantic gate for Checkpoint Lite Pilot v2."""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any, Mapping

from .core import LiteValidationError, _freeze_json, _thaw_json, _require_positive_int, _require_text, ensure_json_value
from .storage import reject_symlink_chain, StorageError


def _items(value: Any, name: str, fields: tuple[str, ...], *, nonempty: bool = True) -> None:
    if not isinstance(value, (list, tuple)) or (nonempty and not value):
        raise LiteValidationError(f"{name} must be {'a non-empty ' if nonempty else 'an '}array")
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise LiteValidationError(f"{name}[{index}] must be an object")
        for field in fields:
            _require_text(item.get(field), f"{name}[{index}].{field}")


@dataclass(frozen=True)
class ProblemDefinition:
    schema_version: int
    revision: int
    title: str
    overall_objective: str
    source_data: tuple[Mapping[str, Any], ...]
    subproblems: tuple[Mapping[str, Any], ...]
    shared_semantics: Mapping[str, Any]
    dependencies: Mapping[str, tuple[int, ...]]
    shared_outputs: tuple[Mapping[str, Any], ...]
    ambiguities: tuple[Mapping[str, Any], ...]

    def __post_init__(self) -> None:
        if self.schema_version != 3:
            raise LiteValidationError("Problem Definition schema_version must be 3")
        _require_positive_int(self.revision, "revision")
        _require_text(self.title, "title")
        _require_text(self.overall_objective, "overall_objective")
        _items(self.source_data, "source_data", ("name", "role", "scope"))
        _items(self.subproblems, "subproblems", ("statement", "objective"))
        _items(self.shared_outputs, "shared_outputs", ("name", "definition"), nonempty=False)
        ensure_json_value(self.payload())
        nodes: list[int] = []
        for index, item in enumerate(self.subproblems):
            problem = item.get("problem")
            _require_positive_int(problem, f"subproblems[{index}].problem")
            if not isinstance(item.get("inputs"), (list, tuple)) or not isinstance(item.get("outputs"), (list, tuple)):
                raise LiteValidationError(f"subproblems[{index}] inputs and outputs must be arrays")
            nodes.append(problem)
        if len(nodes) != len(set(nodes)):
            raise LiteValidationError("subproblem numbers must be unique")
        expected = {str(node) for node in nodes}
        if set(self.dependencies) != expected:
            raise LiteValidationError("dependencies must cover exactly all subproblems")
        graph: dict[int, tuple[int, ...]] = {}
        for key, predecessors in self.dependencies.items():
            if not isinstance(predecessors, (list, tuple)):
                raise LiteValidationError(f"dependencies.{key} must be an array")
            node = int(key)
            graph[node] = tuple(predecessors)
            for predecessor in predecessors:
                if predecessor not in nodes:
                    raise LiteValidationError(f"dependency {predecessor} does not exist")
                if predecessor == node:
                    raise LiteValidationError("self dependency is forbidden")
        self._topological(graph)
        _items(self.ambiguities, "ambiguities", ("issue", "resolution", "impact"), nonempty=False)
        for name in ("source_data", "subproblems", "shared_semantics", "dependencies", "shared_outputs", "ambiguities"):
            object.__setattr__(self, name, _freeze_json(getattr(self, name)))

    @staticmethod
    def _topological(graph: Mapping[int, tuple[int, ...]]) -> tuple[int, ...]:
        remaining = {node: set(preds) for node, preds in graph.items()}
        order: list[int] = []
        while remaining:
            ready = sorted(node for node, predecessors in remaining.items() if not predecessors)
            if not ready:
                raise LiteValidationError("dependencies contain a cycle")
            for node in ready:
                order.append(node)
                del remaining[node]
                for predecessors in remaining.values():
                    predecessors.discard(node)
        return tuple(order)

    @property
    def topological_order(self) -> tuple[int, ...]:
        return self._topological({int(k): tuple(v) for k, v in self.dependencies.items()})

    def payload(self) -> dict[str, Any]:
        return {name: _thaw_json(getattr(self, name)) for name in (
            "schema_version", "revision", "title", "overall_objective", "source_data", "subproblems",
            "shared_semantics", "dependencies", "shared_outputs", "ambiguities",
        )}

    @property
    def hash(self) -> str:
        payload = self.payload()
        del payload["revision"]
        encoded = json.dumps(payload, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(encoded).hexdigest()


class DefinitionState(str, Enum):
    DRAFT = "draft"
    AWAITING_REVIEW = "awaiting_review"
    ACCEPTED = "accepted"
    STALE = "stale"


@dataclass(frozen=True)
class ProblemDefinitionWorkflow:
    state: DefinitionState = DefinitionState.DRAFT
    revision: int | None = None
    semantic_hash: str | None = None
    review_document_hash: str | None = None
    stale_reason: str | None = None

    def __post_init__(self) -> None:
        bound = self.state in {DefinitionState.AWAITING_REVIEW, DefinitionState.ACCEPTED}
        bindings = (self.revision, self.semantic_hash, self.review_document_hash)
        if bound and not all(value is not None for value in bindings):
            raise LiteValidationError("reviewed Problem Definition requires complete bindings")
        if not bound and any(value is not None for value in bindings):
            raise LiteValidationError("unreviewed Problem Definition cannot retain review bindings")
        for value in (self.semantic_hash, self.review_document_hash):
            if value is not None and (len(value) != 64 or any(character not in "0123456789abcdef" for character in value)):
                raise LiteValidationError("Problem Definition hashes must be lowercase SHA-256 digests")
        if self.state is DefinitionState.STALE and not self.stale_reason:
            raise LiteValidationError("stale Problem Definition requires a reason")
        if self.state is not DefinitionState.STALE and self.stale_reason is not None:
            raise LiteValidationError("stale reason is only valid while stale")

    def payload(self) -> dict[str, Any]:
        return {"state": self.state.value, "revision": self.revision, "semantic_hash": self.semantic_hash,
                "review_document_hash": self.review_document_hash, "stale_reason": self.stale_reason}


def definition_transition(flow: ProblemDefinitionWorkflow, action: str, **context: Any) -> ProblemDefinitionWorkflow:
    if action == "submit" and flow.state is DefinitionState.DRAFT:
        definition, document_hash = context.get("definition"), context.get("document_hash")
        if not isinstance(definition, ProblemDefinition):
            raise LiteValidationError("submit requires a valid Problem Definition")
        return ProblemDefinitionWorkflow(DefinitionState.AWAITING_REVIEW, definition.revision, definition.hash,
                                         document_hash)
    if action == "accept" and flow.state is DefinitionState.AWAITING_REVIEW:
        if not str(context.get("user_message", "")).strip():
            raise LiteValidationError("accept requires non-empty user wording")
        return replace(flow, state=DefinitionState.ACCEPTED)
    if action == "replan" and flow.state in {DefinitionState.AWAITING_REVIEW, DefinitionState.ACCEPTED}:
        return ProblemDefinitionWorkflow()
    if action == "mark-stale" and flow.state in {DefinitionState.AWAITING_REVIEW, DefinitionState.ACCEPTED}:
        reason = str(context.get("reason", "")).strip()
        if not reason:
            raise LiteValidationError("stale reason must be non-empty")
        return ProblemDefinitionWorkflow(DefinitionState.STALE, stale_reason=reason)
    if action == "recover" and flow.state is DefinitionState.STALE:
        return ProblemDefinitionWorkflow()
    raise LiteValidationError(f"action {action!r} is invalid from {flow.state.value}")


def definition_from_payload(data: Mapping[str, Any]) -> ProblemDefinition:
    payload = dict(data)
    for name in ("source_data", "subproblems", "shared_outputs", "ambiguities"):
        payload[name] = tuple(payload.get(name, ()))
    payload["dependencies"] = {str(key): tuple(value) for key, value in payload["dependencies"].items()}
    return ProblemDefinition(**payload)


class ProblemDefinitionStore:
    """Small atomic store at the global checkpoint directory."""

    def __init__(self, root: str | Path):
        try: requested = reject_symlink_chain(root)
        except StorageError as exc: raise LiteValidationError(str(exc)) from exc
        self.root = requested.resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        try: reject_symlink_chain(requested)
        except StorageError as exc: raise LiteValidationError(str(exc)) from exc

    def _path(self, name: str) -> Path:
        path = self.root / name
        if path.is_symlink() or path.resolve().parent != self.root:
            raise LiteValidationError("Problem Definition store path is unsafe")
        return path

    def _save(self, name: str, payload: Mapping[str, Any]) -> None:
        path = self._path(name)
        descriptor, temporary = tempfile.mkstemp(prefix=f".{name}.", dir=self.root)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":"))
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, path)
        except Exception:
            Path(temporary).unlink(missing_ok=True)
            raise

    def save_workflow(self, flow: ProblemDefinitionWorkflow) -> None:
        self._save("workflow.json", flow.payload())

    def load_workflow(self) -> ProblemDefinitionWorkflow:
        try:
            data = json.loads(self._path("workflow.json").read_text(encoding="utf-8"))
            return ProblemDefinitionWorkflow(
                DefinitionState(data["state"]), data.get("revision"), data.get("semantic_hash"),
                data.get("review_document_hash"), data.get("stale_reason"),
            )
        except (OSError, ValueError, KeyError, TypeError) as exc:
            raise LiteValidationError("invalid Problem Definition workflow") from exc

    def append_event(self, action: str, user_message: str | None = None) -> None:
        event = {"action": action}
        if user_message is not None:
            event["user_message"] = user_message
        with self._path("events.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")
