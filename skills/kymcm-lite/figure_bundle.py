"""Same-stem delivery contract for formal KyMCM Lite data figures."""

from __future__ import annotations

import os
import re
import tempfile
from pathlib import Path


BUNDLE_ID = "kymcm-figure-bundle-v1"
REQUIRED_SUFFIXES = (".pdf", ".png", ".py", ".txt")
FORBIDDEN_IMAGE_SUFFIXES = (
    ".svg", ".tif", ".tiff", ".jpg", ".jpeg", ".eps", ".ps", ".webp", ".bmp",
)
_PLACEHOLDER = re.compile(r"TODO|TBD|待补充", re.IGNORECASE)
_PAPER_NUMBER = re.compile(r"^\s*(?:图|Figure|Fig\.)\s*[0-9一二三四五六七八九十]+", re.IGNORECASE)


class FigureBundleError(RuntimeError):
    """A formal figure bundle does not satisfy its delivery contract."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise FigureBundleError(message)


def _stem_path(output_stem) -> Path:
    stem = Path(output_stem)
    _require(not stem.suffix, "output_stem must not include a file extension")
    return stem


def _forbidden_format(stem: Path) -> str | None:
    if not stem.parent.is_dir():
        return None
    for candidate in stem.parent.iterdir():
        if candidate.name.startswith(stem.name):
            suffix = candidate.name[len(stem.name):]
            if suffix.lower() in FORBIDDEN_IMAGE_SUFFIXES:
                return suffix
    return None


def _canonical_note(title: str, caption: str) -> str:
    _require(isinstance(title, str), "figure title must be text")
    _require(isinstance(caption, str), "figure caption must be text")
    _require(len(title.splitlines()) <= 1 and "\n" not in title and "\r" not in title,
             "figure title must be one physical line")
    clean_title = title.strip()
    _require(bool(clean_title), "figure title must not be blank")
    _require(_PAPER_NUMBER.search(clean_title) is None,
             "figure title must not include paper-owned figure numbering")
    lines = caption.splitlines()
    _require(bool(lines) and all(line.strip() for line in lines),
             "figure caption must contain one or more non-empty lines")
    clean_lines = [line.strip() for line in lines]
    content = "\n".join((f"图题：{clean_title}", "图注：", *clean_lines)) + "\n"
    _require("\x00" not in content, "figure note must be plain text")
    _require(_PLACEHOLDER.search(content) is None, "final figure note contains a placeholder")
    return content


def _validate_note_text(text: str) -> None:
    _require(text.endswith("\n") and not text.endswith("\n\n"),
             "figure note must have one deterministic trailing newline")
    _require("\r" not in text, "figure note must use normalized UTF-8 newlines")
    lines = text.splitlines()
    _require(len(lines) >= 3, "figure note is missing title or caption fields")
    _require(lines[0].startswith("图题："), "figure note must begin with exact 图题： field")
    _require(lines[1] == "图注：", "figure note must use exact 图注： second field")
    _require(text == _canonical_note(lines[0][len("图题："):], "\n".join(lines[2:])),
             "figure note is not in canonical v1 grammar")


def write_figure_note(output_stem, *, title: str, caption: str) -> Path:
    """Atomically write the same-stem UTF-8 title and caption file."""
    stem = _stem_path(output_stem)
    content = _canonical_note(title, caption)
    stem.parent.mkdir(parents=True, exist_ok=True)
    destination = stem.with_suffix(".txt")
    handle, name = tempfile.mkstemp(prefix=f".{stem.name}-", suffix=".txt", dir=stem.parent)
    temporary = Path(name)
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
        return destination
    except FigureBundleError:
        raise
    except Exception as exc:
        raise FigureBundleError(f"figure note write failed: {exc}") from exc
    finally:
        temporary.unlink(missing_ok=True)


def validate_figure_bundle(output_stem, *, source_path) -> dict[str, Path]:
    """Validate and return the four required same-stem delivery paths."""
    stem = _stem_path(output_stem)
    paths = {suffix[1:]: stem.with_suffix(suffix) for suffix in REQUIRED_SUFFIXES}
    source = Path(source_path)
    _require(source.resolve() == paths["py"].resolve(),
             "source_path must be the same-stem canonical Python entrypoint")
    for role, path in paths.items():
        _require(path.is_file(), f"required same-stem {role.upper()} file is missing")
        _require(path.stat().st_size > 0, f"required same-stem {role.upper()} file is empty")
    for role in ("py", "txt"):
        try:
            decoded = paths[role].read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise FigureBundleError(f"same-stem {role.upper()} file is not valid UTF-8") from exc
        _require(bool(decoded.strip()), f"required same-stem {role.upper()} file is empty")
        _require("\x00" not in decoded, f"same-stem {role.upper()} file is opaque binary content")
        if role == "txt":
            _validate_note_text(decoded)
    forbidden = _forbidden_format(stem)
    _require(forbidden is None, f"forbidden same-stem formal format exists: {forbidden}")
    return paths
