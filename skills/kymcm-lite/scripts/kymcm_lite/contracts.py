from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import shutil
import subprocess

from .diagnostics import Diagnostic, error, warning
from .paths import (
    MANAGED_ROOTS, discover_questions, evidence_path_diagnostics, marker_diagnostics,
    question_layout_diagnostics, safe_relative_path, symlink_diagnostics,
)


CONTEXT_HEADINGS = (
    "# FROZEN CONTEXT", "## 1. 共享定义与符号", "## 2. 全局数据口径", "## 3. 已冻结参数与规则",
    "## 4. 跨题输出与文件接口", "## 5. 当前限制与注意事项",
)
START_HEADINGS = (
    "## 1. 问题目标与直接交付", "## 2. 已冻结输入与前问继承", "## 3. 数据口径与预处理",
    "## 4. 数学模型、参数与判定规则", "## 5. Codex 执行边界", "## 6. 输出与证据清单",
    "## 7. 验证、求解预算与停止规则", "## 8. 未决问题",
)
RESULT_HEADINGS = (
    "## 1. 直接答案", "## 2. 实际执行方案与 START 偏差", "## 3. 关键结果", "## 4. 验证与审计",
    "## 5. 证据索引", "## 6. 局限性与风险", "## 7. 下游冻结输出",
)
EVIDENCE_LINE = re.compile(r"^- (E[0-9]+) — `([^`]*)` — (\S.*)$")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*$")


@dataclass(frozen=True)
class Markdown:
    text: str
    headings: tuple[tuple[str, int], ...]

    def section(self, heading: str, required: tuple[str, ...]) -> str:
        matches = [line for text, line in self.headings if text == heading]
        if len(matches) != 1:
            return ""
        start = matches[0]
        following = [line for text, line in self.headings if text in required and line > start]
        end = min(following) - 1 if following else len(self.text.splitlines())
        return "\n".join(self.text.splitlines()[start:end]).strip()


def parse_markdown(text: str) -> Markdown:
    headings: list[tuple[str, int]] = []
    for index, line in enumerate(visible_content(text).splitlines(), 1):
        if match := HEADING.match(line):
            headings.append((f"{match.group(1)} {match.group(2).rstrip()}", index))
    return Markdown(text, tuple(headings))


def visible_content(text: str) -> str:
    without_comments = re.sub(
        r"<!--.*?-->",
        lambda match: "\n" * match.group(0).count("\n"),
        text,
        flags=re.DOTALL,
    )
    lines: list[str] = []
    fence_char: str | None = None
    fence_length = 0
    for line in without_comments.splitlines():
        match = FENCE.match(line)
        if match:
            token = match.group(1)
            if fence_char is None:
                fence_char, fence_length = token[0], len(token)
                lines.append("")
                continue
            if token[0] == fence_char and len(token) >= fence_length:
                fence_char, fence_length = None, 0
                lines.append("")
                continue
        lines.append(line if fence_char is None else "")
    return "\n".join(lines)


def meaningful(text: str) -> bool:
    return bool(visible_content(text).strip())


def _read_contract(path: Path, location: str, identifier: str, expected_title: str) -> tuple[Markdown | None, list[Diagnostic]]:
    if path.is_symlink() or not path.is_file():
        return None, [error(identifier, location, f"missing or unsafe contract; expected {expected_title}")]
    parsed = parse_markdown(path.read_text(encoding="utf-8"))
    titles = [text for text, _ in parsed.headings if text.startswith("# ") and not text.startswith("## ")]
    if titles != [expected_title]:
        return parsed, [error(identifier, location, f"title must be exactly {expected_title}")]
    return parsed, []


def _heading_diagnostics(parsed: Markdown, required: tuple[str, ...], identifier: str, location: str) -> list[Diagnostic]:
    found = [text for text, _ in parsed.headings if text in required]
    counts = {heading: found.count(heading) for heading in required}
    if any(counts[item] != 1 for item in required) or found != list(required):
        return [error(identifier, location, "required headings are missing, duplicated, or reordered")]
    return []


def _git_warning(workspace: Path) -> list[Diagnostic]:
    if shutil.which("git") is None:
        return [warning("LITE-GIT-WARN-001", ".", "Git executable is unavailable; revision diagnostics are disabled")]
    completed = subprocess.run(["git", "-C", str(workspace), "rev-parse", "--show-toplevel"], text=True, capture_output=True)
    if completed.returncode:
        return [warning("LITE-GIT-WARN-001", ".", "workspace is not inside a Git repository")]
    return []


def _base(workspace: Path, problem: int) -> tuple[list[Diagnostic], list[int]]:
    diagnostics = marker_diagnostics(workspace)
    numbers, discovery = discover_questions(workspace)
    diagnostics.extend(discovery)
    if problem not in numbers:
        diagnostics.append(error("LITE-LAYOUT-001", f"problems/q{problem}", "requested managed question does not exist"))
    else:
        diagnostics.extend(question_layout_diagnostics(workspace, problem))
    context = workspace / "FROZEN_CONTEXT.md"
    if context.is_symlink() or not context.is_file():
        diagnostics.append(error("LITE-CONTEXT-001", "FROZEN_CONTEXT.md", "context is missing, unreadable, or unsafe"))
    else:
        context.read_text(encoding="utf-8")
    return diagnostics, numbers


def check_start(workspace: Path, problem: int, *, include_git: bool = True) -> list[Diagnostic]:
    diagnostics, numbers = _base(workspace, problem)
    location = f"problems/q{problem}/spec/START_Q{problem}.md"
    parsed, reading = _read_contract(workspace / location, location, "LITE-START-001", f"# START Q{problem}")
    diagnostics.extend(reading)
    if parsed is not None:
        structure = _heading_diagnostics(parsed, START_HEADINGS, "LITE-START-HEADING-001", location)
        diagnostics.extend(structure)
        if not structure:
            for heading in START_HEADINGS[:-1]:
                if not meaningful(parsed.section(heading, START_HEADINGS)):
                    diagnostics.append(warning("LITE-START-EMPTY-WARN-001", location, f"{heading} has no meaningful author content"))
            unresolved = parsed.section(START_HEADINGS[-1], START_HEADINGS).strip().strip("*_`").strip()
            if unresolved not in {"无", "None", "N/A"}:
                diagnostics.append(error("LITE-START-UNRESOLVED-001", location, "section 8 must be exactly 无, None, or N/A after trimming"))
    if problem >= 2 and (workspace / "FROZEN_CONTEXT.md").is_file():
        context = parse_markdown((workspace / "FROZEN_CONTEXT.md").read_text(encoding="utf-8"))
        interface = context.section("## 4. 跨题输出与文件接口", CONTEXT_HEADINGS[1:])
        if not meaningful(interface):
            diagnostics.append(warning("LITE-CONTEXT-SPARSE-WARN-001", "FROZEN_CONTEXT.md", "Q2+ context lacks a meaningful cross-question interface"))
    if include_git:
        diagnostics.extend(_git_warning(workspace))
    return diagnostics


def check_result(workspace: Path, problem: int) -> list[Diagnostic]:
    diagnostics = check_start(workspace, problem, include_git=False)
    location = f"problems/q{problem}/result/RESULT_Q{problem}.md"
    parsed, reading = _read_contract(workspace / location, location, "LITE-RESULT-001", f"# RESULT Q{problem}")
    diagnostics.extend(reading)
    if parsed is not None:
        structure = _heading_diagnostics(parsed, RESULT_HEADINGS, "LITE-RESULT-HEADING-001", location)
        diagnostics.extend(structure)
        if not structure:
            deviation = visible_content(parsed.section(RESULT_HEADINGS[1], RESULT_HEADINGS))
            paths = re.findall(r"`([^`]*)`", deviation)
            authorized = "授权偏差" in deviation and any(safe_relative_path(path) for path in paths)
            if "无偏差" not in deviation and not authorized:
                diagnostics.append(error("LITE-RESULT-DEVIATION-001", location, "section 2 must state 无偏差 or an 授权偏差 with evidence path"))
            if not meaningful(parsed.section(RESULT_HEADINGS[3], RESULT_HEADINGS)):
                diagnostics.append(warning("LITE-RESULT-VALIDATION-WARN-001", location, "section 4 has no meaningful validation detail"))
            downstream = visible_content(parsed.section(RESULT_HEADINGS[6], RESULT_HEADINGS))
            if not meaningful(downstream) and not any(item in downstream for item in ("无", "None", "N/A", "无后续问题")):
                diagnostics.append(warning("LITE-RESULT-DOWNSTREAM-WARN-001", location, "section 7 lacks downstream output status"))
            evidence_section = visible_content(parsed.section(RESULT_HEADINGS[4], RESULT_HEADINGS))
            candidate_lines = [line for line in evidence_section.splitlines() if line.lstrip().startswith("- E")]
            if not candidate_lines:
                diagnostics.append(error("LITE-EVIDENCE-FORMAT-001", location, "section 5 must contain at least one evidence bullet"))
            identifiers: set[str] = set()
            for line in candidate_lines:
                backticks = re.findall(r"`([^`]*)`", line)
                match = EVIDENCE_LINE.fullmatch(line)
                if len(backticks) != 1 or match is None:
                    diagnostics.append(error("LITE-EVIDENCE-FORMAT-001", location, f"malformed evidence bullet: {line}"))
                    continue
                identifier, raw, _ = match.groups()
                if identifier in identifiers:
                    diagnostics.append(error("LITE-EVIDENCE-FORMAT-001", location, f"duplicate evidence ID {identifier}"))
                    continue
                identifiers.add(identifier)
                diagnostics.extend(evidence_path_diagnostics(workspace, problem, raw))
    diagnostics.extend(_git_warning(workspace))
    if shutil.which("git") and not any(item.identifier == "LITE-GIT-WARN-001" for item in diagnostics):
        scoped = [f"problems/q{problem}/code", f"problems/q{problem}/data/derived"]
        dirty = subprocess.run(["git", "-C", str(workspace), "status", "--porcelain", "--", *scoped], text=True, capture_output=True)
        if dirty.returncode == 0 and dirty.stdout.strip():
            diagnostics.append(warning("LITE-GIT-DIRTY-WARN-001", f"problems/q{problem}", "current-question code or derived data has Git changes"))
    start = workspace / f"problems/q{problem}/spec/START_Q{problem}.md"
    result = workspace / location
    if start.is_file() and result.is_file() and result.stat().st_mtime < start.stat().st_mtime:
        diagnostics.append(warning("LITE-STALE-WARN-001", location, "RESULT is older than START; advisory mtime heuristic only"))
    return diagnostics


def doctor(workspace: Path) -> tuple[list[str], list[Diagnostic]]:
    diagnostics = marker_diagnostics(workspace)
    diagnostics.extend(symlink_diagnostics(workspace, list(MANAGED_ROOTS)))
    for name in (".kymcm", "input", "paper", "reports", "problems"):
        path = workspace / name
        if not path.is_dir() or path.is_symlink():
            diagnostics.append(error("LITE-LAYOUT-001", name, "required managed directory is missing or unsafe"))
    context = workspace / "FROZEN_CONTEXT.md"
    if context.is_symlink() or not context.is_file():
        diagnostics.append(error("LITE-CONTEXT-001", "FROZEN_CONTEXT.md", "context is missing, unreadable, or unsafe"))
    else:
        context.read_text(encoding="utf-8")
    numbers, discovery = discover_questions(workspace)
    diagnostics.extend(discovery)
    for problem in numbers:
        diagnostics.extend(question_layout_diagnostics(workspace, problem))
    if not (3, 11) <= (__import__("sys").version_info[:2]) <= (3, 13):
        diagnostics.append(error("LITE-TOOL-001", "python", "Python 3.11 through 3.13 is required"))
    diagnostics.extend(_git_warning(workspace))
    known = set(MANAGED_ROOTS)
    unknown = sorted(path.name for path in workspace.iterdir() if path.name not in known) if workspace.is_dir() else []
    info = [f"INFO workspace={workspace}", f"INFO questions={','.join(map(str, numbers)) or 'none'}"]
    info.append(f"INFO unknown-root-entries={','.join(unknown) if unknown else 'none'}")
    problems = workspace / "problems"
    unknown_problems = sorted(
        path.name for path in problems.iterdir()
        if not re.fullmatch(r"q[1-9][0-9]*", path.name)
    ) if problems.is_dir() and not problems.is_symlink() else []
    info.append(f"INFO unknown-problem-entries={','.join(unknown_problems) if unknown_problems else 'none'}")
    for problem in numbers:
        start = (workspace / f"problems/q{problem}/spec/START_Q{problem}.md").is_file()
        result = (workspace / f"problems/q{problem}/result/RESULT_Q{problem}.md").is_file()
        info.append(f"INFO q{problem} start={'present' if start else 'absent'} result={'present' if result else 'absent'}")
    return info, diagnostics
