from __future__ import annotations

import json
import os
from pathlib import Path, PureWindowsPath
import re

from .diagnostics import Diagnostic, error


MARKER_BYTES = b'{"workflow":"kymcm_lite","version":3}\n'
QUESTION = re.compile(r"q([1-9][0-9]*)")
MANAGED_ROOTS = (".kymcm", "input", "paper", "reports", "problems")
LEGACY_IGNORED_ROOTS = ("FROZEN_CONTEXT.md",)
QUESTION_DIRS = ("spec", "code", "data", "data/derived", "outputs", "notes", "result")
EVIDENCE_DIRS = ("code", "data/derived", "outputs", "notes")


def workspace_path(raw: str | Path) -> Path:
    return Path(os.path.abspath(os.path.expanduser(os.fspath(raw))))


def marker_diagnostics(workspace: Path) -> list[Diagnostic]:
    location = ".kymcm/mode.json"
    marker = workspace / location
    if marker.is_symlink():
        return [error("LITE-LAYOUT-SYMLINK-001", location, "managed marker must not be a symlink")]
    if not marker.is_file():
        return [error("LITE-MODE-001", location, "exact Lite v3 marker is missing")]
    content = marker.read_bytes()
    try:
        value = json.loads(content.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return [error("LITE-MODE-001", location, "marker is malformed; expected exact Lite v3 marker")]
    if value != {"workflow": "kymcm_lite", "version": 3} or content != MARKER_BYTES:
        return [error("LITE-MODE-001", location, "marker is not exactly kymcm_lite version 3")]
    return []


def symlink_diagnostics(workspace: Path, relatives: list[str]) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    if workspace.is_symlink():
        diagnostics.append(error("LITE-LAYOUT-SYMLINK-001", ".", "workspace root must not be a symlink"))
        return diagnostics
    seen: set[str] = set()
    for relative in relatives:
        current = workspace
        for part in Path(relative).parts:
            current /= part
            shown = current.relative_to(workspace).as_posix()
            if shown not in seen and current.is_symlink():
                diagnostics.append(error("LITE-LAYOUT-SYMLINK-001", shown, "managed path component must not be a symlink"))
                seen.add(shown)
                break
    return diagnostics


def discover_questions(workspace: Path) -> tuple[list[int], list[Diagnostic]]:
    problems = workspace / "problems"
    if problems.is_symlink() or not problems.is_dir():
        return [], [error("LITE-LAYOUT-001", "problems", "managed problems directory is missing or unsafe")]
    numbers = sorted(
        int(match.group(1))
        for child in problems.iterdir()
        if (match := QUESTION.fullmatch(child.name))
    )
    if not numbers:
        return [], [error("LITE-LAYOUT-001", "problems", "at least problems/q1 is required")]
    expected = list(range(1, max(numbers) + 1))
    if numbers != expected:
        return numbers, [error("LITE-LAYOUT-001", "problems", f"question directories must be contiguous from q1; found {numbers}")]
    return numbers, []


def question_layout_diagnostics(workspace: Path, problem: int) -> list[Diagnostic]:
    root = workspace / f"problems/q{problem}"
    diagnostics: list[Diagnostic] = []
    relatives = [".kymcm", "problems", f"problems/q{problem}"]
    relatives.extend(f"problems/q{problem}/{part}" for part in QUESTION_DIRS)
    diagnostics.extend(symlink_diagnostics(workspace, relatives))
    for part in QUESTION_DIRS:
        path = root / part
        if not path.is_dir() or path.is_symlink():
            diagnostics.append(error("LITE-LAYOUT-001", f"problems/q{problem}/{part}", "required managed directory is missing or unsafe"))
    return diagnostics


def safe_relative_path(raw: str) -> bool:
    if not raw or any(ord(character) < 32 or ord(character) == 127 for character in raw):
        return False
    if Path(raw).is_absolute() or PureWindowsPath(raw).is_absolute() or PureWindowsPath(raw).drive:
        return False
    if raw.startswith(("/", "\\", "//")) or ".." in Path(raw).parts or ".." in PureWindowsPath(raw).parts:
        return False
    return True


def evidence_path_diagnostics(workspace: Path, problem: int, raw: str) -> list[Diagnostic]:
    location = f"problems/q{problem}/result/RESULT_Q{problem}.md"
    if not safe_relative_path(raw):
        return [error("LITE-EVIDENCE-PATH-001", location, f"unsafe evidence path {raw!r}")]
    relative = Path(raw)
    allowed_prefixes = tuple(Path(f"problems/q{problem}/{part}") for part in EVIDENCE_DIRS)
    if not any(relative == prefix or prefix in relative.parents for prefix in allowed_prefixes):
        return [error("LITE-EVIDENCE-SCOPE-001", location, f"evidence is outside Q{problem} allowed directories: {raw}")]
    current = workspace
    for part in relative.parts:
        current /= part
        if os.path.lexists(current) and current.is_symlink():
            return [error("LITE-EVIDENCE-SYMLINK-001", raw, "evidence path contains a symlink")]
    target = workspace / relative
    if not target.is_file() or target.is_symlink():
        return [error("LITE-EVIDENCE-MISSING-001", raw, "evidence must be an existing ordinary file")]
    resolved = target.resolve()
    question = (workspace / f"problems/q{problem}").resolve()
    if question not in resolved.parents:
        return [error("LITE-EVIDENCE-SCOPE-001", raw, "evidence resolves outside the current question")]
    return []
