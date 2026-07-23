from __future__ import annotations

from dataclasses import dataclass
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
CONTRACT_LIKE = re.compile(r"^(?:START|RESULT)_Q")
START_CONTRACT = re.compile(r"^START_Q([1-9][0-9]*)(?:_([1-9][0-9]*))?\.md$")
RESULT_CONTRACT = re.compile(r"^RESULT_Q([1-9][0-9]*)(?:_([1-9][0-9]*))?\.md$")


@dataclass(frozen=True, order=True)
class ContractId:
    question: int
    subproblem: int | None = None

    def __post_init__(self) -> None:
        if self.question < 1 or (self.subproblem is not None and self.subproblem < 1):
            raise ValueError("contract identifiers require positive integers")

    @property
    def token(self) -> str:
        suffix = f"_{self.subproblem}" if self.subproblem is not None else ""
        return f"Q{self.question}{suffix}"

    @property
    def start_path(self) -> str:
        return f"problems/q{self.question}/spec/START_{self.token}.md"

    @property
    def result_path(self) -> str:
        return f"problems/q{self.question}/result/RESULT_{self.token}.md"

    def title(self, kind: str) -> str:
        return f"# {kind} {self.token}"


@dataclass(frozen=True)
class ContractDiscovery:
    mode: str
    starts: tuple[ContractId, ...]
    results: tuple[ContractId, ...]
    diagnostics: tuple[Diagnostic, ...]


def _contract_entries(
    workspace: Path,
    problem: int,
    directory: str,
    kind: str,
) -> tuple[list[ContractId], list[Diagnostic]]:
    root = workspace / f"problems/q{problem}/{directory}"
    pattern = START_CONTRACT if kind == "START" else RESULT_CONTRACT
    found: list[ContractId] = []
    diagnostics: list[Diagnostic] = []
    if not root.is_dir() or root.is_symlink():
        return found, diagnostics
    for entry in sorted(root.iterdir(), key=lambda item: item.name):
        if not CONTRACT_LIKE.match(entry.name):
            continue
        location = entry.relative_to(workspace).as_posix()
        match = pattern.fullmatch(entry.name)
        if (
            match is None
            or int(match.group(1)) != problem
            or entry.is_symlink()
            or not entry.is_file()
        ):
            diagnostics.append(error(
                "LITE-CONTRACT-LAYOUT-001",
                location,
                f"malformed, misplaced, or unsafe {kind} contract-like entry",
            ))
            continue
        found.append(ContractId(problem, int(match.group(2)) if match.group(2) else None))
    return found, diagnostics


def discover_contracts(workspace: Path, problem: int) -> ContractDiscovery:
    starts, diagnostics = _contract_entries(workspace, problem, "spec", "START")
    results, result_diagnostics = _contract_entries(workspace, problem, "result", "RESULT")
    order = lambda item: (item.question, item.subproblem or 0)
    starts.sort(key=order)
    results.sort(key=order)
    diagnostics.extend(result_diagnostics)
    single_starts = [item for item in starts if item.subproblem is None]
    split_starts = [item for item in starts if item.subproblem is not None]
    if single_starts and split_starts:
        mode = "invalid"
        diagnostics.append(error(
            "LITE-CONTRACT-LAYOUT-001",
            f"problems/q{problem}/spec",
            "single and split START contracts must not be mixed",
        ))
    elif single_starts:
        mode = "single"
    elif split_starts:
        mode = "split"
    else:
        mode = "none"
    if mode == "split":
        suffixes = [item.subproblem for item in split_starts]
        expected = list(range(1, max(suffixes or [0]) + 1))
        if suffixes != expected:
            diagnostics.append(error(
                "LITE-CONTRACT-LAYOUT-001",
                f"problems/q{problem}/spec",
                f"split START suffixes must be contiguous from 1; found {suffixes}",
            ))
        active = set(split_starts)
        invalid_results = [
            item for item in results
            if item.subproblem is None or item not in active
        ]
    elif mode == "single":
        active = set(single_starts)
        invalid_results = [item for item in results if item not in active]
    else:
        invalid_results = list(results)
    for item in invalid_results:
        diagnostics.append(error(
            "LITE-CONTRACT-LAYOUT-001",
            item.result_path,
            f"RESULT {item.token} does not match the active START contract mode",
        ))
    return ContractDiscovery(
        mode,
        tuple(starts),
        tuple(results),
        tuple(diagnostics),
    )


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


def evidence_path_diagnostics(
    workspace: Path,
    problem: int,
    raw: str,
    *,
    location: str | None = None,
) -> list[Diagnostic]:
    location = location or f"problems/q{problem}/result/RESULT_Q{problem}.md"
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
