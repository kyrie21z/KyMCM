#!/usr/bin/env python3
"""Schema v4 contract, dependency, invalidation, and evidence helpers."""

from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 4
CONTRACT_STATUSES = {"draft", "pending_review", "approved", "superseded"}
PROBLEM_STATUSES = {"not_started", "running", "blocked", "completed", "stale"}
VALIDATION_STATUSES = {
    "pass", "repairable", "contract_change_required", "decision_required",
}
DEPRECATED_STATE_FIELDS = {
    "mode", "active_stages", "stage_reviews", "reviews", "review_round",
    "current_review",
}


def now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def atomic_write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)


def append_event(workspace: Path, event: str, **details: object) -> None:
    path = workspace / "state" / "events.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"timestamp": now(), "event": event, **details}) + "\n")


def read_front_matter(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        raise ValueError(f"Contract front matter missing: {path}")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError(f"Contract front matter is not closed: {path}") from exc
    metadata: dict[str, str] = {}
    for line in lines[1:end]:
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        if key in metadata:
            raise ValueError(f"Duplicate contract field {key}: {path}")
        metadata[key] = value.strip().strip("\"'")
    return metadata


def replace_front_matter_status(path: Path, status: str) -> bytes:
    if status not in CONTRACT_STATUSES:
        raise ValueError(f"Invalid contract status: {status}")
    lines = path.read_text(encoding="utf-8").splitlines()
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError(f"Contract front matter is not closed: {path}") from exc
    matches = [index for index in range(1, end) if lines[index].startswith("status:")]
    if len(matches) != 1:
        raise ValueError(f"Contract requires one status field: {path}")
    lines[matches[0]] = f"status: {status}"
    return ("\n".join(lines) + "\n").encode("utf-8")


def parse_dependencies(value: str, problem_count: int) -> dict[int, list[int]]:
    graph = {problem: [] for problem in range(1, problem_count + 1)}
    seen: set[int] = set()
    for group in value.split(";") if value else []:
        if not group.strip():
            continue
        if ":" not in group:
            raise ValueError(f"Invalid dependency declaration: {group}")
        raw_problem, raw_dependencies = group.split(":", 1)
        problem = int(raw_problem)
        if problem not in graph or problem in seen:
            raise ValueError(f"Invalid or duplicate problem in dependency graph: {problem}")
        dependencies = [int(item) for item in raw_dependencies.split(",") if item.strip()]
        if problem in dependencies or any(item not in graph for item in dependencies):
            raise ValueError(f"Invalid dependencies for Q{problem}: {dependencies}")
        graph[problem] = dependencies
        seen.add(problem)
    return graph


def stable_topological_order(graph: dict[int, list[int]], declared: list[int]) -> list[int]:
    remaining = {problem: set(dependencies) for problem, dependencies in graph.items()}
    order: list[int] = []
    while remaining:
        ready = [problem for problem in declared if problem in remaining and not remaining[problem]]
        if not ready:
            raise ValueError("Problem dependency graph contains a cycle")
        problem = ready[0]
        order.append(problem)
        remaining.pop(problem)
        for dependencies in remaining.values():
            dependencies.discard(problem)
    return order


def contract_store() -> dict:
    return {"current_version": None, "versions": {}}


def initialize_state(contest: str, problem_choice: str, problem_count: int) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "contest": contest.upper(),
        "problem_choice": problem_choice,
        "created_at": now(),
        "updated_at": now(),
        "problem_contract": contract_store(),
        "problems": {
            str(problem): {
                "depends_on": [],
                "solution_contract": contract_store(),
                "status": "not_started",
                "outputs": [],
                "validation": None,
                "invalidated_reason": None,
            }
            for problem in range(1, problem_count + 1)
        },
        "problem_order": list(range(1, problem_count + 1)),
        "current_problem": None,
        "expected_action": "contract:problem",
        "global_validation": None,
        "paper": {"status": "draft", "current_version": None, "versions": {}},
    }


def canonical_approval(contract_type: str, version: str, problem: int | None = None) -> str:
    if contract_type == "problem":
        return f"批准 Problem Contract {version}"
    if contract_type == "solution" and problem is not None:
        return f"批准 Solution Contract Q{problem} {version}"
    raise ValueError("Unsupported contract identity")


def approved_entry(store: dict) -> dict | None:
    version = store.get("current_version")
    entry = store.get("versions", {}).get(version) if version else None
    return entry if entry and entry.get("status") == "approved" else None


def contract_identity_issues(
    metadata: dict[str, str], contract_type: str, version: str,
    problem: int | None, expected_status: str,
) -> list[str]:
    issues: list[str] = []
    if metadata.get("contract_type") != contract_type:
        issues.append("contract_type mismatch")
    if metadata.get("version") != version:
        issues.append("version mismatch")
    if metadata.get("status") != expected_status:
        issues.append(f"status must be {expected_status}")
    if contract_type == "solution":
        if problem is None or metadata.get("problem_id") != f"Q{problem}":
            issues.append("problem_id mismatch")
    elif "problem_id" in metadata:
        issues.append("Problem Contract must not declare problem_id")
    return issues


def validate_contract_identity(
    metadata: dict[str, str], contract_type: str, version: str,
    problem: int | None, expected_status: str,
) -> None:
    issues = contract_identity_issues(
        metadata, contract_type, version, problem, expected_status,
    )
    if issues:
        raise ValueError(f"Contract identity mismatch: {', '.join(issues)}")


def get_contract_store(state: dict, contract_type: str, problem: int | None) -> dict:
    if contract_type == "problem":
        if problem is not None:
            raise ValueError("Problem Contract does not accept --problem")
        return state["problem_contract"]
    if contract_type == "solution":
        if problem is None or str(problem) not in state["problems"]:
            raise ValueError(f"Unknown problem: {problem}")
        if approved_entry(state["problem_contract"]) is None:
            raise ValueError("Problem Contract must be approved first")
        return state["problems"][str(problem)]["solution_contract"]
    raise ValueError(f"Unsupported contract type: {contract_type}")


def descendants(state: dict, problem: int) -> list[int]:
    affected = {problem}
    changed = True
    while changed:
        changed = False
        for raw, entry in state["problems"].items():
            candidate = int(raw)
            if candidate not in affected and any(dep in affected for dep in entry["depends_on"]):
                affected.add(candidate)
                changed = True
    return [item for item in state["problem_order"] if item in affected]


def solution_compatibility_issues(state: dict, problem: int) -> list[str]:
    entry = state["problems"][str(problem)]
    solution = approved_entry(entry["solution_contract"])
    if not solution:
        return [f"Q{problem} has no approved Solution Contract"]
    issues: list[str] = []
    if solution.get("problem_contract_version") != state["problem_contract"].get("current_version"):
        issues.append(f"Q{problem} Solution Contract targets an old Problem Contract")
    expected = {
        str(dep): state["problems"][str(dep)]["solution_contract"].get("current_version")
        for dep in entry["depends_on"]
    }
    if solution.get("dependency_solution_versions") != expected:
        issues.append(f"Q{problem} Solution Contract dependency snapshot is stale")
    return issues


def _pending_contracts(state: dict) -> list[str]:
    stores = [("Problem Contract", state["problem_contract"])] + [
        (f"Solution Contract Q{problem}", entry["solution_contract"])
        for problem, entry in state["problems"].items()
    ]
    pending = [
        f"{label} {version}"
        for label, store in stores
        for version, entry in store["versions"].items()
        if entry.get("status") == "pending_review"
    ]
    pending.extend(
        f"Final Paper {version}"
        for version, entry in state["paper"]["versions"].items()
        if entry.get("status") == "pending_review"
    )
    return pending


def submit_contract(
    state: dict, workspace: Path, contract_type: str, version: str,
    file_value: str, problem: int | None,
) -> None:
    pending = _pending_contracts(state)
    if pending:
        raise ValueError(f"Another approval is pending: {pending[0]}")
    current = state.get("current_problem")
    clear_blocked_focus = False
    if current is not None:
        current_entry = state["problems"][str(current)]
        if current_entry["status"] == "blocked" and (
            contract_type == "solution"
            and problem == current
            and state.get("expected_action") == f"contract:solution:q{current}:new_version"
        ):
            clear_blocked_focus = True
        elif current_entry["status"] in {"running", "blocked"}:
            raise ValueError(
                f"Q{current} is {current_entry['status']}; clear active focus before submission"
            )
    store = get_contract_store(state, contract_type, problem)
    if version in store["versions"] and store["versions"][version]["status"] != "draft":
        raise ValueError(f"Contract version already submitted: {version}")
    path = (workspace / file_value).resolve()
    if not path.is_relative_to(workspace.resolve()) or not path.is_file():
        raise ValueError("Contract file must exist inside workspace")
    metadata = read_front_matter(path)
    validate_contract_identity(metadata, contract_type, version, problem, "draft")
    path.write_bytes(replace_front_matter_status(path, "pending_review"))
    store["versions"][version] = {
        "version": version,
        "status": "pending_review",
        "file": str(path.relative_to(workspace)),
        "submitted_at": now(),
        "approved_at": None,
        "approval_text": None,
        "content_sha256": None,
        "approved_file_size": None,
    }
    if clear_blocked_focus:
        current_entry["status"] = "stale"
        current_entry["validation"] = None
        current_entry["invalidated_reason"] = "Solution Contract replacement requested"
        state["current_problem"] = None
    state["expected_action"] = (
        "approval:problem" if contract_type == "problem"
        else f"approval:solution:q{problem}"
    )


def _supersede_entry(workspace: Path, entry: dict) -> None:
    entry["status"] = "superseded"
    path = workspace / entry["file"]
    if path.is_file():
        path.write_bytes(replace_front_matter_status(path, "superseded"))


def invalidate_paper(state: dict, workspace: Path, reason: str) -> None:
    version = state["paper"].get("current_version")
    entry = state["paper"]["versions"].get(version) if version else None
    if entry and entry.get("status") in {"pending_review", "approved"}:
        _supersede_entry(workspace, entry)
        entry["invalidated_reason"] = reason
    state["paper"]["status"] = "draft"
    state["paper"]["current_version"] = None


def invalidate_problems(
    state: dict, problem_ids: list[int] | set[int], reason: str, workspace: Path,
    *, clear_focus: bool = True, invalidate_paper_artifact: bool = True,
) -> list[int]:
    selected = set(problem_ids)
    affected = [problem for problem in state["problem_order"] if problem in selected]
    for problem in affected:
        entry = state["problems"][str(problem)]
        entry["status"] = "stale"
        entry["validation"] = None
        entry["invalidated_reason"] = reason
    if clear_focus and state.get("current_problem") in selected:
        state["current_problem"] = None
    state["global_validation"] = None
    if invalidate_paper_artifact:
        invalidate_paper(state, workspace, reason)
    return affected


def approve_contract(
    state: dict, workspace: Path, contract_type: str, version: str,
    approval_text: str, problem: int | None,
) -> list[int]:
    store = get_contract_store(state, contract_type, problem)
    entry = store["versions"].get(version)
    expected = canonical_approval(contract_type, version, problem)
    if approval_text != expected:
        raise ValueError(f"Approval text must exactly equal: {expected}")
    if not entry or entry.get("status") != "pending_review":
        raise ValueError("Contract is not pending review")
    path = workspace / entry["file"]
    metadata = read_front_matter(path)
    validate_contract_identity(
        metadata, contract_type, version, problem, "pending_review",
    )

    previous = store.get("current_version")
    graph: dict[int, list[int]] | None = None
    order: list[int] | None = None
    if contract_type == "problem":
        count = len(state["problems"])
        if int(metadata.get("problem_count", count)) != count:
            raise ValueError("Problem Contract count differs from initialized state")
        graph = parse_dependencies(metadata.get("dependencies", ""), count)
        order = stable_topological_order(graph, list(range(1, count + 1)))
    else:
        assert problem is not None
        dependencies = state["problems"][str(problem)]["depends_on"]
        missing = [
            dep for dep in dependencies
            if approved_entry(state["problems"][str(dep)]["solution_contract"]) is None
        ]
        if missing:
            raise ValueError(f"Dependency Solution Contracts must be approved first: {missing}")
        if previous and previous != version:
            affected = set(descendants(state, problem))
            current = state.get("current_problem")
            if current is not None and current not in affected:
                raise ValueError(f"Q{current} is active and unrelated to this replacement")

    approved_bytes = replace_front_matter_status(path, "approved")
    path.write_bytes(approved_bytes)
    if previous and previous != version:
        _supersede_entry(workspace, store["versions"][previous])
    entry.update(
        status="approved", approved_at=now(), approval_text=approval_text,
        content_sha256=hashlib.sha256(approved_bytes).hexdigest(),
        approved_file_size=len(approved_bytes),
    )
    store["current_version"] = version

    affected: list[int] = []
    if contract_type == "problem":
        assert graph is not None and order is not None
        for item, dependencies in graph.items():
            state["problems"][str(item)]["depends_on"] = dependencies
        state["problem_order"] = order
        if previous and previous != version:
            candidates = [
                item for item in order
                if approved_entry(state["problems"][str(item)]["solution_contract"])
                or state["problems"][str(item)].get("outputs")
                or state["problems"][str(item)].get("validation")
                or state["problems"][str(item)].get("status") != "not_started"
            ]
            affected = invalidate_problems(
                state, candidates, f"Problem Contract {version} replaced {previous}", workspace,
            )
            state["current_problem"] = None
        state["expected_action"] = "contract:solution:select"
    else:
        assert problem is not None
        entry["problem_contract_version"] = state["problem_contract"]["current_version"]
        entry["dependency_solution_versions"] = {
            str(dep): state["problems"][str(dep)]["solution_contract"]["current_version"]
            for dep in state["problems"][str(problem)]["depends_on"]
        }
        if previous and previous != version:
            affected = invalidate_problems(
                state, descendants(state, problem),
                f"Solution Contract Q{problem} {version} replaced {previous}", workspace,
            )
        state["expected_action"] = derive_expected_action(state, workspace)
    return affected


def _load_json_object(path: Path, workspace: Path, label: str) -> tuple[dict, bytes]:
    resolved = path.resolve()
    if not resolved.is_relative_to(workspace.resolve()) or not resolved.is_file():
        raise ValueError(f"{label} must exist inside workspace")
    content = resolved.read_bytes()
    try:
        value = json.loads(content)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{label} is invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value, content


def _assert_finite(value: Any, path: str = "report") -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError(f"{path} contains NaN or Inf")
    if isinstance(value, dict):
        for key, child in value.items():
            _assert_finite(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _assert_finite(child, f"{path}[{index}]")


def _validate_checks(report: dict, workspace: Path, *, require_pass: bool) -> None:
    checks = report.get("checks")
    if not isinstance(checks, list) or not checks:
        raise ValueError("Validation report requires checks")
    for check in checks:
        if not isinstance(check, dict):
            raise ValueError("Every validation check must be an object")
        if not check.get("id") or not check.get("status") or not check.get("evidence"):
            raise ValueError("Every validation check requires id, status, and evidence")
        evidence = (workspace / str(check["evidence"])).resolve()
        if not evidence.is_relative_to(workspace.resolve()) or not evidence.is_file():
            raise ValueError(f"Validation evidence is unavailable: {check.get('evidence')}")
        if require_pass and check["status"] != "pass":
            raise ValueError("Passing validation report contains a non-pass check")
        for field in ("value", "expected"):
            if isinstance(check.get(field), bool):
                raise ValueError(f"Validation check {field} cannot use bool as a number")


def validate_problem_report(
    state: dict, workspace: Path, problem: int, report_path: Path,
) -> tuple[dict, str]:
    if str(problem) not in state["problems"]:
        raise ValueError(f"Unknown problem: {problem}")
    report, content = _load_json_object(report_path, workspace, "Validation report")
    _assert_finite(report)
    if "solution_contract_version" not in report and "contract_version" in report:
        report["solution_contract_version"] = report["contract_version"]
    required = {
        "problem", "problem_contract_version", "solution_contract_version",
        "dependency_solution_versions", "status", "checks",
    }
    missing = sorted(required - report.keys())
    if missing:
        raise ValueError(f"Validation report missing fields: {missing}")
    if report["problem"] != problem:
        raise ValueError("Validation report problem mismatch")
    if report["status"] not in VALIDATION_STATUSES:
        raise ValueError(f"Invalid validation status: {report['status']}")
    solution = approved_entry(state["problems"][str(problem)]["solution_contract"])
    if not solution:
        raise ValueError("Approved Solution Contract required")
    if report["problem_contract_version"] != state["problem_contract"]["current_version"]:
        raise ValueError("Validation report Problem Contract version mismatch")
    if report["solution_contract_version"] != solution["version"]:
        raise ValueError("Validation report Solution Contract version mismatch")
    if report["dependency_solution_versions"] != solution.get("dependency_solution_versions"):
        raise ValueError("Validation report dependency Solution versions mismatch")
    _validate_checks(report, workspace, require_pass=report["status"] == "pass")
    return report, hashlib.sha256(content).hexdigest()


# Compatibility alias for existing imports.
def validate_report(state: dict, workspace: Path, problem: int, report_path: Path) -> dict:
    return validate_problem_report(state, workspace, problem, report_path)[0]


def validation_metadata(
    state: dict, problem: int, report_path: Path, workspace: Path, sha256: str,
) -> dict:
    solution = approved_entry(state["problems"][str(problem)]["solution_contract"])
    assert solution is not None
    return {
        "file": str(report_path.resolve().relative_to(workspace.resolve())),
        "sha256": sha256,
        "problem_contract_version": state["problem_contract"]["current_version"],
        "solution_contract_version": solution["version"],
        "dependency_solution_versions": dict(solution["dependency_solution_versions"]),
        "recorded_at": now(),
    }


def revalidate_problem(state: dict, workspace: Path, problem: int) -> dict:
    metadata = state["problems"][str(problem)].get("validation")
    if not isinstance(metadata, dict):
        raise ValueError(f"Q{problem} has no recorded validation")
    report, digest = validate_problem_report(
        state, workspace, problem, workspace / str(metadata.get("file", "")),
    )
    if digest != metadata.get("sha256"):
        raise ValueError(f"Q{problem} validation content hash mismatch")
    expected = {
        "problem_contract_version": report["problem_contract_version"],
        "solution_contract_version": report["solution_contract_version"],
        "dependency_solution_versions": report["dependency_solution_versions"],
    }
    for key, value in expected.items():
        if metadata.get(key) != value:
            raise ValueError(f"Q{problem} validation metadata {key} mismatch")
    return report


def ready_problems(state: dict, workspace: Path) -> list[int]:
    ready: list[int] = []
    for problem in state["problem_order"]:
        entry = state["problems"][str(problem)]
        if entry["status"] not in {"not_started", "stale"}:
            continue
        if solution_compatibility_issues(state, problem):
            continue
        dependencies_ready = True
        for dependency in entry["depends_on"]:
            dependency_entry = state["problems"][str(dependency)]
            if dependency_entry["status"] != "completed":
                dependencies_ready = False
                break
            try:
                report = revalidate_problem(state, workspace, dependency)
                if report["status"] != "pass":
                    dependencies_ready = False
                    break
            except ValueError:
                dependencies_ready = False
                break
        if dependencies_ready:
            ready.append(problem)
    return ready


def derive_expected_action(state: dict, workspace: Path) -> str:
    for version, entry in state["problem_contract"]["versions"].items():
        if entry.get("status") == "pending_review":
            return "approval:problem"
    for raw_problem, problem_entry in state["problems"].items():
        for version, entry in problem_entry["solution_contract"]["versions"].items():
            if entry.get("status") == "pending_review":
                return f"approval:solution:q{raw_problem}"
    if state["paper"].get("status") == "pending_review":
        return "approval:paper"
    if state["paper"].get("status") == "approved":
        return "export:final"
    if approved_entry(state["problem_contract"]) is None:
        return "contract:problem"
    current = state.get("current_problem")
    if current is not None:
        entry = state["problems"][str(current)]
        if entry["status"] == "running":
            validation = entry.get("validation")
            if validation:
                try:
                    report = revalidate_problem(state, workspace, current)
                    if report["status"] == "pass":
                        return f"complete:problem:q{current}"
                    if report["status"] == "repairable":
                        return f"repair:problem:q{current}"
                except ValueError:
                    pass
            return f"run:problem:q{current}"
        if entry["status"] == "blocked":
            existing = state.get("expected_action", "")
            if existing in {
                f"contract:solution:q{current}:new_version", f"decision:problem:q{current}",
            }:
                return existing
            return f"decision:problem:q{current}"
    if all(entry["status"] == "completed" for entry in state["problems"].values()):
        return "paper:submit" if state.get("global_validation") else "validation:global"
    ready = ready_problems(state, workspace)
    if len(ready) == 1:
        return f"start:problem:q{ready[0]}"
    if len(ready) > 1:
        return "select:problem"
    return "contract:solution:select"


def validate_global_report(state: dict, workspace: Path, path: Path) -> tuple[dict, str]:
    report, content = _load_json_object(path, workspace, "Global validation report")
    _assert_finite(report)
    required = {"status", "problem_contract_version", "problem_validations", "checks"}
    missing = sorted(required - report.keys())
    if missing:
        raise ValueError(f"Global validation report missing fields: {missing}")
    if report["status"] != "pass":
        raise ValueError("Global validation status must be pass")
    if report["problem_contract_version"] != state["problem_contract"]["current_version"]:
        raise ValueError("Global validation Problem Contract version mismatch")
    snapshots = report["problem_validations"]
    if not isinstance(snapshots, dict) or set(snapshots) != set(state["problems"]):
        raise ValueError("Global validation problem snapshot set mismatch")
    for raw_problem, entry in state["problems"].items():
        problem = int(raw_problem)
        if entry["status"] != "completed":
            raise ValueError(f"Q{problem} is not completed")
        problem_report = revalidate_problem(state, workspace, problem)
        if problem_report["status"] != "pass":
            raise ValueError(f"Q{problem} validation does not pass")
        snapshot = snapshots[raw_problem]
        if not isinstance(snapshot, dict):
            raise ValueError(f"Global validation Q{problem} snapshot must be an object")
        expected = {
            "solution_contract_version": entry["validation"]["solution_contract_version"],
            "validation_sha256": entry["validation"]["sha256"],
        }
        if snapshot != expected:
            raise ValueError(f"Global validation Q{problem} snapshot mismatch")
    _validate_checks(report, workspace, require_pass=True)
    return report, hashlib.sha256(content).hexdigest()


def global_validation_metadata(state: dict, workspace: Path, path: Path, digest: str) -> dict:
    return {
        "file": str(path.resolve().relative_to(workspace.resolve())),
        "sha256": digest,
        "problem_contract_version": state["problem_contract"]["current_version"],
        "problem_validations": {
            raw: {
                "solution_contract_version": entry["validation"]["solution_contract_version"],
                "validation_sha256": entry["validation"]["sha256"],
            }
            for raw, entry in state["problems"].items()
        },
        "recorded_at": now(),
    }


def revalidate_global(state: dict, workspace: Path) -> dict:
    metadata = state.get("global_validation")
    if not isinstance(metadata, dict):
        raise ValueError("Passing global consistency validation required")
    report, digest = validate_global_report(state, workspace, workspace / str(metadata.get("file", "")))
    if digest != metadata.get("sha256"):
        raise ValueError("Global validation content hash mismatch")
    if metadata.get("problem_contract_version") != report["problem_contract_version"]:
        raise ValueError("Global validation metadata Problem Contract mismatch")
    if metadata.get("problem_validations") != report["problem_validations"]:
        raise ValueError("Global validation metadata problem snapshots mismatch")
    return report


def contract_hash_issues(state: dict, workspace: Path) -> list[str]:
    stores = [("problem", "problem", None, state["problem_contract"])] + [
        (f"solution Q{problem}", "solution", int(problem), entry["solution_contract"])
        for problem, entry in state["problems"].items()
    ]
    issues: list[str] = []
    for label, contract_type, problem, store in stores:
        current = store.get("current_version")
        if current:
            current_entry = store.get("versions", {}).get(current)
            if not current_entry or current_entry.get("status") != "approved":
                issues.append(f"{label} current version {current} is not approved")
        for version, entry in store.get("versions", {}).items():
            if entry.get("status") != "approved":
                continue
            if version != current:
                issues.append(f"{label} {version} approved but not current")
            path = workspace / entry.get("file", "")
            if not path.is_file():
                issues.append(f"{label} {version} file missing")
                continue
            try:
                metadata = read_front_matter(path)
                identity = contract_identity_issues(
                    metadata, contract_type, version, problem, "approved",
                )
                if identity:
                    issues.append(f"{label} {version} identity mismatch: {', '.join(identity)}")
            except ValueError as exc:
                issues.append(str(exc))
            if hashlib.sha256(path.read_bytes()).hexdigest() != entry.get("content_sha256"):
                issues.append(f"{label} {version} content hash mismatch")
    return issues


def validate_state(state: dict, workspace: Path) -> list[str]:
    issues: list[str] = []
    if state.get("schema_version") != SCHEMA_VERSION:
        return [f"schema_version must be {SCHEMA_VERSION}"]
    for field in DEPRECATED_STATE_FIELDS:
        if field in state:
            issues.append(f"deprecated state field present: {field}")
    problems = state.get("problems")
    if not isinstance(problems, dict) or not problems:
        return issues + ["problems must be a non-empty object"]
    try:
        graph = {int(key): list(value.get("depends_on", [])) for key, value in problems.items()}
        expected_order = stable_topological_order(graph, sorted(graph))
        if state.get("problem_order") != expected_order:
            issues.append("problem_order does not match dependency graph")
    except (TypeError, ValueError) as exc:
        issues.append(str(exc))

    pending = _pending_contracts(state)
    if len(pending) > 1:
        issues.append("multiple pending approvals violate the single approval invariant")
    contract_stores = [("problem", None, state["problem_contract"])] + [
        ("solution", int(raw), entry["solution_contract"])
        for raw, entry in problems.items()
    ]
    for contract_type, problem, store in contract_stores:
        for version, contract in store.get("versions", {}).items():
            if contract.get("status") != "pending_review":
                continue
            path = (workspace / str(contract.get("file", ""))).resolve()
            if not path.is_relative_to(workspace.resolve()) or not path.is_file():
                issues.append(f"pending {contract_type} contract {version} file missing")
                continue
            try:
                metadata = read_front_matter(path)
                if contract_identity_issues(
                    metadata, contract_type, version, problem, "pending_review",
                ):
                    issues.append(f"pending {contract_type} contract {version} identity mismatch")
            except ValueError as exc:
                issues.append(str(exc))

    active: list[int] = []
    for raw_problem, entry in problems.items():
        problem = int(raw_problem)
        if "stages" in entry or "validation_report" in entry:
            issues.append(f"Q{problem} contains deprecated fields")
        status = entry.get("status")
        if status not in PROBLEM_STATUSES:
            issues.append(f"Q{problem} has invalid status")
        if status in {"running", "blocked"}:
            active.append(problem)
        if status in {"running", "blocked", "completed"}:
            if approved_entry(state["problem_contract"]) is None:
                issues.append(f"Q{problem} {status} requires an approved Problem Contract")
            solution = approved_entry(entry.get("solution_contract", {}))
            if solution is None:
                issues.append(f"Q{problem} {status} requires an approved Solution Contract")
            elif status in {"running", "completed"}:
                issues.extend(solution_compatibility_issues(state, problem))
            for dependency in entry.get("depends_on", []):
                dependency_entry = problems.get(str(dependency), {})
                if dependency_entry.get("status") != "completed":
                    issues.append(f"Q{problem} dependency Q{dependency} is not completed")
                    continue
                try:
                    dependency_report = revalidate_problem(state, workspace, dependency)
                    if dependency_report["status"] != "pass":
                        issues.append(f"Q{problem} dependency Q{dependency} does not pass")
                except ValueError as exc:
                    issues.append(f"Q{problem} dependency Q{dependency} is invalid: {exc}")
        validation = entry.get("validation")
        if status in {"not_started", "stale"} and validation is not None:
            issues.append(f"Q{problem} {status} must not retain validation")
        if validation is not None:
            try:
                report = revalidate_problem(state, workspace, problem)
                if status == "completed" and report["status"] != "pass":
                    issues.append(f"Q{problem} completed without passing validation")
            except ValueError as exc:
                issues.append(str(exc))
        elif status == "completed":
            issues.append(f"Q{problem} has no recorded validation")

    current = state.get("current_problem")
    if len(active) > 1:
        issues.append("multiple active problems violate single focus")
    if active and current != active[0]:
        issues.append("current_problem must identify the unique active problem")
    if not active and current is not None:
        issues.append("current_problem must be null without an active problem")
    if current is not None and str(current) not in problems:
        issues.append("current_problem is unknown")
    if active and pending:
        issues.append("active problem and pending approval violate single focus")
    issues.extend(contract_hash_issues(state, workspace))

    if state.get("global_validation") is not None:
        try:
            revalidate_global(state, workspace)
        except ValueError as exc:
            issues.append(str(exc))
    paper = state.get("paper", {})
    pending_papers = [
        (version, entry) for version, entry in paper.get("versions", {}).items()
        if entry.get("status") == "pending_review"
    ]
    if pending_papers:
        version, entry = pending_papers[0]
        if paper.get("status") != "pending_review" or paper.get("current_version") != version:
            issues.append("pending paper registry is not the current paper")
        path = (workspace / str(entry.get("file", ""))).resolve()
        if not path.is_relative_to(workspace.resolve()) or not path.is_file():
            issues.append(f"pending paper {version} file missing")
        else:
            try:
                metadata = read_front_matter(path)
                if (
                    metadata.get("artifact_type") != "final_paper"
                    or metadata.get("version") != version
                    or metadata.get("status") != "pending_review"
                ):
                    issues.append(f"pending paper {version} identity mismatch")
            except ValueError as exc:
                issues.append(str(exc))
            if hashlib.sha256(path.read_bytes()).hexdigest() != entry.get("content_sha256"):
                issues.append(f"pending paper {version} content hash mismatch")
    elif paper.get("status") == "pending_review":
        issues.append("paper is pending_review without a pending version")
    if paper.get("status") in {"pending_review", "approved"}:
        try:
            revalidate_global(state, workspace)
        except ValueError as exc:
            issues.append(f"paper upstream invalid: {exc}")
        version = paper.get("current_version")
        entry = paper.get("versions", {}).get(version) if version else None
        if not entry or entry.get("status") != paper.get("status"):
            issues.append("paper current version/status mismatch")
        else:
            path = workspace / entry.get("file", "")
            if not path.is_file():
                issues.append("paper file missing")
            elif hashlib.sha256(path.read_bytes()).hexdigest() != entry.get("content_sha256"):
                issues.append("paper content hash mismatch")
    try:
        derived = derive_expected_action(state, workspace)
        if state.get("expected_action") != derived:
            issues.append(
                f"expected_action mismatch: {state.get('expected_action')} != {derived}"
            )
    except (KeyError, ValueError) as exc:
        issues.append(f"expected_action cannot be derived: {exc}")
    return issues
