#!/usr/bin/env python3
"""Resolve KyMCM Full and compatibility workflow markers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


class WorkflowModeError(ValueError):
    """The workspace mode marker is present but invalid."""


MARKER = Path(".kymcm/mode.json")
LITE_WORKFLOW = "checkpoint_lite"
LITE_VERSION = 2
FULL_WORKFLOW = "kymcm_full"
FULL_VERSION = 1


def workspace_mode(workspace: str | Path) -> str:
    """Return the exact recognized workflow name; never guess invalid markers."""
    root = Path(workspace).expanduser().resolve()
    marker = root / MARKER
    if not marker.exists():
        return "legacy"
    if marker.is_symlink() or not marker.is_file():
        raise WorkflowModeError(f"invalid KyMCM mode marker: {marker}")
    try:
        payload: Any = json.loads(marker.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise WorkflowModeError(f"cannot read valid KyMCM mode marker: {marker}") from exc
    if not isinstance(payload, dict):
        raise WorkflowModeError("KyMCM mode marker must be a JSON object")
    if set(payload) != {"workflow", "version"}:
        raise WorkflowModeError("KyMCM mode marker must contain only workflow and version")
    marker = (payload["workflow"], payload["version"])
    if marker == (FULL_WORKFLOW, FULL_VERSION):
        return FULL_WORKFLOW
    if marker == (LITE_WORKFLOW, LITE_VERSION):
        return LITE_WORKFLOW
    if marker not in ((FULL_WORKFLOW, FULL_VERSION), (LITE_WORKFLOW, LITE_VERSION)):
        raise WorkflowModeError(
            f"unsupported KyMCM workflow marker: {payload.get('workflow')!r} "
            f"version {payload.get('version')!r}"
        )
    raise AssertionError("unreachable")


def require_mode(workspace: str | Path, expected: str) -> None:
    actual = workspace_mode(workspace)
    if actual != expected:
        raise WorkflowModeError(f"command requires {expected} mode; workspace uses {actual} mode")


def require_full_mode(workspace: str | Path) -> None:
    actual = workspace_mode(workspace)
    if actual not in (FULL_WORKFLOW, LITE_WORKFLOW):
        raise WorkflowModeError(f"command requires KyMCM Full mode; workspace uses {actual} mode")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        print(workspace_mode(args.workspace))
    except WorkflowModeError as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
