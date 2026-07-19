#!/usr/bin/env python3
"""Read-only compatibility utility for schema v4 workflow and audit events."""

import argparse
import json
from pathlib import Path

from workspace_context import add_workspace_argument, resolve_workspace


def main() -> None:
    parser = argparse.ArgumentParser()
    add_workspace_argument(parser)
    parser.add_argument("command", choices=["status", "events"], default="status", nargs="?")
    args = parser.parse_args()
    workspace = resolve_workspace(args.workspace)
    if args.command == "status":
        path = workspace / "state" / "pipeline.json"
        if not path.exists():
            print("{}")
            return
        state = json.loads(path.read_text(encoding="utf-8"))
        print(json.dumps({
            "schema_version": state.get("schema_version"),
            "current_problem": state.get("current_problem"),
            "expected_action": state.get("expected_action"),
        }, ensure_ascii=False, indent=2))
    else:
        path = workspace / "state" / "events.jsonl"
        print(path.read_text(encoding="utf-8") if path.exists() else "", end="")


if __name__ == "__main__":
    main()
