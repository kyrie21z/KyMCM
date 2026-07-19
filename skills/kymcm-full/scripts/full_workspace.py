#!/usr/bin/env python3
"""Initialize and diagnose KyMCM Full v1 contest workspaces."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

from checkpoint_full.problem_definition import ProblemDefinitionStore, ProblemDefinitionWorkflow
from checkpoint_full.storage import CheckpointStore
from checkpoint_full.workflow import Workflow
from full_checkpoint import ROOT_ALLOWLIST, validate_layout
from workflow_mode import FULL_WORKFLOW, FULL_VERSION, WorkflowModeError, require_full_mode, workspace_mode


DIRECTORIES = (
    "input/problem", "input/data", "paper", "problems/problem_definition", "reports",
    *(f"problems/q{q}/{part}" for q in range(1, 5)
      for part in ("spec", "code", "data/derived", "outputs", "notes", "result")),
)
DEPENDENCIES = ("numpy", "pandas", "matplotlib", "yaml", "PIL", "openpyxl", "xlrd")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def initialize(workspace: Path, contest: str) -> None:
    workspace = workspace.expanduser().resolve()
    if workspace.exists() and any(workspace.iterdir()):
        raise ValueError(f"workspace target is not empty: {workspace}")
    workspace.mkdir(parents=True, exist_ok=True)
    for relative in DIRECTORIES:
        (workspace / relative).mkdir(parents=True, exist_ok=True)
    _write(workspace / ".kymcm/mode.json", json.dumps(
        {"workflow": FULL_WORKFLOW, "version": FULL_VERSION}, separators=(",", ":"),
    ) + "\n")
    _write(workspace / ".gitignore", "__pycache__/\n*.py[cod]\n*.tmp\n.DS_Store\n")
    _write(workspace / "AGENTS.md", "# Workspace Instructions\n\nUse the `kymcm-full` Skill and KyMCM Full workflow only.\n")
    _write(workspace / "README.md", f"# {contest} KyMCM Full Workspace\n\nInitialized with KyMCM Full v1.0.0. No modeling has started.\n")
    definition = ProblemDefinitionStore(workspace / ".kymcm/checkpoint_lite/problem_definition")
    definition.save_workflow(ProblemDefinitionWorkflow())
    definition.append_event("init")
    for problem in range(1, 5):
        state_root = workspace / f".kymcm/checkpoint_lite/q{problem}"
        state_root.mkdir(parents=True, exist_ok=True)
        store = CheckpointStore(state_root)
        store.save_workflow(Workflow(problem))
        store.append_event({"action": "init"})
    validate_layout(workspace)
    print(f"initialized KyMCM Full workspace: {workspace}")
    print("next: add contest inputs, draft the complete Problem Definition, and request user review")


def doctor(workspace: Path) -> int:
    workspace = workspace.expanduser().resolve()
    before = {p.relative_to(workspace).as_posix(): (p.stat().st_size, p.stat().st_mtime_ns)
              for p in workspace.rglob("*") if p.is_file()} if workspace.is_dir() else {}
    checks: dict[str, object] = {}
    try:
        require_full_mode(workspace)
        checks["workflow"] = workspace_mode(workspace)
        validate_layout(workspace)
        checks["layout"] = "valid"
    except (OSError, ValueError, WorkflowModeError) as exc:
        checks["workspace_error"] = str(exc)
    checks["core_importable"] = True
    checks["python_supported"] = (3, 11) <= sys.version_info[:2] <= (3, 13)
    checks["dependencies"] = {name: importlib.util.find_spec(name) is not None for name in DEPENDENCIES}
    checks["git_available"] = shutil.which("git") is not None
    if checks["git_available"]:
        probe = subprocess.run(["git", "-C", str(workspace), "rev-parse", "--show-toplevel"],
                               text=True, capture_output=True)
        checks["contest_git_repository"] = probe.returncode == 0
    checks["unsafe_symlinks"] = [p.relative_to(workspace).as_posix() for p in workspace.rglob("*") if p.is_symlink()]
    checks["root_entries"] = sorted(p.name for p in workspace.iterdir()) if workspace.is_dir() else []
    checks["root_allowlist"] = not (set(checks["root_entries"]) - ROOT_ALLOWLIST)
    after = {p.relative_to(workspace).as_posix(): (p.stat().st_size, p.stat().st_mtime_ns)
             for p in workspace.rglob("*") if p.is_file()} if workspace.is_dir() else {}
    checks["read_only"] = before == after
    print(json.dumps(checks, ensure_ascii=False, sort_keys=True))
    required = ("workspace_error" not in checks and checks["python_supported"] and checks["git_available"]
                and checks.get("contest_git_repository") and not checks["unsafe_symlinks"]
                and checks["root_allowlist"] and checks["read_only"]
                and all(checks["dependencies"].values()))
    return 0 if required else 1


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    sub = result.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init")
    init.add_argument("--workspace", type=Path, required=True)
    init.add_argument("--contest", choices=("CUMCM", "MCM", "ICM"), required=True)
    check = sub.add_parser("doctor")
    check.add_argument("--workspace", type=Path, required=True)
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        if args.command == "init":
            initialize(args.workspace, args.contest)
            return 0
        return doctor(args.workspace)
    except (OSError, ValueError, WorkflowModeError) as exc:
        raise SystemExit(f"error: {exc}") from exc


if __name__ == "__main__":
    raise SystemExit(main())
