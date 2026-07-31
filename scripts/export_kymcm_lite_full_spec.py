#!/usr/bin/env python3
"""Export the complete KyMCM Lite specification as one deterministic document."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import sys
import tempfile
from typing import Iterable, Sequence


FORMAT_VERSION = "full-spec-export-v1"
DEFAULT_OUTPUT = Path("docs/lite-v3/KyMCM_Lite_FULL_SPEC.md")
MARKER_DISPLAY = '{"workflow":"kymcm_lite","version":3}'
MARKER_BYTES_DISPLAY = MARKER_DISPLAY + r"\n"

CORE_SKILL_FILES: tuple[str, ...] = (
    "skills/kymcm-lite/VERSION",
    "skills/kymcm-lite/SKILL.md",
)
PROTOCOL_FILE = "skills/kymcm-lite/docs/protocol.md"
MACHINE_CONTRACT_NAME = "machine_contract.md"
AGENT_FILE = "skills/kymcm-lite/agents/openai.yaml"
SKILL_README = "skills/kymcm-lite/README.md"

REPOSITORY_NORMATIVE_DOCS: tuple[tuple[str, str], ...] = (
    ("docs/lite-v3/diagnostics.md", "product-documentation"),
    ("docs/compatibility.md", "product-documentation"),
    ("docs/installation.md", "product-documentation"),
    ("docs/known-limitations.md", "product-documentation"),
    ("docs/lite-v3-rfc.md", "product-documentation"),
    ("docs/lite-v3-release-notes.md", "product-documentation"),
    ("docs/release-checklist.md", "repository-maintenance"),
    ("docs/system-dependencies.md", "repository-maintenance"),
    ("README.md", "product-documentation"),
)

EXCLUDED_LITE_V3_DOCS: tuple[str, ...] = (
    "docs/lite-v3/KyMCM_Lite_FULL_SPEC.md",
    "docs/lite-v3/benchmark-method.md",
    "docs/lite-v3/benchmark-report.md",
    "docs/lite-v3/reviewer-record.md",
)

EXPLICIT_EXCLUSIONS: tuple[tuple[str, str], ...] = (
    ("skills/kymcm-full/**", "different KyMCM product"),
    (
        "skills/kymcm-lite/scripts/**/*.py",
        "implementation code; its observable behavior is described by machine_contract.md and diagnostics.md",
    ),
    ("tests/**", "verification material rather than user specification"),
    ("CHANGELOG.md", "historical release record"),
    ("skills/kymcm-lite/CHANGELOG.md", "historical Skill release record"),
    ("docs/lite-v3-phase*-plan.md", "historical implementation plans"),
    ("docs/lite-v3/benchmark-*", "benchmark material"),
    ("docs/lite-v3/reviewer-record.md", "review and acceptance material"),
    ("docs/full-workflow.md", "Full product documentation"),
    ("docs/lite-v3-phase1-plan.md", "historical implementation plan"),
    ("docs/lite-v3-phase2-plan.md", "historical implementation plan"),
    ("docs/lite-v3-phase3-plan.md", "historical implementation plan"),
    ("LICENSE, NOTICE.md, SECURITY.md", "legal or repository-governance material"),
    (".ai-bridge/**", "local collaboration material"),
    ("caches, fonts, binaries, and generated intermediates", "not normative source text"),
)

SECTION_TITLES: tuple[str, ...] = (
    "## 2. Core skill",
    "## 3. Protocol",
    "## 4. Machine-enforced contract and diagnostics",
    "## 5. References",
    "## 6. Templates",
    "## 7. Agent metadata",
    "## 8. Current product and maintenance documentation",
)


class ExporterError(RuntimeError):
    """An invalid repository input or unsafe output operation."""


@dataclass(frozen=True)
class Source:
    path: str
    role: str
    authority: str
    section: str
    content: bytes
    mirrors: tuple[str, ...] = ()

    @property
    def size(self) -> int:
        return len(self.content)

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.content).hexdigest()


def resolve_repo_root(raw: str | Path | None = None) -> Path:
    """Resolve and validate the repository root without consulting the environment."""

    candidate = (
        Path(__file__).resolve().parents[1]
        if raw is None
        else Path(raw).expanduser().absolute()
    )
    if candidate.is_symlink() or not candidate.is_dir():
        raise ExporterError(f"repository root is not an ordinary directory: {candidate}")
    return candidate.resolve()


def _safe_relative(raw: str) -> bool:
    path = Path(raw)
    return bool(raw) and not path.is_absolute() and ".." not in path.parts


def _path_for(root: Path, relative: str) -> Path:
    if not _safe_relative(relative):
        raise ExporterError(f"unsafe repository-relative path: {relative!r}")
    return root.joinpath(*Path(relative).parts)


def _reject_symlink_components(root: Path, path: Path) -> None:
    try:
        relative = path.relative_to(root)
    except ValueError as exc:
        raise ExporterError(f"path escapes repository root: {path}") from exc
    current = root
    for part in relative.parts:
        current /= part
        if current.is_symlink():
            raise ExporterError(f"symlink component is not allowed: {relative}")


def _read_source(root: Path, relative: str) -> bytes:
    path = _path_for(root, relative)
    _reject_symlink_components(root, path)
    if not path.exists() or not path.is_file():
        raise ExporterError(f"required source is missing or not a file: {relative}")
    try:
        content = path.read_bytes()
        content.decode("utf-8")
    except UnicodeError as exc:
        raise ExporterError(f"source is not valid UTF-8: {relative}") from exc
    except OSError as exc:
        raise ExporterError(f"cannot read source {relative}: {exc}") from exc
    return content


def _maybe_mirror(root: Path, canonical: str, content: bytes) -> tuple[str, ...]:
    """Validate a real repository mirror when the current tree provides one."""

    if not (
        canonical.startswith("skills/kymcm-lite/references/")
        or canonical.startswith("skills/kymcm-lite/templates/")
    ):
        return ()
    expected = f"docs/lite-v3/{Path(canonical).name}"
    path = _path_for(root, expected)
    if not os.path.lexists(path):
        return ()
    mirror = _read_source(root, expected)
    if mirror != content:
        raise ExporterError(
            f"canonical and mirror differ: {canonical} != {expected}"
        )
    return (expected,)


def _spec(
    root: Path,
    relative: str,
    role: str,
    authority: str,
    section: str,
    *,
    mirror: bool = True,
) -> Source:
    content = _read_source(root, relative)
    mirrors = _maybe_mirror(root, relative, content) if mirror else ()
    return Source(relative, role, authority, section, content, mirrors)


def _ordinary_markdown_paths(root: Path, directory: str) -> tuple[str, ...]:
    base = _path_for(root, directory)
    if not base.is_dir() or base.is_symlink():
        raise ExporterError(f"required directory is missing or unsafe: {directory}")
    paths: list[str] = []
    for path in sorted(base.iterdir(), key=lambda item: item.name):
        if path.suffix != ".md":
            continue
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            raise ExporterError(f"Markdown source must not be a symlink: {relative}")
        if not path.is_file():
            raise ExporterError(f"Markdown source is not an ordinary file: {relative}")
        paths.append(relative)
    return tuple(paths)


def _validate_lite_doc_classification(
    root: Path,
    reference_mirrors: Iterable[str],
    template_mirrors: Iterable[str],
) -> None:
    actual = set(_ordinary_markdown_paths(root, "docs/lite-v3"))
    included = {
        path for path, _role in REPOSITORY_NORMATIVE_DOCS if path.startswith("docs/lite-v3/")
    }
    included.update(reference_mirrors)
    included.update(template_mirrors)
    excluded = set(EXCLUDED_LITE_V3_DOCS)
    if included & excluded:
        overlap = ", ".join(sorted(included & excluded))
        raise ExporterError(f"docs/lite-v3 classification overlaps: {overlap}")
    classified = included | excluded
    # Excluded files may be absent in a clean checkout; included files may not.
    missing = sorted(included - actual)
    unexpected = sorted(actual - classified)
    if missing:
        raise ExporterError(
            "docs/lite-v3 classification names missing files: " + ", ".join(missing)
        )
    if unexpected:
        raise ExporterError(
            "ordinary docs/lite-v3 Markdown is unclassified: " + ", ".join(unexpected)
        )


def _validate_no_duplicate(sources: Sequence[Source]) -> None:
    paths = [source.path for source in sources]
    if len(paths) != len(set(paths)):
        duplicates = sorted({path for path in paths if paths.count(path) > 1})
        raise ExporterError("duplicate canonical source: " + ", ".join(duplicates))


def collect_sources(root: Path | str) -> tuple[Source, ...]:
    """Collect and validate every canonical source in deterministic order."""

    repository = resolve_repo_root(root)
    sources: list[Source] = []
    sources.extend(
        _spec(repository, path, "identity" if path.endswith("VERSION") else "core-skill",
              "runtime identity" if path.endswith("VERSION") else "Skill behavior",
              SECTION_TITLES[0], mirror=False)
        for path in CORE_SKILL_FILES
    )
    sources.append(_spec(repository, PROTOCOL_FILE, "protocol", "Lite protocol", SECTION_TITLES[1], mirror=False))

    references = _ordinary_markdown_paths(repository, "skills/kymcm-lite/references")
    reference_mirrors: list[str] = []
    for relative in references:
        if Path(relative).name == MACHINE_CONTRACT_NAME:
            source = _spec(
                repository, relative, "machine-contract", "runtime behavior", SECTION_TITLES[2]
            )
        else:
            source = _spec(
                repository, relative, "reference", "specialized reference", SECTION_TITLES[3]
            )
        sources.append(source)
        reference_mirrors.extend(source.mirrors)

    diagnostics = _spec(
        repository,
        "docs/lite-v3/diagnostics.md",
        "diagnostic-catalog",
        "diagnostic catalog",
        SECTION_TITLES[2],
        mirror=False,
    )
    # Keep the machine contract before diagnostics in the machine section.
    machine = [source for source in sources if source.role == "machine-contract"]
    sources = [source for source in sources if source.role != "machine-contract"]
    insertion = next(
        (index for index, source in enumerate(sources) if source.section == SECTION_TITLES[3]),
        len(sources),
    )
    sources[insertion:insertion] = machine + [diagnostics]

    templates = _ordinary_markdown_paths(repository, "skills/kymcm-lite/templates")
    template_sources: list[Source] = []
    template_mirrors: list[str] = []
    for relative in templates:
        source = _spec(
            repository, relative, "template", "contract template", SECTION_TITLES[4]
        )
        template_sources.append(source)
        template_mirrors.extend(source.mirrors)
    sources.extend(template_sources)

    sources.append(_spec(repository, AGENT_FILE, "agent-metadata", "agent metadata", SECTION_TITLES[5], mirror=False))
    sources.append(_spec(repository, SKILL_README, "product-documentation", "product documentation", SECTION_TITLES[6], mirror=False))

    for relative, role in REPOSITORY_NORMATIVE_DOCS:
        if relative == "docs/lite-v3/diagnostics.md":
            continue
        authority = "repository maintenance" if role == "repository-maintenance" else "product documentation"
        sources.append(_spec(repository, relative, role, authority, SECTION_TITLES[6], mirror=False))

    _validate_lite_doc_classification(repository, reference_mirrors, template_mirrors)
    _validate_no_duplicate(sources)
    return tuple(sources)


def _source_by_section(sources: Sequence[Source], title: str) -> tuple[Source, ...]:
    return tuple(source for source in sources if source.section == title)


def _render_source(source: Source) -> str:
    marker = f"<!-- BEGIN KYMCM-LITE SOURCE: {source.path} -->"
    end = f"<!-- END KYMCM-LITE SOURCE: {source.path} -->"
    text = source.content.decode("utf-8")
    if marker in text or end in text:
        raise ExporterError(f"source contains a reserved boundary marker: {source.path}")
    if not text.endswith("\n"):
        text += "\n"
    # Keep the source bytes represented by ``text`` unchanged.  Only the
    # separator needed to put the END marker on its own line is added when a
    # source has no final newline.
    body = text if text.endswith("\n") else text + "\n"
    return "".join(
        (
            f"### Source: `{source.path}`\n",
            f"Role: `{source.role}`\n",
            f"Authority: {source.authority}\n\n",
            marker,
            "\n",
            body,
            end,
            "\n\n",
        )
    )


def _render_manifest(sources: Sequence[Source]) -> str:
    lines = [
        "## 1. Source manifest",
        "",
        "| No. | canonical path | role | bytes | SHA-256 | mirror path(s) | mirror status |",
        "|---:|---|---|---:|---|---|---|",
    ]
    for index, source in enumerate(sources, 1):
        mirrors = ", ".join(f"`{path}`" for path in source.mirrors) or "—"
        status = "byte-identical" if source.mirrors else "none"
        lines.append(
            f"| {index} | `{source.path}` | `{source.role}` | {source.size} | "
            f"`{source.sha256}` | {mirrors} | {status} |"
        )
    return "\n".join(lines + [""])


def _render_preamble(sources: Sequence[Source]) -> str:
    version = next(source for source in sources if source.path.endswith("/VERSION"))
    mirror_count = sum(len(source.mirrors) for source in sources)
    total_bytes = sum(source.size for source in sources)
    lines = [
        "# KyMCM Lite Complete Specification for ChatGPT Project Sources",
        "",
        "> This file is generated from the current KyMCM Lite repository sources. It is intended for direct upload to ChatGPT Project Sources.",
        "> ChatGPT is responsible for mathematical modeling design and contract writing; Codex is responsible for local engineering execution and evidence checks.",
        "> Do not edit this file by hand. After a normative source change, run the exporter and then its `--check` mode.",
        "> Source paths and SHA-256 values are the traceability authority; generated section numbering is only navigation.",
        "",
        "## 0. 使用说明、版本与权威优先级",
        "",
        f"- Product: `KyMCM Lite`; `VERSION`: `{version.content.decode('utf-8').strip()}`.",
        f"- Lite v3 marker bytes: `{MARKER_BYTES_DISPLAY}` (the final `\\n` is part of the required bytes).",
        f"- Export format: `{FORMAT_VERSION}`.",
        f"- Canonical source files: `{len(sources)}`; canonical total bytes: `{total_bytes}`.",
        f"- Mirror files validated: `{mirror_count}`.",
        "- Generation: `python scripts/export_kymcm_lite_full_spec.py --output docs/lite-v3/KyMCM_Lite_FULL_SPEC.md`.",
        "- The export is repository documentation, not a Lite workspace file, evidence item, appendix target, command, state, JSON, or runtime dependency.",
        "",
        "Authority priority when descriptions appear to differ:",
        "1. Python runtime and its frozen tests (observable acceptance, diagnostics, and exit codes).",
        "2. `skills/kymcm-lite/SKILL.md` (overall agent behavior and boundaries).",
        "3. `skills/kymcm-lite/docs/protocol.md` (complete Lite protocol).",
        "4. `skills/kymcm-lite/references/*.md` (specialized semantics).",
        "5. `skills/kymcm-lite/templates/*.md` (contract structures and authoring requirements).",
        "6. Agent metadata, README, and repository current documentation (usage and maintenance guidance only).",
        "7. Changelogs, historical plans, benchmarks, and reviewer records (history/verification only; excluded from canonical正文).",
        "",
        "The complete source text is intentionally long. It is not a summary: each canonical source appears once below with stable BEGIN/END boundaries.",
        "",
    ]
    return "\n".join(lines)


def _render_sources(sources: Sequence[Source]) -> str:
    chunks: list[str] = []
    for title in SECTION_TITLES:
        chunks.append(title)
        chunks.append("")
        for source in _source_by_section(sources, title):
            chunks.append(_render_source(source))
    return "\n".join(chunks)


def _render_mirrors(sources: Sequence[Source]) -> str:
    lines = ["## 9. Mirror map", "", "Byte-identical repository mirrors are listed without repeating their正文:", ""]
    mirrored = [source for source in sources if source.mirrors]
    if not mirrored:
        lines.append("No mirrors are present.")
    for source in mirrored:
        for mirror in source.mirrors:
            lines.extend(
                (
                    f"- canonical: `{source.path}`",
                    f"  mirror: `{mirror}`",
                    f"  bytes: `{source.size}`",
                    f"  SHA-256: `{source.sha256}`",
                    "  status: `byte-identical`",
                    "",
                )
            )
    return "\n".join(lines)


def _render_exclusions() -> str:
    lines = [
        "## 10. Explicit exclusions",
        "",
        "Excluded material is named for boundary clarity but its正文 is not pasted into this specification:",
    ]
    lines.extend(f"- `{path}` — {reason}." for path, reason in EXPLICIT_EXCLUSIONS)
    lines.extend(
        (
            "",
            "Within `docs/lite-v3/`, every ordinary Markdown file is classified. The included set consists of current diagnostics and the validated mirrors of references/templates; the excluded set consists of the generated target, benchmark files, and reviewer record. An unclassified ordinary Markdown file blocks export.",
            "",
        )
    )
    return "\n".join(lines)


def build_document(root: Path | str) -> bytes:
    """Build the complete deterministic document in memory."""

    sources = collect_sources(resolve_repo_root(root))
    parts = [
        _render_preamble(sources),
        _render_manifest(sources),
        _render_sources(sources),
        _render_mirrors(sources),
        _render_exclusions(),
    ]
    document = "\n".join(parts).rstrip("\n") + "\n"
    return document.encode("utf-8")


def _resolve_output(raw: str | Path, root: Path) -> Path:
    candidate = Path(raw).expanduser()
    if not candidate.is_absolute():
        candidate = root / candidate
    return candidate.absolute().resolve(strict=False)


def _validate_output_parent(path: Path) -> None:
    parent = path.parent
    if parent.exists() and parent.is_symlink():
        raise ExporterError(f"output parent is a symlink: {parent}")
    if not parent.exists():
        parent.mkdir(parents=True, exist_ok=True)
    if not parent.is_dir():
        raise ExporterError(f"output parent is not a directory: {parent}")
    current = parent
    while current != current.parent:
        if current.is_symlink():
            raise ExporterError(f"output path contains a symlink component: {current}")
        current = current.parent


def write_or_check(root: Path | str, output: Path | str, *, check: bool) -> int:
    """Write atomically or compare without mutation; return the plan exit code."""

    repository = resolve_repo_root(root)
    target = _resolve_output(output, repository)
    expected = build_document(repository)
    if check:
        if target.is_symlink() or (target.exists() and not target.is_file()):
            raise ExporterError(f"output is not an ordinary file: {target}")
        if not target.exists():
            print("full specification is stale: output is missing")
            return 1
        try:
            actual = target.read_bytes()
        except OSError as exc:
            raise ExporterError(f"cannot read output: {exc}") from exc
        if actual != expected:
            print("full specification is stale: generated bytes differ")
            return 1
        print("full specification is up to date")
        return 0

    if target.exists() and target.is_symlink():
        raise ExporterError(f"output is a symlink: {target}")
    _validate_output_parent(target)
    if target.exists() and target.read_bytes() == expected:
        print("full specification already current")
        return 0
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{target.name}.", suffix=".tmp", dir=str(target.parent)
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(expected)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, target)
    except OSError as exc:
        temporary.unlink(missing_ok=True)
        raise ExporterError(f"cannot atomically write output: {exc}") from exc
    print(f"generated full specification ({len(expected)} bytes)")
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Export the complete KyMCM Lite specification")
    result.add_argument("--repo-root", help="repository root (default: derive from this script)")
    result.add_argument("--output", default=DEFAULT_OUTPUT.as_posix(), help="generated Markdown path")
    result.add_argument("--check", action="store_true", help="compare without writing")
    return result


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        root = resolve_repo_root(args.repo_root)
        return write_or_check(root, _resolve_output(args.output, root), check=args.check)
    except (ExporterError, OSError, UnicodeError) as exc:
        print(f"export error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
