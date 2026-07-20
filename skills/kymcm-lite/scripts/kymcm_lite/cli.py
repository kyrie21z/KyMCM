from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys

from .contracts import check_result, check_start, doctor
from .diagnostics import error, exit_code, render
from .paths import MANAGED_ROOTS, MARKER_BYTES, workspace_path


def positive(value: str) -> int:
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return number


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="KyMCM Lite v3 Markdown handoff checks")
    sub = result.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init"); init.add_argument("--workspace", required=True); init.add_argument("--questions", type=positive, required=True)
    doctor_parser = sub.add_parser("doctor"); doctor_parser.add_argument("--workspace", required=True)
    for name in ("check-start", "check-result"):
        command = sub.add_parser(name); command.add_argument("--workspace", required=True); command.add_argument("--problem", type=positive, required=True)
    return result


def _context_template() -> str:
    path = Path(__file__).resolve().parents[2] / "templates/FROZEN_CONTEXT.template.md"
    lines = path.read_text(encoding="utf-8").splitlines()
    filtered = [line for line in lines if not line.startswith(">")]
    while len(filtered) > 1 and not filtered[1].strip():
        del filtered[1]
    return "\n".join(filtered) + "\n"


def _write(path: Path, content: bytes | str) -> None:
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content, encoding="utf-8")


def initialize(workspace: Path, questions: int) -> int:
    if workspace.is_symlink() or (workspace.exists() and not workspace.is_dir()):
        print(error("LITE-LAYOUT-001", ".", "workspace target is a symlink or is not a directory").render())
        return 1
    conflicts = [name for name in MANAGED_ROOTS if os.path.lexists(workspace / name)]
    if conflicts:
        for name in conflicts:
            print(error("LITE-LAYOUT-001", name, "managed root path already exists; initialization refused").render())
        return 1
    created: list[Path] = []
    workspace_preexisting = workspace.exists()
    try:
        if not workspace_preexisting:
            missing_ancestors: list[Path] = []
            current = workspace
            while not current.exists():
                missing_ancestors.append(current)
                current = current.parent
            workspace.mkdir(parents=True)
            created.extend(reversed(missing_ancestors))
        directories = [workspace / ".kymcm", workspace / "input", workspace / "paper", workspace / "reports", workspace / "problems"]
        for problem in range(1, questions + 1):
            root = workspace / f"problems/q{problem}"
            directories.extend((root, root / "spec", root / "code", root / "data", root / "data/derived", root / "outputs", root / "notes", root / "result"))
        for directory in directories:
            directory.mkdir()
            created.append(directory)
        marker = workspace / ".kymcm/mode.json"; _write(marker, MARKER_BYTES); created.append(marker)
        context = workspace / "FROZEN_CONTEXT.md"; _write(context, _context_template()); created.append(context)
    except Exception:
        for path in reversed(created):
            if path.is_file() or path.is_symlink():
                path.unlink(missing_ok=True)
            elif path.is_dir():
                try: path.rmdir()
                except OSError: pass
        raise
    print(f"Initialized KyMCM Lite workspace: {workspace}")
    print(f"Questions: {questions}")
    print("Next: author problems/q1/spec/START_Q1.md, then run check-start")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    workspace = workspace_path(args.workspace)
    try:
        if args.command == "init":
            return initialize(workspace, args.questions)
        if not workspace.is_dir():
            diagnostics = [error("LITE-LAYOUT-001", ".", "workspace directory does not exist")]
            for line in render(diagnostics): print(line)
            return 1
        if args.command == "doctor":
            info, diagnostics = doctor(workspace)
            for line in info + render(diagnostics): print(line)
            return exit_code(diagnostics)
        diagnostics = check_start(workspace, args.problem) if args.command == "check-start" else check_result(workspace, args.problem)
        for line in render(diagnostics): print(line)
        return exit_code(diagnostics)
    except (UnicodeError, OSError, subprocess.SubprocessError) as exc:
        diagnostic = error("LITE-TOOL-001", ".", f"{type(exc).__name__}: {exc}")
        for line in render([diagnostic]):
            print(line, file=sys.stderr)
        return exit_code([diagnostic])


if __name__ == "__main__":
    raise SystemExit(main())
