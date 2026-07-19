#!/usr/bin/env python3
"""Shared path resolution for KyMCM command-line tools."""

import argparse
import os
from pathlib import Path


WORKSPACE_ENV = "KYMCM_WORKSPACE"
DEFAULT_WORKSPACE_NAME = "CUMCM_Workspace"


def resolve_skill_root() -> Path:
    """Return the installed KyMCM skill directory."""
    return Path(__file__).resolve().parents[1]


def resolve_workspace(cli_value: str | Path | None = None) -> Path:
    """Resolve one workspace using CLI, environment, then cwd precedence."""
    raw_value = cli_value if cli_value is not None else os.environ.get(WORKSPACE_ENV)
    path = Path(raw_value).expanduser() if raw_value else Path.cwd() / DEFAULT_WORKSPACE_NAME
    if not path.is_absolute():
        path = Path.cwd() / path
    try:
        return path.resolve()
    except OSError as exc:
        raise ValueError(f"Unable to resolve KyMCM workspace path: {path}") from exc


def add_workspace_argument(parser: argparse.ArgumentParser) -> None:
    """Add the shared workspace option to a command-line parser."""
    parser.add_argument(
        "--workspace",
        metavar="PATH",
        help=(
            "Competition workspace path. Overrides KYMCM_WORKSPACE; "
            "defaults to ./CUMCM_Workspace."
        ),
    )


def resolve_workspace_path(value: str | Path, workspace: str | Path) -> Path:
    """Resolve an input path and require it to stay inside the workspace."""
    root = Path(workspace).expanduser().resolve()
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = root / path
    path = path.resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"Path is outside KyMCM workspace {root}: {path}")
    return path
