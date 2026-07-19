"""Basic, non-executing integrity checks for generated Figure assets."""

from __future__ import annotations

import hashlib
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_pdf(path: Path) -> None:
    content = path.read_bytes()
    if not content.startswith(b"%PDF-") or b"%%EOF" not in content[-1024:]:
        raise ValueError("PDF invalid: missing PDF header or EOF marker")


def validate_svg(path: Path) -> None:
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError) as exc:
        raise ValueError(f"SVG invalid: {exc}") from exc
    local_name = root.tag.rsplit("}", 1)[-1].lower()
    if local_name != "svg":
        raise ValueError("SVG invalid: root element is not svg")


def validate_png(path: Path) -> tuple[int, int]:
    try:
        with Image.open(path) as image:
            if image.format != "PNG":
                raise ValueError(f"PNG invalid: decoded format is {image.format}")
            image.verify()
        with Image.open(path) as image:
            if image.format != "PNG":
                raise ValueError(f"PNG invalid: decoded format is {image.format}")
            return image.size
    except (OSError, SyntaxError) as exc:
        raise ValueError(f"PNG invalid: {exc}") from exc


def validate_output(path: Path, format_name: str) -> tuple[int, int] | None:
    if not path.is_file() or path.stat().st_size == 0:
        raise ValueError(f"{format_name.upper()} invalid: file is missing or empty")
    if format_name == "pdf":
        validate_pdf(path)
        return None
    if format_name == "svg":
        validate_svg(path)
        return None
    if format_name == "png":
        return validate_png(path)
    raise ValueError(f"Unsupported Figure output format: {format_name}")
