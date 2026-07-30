from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import shutil
import subprocess

from .diagnostics import Diagnostic, error, warning
from .paths import (
    ContractDiscovery, ContractId, LEGACY_IGNORED_ROOTS, MANAGED_ROOTS, OPTIONAL_ROOTS,
    PREPROCESS_RESULT, PREPROCESS_ROOT, PREPROCESS_START,
    discover_contracts, discover_questions,
    evidence_path_diagnostics, marker_diagnostics, preprocess_evidence_path_diagnostics,
    preprocess_layout_diagnostics, question_layout_diagnostics, safe_relative_path,
    symlink_diagnostics,
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
PREPROCESS_START_HEADINGS = (
    "## 1. 预处理目标与下游交付",
    "## 2. 原始数据、口径与数据字典",
    "## 3. 数据质量审计与处理规则",
    "## 4. 探索性分析计划与表述边界",
    "## 5. Codex 执行边界",
    "## 6. 输出与证据清单",
    "## 7. 验证、计算预算与停止规则",
    "## 8. 未决问题",
)
PREPROCESS_RESULT_HEADINGS = (
    "## 1. 预处理结论",
    "## 2. 实际执行方案与 START_PRE 偏差",
    "## 3. 数据质量与样本变化",
    "## 4. 探索性分析结果",
    "## 5. 冻结数据产品与数据字典",
    "## 6. 验证与审计",
    "## 7. 证据索引",
    "## 8. 局限性与下游使用边界",
)
EVIDENCE_LINE = re.compile(r"^- (E[0-9]+) — `([^`]*)` — (\S.*)$")
DEPENDENCY_LABEL = "**前问依赖：**"
PREPROCESS_DEPENDENCY_LABEL = "**预处理依赖：**"
DEPENDENCY_TOKEN = r"Q(?:0|-[1-9][0-9]*|[1-9][0-9]*)(?:_[1-9][0-9]*)?"
DEPENDENCY_VALUE = re.compile(rf"^(?:无|{DEPENDENCY_TOKEN}(?:, {DEPENDENCY_TOKEN})*)$")
DEPENDENCY_PARSE = re.compile(r"^Q(-?[0-9]+)(?:_([1-9][0-9]*))?$")
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


def read_contract(path: Path, location: str, identifier: str, expected_title: str) -> tuple[Markdown | None, list[Diagnostic]]:
    if path.is_symlink() or not path.is_file():
        return None, [error(identifier, location, f"missing or unsafe contract; expected {expected_title}")]
    parsed = parse_markdown(path.read_text(encoding="utf-8"))
    titles = [text for text, _ in parsed.headings if text.startswith("# ") and not text.startswith("## ")]
    if titles != [expected_title]:
        return parsed, [error(identifier, location, f"title must be exactly {expected_title}")]
    return parsed, []


def heading_diagnostics(parsed: Markdown, required: tuple[str, ...], identifier: str, location: str) -> list[Diagnostic]:
    found = [text for text, _ in parsed.headings if text in required]
    counts = {heading: found.count(heading) for heading in required}
    if any(counts[item] != 1 for item in required) or found != list(required):
        return [error(identifier, location, "required headings are missing, duplicated, or reordered")]
    return []


def dependency_diagnostics(
    workspace: Path,
    current: ContractId,
    numbers: list[int],
    parsed: Markdown,
    location: str,
) -> list[Diagnostic]:
    section = visible_content(parsed.section(START_HEADINGS[1], START_HEADINGS))
    candidates = [line for line in section.splitlines() if "前问依赖" in line]
    if len(candidates) != 1:
        return [
            error(
                "LITE-START-DEPENDENCY-001",
                location,
                "section 2 must contain exactly one visible dependency declaration",
            )
        ]
    declaration = candidates[0]
    prefix = f"{DEPENDENCY_LABEL} "
    if not declaration.startswith(prefix):
        return [
            error(
                "LITE-START-DEPENDENCY-001",
                location,
                f"dependency declaration must use exactly {DEPENDENCY_LABEL} followed by one space",
            )
        ]
    raw = declaration[len(prefix):]
    if not DEPENDENCY_VALUE.fullmatch(raw):
        return [
            error(
                "LITE-START-DEPENDENCY-001",
                location,
                "dependency value must be 无 or an exact ascending list such as Q1, Q1_1, Q2",
            )
        ]
    raw_dependencies = [] if raw == "无" else raw.split(", ")
    dependencies = [
        (int(match.group(1)), int(match.group(2)) if match.group(2) else None)
        for item in raw_dependencies
        if (match := DEPENDENCY_PARSE.fullmatch(item))
    ]
    order = [(question, subproblem or 0) for question, subproblem in dependencies]
    if (
        len(dependencies) != len(raw_dependencies)
        or (current.question == 1 and dependencies)
        or len(dependencies) != len(set(dependencies))
        or order != sorted(order)
        or any(
            question < 1
            or question >= current.question
            or question not in numbers
            for question, _ in dependencies
        )
    ):
        return [
            error(
                "LITE-START-DEPENDENCY-SCOPE-001",
                location,
                "dependencies must be unique, strictly ordered exact units from existing earlier questions; Q1 must use 无",
            )
        ]
    diagnostics: list[Diagnostic] = []
    for question, subproblem in dependencies:
        dependency = ContractId(question, subproblem)
        discovery = discover_contracts(workspace, question)
        valid_mode = (
            (
                subproblem is None
                and discovery.mode == "single"
                and dependency in discovery.starts
            )
            or (
                subproblem is not None
                and discovery.mode == "split"
                and dependency in discovery.starts
            )
            or discovery.mode == "none"
        )
        if not valid_mode:
            diagnostics.append(error(
                "LITE-START-DEPENDENCY-SCOPE-001",
                location,
                f"{dependency.token} is not an exact active upstream contract unit",
            ))
            continue
        contracts = (
            (
                dependency.start_path,
                dependency.title("START"),
                START_HEADINGS,
            ),
            (
                dependency.result_path,
                dependency.title("RESULT"),
                RESULT_HEADINGS,
            ),
        )
        for upstream_location, title, headings in contracts:
            try:
                upstream, reading = read_contract(
                    workspace / upstream_location,
                    upstream_location,
                    "LITE-START-DEPENDENCY-CONTRACT-001",
                    title,
                )
            except (UnicodeError, OSError) as exc:
                diagnostics.append(
                    error(
                        "LITE-START-DEPENDENCY-CONTRACT-001",
                        upstream_location,
                        f"upstream contract is unreadable: {type(exc).__name__}",
                    )
                )
                continue
            diagnostics.extend(reading)
            if upstream is not None:
                diagnostics.extend(
                    heading_diagnostics(
                        upstream,
                        headings,
                        "LITE-START-DEPENDENCY-CONTRACT-001",
                        upstream_location,
                    )
                )
    return diagnostics


def preprocess_dependency_diagnostics(
    workspace: Path,
    parsed: Markdown,
    location: str,
) -> tuple[str | None, list[Diagnostic]]:
    visible = visible_content(parsed.text)
    section = visible_content(parsed.section(START_HEADINGS[1], START_HEADINGS))
    all_candidates = [
        line for line in visible.splitlines() if "预处理依赖" in line
    ]
    section_candidates = [
        line for line in section.splitlines() if "预处理依赖" in line
    ]
    preprocess_exists = (workspace / PREPROCESS_ROOT).exists()
    if not all_candidates:
        if preprocess_exists:
            return None, [warning(
                "LITE-START-PREPROCESS-WARN-001", location,
                "preprocess exists but this legacy START has no explicit 预处理依赖 declaration",
            )]
        return None, []
    if len(all_candidates) != 1 or len(section_candidates) != 1:
        return None, [error(
            "LITE-START-PREPROCESS-001", location,
            "exactly one visible preprocess declaration is allowed in section 2",
        )]
    declaration = section_candidates[0]
    prefix = f"{PREPROCESS_DEPENDENCY_LABEL} "
    if not declaration.startswith(prefix):
        return None, [error(
            "LITE-START-PREPROCESS-001", location,
            f"preprocess declaration must use exactly {PREPROCESS_DEPENDENCY_LABEL} followed by one space",
        )]
    value = declaration[len(prefix):]
    if value not in {"无", "PRE"}:
        return None, [error(
            "LITE-START-PREPROCESS-001", location,
            "preprocess dependency value must be exactly 无 or PRE",
        )]
    lines = [line for line in section.splitlines() if line.strip()]
    preprocess_index = lines.index(declaration)
    dependency_indices = [
        index for index, line in enumerate(lines) if "前问依赖" in line
    ]
    if dependency_indices and preprocess_index > dependency_indices[0]:
        return value, [error(
            "LITE-START-PREPROCESS-001", location,
            "预处理依赖 declaration must appear before 前问依赖 in section 2",
        )]
    if value == "无":
        return value, []
    diagnostics = preprocess_layout_diagnostics(workspace, required=True)
    contracts = (
        (PREPROCESS_START, "# START PRE", PREPROCESS_START_HEADINGS),
        (PREPROCESS_RESULT, "# RESULT PRE", PREPROCESS_RESULT_HEADINGS),
    )
    for upstream_location, title, headings in contracts:
        try:
            upstream, reading = read_contract(
                workspace / upstream_location,
                upstream_location,
                "LITE-START-PREPROCESS-CONTRACT-001",
                title,
            )
        except (UnicodeError, OSError) as exc:
            diagnostics.append(error(
                "LITE-START-PREPROCESS-CONTRACT-001", upstream_location,
                f"PRE contract is unreadable: {type(exc).__name__}",
            ))
            continue
        diagnostics.extend(reading)
        if upstream is not None:
            diagnostics.extend(heading_diagnostics(
                upstream, headings,
                "LITE-START-PREPROCESS-CONTRACT-001", upstream_location,
            ))
    return value, diagnostics


def git_warning(workspace: Path) -> list[Diagnostic]:
    if shutil.which("git") is None:
        return [warning("LITE-GIT-WARN-001", ".", "Git executable is unavailable; revision diagnostics are disabled")]
    completed = subprocess.run(["git", "-C", str(workspace), "rev-parse", "--show-toplevel"], text=True, capture_output=True)
    if completed.returncode:
        return [warning("LITE-GIT-WARN-001", ".", "workspace is not inside a Git repository")]
    return []


def _base(
    workspace: Path,
    problem: int,
) -> tuple[list[Diagnostic], list[int], ContractDiscovery]:
    diagnostics = marker_diagnostics(workspace)
    numbers, discovery = discover_questions(workspace)
    diagnostics.extend(discovery)
    contracts = discover_contracts(workspace, problem)
    if problem not in numbers:
        diagnostics.append(error("LITE-LAYOUT-001", f"problems/q{problem}", "requested managed question does not exist"))
    else:
        diagnostics.extend(question_layout_diagnostics(workspace, problem))
        diagnostics.extend(contracts.diagnostics)
    return diagnostics, numbers, contracts


def select_contract(
    discovery: ContractDiscovery,
    problem: int,
    subproblem: int | None,
) -> tuple[ContractId | None, list[Diagnostic]]:
    requested = ContractId(problem, subproblem)
    location = requested.start_path
    if discovery.mode == "none":
        return requested, []
    if discovery.mode == "single":
        if subproblem is None:
            return requested, []
        return None, [error(
            "LITE-CONTRACT-SELECT-001",
            location,
            f"Q{problem} uses single mode; omit --subproblem",
        )]
    if discovery.mode == "split":
        if subproblem is None:
            available = ",".join(item.token for item in discovery.starts)
            return None, [error(
                "LITE-CONTRACT-SELECT-001",
                f"problems/q{problem}/spec",
                f"Q{problem} uses split mode; supply --subproblem from {available}",
            )]
        if requested in discovery.starts:
            return requested, []
        available = ",".join(item.token for item in discovery.starts)
        return None, [error(
            "LITE-CONTRACT-SELECT-001",
            location,
            f"selected {requested.token} is unavailable; active units are {available}",
        )]
    return None, [error(
        "LITE-CONTRACT-SELECT-001",
        f"problems/q{problem}/spec",
        f"cannot select {requested.token} from an invalid contract layout",
    )]


def check_start(
    workspace: Path,
    problem: int,
    subproblem: int | None = None,
    *,
    include_git: bool = True,
) -> list[Diagnostic]:
    diagnostics, numbers, discovery = _base(workspace, problem)
    selected, selection = select_contract(discovery, problem, subproblem)
    diagnostics.extend(selection)
    if selected is None:
        if include_git:
            diagnostics.extend(git_warning(workspace))
        return diagnostics
    location = selected.start_path
    parsed, reading = read_contract(
        workspace / location,
        location,
        "LITE-START-001",
        selected.title("START"),
    )
    diagnostics.extend(reading)
    if parsed is not None:
        structure = heading_diagnostics(parsed, START_HEADINGS, "LITE-START-HEADING-001", location)
        diagnostics.extend(structure)
        if not structure:
            _, preprocess_found = preprocess_dependency_diagnostics(
                workspace, parsed, location
            )
            diagnostics.extend(preprocess_found)
            diagnostics.extend(dependency_diagnostics(workspace, selected, numbers, parsed, location))
            for heading in START_HEADINGS[:-1]:
                if not meaningful(parsed.section(heading, START_HEADINGS)):
                    diagnostics.append(warning("LITE-START-EMPTY-WARN-001", location, f"{heading} has no meaningful author content"))
            unresolved = parsed.section(START_HEADINGS[-1], START_HEADINGS).strip().strip("*_`").strip()
            if unresolved not in {"无", "None", "N/A"}:
                diagnostics.append(error("LITE-START-UNRESOLVED-001", location, "section 8 must be exactly 无, None, or N/A after trimming"))
    if include_git:
        diagnostics.extend(git_warning(workspace))
    return diagnostics


def check_result(
    workspace: Path,
    problem: int,
    subproblem: int | None = None,
) -> list[Diagnostic]:
    diagnostics = check_start(workspace, problem, subproblem, include_git=False)
    discovery = discover_contracts(workspace, problem)
    selected, _ = select_contract(discovery, problem, subproblem)
    if selected is None:
        diagnostics.extend(git_warning(workspace))
        return diagnostics
    location = selected.result_path
    parsed, reading = read_contract(
        workspace / location,
        location,
        "LITE-RESULT-001",
        selected.title("RESULT"),
    )
    diagnostics.extend(reading)
    if parsed is not None:
        structure = heading_diagnostics(parsed, RESULT_HEADINGS, "LITE-RESULT-HEADING-001", location)
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
                diagnostics.extend(evidence_path_diagnostics(workspace, problem, raw, location=location))
    diagnostics.extend(git_warning(workspace))
    if shutil.which("git") and not any(item.identifier == "LITE-GIT-WARN-001" for item in diagnostics):
        scoped = [f"problems/q{problem}/code", f"problems/q{problem}/data/derived"]
        dirty = subprocess.run(["git", "-C", str(workspace), "status", "--porcelain", "--", *scoped], text=True, capture_output=True)
        if dirty.returncode == 0 and dirty.stdout.strip():
            diagnostics.append(warning("LITE-GIT-DIRTY-WARN-001", f"problems/q{problem}", "current-question code or derived data has Git changes"))
    start = workspace / selected.start_path
    result = workspace / location
    if start.is_file() and result.is_file() and result.stat().st_mtime < start.stat().st_mtime:
        diagnostics.append(warning("LITE-STALE-WARN-001", location, "RESULT is older than START; advisory mtime heuristic only"))
    start_parsed, _ = read_contract(
        workspace / selected.start_path,
        selected.start_path,
        "LITE-START-001",
        selected.title("START"),
    )
    if start_parsed is not None:
        preprocess_value, _ = preprocess_dependency_diagnostics(
            workspace, start_parsed, selected.start_path
        )
        preprocess_result = workspace / PREPROCESS_RESULT
        if (
            preprocess_value == "PRE"
            and preprocess_result.is_file()
            and result.is_file()
            and result.stat().st_mtime < preprocess_result.stat().st_mtime
        ):
            diagnostics.append(warning(
                "LITE-PREPROCESS-STALE-WARN-001", location,
                "RESULT is older than RESULT_PRE; advisory downstream-impact heuristic only",
            ))
    return diagnostics


def check_preprocess_start(
    workspace: Path, *, include_git: bool = True
) -> list[Diagnostic]:
    diagnostics = marker_diagnostics(workspace)
    diagnostics.extend(preprocess_layout_diagnostics(workspace, required=True))
    parsed, reading = read_contract(
        workspace / PREPROCESS_START,
        PREPROCESS_START,
        "LITE-PREPROCESS-START-001",
        "# START PRE",
    )
    diagnostics.extend(reading)
    if parsed is not None:
        structure = heading_diagnostics(
            parsed, PREPROCESS_START_HEADINGS,
            "LITE-PREPROCESS-START-HEADING-001", PREPROCESS_START,
        )
        diagnostics.extend(structure)
        if not structure:
            for heading in PREPROCESS_START_HEADINGS[:-1]:
                if not meaningful(parsed.section(heading, PREPROCESS_START_HEADINGS)):
                    diagnostics.append(warning(
                        "LITE-PREPROCESS-START-EMPTY-WARN-001",
                        PREPROCESS_START,
                        f"{heading} has no meaningful author content",
                    ))
            unresolved = (
                parsed.section(PREPROCESS_START_HEADINGS[-1], PREPROCESS_START_HEADINGS)
                .strip().strip("*_`").strip()
            )
            if unresolved not in {"无", "None", "N/A"}:
                diagnostics.append(error(
                    "LITE-PREPROCESS-START-UNRESOLVED-001",
                    PREPROCESS_START,
                    "section 8 must be exactly 无, None, or N/A after trimming",
                ))
    if include_git:
        diagnostics.extend(git_warning(workspace))
    return diagnostics


def check_preprocess_result(workspace: Path) -> list[Diagnostic]:
    diagnostics = check_preprocess_start(workspace, include_git=False)
    parsed, reading = read_contract(
        workspace / PREPROCESS_RESULT,
        PREPROCESS_RESULT,
        "LITE-PREPROCESS-RESULT-001",
        "# RESULT PRE",
    )
    diagnostics.extend(reading)
    if parsed is not None:
        structure = heading_diagnostics(
            parsed, PREPROCESS_RESULT_HEADINGS,
            "LITE-PREPROCESS-RESULT-HEADING-001", PREPROCESS_RESULT,
        )
        diagnostics.extend(structure)
        if not structure:
            deviation = visible_content(
                parsed.section(PREPROCESS_RESULT_HEADINGS[1], PREPROCESS_RESULT_HEADINGS)
            )
            paths = re.findall(r"`([^`]*)`", deviation)
            authorized = (
                "授权偏差" in deviation
                and any(safe_relative_path(path) for path in paths)
            )
            if "无偏差" not in deviation and not authorized:
                diagnostics.append(error(
                    "LITE-PREPROCESS-RESULT-DEVIATION-001", PREPROCESS_RESULT,
                    "section 2 must state 无偏差 or an 授权偏差 with evidence path",
                ))
            if not meaningful(
                parsed.section(PREPROCESS_RESULT_HEADINGS[5], PREPROCESS_RESULT_HEADINGS)
            ):
                diagnostics.append(warning(
                    "LITE-PREPROCESS-RESULT-VALIDATION-WARN-001",
                    PREPROCESS_RESULT,
                    "section 6 has no meaningful validation detail",
                ))
            evidence = visible_content(
                parsed.section(PREPROCESS_RESULT_HEADINGS[6], PREPROCESS_RESULT_HEADINGS)
            )
            lines = [line for line in evidence.splitlines() if line.lstrip().startswith("- E")]
            if not lines:
                diagnostics.append(error(
                    "LITE-EVIDENCE-FORMAT-001", PREPROCESS_RESULT,
                    "section 7 must contain at least one evidence bullet",
                ))
            identifiers: set[str] = set()
            for line in lines:
                backticks = re.findall(r"`([^`]*)`", line)
                match = EVIDENCE_LINE.fullmatch(line)
                if len(backticks) != 1 or match is None:
                    diagnostics.append(error(
                        "LITE-EVIDENCE-FORMAT-001", PREPROCESS_RESULT,
                        f"malformed evidence bullet: {line}",
                    ))
                    continue
                identifier, raw, _ = match.groups()
                if identifier in identifiers:
                    diagnostics.append(error(
                        "LITE-EVIDENCE-FORMAT-001", PREPROCESS_RESULT,
                        f"duplicate evidence ID {identifier}",
                    ))
                    continue
                identifiers.add(identifier)
                diagnostics.extend(preprocess_evidence_path_diagnostics(
                    workspace, raw, location=PREPROCESS_RESULT
                ))
    diagnostics.extend(git_warning(workspace))
    if shutil.which("git") and not any(
        item.identifier == "LITE-GIT-WARN-001" for item in diagnostics
    ):
        dirty = subprocess.run(
            ["git", "-C", str(workspace), "status", "--porcelain", "--",
             f"{PREPROCESS_ROOT}/code", f"{PREPROCESS_ROOT}/data/derived"],
            text=True, capture_output=True,
        )
        if dirty.returncode == 0 and dirty.stdout.strip():
            diagnostics.append(warning(
                "LITE-GIT-DIRTY-WARN-001", PREPROCESS_ROOT,
                "preprocess code or derived data has Git changes",
            ))
    start = workspace / PREPROCESS_START
    result = workspace / PREPROCESS_RESULT
    if start.is_file() and result.is_file() and result.stat().st_mtime < start.stat().st_mtime:
        diagnostics.append(warning(
            "LITE-STALE-WARN-001", PREPROCESS_RESULT,
            "RESULT_PRE is older than START_PRE; advisory mtime heuristic only",
        ))
    return diagnostics


def doctor(workspace: Path) -> tuple[list[str], list[Diagnostic]]:
    diagnostics = marker_diagnostics(workspace)
    diagnostics.extend(symlink_diagnostics(workspace, list(MANAGED_ROOTS)))
    for name in (".kymcm", "input", "reports", "problems"):
        path = workspace / name
        if not path.is_dir() or path.is_symlink():
            diagnostics.append(error("LITE-LAYOUT-001", name, "required managed directory is missing or unsafe"))
    numbers, discovery = discover_questions(workspace)
    diagnostics.extend(discovery)
    for problem in numbers:
        diagnostics.extend(question_layout_diagnostics(workspace, problem))
        diagnostics.extend(discover_contracts(workspace, problem).diagnostics)
    diagnostics.extend(preprocess_layout_diagnostics(workspace))
    if not (3, 11) <= (__import__("sys").version_info[:2]) <= (3, 13):
        diagnostics.append(error("LITE-TOOL-001", "python", "Python 3.11 through 3.13 is required"))
    diagnostics.extend(git_warning(workspace))
    known = (
        set(MANAGED_ROOTS)
        | set(OPTIONAL_ROOTS)
        | set(LEGACY_IGNORED_ROOTS)
        | {"appendix", "code"}
    )
    unknown = sorted(path.name for path in workspace.iterdir() if path.name not in known) if workspace.is_dir() else []
    info = [f"INFO workspace={workspace}", f"INFO questions={','.join(map(str, numbers)) or 'none'}"]
    info.append(f"INFO unknown-root-entries={','.join(unknown) if unknown else 'none'}")
    problems = workspace / "problems"
    unknown_problems = sorted(
        path.name for path in problems.iterdir()
        if path.name != "preprocess" and not re.fullmatch(r"q[1-9][0-9]*", path.name)
    ) if problems.is_dir() and not problems.is_symlink() else []
    info.append(f"INFO unknown-problem-entries={','.join(unknown_problems) if unknown_problems else 'none'}")
    preprocess = workspace / PREPROCESS_ROOT
    if preprocess.is_dir() and not preprocess.is_symlink():
        info.append(
            "INFO preprocess=present "
            f"start={'yes' if (workspace / PREPROCESS_START).is_file() else 'no'} "
            f"result={'yes' if (workspace / PREPROCESS_RESULT).is_file() else 'no'}"
        )
    else:
        info.append("INFO preprocess=absent")
    for problem in numbers:
        contracts = discover_contracts(workspace, problem)
        starts = ",".join(item.token for item in contracts.starts) or "none"
        results = ",".join(item.token for item in contracts.results) or "none"
        info.append(f"INFO q{problem} mode={contracts.mode} starts={starts} results={results}")
    return info, diagnostics
