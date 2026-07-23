from __future__ import annotations

import ast
import csv
from dataclasses import dataclass
import hashlib
import io
import os
from pathlib import Path
import re
import shutil
import subprocess
import zipfile
import xml.etree.ElementTree as ET

from .contracts import (
    Markdown, git_warning, heading_diagnostics, meaningful, parse_markdown,
    read_contract, visible_content,
)
from .diagnostics import Diagnostic, error, warning
from .paths import (
    discover_contracts, discover_questions, marker_diagnostics,
    safe_relative_path,
)


APPENDIX_START_HEADINGS = (
    "## 1. 提交范围与比赛要求",
    "## 2. 论文引用、正式结果与认证边界",
    "## 3. appendix 目标结构",
    "## 4. appendix 文件白名单",
    "## 5. code 文件白名单",
    "## 6. 依赖闭包与机械裁剪规则",
    "## 7. 环境、外部资料与强制结果文件",
    "## 8. 验收方法与停止规则",
    "## 9. 未决问题",
)
APPENDIX_RESULT_HEADINGS = (
    "## 1. 最终交付结构",
    "## 2. 实际整理方案与 APPENDIX_START 偏差",
    "## 3. 白名单执行结果",
    "## 4. 依赖闭包与编译构建验证",
    "## 5. 正式结果与论文一致性",
    "## 6. 强制结果文件核验",
    "## 7. 排除项与敏感信息扫描",
    "## 8. 原始工程只读验证",
    "## 9. 证据索引",
    "## 10. 局限性与人工复核事项",
)
ENVIRONMENT_TARGETS = {
    "appendix/environment/README.md",
    "appendix/environment/requirements.txt",
    "appendix/environment/system_info.txt",
}
START_LOCATION = "reports/appendix/APPENDIX_START.md"
RESULT_LOCATION = "reports/appendix/APPENDIX_RESULT.md"
INTEGRITY_LOCATION = "reports/appendix/evidence/source_integrity.csv"
COPY_CURATE_LINE = re.compile(
    r"^- ([AC][0-9]{3,}) — (COPY|CURATE) — "
    r"(`[^`]+`(?:; `[^`]+`)*) → (`[^`]+`) — (\S.*)$"
)
GENERATE_LINE = re.compile(
    r"^- ([AC][0-9]{3,}) — GENERATE — (`[^`]+`) — (\S.*)$"
)
EVIDENCE_LINE = re.compile(r"^- (E[0-9]+) — `([^`]*)` — (\S.*)$")
SOURCE_ROOTS = ("problems/", "input/", "paper/")
TEXT_SUFFIXES = {
    ".c", ".cc", ".cmake", ".cpp", ".csv", ".cxx", ".h", ".hh", ".hpp",
    ".hxx", ".ini", ".md", ".py", ".rst", ".toml", ".tsv", ".txt",
    ".yaml", ".yml",
}
PYTHON_SUFFIXES = {".py", ".pyw"}
C_SUFFIXES = {".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx"}
FORBIDDEN_DIR_NAMES = {
    ".ai-bridge", ".git", ".github", ".idea", ".kymcm", ".mypy_cache",
    ".pytest_cache", ".ruff_cache", ".vscode", "__pycache__", "archive",
    "backup", "build", "checkpoint", "checkpoints", "dist", "scheduler",
    "test", "tests",
}
FORBIDDEN_SUFFIXES = {
    ".7z", ".a", ".dll", ".dylib", ".exe", ".gz", ".jar", ".log", ".o",
    ".obj", ".out", ".pyo", ".pyc", ".so", ".tar", ".whl", ".zip",
}
ROOT_CODE_DATA_SUFFIXES = {
    ".csv", ".feather", ".json", ".parquet", ".tsv", ".xls", ".xlsx",
}
FORBIDDEN_NAME = re.compile(
    r"(?i)(?:^|[_-])(?:backup|checkpoint|copy|final[0-9]+|hash[_-]?ledger|"
    r"manifest|old|resource[_-]?monitor|run[_-]?status|stage[_-]?ledger|"
    r"supervisor|temporary|tmp)(?:[_\-.]|$)"
)
DYNAMIC_PYTHON = re.compile(
    r"\b(?:__import__|exec|importlib\.import_module)\s*\(|"
    r"\bmodule(?:_name|name)\s*[+=]"
)
LOCAL_INCLUDE = re.compile(r'^\s*#\s*include\s*"([^"]+)"', re.MULTILINE)
MACRO_INCLUDE = re.compile(r"^\s*#\s*include\s*(?![<\"])(\S+)", re.MULTILINE)
CMAKE_BLOCK = re.compile(
    r"(?is)\b(?:add_executable|add_library|target_sources)\s*\((.*?)\)"
)
CMAKE_LITERAL = re.compile(
    r"(?<![$<{])(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+\."
    r"(?:c|cc|cpp|cxx|h|hh|hpp|hxx)\b"
)
CERTIFICATION = re.compile(
    r"全局最优|完整反馈均衡|\bglobal\s+optimum\b|\bfull\s+equilibrium\b",
    re.IGNORECASE,
)
LIMITATION = re.compile(
    r"有限|部分|受限|启发式|不完整|求解器间隙|finite|partial|restricted|"
    r"heuristic|incomplete|solver\s+gap",
    re.IGNORECASE,
)
SECRET_PATTERNS = (
    re.compile(r"/(?:home|Users)/[^/\s]+/[^\s]*"),
    re.compile(r"C:\\Users\\[^\\\s]+\\[^\s]*", re.IGNORECASE),
    re.compile(r"\bgh[opusr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"(?i)\bAuthorization\s*:\s*(?:Bearer|Basic)\s+\S+"),
    re.compile(r"(?i)\b(?:password|passwd|pwd)\s*[:=]\s*[^\s]+"),
    re.compile(r"~[/\\]\.config[/\\]gh[/\\]hosts\.yml", re.IGNORECASE),
)


@dataclass(frozen=True)
class AppendixEntry:
    identifier: str
    category: str
    mode: str
    sources: tuple[str, ...]
    target: str
    purpose: str


@dataclass(frozen=True)
class AppendixPlan:
    parsed: Markdown | None
    entries: tuple[AppendixEntry, ...]
    external_materials: bool | None
    mandatory_result: bool | None
    diagnostics: tuple[Diagnostic, ...]


def _contains_symlink(workspace: Path, raw: str) -> bool:
    current = workspace
    for part in Path(raw).parts:
        current /= part
        if os.path.lexists(current) and current.is_symlink():
            return True
    return False


def _ordinary_file(workspace: Path, raw: str) -> bool:
    path = workspace / raw
    return path.is_file() and not path.is_symlink() and not _contains_symlink(workspace, raw)


def _appendix_base(workspace: Path) -> tuple[list[Diagnostic], list[int]]:
    diagnostics = marker_diagnostics(workspace)
    numbers, discovery = discover_questions(workspace)
    diagnostics.extend(discovery)
    return diagnostics, numbers


def _strip_inline_markup(text: str) -> str:
    return text.strip().strip("*_`").strip()


def _parse_declaration(section: str, label: str, choices: dict[str, bool]) -> tuple[bool | None, list[Diagnostic]]:
    visible = visible_content(section)
    lines = [line.strip() for line in visible.splitlines() if line.strip().startswith(label)]
    location = START_LOCATION
    if len(lines) != 1 or lines[0] not in choices:
        return None, [error(
            "LITE-APPENDIX-DECLARATION-001", location,
            f"{label} must appear exactly once with one allowed exact value",
        )]
    return choices[lines[0]], []


def _source_mapping_valid(source: str, target: str) -> bool:
    match = re.match(r"appendix/problems/(q[1-9][0-9]*)/(code|result)/", target)
    if match:
        question, kind = match.groups()
        if kind == "code":
            return source.startswith(f"problems/{question}/code/")
        return (
            source.startswith(f"problems/{question}/outputs/")
            or source.startswith(f"problems/{question}/data/derived/")
        )
    if target.startswith("appendix/input/"):
        return source.startswith("input/")
    if target == "appendix/Result.xlsx":
        return source.startswith("input/") or bool(
            re.match(r"problems/q[1-9][0-9]*/outputs/", source)
        )
    if target.startswith("code/"):
        return bool(re.match(r"problems/q[1-9][0-9]*/code/", source))
    return False


def _target_valid(category: str, target: str, numbers: list[int]) -> bool:
    if category == "code":
        path = Path(target)
        return (
            len(path.parts) == 2
            and path.parts[0] == "code"
            and bool(path.name)
        )
    if target in ENVIRONMENT_TARGETS or target == "appendix/Result.xlsx":
        return True
    if target.startswith("appendix/input/"):
        return len(Path(target).parts) >= 3
    match = re.match(
        r"^appendix/problems/q([1-9][0-9]*)/(?:code|result)/.+$", target
    )
    return bool(match and int(match.group(1)) in numbers)


def _mode_valid(entry: AppendixEntry) -> bool:
    target = entry.target
    if target in ENVIRONMENT_TARGETS:
        return entry.mode == "GENERATE"
    if (
        target == "appendix/Result.xlsx"
        or target.startswith("appendix/input/")
        or re.match(r"appendix/problems/q[1-9][0-9]*/result/", target)
    ):
        return entry.mode == "COPY"
    if target.startswith("appendix/problems/") or target.startswith("code/"):
        return entry.mode in {"COPY", "CURATE"}
    return False


def _parse_whitelist(
    workspace: Path, section: str, category: str, numbers: list[int]
) -> tuple[list[AppendixEntry], list[Diagnostic]]:
    diagnostics: list[Diagnostic] = []
    entries: list[AppendixEntry] = []
    visible = visible_content(section)
    bullets = [line for line in visible.splitlines() if line.lstrip().startswith("- ")]
    for line in visible.splitlines():
        if re.search(r"\b[AC][0-9]{3,}\b", line) and not line.lstrip().startswith("- "):
            diagnostics.append(error(
                "LITE-APPENDIX-WHITELIST-FORMAT-001", START_LOCATION,
                f"whitelist-like entry must use exact bullet grammar: {line.strip()}",
            ))
    for line in bullets:
        copy_match = COPY_CURATE_LINE.fullmatch(line)
        generate_match = GENERATE_LINE.fullmatch(line)
        if copy_match:
            identifier, mode, source_field, target_field, purpose = copy_match.groups()
            sources = tuple(re.findall(r"`([^`]*)`", source_field))
            target = target_field[1:-1]
        elif generate_match:
            identifier, target_field, purpose = generate_match.groups()
            mode, sources, target = "GENERATE", (), target_field[1:-1]
        else:
            diagnostics.append(error(
                "LITE-APPENDIX-WHITELIST-FORMAT-001", START_LOCATION,
                f"malformed {category} whitelist bullet: {line}",
            ))
            continue
        expected = "A" if category == "appendix" else "C"
        if not identifier.startswith(expected):
            diagnostics.append(error(
                "LITE-APPENDIX-WHITELIST-FORMAT-001", START_LOCATION,
                f"{identifier} is not valid in the {category} whitelist",
            ))
        entry = AppendixEntry(identifier, category, mode, sources, target, purpose)
        entries.append(entry)
        paths = (*sources, target)
        for raw in paths:
            if not safe_relative_path(raw):
                diagnostics.append(error(
                    "LITE-APPENDIX-TARGET-PATH-001" if raw == target else "LITE-APPENDIX-SOURCE-PATH-001",
                    START_LOCATION, f"unsafe path {raw!r}",
                ))
            elif _contains_symlink(workspace, raw):
                diagnostics.append(error(
                    "LITE-APPENDIX-SYMLINK-001", raw,
                    "path contains a symlink component",
                ))
        if mode == "COPY" and len(sources) != 1:
            diagnostics.append(error(
                "LITE-APPENDIX-WHITELIST-FORMAT-001", START_LOCATION,
                f"{identifier} COPY requires exactly one source",
            ))
        if mode == "CURATE" and not sources:
            diagnostics.append(error(
                "LITE-APPENDIX-WHITELIST-FORMAT-001", START_LOCATION,
                f"{identifier} CURATE requires at least one source",
            ))
        if mode == "GENERATE" and (sources or target not in ENVIRONMENT_TARGETS):
            diagnostics.append(error(
                "LITE-APPENDIX-WHITELIST-FORMAT-001", START_LOCATION,
                f"{identifier} GENERATE is restricted to exact environment targets",
            ))
        if safe_relative_path(target) and not _target_valid(category, target, numbers):
            diagnostics.append(error(
                "LITE-APPENDIX-TARGET-PATH-001", target,
                "target is outside the allowed appendix surface",
            ))
        if not _mode_valid(entry):
            diagnostics.append(error(
                "LITE-APPENDIX-WHITELIST-FORMAT-001", target,
                f"{mode} is not permitted for this target",
            ))
        for source in sources:
            if not safe_relative_path(source):
                continue
            if not source.startswith(SOURCE_ROOTS) or source.startswith(
                ("reports/", "appendix/", "code/", ".kymcm/", ".git/")
            ):
                diagnostics.append(error(
                    "LITE-APPENDIX-SOURCE-PATH-001", source,
                    "source is outside problems/, input/, or paper/",
                ))
            elif re.match(
                r"problems/q[1-9][0-9]*/(?:spec/START_Q[1-9][0-9]*(?:_[1-9][0-9]*)?\.md|"
                r"result/RESULT_Q[1-9][0-9]*(?:_[1-9][0-9]*)?\.md)$", source
            ):
                diagnostics.append(error(
                    "LITE-APPENDIX-SOURCE-PATH-001", source,
                    "START and RESULT contracts are references and cannot be copied",
                ))
            elif not _ordinary_file(workspace, source):
                diagnostics.append(error(
                    "LITE-APPENDIX-SOURCE-MISSING-001", source,
                    "source must already exist as an ordinary non-symlink file",
                ))
            elif not _source_mapping_valid(source, target):
                diagnostics.append(error(
                    "LITE-APPENDIX-SOURCE-PATH-001", source,
                    f"source is not allowed to map to {target}",
                ))
    if not entries:
        diagnostics.append(error(
            "LITE-APPENDIX-WHITELIST-FORMAT-001", START_LOCATION,
            f"section for {category} must contain at least one valid whitelist entry",
        ))
    return entries, diagnostics


def _parse_appendix_start(
    workspace: Path, numbers: list[int], *, warn_stale: bool
) -> AppendixPlan:
    parsed, diagnostics = read_contract(
        workspace / START_LOCATION, START_LOCATION,
        "LITE-APPENDIX-START-001", "# APPENDIX START",
    )
    entries: list[AppendixEntry] = []
    external: bool | None = None
    mandatory: bool | None = None
    if parsed is not None:
        structure = heading_diagnostics(
            parsed, APPENDIX_START_HEADINGS,
            "LITE-APPENDIX-START-HEADING-001", START_LOCATION,
        )
        diagnostics.extend(structure)
        if not structure:
            for heading in APPENDIX_START_HEADINGS[:-1]:
                if not meaningful(parsed.section(heading, APPENDIX_START_HEADINGS)):
                    diagnostics.append(warning(
                        "LITE-APPENDIX-START-EMPTY-WARN-001", START_LOCATION,
                        f"{heading} has no meaningful author content",
                    ))
            unresolved = _strip_inline_markup(
                parsed.section(APPENDIX_START_HEADINGS[-1], APPENDIX_START_HEADINGS)
            )
            if unresolved not in {"无", "None", "N/A"}:
                diagnostics.append(error(
                    "LITE-APPENDIX-UNRESOLVED-001", START_LOCATION,
                    "section 9 must be exactly 无, None, or N/A after trimming",
                ))
            section7 = parsed.section(APPENDIX_START_HEADINGS[6], APPENDIX_START_HEADINGS)
            external, found = _parse_declaration(
                section7, "外部资料：",
                {"外部资料：无": False, "外部资料：`appendix/input`": True},
            )
            diagnostics.extend(found)
            mandatory, found = _parse_declaration(
                section7, "强制结果文件：",
                {"强制结果文件：无": False, "强制结果文件：`appendix/Result.xlsx`": True},
            )
            diagnostics.extend(found)
            if external:
                other = "\n".join(
                    line for line in visible_content(section7).splitlines()
                    if not line.strip().startswith(("外部资料：", "强制结果文件："))
                )
                if not meaningful(other):
                    diagnostics.append(error(
                        "LITE-APPENDIX-DECLARATION-001", START_LOCATION,
                        "external materials require visible source, purpose, and necessity statements",
                    ))
                elif not all(
                    re.search(pattern, other, re.IGNORECASE)
                    for pattern in (
                        r"来源|\bsource\b",
                        r"用途|\bpurpose\b",
                        r"必要|\bnecess(?:ary|ity)\b",
                    )
                ):
                    diagnostics.append(error(
                        "LITE-APPENDIX-DECLARATION-001", START_LOCATION,
                        "external materials must visibly identify source, purpose, and necessity",
                    ))
            appendix_entries, found = _parse_whitelist(
                workspace, parsed.section(APPENDIX_START_HEADINGS[3], APPENDIX_START_HEADINGS),
                "appendix", numbers,
            )
            entries.extend(appendix_entries)
            diagnostics.extend(found)
            code_entries, found = _parse_whitelist(
                workspace, parsed.section(APPENDIX_START_HEADINGS[4], APPENDIX_START_HEADINGS),
                "code", numbers,
            )
            entries.extend(code_entries)
            diagnostics.extend(found)
            identifiers = [entry.identifier for entry in entries]
            targets = [entry.target for entry in entries]
            if len(set(identifiers)) != len(identifiers):
                diagnostics.append(error(
                    "LITE-APPENDIX-WHITELIST-DUPLICATE-001", START_LOCATION,
                    "whitelist IDs must be globally unique",
                ))
            if len(set(targets)) != len(targets):
                diagnostics.append(error(
                    "LITE-APPENDIX-WHITELIST-DUPLICATE-001", START_LOCATION,
                    "whitelist target paths must be unique",
                ))
            environment = {entry.target for entry in entries if entry.mode == "GENERATE"}
            if environment != ENVIRONMENT_TARGETS:
                diagnostics.append(error(
                    "LITE-APPENDIX-WHITELIST-FORMAT-001", START_LOCATION,
                    "the three exact environment targets must each appear once as GENERATE",
                ))
            has_input = any(entry.target.startswith("appendix/input/") for entry in entries)
            if external is not None and has_input != external:
                diagnostics.append(error(
                    "LITE-APPENDIX-DECLARATION-001", START_LOCATION,
                    "external-material declaration and appendix/input whitelist disagree",
                ))
            has_result = any(entry.target == "appendix/Result.xlsx" for entry in entries)
            if mandatory is not None and has_result != mandatory:
                diagnostics.append(error(
                    "LITE-APPENDIX-DECLARATION-001", START_LOCATION,
                    "mandatory-result declaration and appendix/Result.xlsx whitelist disagree",
                ))
    if warn_stale:
        for root in ("appendix", "code"):
            path = workspace / root
            if path.is_dir() and not path.is_symlink() and any(path.rglob("*")):
                diagnostics.append(warning(
                    "LITE-APPENDIX-STALE-WARN-001", root,
                    "pre-existing appendix output may be stale; do not overwrite silently",
                ))
    return AppendixPlan(parsed, tuple(entries), external, mandatory, tuple(diagnostics))


def _git_source_diagnostics(workspace: Path) -> list[Diagnostic]:
    diagnostics = git_warning(workspace)
    if shutil.which("git") and not any(
        item.identifier == "LITE-GIT-WARN-001" for item in diagnostics
    ):
        completed = subprocess.run(
            ["git", "-C", str(workspace), "status", "--porcelain", "--",
             "problems", "input", "paper"],
            text=True, capture_output=True,
        )
        if completed.returncode == 0 and completed.stdout.strip():
            diagnostics.append(warning(
                "LITE-GIT-DIRTY-WARN-001", ".",
                "original problems/, input/, or paper/ sources have Git changes",
            ))
    return diagnostics


def check_appendix_start(workspace: Path) -> list[Diagnostic]:
    diagnostics, numbers = _appendix_base(workspace)
    plan = _parse_appendix_start(workspace, numbers, warn_stale=True)
    diagnostics.extend(plan.diagnostics)
    diagnostics.extend(_git_source_diagnostics(workspace))
    return diagnostics


def _declared_directories(entries: tuple[AppendixEntry, ...]) -> set[str]:
    declared: set[str] = set()
    for entry in entries:
        current = Path(entry.target).parent
        while current != Path("."):
            declared.add(current.as_posix())
            current = current.parent
    return declared


def _scan_exact_tree(
    workspace: Path, plan: AppendixPlan, numbers: list[int]
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    declared_files = {entry.target for entry in plan.entries}
    declared_dirs = _declared_directories(plan.entries)
    found_files: set[str] = set()
    found_dirs: set[str] = set()
    for root_name in ("appendix", "code"):
        root = workspace / root_name
        if not root.is_dir() or root.is_symlink():
            diagnostics.append(error(
                "LITE-APPENDIX-STRUCTURE-001", root_name,
                "declared output root must be an ordinary directory",
            ))
            continue
        for path in root.rglob("*"):
            relative = path.relative_to(workspace).as_posix()
            if path.is_symlink():
                diagnostics.append(error(
                    "LITE-APPENDIX-SYMLINK-001", relative,
                    "submitted output must not contain symlinks",
                ))
            elif path.is_dir():
                found_dirs.add(relative)
                try:
                    next(path.iterdir())
                except StopIteration:
                    diagnostics.append(error(
                        "LITE-APPENDIX-STRUCTURE-001", relative,
                        "empty directories are forbidden",
                    ))
            elif path.is_file():
                found_files.add(relative)
            else:
                diagnostics.append(error(
                    "LITE-APPENDIX-STRUCTURE-001", relative,
                    "submitted output must contain only ordinary files and directories",
                ))
    for missing in sorted(declared_files - found_files):
        diagnostics.append(error(
            "LITE-APPENDIX-OUTPUT-MISSING-001", missing,
            "declared whitelist target is missing",
        ))
    for extra in sorted(found_files - declared_files):
        diagnostics.append(error(
            "LITE-APPENDIX-OUTPUT-EXTRA-001", extra,
            "submitted file is not declared by APPENDIX_START",
        ))
    for extra in sorted(found_dirs - declared_dirs):
        diagnostics.append(error(
            "LITE-APPENDIX-STRUCTURE-001", extra,
            "directory is not implied by a declared target",
        ))
    if plan.external_materials is False and (workspace / "appendix/input").exists():
        diagnostics.append(error(
            "LITE-APPENDIX-STRUCTURE-001", "appendix/input",
            "appendix/input must be absent when external materials are none",
        ))
    if plan.mandatory_result is False and (workspace / "appendix/Result.xlsx").exists():
        diagnostics.append(error(
            "LITE-APPENDIX-STRUCTURE-001", "appendix/Result.xlsx",
            "Result.xlsx must be absent when no mandatory result is declared",
        ))
    for directory in found_dirs:
        parts = Path(directory).parts
        if parts[0] == "code" and len(parts) > 1:
            diagnostics.append(error(
                "LITE-APPENDIX-STRUCTURE-001", directory,
                "root code/ permits direct files only",
            ))
        if parts[0] == "appendix" and len(parts) >= 2:
            if parts[1] not in {"problems", "environment", "input"}:
                diagnostics.append(error(
                    "LITE-APPENDIX-STRUCTURE-001", directory,
                    "unexpected first-level appendix directory",
                ))
            if len(parts) >= 3 and parts[1] == "problems":
                match = re.fullmatch(r"q([1-9][0-9]*)", parts[2])
                if not match or int(match.group(1)) not in numbers:
                    diagnostics.append(error(
                        "LITE-APPENDIX-STRUCTURE-001", directory,
                        "appendix question directory is not a discovered qN",
                    ))
                elif len(parts) >= 4 and parts[3] not in {"code", "result"}:
                    diagnostics.append(error(
                        "LITE-APPENDIX-STRUCTURE-001", directory,
                        "appendix qN permits only code/ and result/",
                    ))
    return diagnostics


def _copy_diagnostics(workspace: Path, entries: tuple[AppendixEntry, ...]) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for entry in entries:
        if entry.mode != "COPY" or len(entry.sources) != 1:
            continue
        source, target = workspace / entry.sources[0], workspace / entry.target
        if (
            source.is_file() and not source.is_symlink()
            and target.is_file() and not target.is_symlink()
            and hashlib.sha256(source.read_bytes()).digest()
            != hashlib.sha256(target.read_bytes()).digest()
        ):
            diagnostics.append(error(
                "LITE-APPENDIX-COPY-MISMATCH-001", entry.target,
                f"COPY target does not preserve bytes from {entry.sources[0]}",
            ))
    return diagnostics


def _integrity_diagnostics(
    workspace: Path, entries: tuple[AppendixEntry, ...]
) -> list[Diagnostic]:
    path = workspace / INTEGRITY_LOCATION
    if not _ordinary_file(workspace, INTEGRITY_LOCATION):
        return [error(
            "LITE-APPENDIX-INTEGRITY-001", INTEGRITY_LOCATION,
            "required execution-provided source integrity record is missing or unsafe",
        )]
    diagnostics: list[Diagnostic] = []
    rows = list(csv.reader(io.StringIO(path.read_text(encoding="utf-8"))))
    if not rows or rows[0] != ["path", "before_sha256", "after_sha256", "status"]:
        return [error(
            "LITE-APPENDIX-INTEGRITY-001", INTEGRITY_LOCATION,
            "header must be exactly path,before_sha256,after_sha256,status",
        )]
    if len(rows) < 2:
        diagnostics.append(error(
            "LITE-APPENDIX-INTEGRITY-001", INTEGRITY_LOCATION,
            "integrity record requires at least one source row",
        ))
    digest = re.compile(r"[0-9a-f]{64}")
    recorded: set[str] = set()
    for index, row in enumerate(rows[1:], 2):
        if (
            len(row) != 4
            or not safe_relative_path(row[0])
            or not row[0].startswith(SOURCE_ROOTS)
            or not digest.fullmatch(row[1] if len(row) > 1 else "")
            or not digest.fullmatch(row[2] if len(row) > 2 else "")
            or row[1] != row[2]
            or row[3] != "unchanged"
        ):
            diagnostics.append(error(
                "LITE-APPENDIX-INTEGRITY-001", f"{INTEGRITY_LOCATION}:{index}",
                "row must contain a safe source, equal lowercase SHA-256 values, and unchanged",
            ))
        elif len(row) == 4:
            recorded.add(row[0])
    expected = {source for entry in entries for source in entry.sources}
    missing = sorted(expected - recorded)
    if missing:
        diagnostics.append(error(
            "LITE-APPENDIX-INTEGRITY-001", INTEGRITY_LOCATION,
            f"integrity record omits declared sources: {', '.join(missing)}",
        ))
    return diagnostics


def _forbidden_diagnostics(workspace: Path, entries: tuple[AppendixEntry, ...]) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    result_hashes: dict[bytes, str] = {}
    for entry in entries:
        path = workspace / entry.target
        if not path.is_file() or path.is_symlink():
            continue
        relative = Path(entry.target)
        lower_parts = [part.lower() for part in relative.parts]
        name = relative.name
        if (
            any(part in FORBIDDEN_DIR_NAMES or part.startswith(".") for part in lower_parts[1:-1])
            or name.startswith(".")
            or relative.suffix.lower() in FORBIDDEN_SUFFIXES
            or path.stat().st_mode & 0o111
            or re.fullmatch(r"RESULT.*\.md", name, re.IGNORECASE)
            or FORBIDDEN_NAME.search(name)
        ):
            diagnostics.append(error(
                "LITE-APPENDIX-FORBIDDEN-001", entry.target,
                "submitted name or file type is forbidden",
            ))
        if entry.target.startswith("code/"):
            lowered = name.lower()
            if (
                lowered.startswith("readme")
                or relative.suffix.lower() in ROOT_CODE_DATA_SUFFIXES
                or any(word in lowered for word in (
                    "environment", "plot", "result", "schedule", "logging",
                    "export", "backend",
                ))
            ):
                diagnostics.append(error(
                    "LITE-APPENDIX-FORBIDDEN-001", entry.target,
                    "root code/ contains a non-core-algorithm file",
                ))
            if relative.suffix.lower() in TEXT_SUFFIXES:
                line_count = len(path.read_text(encoding="utf-8").splitlines())
                if not 150 <= line_count <= 400:
                    diagnostics.append(warning(
                        "LITE-APPENDIX-DEPENDENCY-WARN-001", entry.target,
                        f"core-code file has {line_count} lines; usual guideline is 150–400",
                    ))
        if "/result/" in entry.target:
            digest = hashlib.sha256(path.read_bytes()).digest()
            if digest in result_hashes:
                diagnostics.append(error(
                    "LITE-APPENDIX-DUPLICATE-001", entry.target,
                    f"byte-identical formal result duplicates {result_hashes[digest]}",
                ))
            else:
                result_hashes[digest] = entry.target
    return diagnostics


def _python_diagnostics(workspace: Path, entries: tuple[AppendixEntry, ...]) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    targets = {entry.target for entry in entries}
    for entry in entries:
        if Path(entry.target).suffix.lower() not in PYTHON_SUFFIXES:
            continue
        path = workspace / entry.target
        if not path.is_file() or path.is_symlink():
            continue
        text = path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(text, filename=entry.target)
        except SyntaxError as exc:
            diagnostics.append(error(
                "LITE-APPENDIX-PYTHON-001", entry.target,
                f"Python syntax error at line {exc.lineno}",
            ))
            continue
        if DYNAMIC_PYTHON.search(text):
            diagnostics.append(warning(
                "LITE-APPENDIX-DEPENDENCY-WARN-001", entry.target,
                "dynamic import or execution prevents complete static closure proof",
            ))
        parent = Path(entry.target).parent
        local_stems = {
            Path(target).stem for target in targets
            if Path(target).parent == parent and Path(target).suffix == ".py"
        }
        for node in ast.walk(tree):
            candidates: list[Path] = []
            imported_names: list[str] = []
            if isinstance(node, ast.ImportFrom) and node.level:
                base = parent
                for _ in range(node.level - 1):
                    base = base.parent
                if node.module:
                    candidates.append(base / Path(*node.module.split(".")))
                else:
                    candidates.extend(base / alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                first = node.module.split(".", 1)[0]
                imported_names.append(first)
                if first in local_stems:
                    candidates.append(parent / Path(*node.module.split(".")))
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    first = alias.name.split(".", 1)[0]
                    imported_names.append(first)
                    if first in local_stems:
                        candidates.append(parent / Path(*alias.name.split(".")))
            for candidate in candidates:
                options = {
                    candidate.with_suffix(".py").as_posix(),
                    (candidate / "__init__.py").as_posix(),
                }
                if not options & targets:
                    diagnostics.append(error(
                        "LITE-APPENDIX-PYTHON-001", entry.target,
                        f"missing submitted local module for {candidate.name}",
                    ))
            for name in imported_names:
                source_local = any(
                    (workspace / source).parent.joinpath(f"{name}.py").is_file()
                    for source in entry.sources
                )
                if source_local and (parent / f"{name}.py").as_posix() not in targets:
                    diagnostics.append(error(
                        "LITE-APPENDIX-PYTHON-001", entry.target,
                        f"source-local module {name}.py is absent from submitted dependency closure",
                    ))
    return diagnostics


def _native_dependency_diagnostics(
    workspace: Path, entries: tuple[AppendixEntry, ...]
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    targets = {entry.target for entry in entries}
    for entry in entries:
        path = workspace / entry.target
        if not path.is_file() or path.is_symlink():
            continue
        suffix = path.suffix.lower()
        if suffix in C_SUFFIXES:
            text = path.read_text(encoding="utf-8")
            for include in MACRO_INCLUDE.findall(text):
                diagnostics.append(warning(
                    "LITE-APPENDIX-DEPENDENCY-WARN-001", entry.target,
                    f"macro/generated include cannot be resolved statically: {include}",
                ))
            for include in LOCAL_INCLUDE.findall(text):
                if "$" in include or re.search(r"[/\\]?\w*\([^)]*\)", include):
                    diagnostics.append(warning(
                        "LITE-APPENDIX-DEPENDENCY-WARN-001", entry.target,
                        f"macro/generated include cannot be resolved statically: {include}",
                    ))
                    continue
                candidate = (Path(entry.target).parent / include).as_posix()
                if candidate not in targets:
                    diagnostics.append(error(
                        "LITE-APPENDIX-OUTPUT-MISSING-001", entry.target,
                        f"missing submitted local include {include}",
                    ))
        if path.name == "CMakeLists.txt" or suffix == ".cmake":
            text = path.read_text(encoding="utf-8")
            for block in CMAKE_BLOCK.findall(text):
                if "${" in block or "$<" in block:
                    diagnostics.append(warning(
                        "LITE-APPENDIX-DEPENDENCY-WARN-001", entry.target,
                        "CMake variables or generator expressions limit static closure proof",
                    ))
                for literal in CMAKE_LITERAL.findall(block):
                    candidate = (Path(entry.target).parent / literal).as_posix()
                    if candidate not in targets:
                        diagnostics.append(error(
                            "LITE-APPENDIX-OUTPUT-MISSING-001", entry.target,
                            f"CMake references missing literal source {literal}",
                        ))
    return diagnostics


def _xlsx_diagnostics(workspace: Path, plan: AppendixPlan) -> list[Diagnostic]:
    if not plan.mandatory_result:
        return []
    path = workspace / "appendix/Result.xlsx"
    if not path.is_file() or path.is_symlink():
        return []
    try:
        with zipfile.ZipFile(path) as archive:
            names = set(archive.namelist())
            required = {"[Content_Types].xml", "xl/workbook.xml"}
            if not required <= names:
                raise ValueError("required XLSX members are missing")
            ET.fromstring(archive.read("[Content_Types].xml"))
            workbook = ET.fromstring(archive.read("xl/workbook.xml"))
            sheets = [
                element for element in workbook.iter()
                if element.tag.rsplit("}", 1)[-1] == "sheet"
            ]
            if not sheets:
                raise ValueError("workbook contains no sheet")
    except (OSError, ValueError, zipfile.BadZipFile, ET.ParseError) as exc:
        return [error(
            "LITE-APPENDIX-XLSX-001", "appendix/Result.xlsx",
            f"workbook is unreadable or structurally invalid: {type(exc).__name__}",
        )]
    return []


def _sensitive_diagnostics(
    workspace: Path, entries: tuple[AppendixEntry, ...]
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for entry in entries:
        path = workspace / entry.target
        if not path.is_file() or path.is_symlink():
            continue
        raw = path.read_bytes()
        text = raw.decode("utf-8", errors="ignore")
        for pattern in SECRET_PATTERNS:
            match = pattern.search(text)
            if match:
                line = text.count("\n", 0, match.start()) + 1
                diagnostics.append(error(
                    "LITE-APPENDIX-SENSITIVE-001", f"{entry.target}:{line}",
                    "high-confidence sensitive content detected (value redacted)",
                ))
                break
        if entry.target == "appendix/environment/system_info.txt":
            if re.search(
                r"(?im)^\s*(?:host(?:name)?|user(?:name)?|home|ip(?: address)?)\s*[:=]",
                text,
            ):
                diagnostics.append(error(
                    "LITE-APPENDIX-SENSITIVE-001", entry.target,
                    "system_info.txt contains forbidden machine identity data",
                ))
    return diagnostics


def _certification_diagnostics(
    workspace: Path, plan: AppendixPlan, result: Markdown
) -> list[Diagnostic]:
    reference_texts = [result.text]
    for number in discover_questions(workspace)[0]:
        contracts = discover_contracts(workspace, number)
        relatives = (
            [item.start_path for item in contracts.starts]
            + [item.result_path for item in contracts.results]
        )
        for relative in relatives:
            path = workspace / relative
            if path.is_file() and not path.is_symlink():
                reference_texts.append(path.read_text(encoding="utf-8"))
    limitation_present = any(LIMITATION.search(text) for text in reference_texts)
    if not limitation_present:
        return []
    diagnostics: list[Diagnostic] = []
    for entry in plan.entries:
        path = workspace / entry.target
        if (
            path.is_file() and not path.is_symlink()
            and path.suffix.lower() in TEXT_SUFFIXES
            and CERTIFICATION.search(path.read_text(encoding="utf-8"))
        ):
            diagnostics.append(warning(
                "LITE-APPENDIX-CERTIFICATION-WARN-001", entry.target,
                "unqualified global-certification language conflicts with visible limitations",
            ))
    if CERTIFICATION.search(result.text):
        diagnostics.append(warning(
            "LITE-APPENDIX-CERTIFICATION-WARN-001", RESULT_LOCATION,
            "unqualified global-certification language conflicts with visible limitations",
        ))
    return diagnostics


def _result_contract_diagnostics(
    workspace: Path, plan: AppendixPlan
) -> tuple[Markdown | None, list[Diagnostic]]:
    parsed, diagnostics = read_contract(
        workspace / RESULT_LOCATION, RESULT_LOCATION,
        "LITE-APPENDIX-RESULT-001", "# APPENDIX RESULT",
    )
    if parsed is None:
        return None, diagnostics
    structure = heading_diagnostics(
        parsed, APPENDIX_RESULT_HEADINGS,
        "LITE-APPENDIX-RESULT-HEADING-001", RESULT_LOCATION,
    )
    diagnostics.extend(structure)
    if structure:
        return parsed, diagnostics
    deviation = visible_content(
        parsed.section(APPENDIX_RESULT_HEADINGS[1], APPENDIX_RESULT_HEADINGS)
    )
    paths = re.findall(r"`([^`]*)`", deviation)
    authorized = (
        "授权偏差" in deviation
        and any(
            safe_relative_path(raw)
            and (
                raw.startswith("reports/appendix/evidence/")
                or raw.startswith("appendix/")
                or raw.startswith("code/")
            )
            for raw in paths
        )
    )
    if "无偏差" not in deviation and not authorized:
        diagnostics.append(error(
            "LITE-APPENDIX-DEVIATION-001", RESULT_LOCATION,
            "section 2 must state 无偏差 or an 授权偏差 with a safe evidence path",
        ))
    execution = visible_content(
        parsed.section(APPENDIX_RESULT_HEADINGS[2], APPENDIX_RESULT_HEADINGS)
    )
    expected = {entry.identifier for entry in plan.entries}
    mentioned = set(re.findall(r"\b[AC][0-9]{3,}\b", execution))
    for identifier in sorted(expected - mentioned):
        diagnostics.append(error(
            "LITE-APPENDIX-RESULT-001", RESULT_LOCATION,
            f"section 3 does not account for whitelist ID {identifier}",
        ))
    for identifier in sorted(mentioned - expected):
        diagnostics.append(error(
            "LITE-APPENDIX-RESULT-001", RESULT_LOCATION,
            f"unknown whitelist-like ID {identifier} cannot authorize output",
        ))
    evidence = visible_content(
        parsed.section(APPENDIX_RESULT_HEADINGS[8], APPENDIX_RESULT_HEADINGS)
    )
    bullets = [line for line in evidence.splitlines() if line.lstrip().startswith("- E")]
    if not bullets:
        diagnostics.append(error(
            "LITE-APPENDIX-EVIDENCE-001", RESULT_LOCATION,
            "section 9 must contain at least one evidence bullet",
        ))
    identifiers: set[str] = set()
    evidence_paths: set[str] = set()
    for line in bullets:
        match = EVIDENCE_LINE.fullmatch(line)
        backticks = re.findall(r"`([^`]*)`", line)
        if match is None or len(backticks) != 1:
            diagnostics.append(error(
                "LITE-APPENDIX-EVIDENCE-001", RESULT_LOCATION,
                f"malformed evidence bullet: {line}",
            ))
            continue
        identifier, raw, _ = match.groups()
        if identifier in identifiers:
            diagnostics.append(error(
                "LITE-APPENDIX-EVIDENCE-001", RESULT_LOCATION,
                f"duplicate evidence ID {identifier}",
            ))
        identifiers.add(identifier)
        if (
            not safe_relative_path(raw)
            or not raw.startswith(("reports/appendix/evidence/", "appendix/", "code/"))
        ):
            diagnostics.append(error(
                "LITE-APPENDIX-EVIDENCE-001", raw,
                "evidence path is unsafe or outside allowed roots",
            ))
        elif not _ordinary_file(workspace, raw):
            diagnostics.append(error(
                "LITE-APPENDIX-EVIDENCE-001", raw,
                "evidence must be an existing ordinary non-symlink file",
            ))
        evidence_paths.add(raw)
    if INTEGRITY_LOCATION not in evidence_paths:
        diagnostics.append(error(
            "LITE-APPENDIX-EVIDENCE-001", RESULT_LOCATION,
            f"section 9 must index {INTEGRITY_LOCATION}",
        ))
    return parsed, diagnostics


def check_appendix_result(workspace: Path) -> list[Diagnostic]:
    diagnostics, numbers = _appendix_base(workspace)
    plan = _parse_appendix_start(workspace, numbers, warn_stale=False)
    diagnostics.extend(plan.diagnostics)
    parsed, found = _result_contract_diagnostics(workspace, plan)
    diagnostics.extend(found)
    diagnostics.extend(_scan_exact_tree(workspace, plan, numbers))
    diagnostics.extend(_copy_diagnostics(workspace, plan.entries))
    diagnostics.extend(_integrity_diagnostics(workspace, plan.entries))
    diagnostics.extend(_forbidden_diagnostics(workspace, plan.entries))
    diagnostics.extend(_python_diagnostics(workspace, plan.entries))
    diagnostics.extend(_native_dependency_diagnostics(workspace, plan.entries))
    diagnostics.extend(_xlsx_diagnostics(workspace, plan))
    diagnostics.extend(_sensitive_diagnostics(workspace, plan.entries))
    if parsed is not None:
        diagnostics.extend(_certification_diagnostics(workspace, plan, parsed))
    diagnostics.extend(_git_source_diagnostics(workspace))
    return diagnostics
