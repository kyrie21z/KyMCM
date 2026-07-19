#!/usr/bin/env python3
"""KyMCM schema v4 single-focus workflow CLI."""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

from contract_state import (
    SCHEMA_VERSION,
    _pending_contracts,
    append_event,
    approve_contract,
    approved_entry,
    atomic_write_json,
    contract_hash_issues,
    derive_expected_action,
    descendants,
    global_validation_metadata,
    initialize_state,
    invalidate_paper,
    invalidate_problems,
    now,
    read_front_matter,
    ready_problems,
    replace_front_matter_status,
    revalidate_global,
    revalidate_problem,
    solution_compatibility_issues,
    submit_contract,
    validate_global_report,
    validate_problem_report,
    validate_state,
    validation_metadata,
)
from workspace_context import add_workspace_argument, resolve_workspace
from workflow_mode import WorkflowModeError, require_mode

try:
    import contest_git as _contest_git
except ImportError:
    _contest_git = None


WORKSPACE: Path
PIPELINE: Path


def configure_workspace(value: str | Path | None) -> None:
    global WORKSPACE, PIPELINE
    WORKSPACE = resolve_workspace(value)
    PIPELINE = WORKSPACE / "state" / "pipeline.json"
    if _contest_git:
        _contest_git.configure_workspace(WORKSPACE)


def ensure_workspace() -> None:
    for relative in (
        "data", "contracts", "plans", "state", "src/models", "src/verifications",
        "results", "latex/images", "output",
    ):
        (WORKSPACE / relative).mkdir(parents=True, exist_ok=True)


def load() -> dict:
    try:
        import json
        state = json.loads(PIPELINE.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        sys.exit(f"[pipeline] state unavailable: {exc}")
    if state.get("schema_version") != SCHEMA_VERSION:
        sys.exit("[pipeline] schema v4 required; legacy workspaces are read-only evidence")
    return state


def save(state: dict) -> None:
    state["updated_at"] = now()
    atomic_write_json(PIPELINE, state)


def fail(message: str) -> None:
    sys.exit(f"[pipeline] {message}")


def cmd_init(args: argparse.Namespace) -> None:
    if PIPELINE.exists():
        fail("workspace is already initialized")
    ensure_workspace()
    state = initialize_state(args.contest, args.choice or "", args.problems)
    save(state)
    (WORKSPACE / "state" / "events.jsonl").touch()
    append_event(WORKSPACE, "workflow_initialized", contest=state["contest"], problems=args.problems)
    if args.git and _contest_git:
        _contest_git.init(contest_name=f"{state['contest']} {state['problem_choice']}".strip())
    print("[pipeline] schema v4 workflow initialized")
    print(f"  contest: {state['contest']}")
    print(f"  problems: {args.problems}")
    print("  execution: dependency-driven single focus")


def cmd_status(args: argparse.Namespace) -> None:
    state = load()
    print("KyMCM Pipeline schema v4")
    print(f"current_problem: {state['current_problem']}")
    print(f"problem_order: {state['problem_order']}")
    print(f"ready_problems: {ready_problems(state, WORKSPACE)}")
    print(f"expected_action: {state['expected_action']}")
    for problem in state["problem_order"]:
        entry = state["problems"][str(problem)]
        solution = entry["solution_contract"].get("current_version")
        print(f"Q{problem}: {entry['status']} solution={solution}")
    print(f"paper: {state['paper']['status']}")


def cmd_validate(args: argparse.Namespace) -> None:
    issues = validate_state(load(), WORKSPACE)
    if issues:
        print("[pipeline] state validation failed:")
        for issue in issues:
            print(f"  - {issue}")
        raise SystemExit(1)
    print("[pipeline] state is consistent")


def cmd_contract(args: argparse.Namespace) -> None:
    state = load()
    try:
        problem = getattr(args, "problem", None)
        if args.contract_command == "create":
            if args.type == "problem":
                path = WORKSPACE / "contracts" / f"problem_{args.version}.md"
                body = (
                    "---\ncontract_type: problem\n"
                    f"version: {args.version}\nstatus: draft\n"
                    f"problem_count: {len(state['problems'])}\n"
                    "dependencies: " + ";".join(
                        f"{item}:" for item in state["problem_order"]
                    ) + "\n---\n\n# Problem Contract\n"
                )
            else:
                if problem is None:
                    raise ValueError("Solution Contract requires --problem")
                path = WORKSPACE / "contracts" / f"solution_q{problem}_{args.version}.md"
                body = (
                    "---\ncontract_type: solution\n"
                    f"problem_id: Q{problem}\nversion: {args.version}\nstatus: draft\n"
                    "---\n\n# Solution Contract\n"
                )
            if path.exists():
                raise ValueError(f"Contract already exists: {path}")
            path.write_text(body, encoding="utf-8")
            print(path.relative_to(WORKSPACE))
            return
        if args.contract_command == "submit":
            submit_contract(state, WORKSPACE, args.type, args.version, args.file, problem)
            append_event(
                WORKSPACE, "contract_submitted", contract_type=args.type,
                problem=problem, version=args.version,
            )
        elif args.contract_command == "approve":
            affected = approve_contract(
                state, WORKSPACE, args.type, args.version, args.approval_text, problem,
            )
            if args.type == "solution":
                plan = WORKSPACE / "plans" / f"implementation_q{problem}.md"
                plan.write_text(
                    f"# Implementation Plan Q{problem}\n\n"
                    f"Based on approved Solution Contract {args.version}.\n\n"
                    "This execution checklist is not an approval boundary.\n",
                    encoding="utf-8",
                )
            append_event(
                WORKSPACE, "contract_approved", contract_type=args.type,
                problem=problem, version=args.version, affected=affected,
            )
        elif args.contract_command == "supersede":
            store = (
                state["problem_contract"] if args.type == "problem"
                else state["problems"][str(problem)]["solution_contract"]
            )
            entry = store["versions"].get(args.version)
            if not entry or entry["status"] != "approved":
                raise ValueError("Only an approved version can be superseded")
            entry["status"] = "superseded"
            path = WORKSPACE / entry["file"]
            path.write_bytes(replace_front_matter_status(path, "superseded"))
            if store.get("current_version") == args.version:
                store["current_version"] = None
            affected = (
                list(state["problem_order"]) if args.type == "problem"
                else descendants(state, int(problem))
            )
            invalidate_problems(
                state, affected, f"{args.type} contract {args.version} superseded", WORKSPACE,
            )
            state["expected_action"] = "contract:problem" if args.type == "problem" else derive_expected_action(state, WORKSPACE)
            append_event(WORKSPACE, "contract_superseded", version=args.version, affected=affected)
        else:
            raise ValueError("Contract subcommand required")
    except (OSError, ValueError, KeyError) as exc:
        fail(f"contract rejected: {exc}")
    save(state)
    print(f"[pipeline] contract {args.contract_command} complete")


def cmd_start_problem(args: argparse.Namespace) -> None:
    state = load()
    problem = args.problem
    if str(problem) not in state["problems"]:
        fail(f"unknown problem Q{problem}")
    pending = _pending_contracts(state)
    if pending:
        fail(f"pending approval must be resolved first: {pending[0]}")
    active = [
        int(raw) for raw, entry in state["problems"].items()
        if entry["status"] in {"running", "blocked"}
    ]
    if state.get("current_problem") is not None or active:
        fail(f"another problem is active: {active or [state['current_problem']]}")
    entry = state["problems"][str(problem)]
    if entry["status"] not in {"not_started", "stale"}:
        fail(f"Q{problem} cannot start from {entry['status']}")
    compatibility = solution_compatibility_issues(state, problem)
    if compatibility:
        fail(compatibility[0])
    for dependency in entry["depends_on"]:
        dependency_entry = state["problems"][str(dependency)]
        if dependency_entry["status"] != "completed":
            fail(f"dependency Q{dependency} is not completed")
        try:
            report = revalidate_problem(state, WORKSPACE, dependency)
        except ValueError as exc:
            fail(f"dependency Q{dependency} validation is invalid: {exc}")
        if report["status"] != "pass":
            fail(f"dependency Q{dependency} validation does not pass")
    entry["status"] = "running"
    entry["validation"] = None
    entry["invalidated_reason"] = None
    state["current_problem"] = problem
    state["expected_action"] = f"run:problem:q{problem}"
    save(state)
    append_event(WORKSPACE, "problem_started", problem=problem)
    print(f"[pipeline] Q{problem} started")


def cmd_record_validation(args: argparse.Namespace) -> None:
    state = load()
    problem = args.problem
    if state.get("current_problem") != problem:
        fail(f"Q{problem} is not the current problem")
    entry = state["problems"][str(problem)]
    if entry["status"] not in {"running", "blocked"}:
        fail(f"Q{problem} cannot record validation from {entry['status']}")
    report_path = (WORKSPACE / args.report).resolve()
    try:
        report, digest = validate_problem_report(state, WORKSPACE, problem, report_path)
    except ValueError as exc:
        fail(f"validation rejected: {exc}")
    invalidate_paper(state, WORKSPACE, f"Q{problem} validation changed")
    state["global_validation"] = None
    entry["validation"] = validation_metadata(state, problem, report_path, WORKSPACE, digest)
    if report["status"] == "pass":
        entry["status"] = "running"
        state["expected_action"] = f"complete:problem:q{problem}"
    elif report["status"] == "repairable":
        entry["status"] = "running"
        state["expected_action"] = f"repair:problem:q{problem}"
    elif report["status"] == "contract_change_required":
        entry["status"] = "blocked"
        state["expected_action"] = f"contract:solution:q{problem}:new_version"
    else:
        entry["status"] = "blocked"
        state["expected_action"] = f"decision:problem:q{problem}"
    save(state)
    append_event(WORKSPACE, "validation_recorded", problem=problem, status=report["status"])
    print(f"[pipeline] validation Q{problem}: {report['status']}")


def cmd_complete_problem(args: argparse.Namespace) -> None:
    state = load()
    problem = args.problem
    if state.get("current_problem") != problem:
        fail(f"Q{problem} is not current")
    entry = state["problems"][str(problem)]
    if entry["status"] != "running":
        fail(f"Q{problem} cannot complete from {entry['status']}")
    try:
        report = revalidate_problem(state, WORKSPACE, problem)
    except ValueError as exc:
        fail(f"completion rejected: {exc}")
    if report["status"] != "pass":
        fail("validation status must be pass")
    entry["status"] = "completed"
    state["current_problem"] = None
    state["expected_action"] = derive_expected_action(state, WORKSPACE)
    save(state)
    append_event(WORKSPACE, "problem_completed", problem=problem)
    print(f"[pipeline] Q{problem} completed")


def cmd_invalidate_problem(args: argparse.Namespace) -> None:
    state = load()
    if str(args.problem) not in state["problems"]:
        fail(f"unknown problem Q{args.problem}")
    affected = invalidate_problems(
        state, descendants(state, args.problem), args.reason, WORKSPACE,
    )
    state["expected_action"] = derive_expected_action(state, WORKSPACE)
    save(state)
    append_event(
        WORKSPACE, "problem_invalidated", problem=args.problem,
        affected=affected, reason=args.reason,
    )
    print(f"[pipeline] stale problems: {affected}")


def cmd_record_global_validation(args: argparse.Namespace) -> None:
    state = load()
    path = (WORKSPACE / args.report).resolve()
    try:
        _, digest = validate_global_report(state, WORKSPACE, path)
    except ValueError as exc:
        fail(f"global validation rejected: {exc}")
    invalidate_paper(state, WORKSPACE, "global validation changed")
    state["global_validation"] = global_validation_metadata(state, WORKSPACE, path, digest)
    state["expected_action"] = "paper:submit"
    save(state)
    append_event(WORKSPACE, "global_validation_recorded", status="pass")
    print("[pipeline] global validation: pass")


def _require_current_evidence(state: dict) -> None:
    pending_contracts = [
        f"{label} {version}"
        for label, store in [
            ("Problem Contract", state["problem_contract"]),
            *[
                (f"Solution Contract Q{raw}", entry["solution_contract"])
                for raw, entry in state["problems"].items()
            ],
        ]
        for version, contract in store["versions"].items()
        if contract.get("status") == "pending_review"
    ]
    if pending_contracts:
        raise ValueError(f"pending contract must be resolved: {pending_contracts[0]}")
    contract_issues = contract_hash_issues(state, WORKSPACE)
    if contract_issues:
        raise ValueError(f"current contract is invalid: {contract_issues[0]}")
    if any(entry["status"] != "completed" for entry in state["problems"].values()):
        raise ValueError("all problems must be completed before Final Paper Checkpoint")
    for raw_problem in state["problems"]:
        report = revalidate_problem(state, WORKSPACE, int(raw_problem))
        if report["status"] != "pass":
            raise ValueError(f"Q{raw_problem} validation does not pass")
    revalidate_global(state, WORKSPACE)


def cmd_paper(args: argparse.Namespace) -> None:
    state = load()
    try:
        _require_current_evidence(state)
        if args.paper_command == "submit":
            pending = [
                version for version, entry in state["paper"]["versions"].items()
                if entry.get("status") == "pending_review"
            ]
            if pending:
                raise ValueError(f"Final Paper {pending[0]} is already pending")
            if args.version in state["paper"]["versions"]:
                raise ValueError(f"Final Paper version already exists: {args.version}")
            path = (WORKSPACE / args.file).resolve()
            if not path.is_relative_to(WORKSPACE.resolve()) or not path.is_file():
                raise ValueError("paper file unavailable")
            metadata = read_front_matter(path)
            if metadata.get("artifact_type") != "final_paper" or metadata.get("version") != args.version:
                raise ValueError("paper front matter identity mismatch")
            approved_current = state["paper"].get("current_version")
            if approved_current and approved_current != args.version:
                old = state["paper"]["versions"].get(approved_current)
                if old and old.get("status") in {"approved", "pending_review"}:
                    old["status"] = "superseded"
                    old_path = WORKSPACE / old["file"]
                    old_path.write_bytes(replace_front_matter_status(old_path, "superseded"))
            pending_bytes = replace_front_matter_status(path, "pending_review")
            path.write_bytes(pending_bytes)
            state["paper"]["versions"][args.version] = {
                "version": args.version,
                "status": "pending_review",
                "file": str(path.relative_to(WORKSPACE)),
                "content_sha256": hashlib.sha256(pending_bytes).hexdigest(),
                "submitted_at": now(),
            }
            state["paper"]["current_version"] = args.version
            state["paper"]["status"] = "pending_review"
            state["expected_action"] = "approval:paper"
        elif args.paper_command == "approve":
            expected = f"批准 Final Paper {args.version}"
            if args.approval_text != expected:
                raise ValueError(f"approval text must exactly equal: {expected}")
            entry = state["paper"]["versions"].get(args.version)
            if not entry or entry["status"] != "pending_review":
                raise ValueError("paper version is not pending review")
            path = WORKSPACE / entry["file"]
            if hashlib.sha256(path.read_bytes()).hexdigest() != entry.get("content_sha256"):
                raise ValueError("paper content changed after submission")
            approved = replace_front_matter_status(path, "approved")
            path.write_bytes(approved)
            entry.update(
                status="approved", content_sha256=hashlib.sha256(approved).hexdigest(),
                approved_at=now(),
            )
            state["paper"]["status"] = "approved"
            state["expected_action"] = "export:final"
        else:
            raise ValueError("paper subcommand required")
    except (OSError, ValueError, KeyError) as exc:
        fail(f"paper rejected: {exc}")
    save(state)
    append_event(WORKSPACE, f"paper_{args.paper_command}", version=args.version)
    print(f"[pipeline] Final Paper {args.paper_command}: {args.version}")


def cmd_contest_git(args: argparse.Namespace) -> None:
    if not _contest_git:
        fail("contest_git unavailable")
    if args.git_command == "status":
        print(_contest_git.status())
    elif args.git_command == "log":
        print(_contest_git.log())
    else:
        fail("contest-git subcommand required")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="KyMCM schema v4 workflow manager")
    add_workspace_argument(parser)
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init")
    init.add_argument("--contest", choices=["CUMCM", "MCM", "ICM"], default="CUMCM")
    init.add_argument("--choice", default="")
    init.add_argument("--problems", type=int, default=1)
    init.add_argument("--git", action="store_true")
    sub.add_parser("status")
    sub.add_parser("validate-state")

    contract = sub.add_parser("contract")
    contract_sub = contract.add_subparsers(dest="contract_command", required=True)
    for command in ("create", "submit", "approve", "supersede"):
        item = contract_sub.add_parser(command)
        item.add_argument("--type", required=True, choices=["problem", "solution"])
        item.add_argument("--problem", type=int)
        item.add_argument("--version", required=True)
        if command == "submit":
            item.add_argument("--file", required=True)
        elif command == "approve":
            item.add_argument("--approval-text", required=True)

    start = sub.add_parser("start-problem")
    start.add_argument("problem", type=int)
    validation = sub.add_parser("record-validation")
    validation.add_argument("problem", type=int)
    validation.add_argument("report")
    complete = sub.add_parser("complete-problem")
    complete.add_argument("problem", type=int)
    invalidate = sub.add_parser("invalidate-problem")
    invalidate.add_argument("problem", type=int)
    invalidate.add_argument("--reason", required=True)
    global_validation = sub.add_parser("record-global-validation")
    global_validation.add_argument("report")

    paper = sub.add_parser("paper")
    paper_sub = paper.add_subparsers(dest="paper_command", required=True)
    submit = paper_sub.add_parser("submit")
    submit.add_argument("--version", required=True)
    submit.add_argument("--file", required=True)
    approve = paper_sub.add_parser("approve")
    approve.add_argument("--version", required=True)
    approve.add_argument("--approval-text", required=True)

    contest = sub.add_parser("contest-git")
    contest_sub = contest.add_subparsers(dest="git_command", required=True)
    contest_sub.add_parser("status")
    contest_sub.add_parser("log")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    try:
        require_mode(resolve_workspace(args.workspace), "legacy")
    except WorkflowModeError as exc:
        fail(str(exc))
    configure_workspace(args.workspace)
    commands = {
        "init": cmd_init,
        "status": cmd_status,
        "validate-state": cmd_validate,
        "contract": cmd_contract,
        "start-problem": cmd_start_problem,
        "record-validation": cmd_record_validation,
        "complete-problem": cmd_complete_problem,
        "invalidate-problem": cmd_invalidate_problem,
        "record-global-validation": cmd_record_global_validation,
        "paper": cmd_paper,
        "contest-git": cmd_contest_git,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
