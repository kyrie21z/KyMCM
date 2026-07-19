#!/usr/bin/env python3
"""KyMCM Full checkpoint CLI with fixed contest-workspace paths."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any, Mapping

from checkpoint_full.core import LiteValidationError, ModelSpec, ResultRecord, ensure_json_value
from checkpoint_full.problem_definition import (
    DefinitionState, ProblemDefinition, ProblemDefinitionStore, ProblemDefinitionWorkflow,
    definition_from_payload, definition_transition,
)
from checkpoint_full.render import (
    public_status, render_problem_definition, render_result_document,
    render_start_document,
)
from checkpoint_full.storage import CheckpointStore, StorageError, reject_symlink_chain
from checkpoint_full.validation import validate_result
from checkpoint_full.workflow import Workflow, WorkflowError, WorkflowState, transition
from workflow_mode import WorkflowModeError, require_full_mode


ROOT_ALLOWLIST = {"AGENTS.md", "README.md", "input", "problems", "paper", "reports", ".kymcm", ".gitignore"}


def digest_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read valid JSON from {path}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def _spec(data: Mapping[str, Any]) -> ModelSpec:
    payload = dict(data)
    for key in ("assumptions", "decision_rules", "required_outputs"):
        payload[key] = tuple(payload.get(key, ()))
    return ModelSpec(**payload)


def _result(data: Mapping[str, Any]) -> ResultRecord:
    payload = dict(data)
    payload.setdefault("statistical_conclusion", None)
    payload.setdefault("operational_conclusion", None)
    for key in (
        "direct_answers", "key_values", "summary_table_ids", "tables", "figures",
        "technical_sections", "validations", "limitations",
    ):
        payload[key] = tuple(payload.get(key, ()))
    return ResultRecord(**payload)


def result_review_hash(payload: Mapping[str, Any]) -> str:
    if not isinstance(payload, Mapping):
        raise LiteValidationError("Result payload must be an object")
    projection = json.loads(json.dumps(payload, ensure_ascii=False, allow_nan=False))
    evidence = projection.get("evidence")
    if not isinstance(evidence, dict):
        raise LiteValidationError("evidence must be an object")
    evidence.pop("result_hash", None)
    ensure_json_value(projection, "result_review")
    encoded = json.dumps(projection, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _bound_result(data: Mapping[str, Any]) -> ResultRecord:
    payload = json.loads(json.dumps(data, ensure_ascii=False, allow_nan=False))
    if not isinstance(payload.get("evidence"), dict):
        raise LiteValidationError("evidence must be an object")
    computed = result_review_hash(payload)
    supplied = payload["evidence"].get("result_hash")
    if supplied not in (None, "", computed):
        raise LiteValidationError("supplied result hash conflicts with reviewed content")
    payload["evidence"]["result_hash"] = computed
    return _result(payload)


def validate_layout(workspace: Path) -> None:
    extras = sorted(path.name for path in workspace.iterdir() if path.name not in ROOT_ALLOWLIST)
    if extras:
        raise ValueError(f"workspace root contains forbidden entries: {', '.join(extras)}")
    for problem in range(1, 5):
        root = workspace / "problems" / f"q{problem}"
        required = {"spec", "code", "data", "outputs", "notes", "result"}
        if root.is_symlink() or not root.is_dir() or not required <= {path.name for path in root.iterdir()}:
            raise ValueError(f"Q{problem} directory protocol is incomplete")
        if any((root / name).is_symlink() or not (root / name).is_dir() for name in required):
            raise ValueError(f"Q{problem} directory protocol contains unsafe paths")
        if not (root / "data/derived").is_dir():
            raise ValueError(f"Q{problem} derived-data directory is missing")


def _paths(workspace: Path, problem: int) -> dict[str, Path]:
    root = workspace / "problems" / f"q{problem}"
    return {"root": root, "spec": root / "spec/model_spec.json", "start": root / f"spec/START_Q{problem}.md",
            "result": root / "result/result_record.json", "result_md": root / f"result/RESULT_Q{problem}.md"}


def _definition_paths(workspace: Path) -> tuple[Path, Path]:
    root = workspace / "problems/problem_definition"
    return root / "problem_definition.json", root / "PROBLEM_DEFINITION.md"


def _definition_store(workspace: Path) -> ProblemDefinitionStore:
    return ProblemDefinitionStore(workspace / ".kymcm/checkpoint_lite/problem_definition")


def _load_accepted_definition(workspace: Path, problem: int | None = None) -> ProblemDefinition:
    json_path, markdown_path = _definition_paths(workspace)
    definition = definition_from_payload(_json(json_path))
    flow = _definition_store(workspace).load_workflow()
    canonical = render_problem_definition(definition)
    if (flow.state is not DefinitionState.ACCEPTED or flow.revision != definition.revision or
        flow.semantic_hash != definition.hash):
        raise ValueError("Problem Definition has not been accepted")
    if not markdown_path.is_file() or markdown_path.read_text(encoding="utf-8") != canonical or flow.review_document_hash != digest_text(canonical):
        raise ValueError("accepted Problem Definition review binding is no longer valid")
    if problem is not None and problem not in {item["problem"] for item in definition.subproblems}:
        raise ValueError(f"Q{problem} is absent from Problem Definition")
    if problem is not None:
        for predecessor in definition.dependencies[str(problem)]:
            predecessor_flow = _store(workspace, predecessor).load_workflow()
            if predecessor_flow.state is not WorkflowState.COMPLETED:
                raise ValueError(f"Q{problem} requires completed predecessor Q{predecessor}")
    return definition


def _store(workspace: Path, problem: int) -> CheckpointStore:
    root = workspace / ".kymcm/checkpoint_lite" / f"q{problem}"
    reject_symlink_chain(root)
    root.mkdir(parents=True, exist_ok=True)
    return CheckpointStore(root)


def _confirmation(value: str | None) -> str:
    if not str(value or "").strip():
        raise ValueError("explicit non-empty user wording is required")
    return str(value).strip()


def _evidence_guard(workspace: Path, problem: int, result: ResultRecord) -> None:
    question_root = (workspace / f"problems/q{problem}").resolve()
    allowed_paths = tuple(workspace / f"problems/q{problem}" / part for part in ("code", "data/derived", "outputs", "notes"))
    if any(path.is_symlink() for path in allowed_paths):
        raise ValueError("current-problem evidence directories must not be symlinks")
    allowed = tuple(path.resolve() for path in allowed_paths)
    if any(question_root not in root.parents for root in allowed):
        raise ValueError("current-problem evidence directories escape the question root")
    artifacts = result.evidence.get("artifacts")
    if not isinstance(artifacts, (list, tuple)) or not artifacts:
        raise ValueError("Result evidence.artifacts must list current-problem files")
    for artifact in artifacts:
        if not isinstance(artifact, Mapping):
            raise ValueError("each Result evidence artifact must be an object")
        raw = artifact.get("path")
        if not isinstance(raw, str) or Path(raw).is_absolute() or ".." in Path(raw).parts:
            raise ValueError(f"unsafe evidence path: {raw!r}")
        path = workspace / raw
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"evidence must be an existing ordinary file: {raw}")
        resolved = path.resolve()
        if not any(root == resolved.parent or root in resolved.parents for root in allowed):
            raise ValueError(f"evidence is outside Q{problem} allowed directories: {raw}")


def _git_guard(workspace: Path, problem: int, result: ResultRecord) -> None:
    try:
        repository_root = Path(subprocess.check_output(
            ["git", "-C", str(workspace), "rev-parse", "--show-toplevel"],
            text=True, stderr=subprocess.PIPE,
        ).strip()).resolve()
        code_revision = subprocess.check_output(
            ["git", "-C", str(repository_root), "rev-parse", "HEAD"],
            text=True, stderr=subprocess.PIPE,
        ).strip()
    except subprocess.CalledProcessError as exc:
        raise ValueError("contest workspace must be inside a Git repository before Result review") from exc
    if result.evidence.get("code_revision") != code_revision:
        raise ValueError("Result code_revision must equal the current Git commit")
    try:
        relative = workspace.resolve().relative_to(repository_root)
    except ValueError as exc:
        raise ValueError("contest workspace is outside its discovered Git repository") from exc
    paths = [str(relative / f"problems/q{problem}/code"), str(relative / f"problems/q{problem}/data/derived")]
    dirty = subprocess.check_output(
        ["git", "-C", str(repository_root), "status", "--porcelain", "--", *paths], text=True,
    )
    if dirty.strip():
        raise ValueError("current-problem code or derived data has uncommitted changes")


def _event(store: CheckpointStore, action: str, user_message: str | None = None, **extra: Any) -> None:
    payload: dict[str, Any] = {"action": action, **extra}
    if user_message is not None:
        payload["user_message"] = user_message
    store.append_event(payload)


def run(args: argparse.Namespace) -> None:
    workspace = args.workspace.expanduser().resolve()
    require_full_mode(workspace)
    if args.command == "validate-layout":
        validate_layout(workspace)
        print("workspace layout valid")
        return
    if args.command == "init-problem-definition":
        store = _definition_store(workspace)
        store.save_workflow(ProblemDefinitionWorkflow())
        store.append_event("init")
        print("全题定义待起草")
        return
    if args.command in {"submit-problem-definition", "accept-problem-definition", "replan-problem-definition", "mark-problem-definition-stale", "recover-problem-definition"}:
        store = _definition_store(workspace)
        flow = store.load_workflow()
        json_path, markdown_path = _definition_paths(workspace)
        if args.command == "submit-problem-definition":
            definition = definition_from_payload(_json(json_path))
            canonical = render_problem_definition(definition)
            updated = definition_transition(flow, "submit", definition=definition,
                                            document_hash=digest_text(canonical))
            _write_text(markdown_path, canonical)
            store.save_workflow(updated); store.append_event("submit")
            print("正式审核对象是 problems/problem_definition/PROBLEM_DEFINITION.md")
        elif args.command == "accept-problem-definition":
            message = _confirmation(args.user_message)
            definition = definition_from_payload(_json(json_path)); canonical = render_problem_definition(definition)
            if (markdown_path.read_text(encoding="utf-8") != canonical or flow.revision != definition.revision or
                flow.semantic_hash != definition.hash or
                flow.review_document_hash != digest_text(canonical)):
                raise ValueError("Problem Definition JSON or Markdown changed; submit it for review again")
            updated = definition_transition(flow, "accept", user_message=message)
            store.save_workflow(updated); store.append_event("accept", message)
            print("全题定义已接受")
        else:
            mapping = {"replan-problem-definition": "replan", "mark-problem-definition-stale": "mark-stale", "recover-problem-definition": "recover"}
            updated = definition_transition(flow, mapping[args.command], reason=getattr(args, "reason", None))
            store.save_workflow(updated); store.append_event(mapping[args.command])
            print(updated.state.value)
        return
    problem = args.problem
    if not problem:
        raise ValueError("--problem is required for problem-level commands")
    paths = _paths(workspace, problem)
    store = _store(workspace, problem)
    if args.command == "init":
        paths["root"].mkdir(parents=True, exist_ok=True)
        store.save_workflow(Workflow(problem)); _event(store, "init")
        print("正在分析"); return
    flow = store.load_workflow()
    try: spec = store.load_model_spec()
    except StorageError: spec = None
    if args.command == "status":
        print(public_status(flow)); return
    if args.command in {"submit-start", "submit-result", "accept-result"}:
        validate_layout(workspace)
    if args.command == "submit-start":
        definition = _load_accepted_definition(workspace, problem)
        candidate = _spec(_json(paths["spec"]))
        canonical = render_start_document(candidate, definition, args.recommendation)
        updated = transition(flow, "submit_start", {"spec": candidate, "review_document_hash": digest_text(canonical)})
        _write_text(paths["start"], canonical); store.save_model_spec(candidate); store.save_workflow(updated); _event(store, "submit_start")
        print(f"正式审核对象是 problems/q{problem}/spec/START_Q{problem}.md")
    elif args.command == "accept-start":
        message = _confirmation(args.user_message); definition = _load_accepted_definition(workspace, problem)
        candidate = _spec(_json(paths["spec"])); canonical = render_start_document(candidate, definition, args.recommendation)
        if paths["start"].read_text(encoding="utf-8") != canonical or flow.review_document_hash != digest_text(canonical):
            raise ValueError("Start JSON or Markdown changed; submit Start for review again")
        updated = transition(flow, "accept_start", {"spec": candidate}); store.save_workflow(updated); _event(store, "accept_start", message)
        print(public_status(updated))
    elif args.command == "notification":
        _event(store, "notification", message=_confirmation(args.message)); print("已记录通知")
    elif args.command == "submit-result":
        _load_accepted_definition(workspace, problem)
        record = _bound_result(_json(paths["result"])); _evidence_guard(workspace, problem, record); _git_guard(workspace, problem, record)
        canonical = render_result_document(record, workspace)
        updated = transition(flow, "submit_result", {"spec": spec, "result": record,
            "review_document_hash": digest_text(canonical)})
        _write_text(paths["result_md"], canonical); store.save_result(record); store.save_workflow(updated); _event(store, "submit_result")
        print(f"正式审核对象是 problems/q{problem}/result/RESULT_Q{problem}.md")
    elif args.command == "accept-result":
        message = _confirmation(args.user_message); record = _bound_result(_json(paths["result"])); _evidence_guard(workspace, problem, record); _git_guard(workspace, problem, record)
        canonical = render_result_document(record, workspace)
        if paths["result_md"].read_text(encoding="utf-8") != canonical or flow.review_document_hash != digest_text(canonical):
            raise ValueError("Result JSON or Markdown changed; submit Result for review again")
        updated = transition(flow, "accept_result", {"spec": spec, "result": record}); store.save_workflow(updated); _event(store, "accept_result", message)
        print(public_status(updated))
    elif args.command in {"repair", "replan", "recover"}:
        updated = transition(flow, args.command); store.save_workflow(updated); _event(store, args.command); print(public_status(updated))
    elif args.command == "mark-stale":
        updated = transition(flow, "mark_stale", {"reason": args.reason, "source": args.source})
        store.save_workflow(updated); _event(store, "mark_stale"); print(public_status(updated))
    elif args.command == "validate":
        report = validate_result(spec, store.load_result()); print(json.dumps({"passed": report.passed}, ensure_ascii=False))


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--workspace", type=Path, default=Path.cwd())
    result.add_argument("--problem", type=int)
    sub = result.add_subparsers(dest="command", required=True)
    for name in ("init", "status", "validate-layout", "init-problem-definition", "submit-problem-definition", "replan-problem-definition", "recover-problem-definition", "validate"):
        sub.add_parser(name)
    command = sub.add_parser("accept-problem-definition"); command.add_argument("--user-message", required=True)
    command = sub.add_parser("mark-problem-definition-stale"); command.add_argument("--reason", required=True)
    command = sub.add_parser("submit-start"); command.add_argument("--recommendation", required=True)
    sub.add_parser("submit-result")
    command = sub.add_parser("accept-start"); command.add_argument("--user-message", required=True); command.add_argument("--recommendation", required=True)
    command = sub.add_parser("accept-result"); command.add_argument("--user-message", required=True)
    command = sub.add_parser("notification"); command.add_argument("--message", required=True)
    for name in ("repair", "replan", "recover"): sub.add_parser(name)
    command = sub.add_parser("mark-stale"); command.add_argument("--reason", choices=("rerun_required", "replan_required"), required=True); command.add_argument("--source", required=True)
    return result


def main() -> int:
    p = parser(); args = p.parse_args()
    try: run(args)
    except (OSError, subprocess.CalledProcessError, KeyError, TypeError, ValueError, RuntimeError, LiteValidationError, StorageError, WorkflowError, WorkflowModeError) as exc:
        p.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
