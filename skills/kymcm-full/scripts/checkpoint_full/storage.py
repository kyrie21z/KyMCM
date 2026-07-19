"""Atomic file persistence confined to a standalone workspace root."""

from __future__ import annotations

from dataclasses import asdict
import json
import os
from pathlib import Path
import tempfile
from typing import Any, Mapping

from .core import LiteValidationError, ModelSpec, ResultRecord
from .workflow import StaleReason, Workflow, WorkflowError, WorkflowState


class StorageError(ValueError):
    pass


def reject_symlink_chain(path: str | Path) -> Path:
    requested = Path(path).expanduser().absolute()
    current = Path(requested.anchor)
    for part in requested.parts[1:]:
        current = current / part
        if current.exists() or current.is_symlink():
            if current.is_symlink(): raise StorageError(f"symlink path component is forbidden: {current}")
    return requested


class CheckpointStore:
    def __init__(self, workspace_root: str | Path):
        requested = reject_symlink_chain(workspace_root)
        self.root = requested.resolve()
        self.checkpoint = self.root / "checkpoint"

    def _ensure_checkpoint(self) -> Path:
        if self.checkpoint.is_symlink():
            raise StorageError("checkpoint directory must not be a symlink")
        try:
            self.checkpoint.mkdir(parents=False, exist_ok=True)
        except OSError as exc:
            raise StorageError("cannot create checkpoint directory") from exc
        resolved = self.checkpoint.resolve()
        if not resolved.is_dir() or resolved.parent != self.root:
            raise StorageError("checkpoint directory escapes workspace root")
        return resolved

    def _path(self, name: str) -> Path:
        if not name or Path(name).is_absolute() or len(Path(name).parts) != 1:
            raise StorageError("storage path must be a single relative filename")
        checkpoint = self._ensure_checkpoint()
        candidate = self.checkpoint / name
        if candidate.is_symlink():
            raise StorageError("storage file must not be a symlink")
        path = candidate.resolve()
        if path.parent != checkpoint or self.root not in path.parents:
            raise StorageError("storage path escapes workspace root")
        return path

    def _atomic_json(self, name: str, payload: Mapping[str, Any]) -> None:
        path = self._path(name)
        descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":"))
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, path)
        except Exception:
            try:
                os.unlink(temporary)
            except FileNotFoundError:
                pass
            raise

    def _read_json(self, name: str) -> Any:
        try:
            with self._path(name).open(encoding="utf-8") as handle:
                return json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            raise StorageError(f"cannot read valid {name}") from exc

    def _append(self, name: str, payload: Mapping[str, Any]) -> None:
        path = self._path(name)
        line = json.dumps(payload, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":"))
        with path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
            handle.flush()

    def save_workflow(self, workflow: Workflow) -> None:
        self._atomic_json("workflow.json", workflow.payload())

    def load_workflow(self) -> Workflow:
        data = self._read_json("workflow.json")
        try:
            return Workflow(
                problem=data["problem"], state=WorkflowState(data["state"]),
                spec_revision=data.get("spec_revision"), spec_hash=data.get("spec_hash"),
                stale_reason=StaleReason(data["stale_reason"]) if data.get("stale_reason") else None,
                stale_source=data.get("stale_source"),
                review_result_hash=data.get("review_result_hash"),
                review_document_hash=data.get("review_document_hash"),
            )
        except (KeyError, TypeError, ValueError, WorkflowError) as exc:
            raise StorageError("workflow.json has invalid structure") from exc

    def save_model_spec(self, spec: ModelSpec) -> None:
        self._atomic_json("model_spec.json", spec.payload())

    def load_model_spec(self) -> ModelSpec:
        try:
            data = self._read_json("model_spec.json")
            data["assumptions"] = tuple(data["assumptions"])
            data["decision_rules"] = tuple(data["decision_rules"])
            data["required_outputs"] = tuple(data["required_outputs"])
            return ModelSpec(**data)
        except (KeyError, TypeError, LiteValidationError) as exc:
            raise StorageError("model_spec.json has invalid structure") from exc

    def save_result(self, result: ResultRecord) -> None:
        self._atomic_json("result_record.json", result.payload())

    def load_result(self) -> ResultRecord:
        try:
            data = self._read_json("result_record.json")
            data.setdefault("statistical_conclusion", None)
            data.setdefault("operational_conclusion", None)
            for field in (
                "direct_answers", "key_values", "summary_table_ids", "tables", "figures",
                "technical_sections", "validations", "limitations",
            ):
                data[field] = tuple(data.get(field, ()))
            return ResultRecord(**data)
        except (KeyError, TypeError, LiteValidationError) as exc:
            raise StorageError("result_record.json has invalid structure") from exc

    def append_event(self, event: Mapping[str, Any]) -> None:
        self._append("events.jsonl", event)
