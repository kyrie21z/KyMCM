# KyMCM Lite 0.1.0

## Highlights

KyMCM Lite 0.1.0 is the first standalone Lite v3 release. It provides a Markdown-first handoff format, variable-question workspace initialization, and deterministic read-only structural and evidence checks. Lite core uses only the Python standard library and remains independent of KyMCM Full.

## Install

Use Python 3.11, 3.12, or 3.13 and copy the complete `skills/kymcm-lite/` directory. Run `python scripts/lite.py --help` from the copied Skill or invoke the script by absolute path.

## Commands

- `init` creates the managed workspace skeleton for a fixed positive question count.
- `doctor` checks marker and layout integrity.
- `check-start` checks one START handoff.
- `check-result` checks START, RESULT, and declared evidence.

Exit code 0 means valid or warnings only, 1 means a contract or evidence failure, and 2 means an unexpected tool or environment failure.

## Protocol identity

The workspace marker is exactly `{"workflow":"kymcm_lite","version":3}`. Product version 0.1.0 and protocol generation 3 are independent identifiers.

## Safety and validation scope

Checkers are read-only. They ignore Markdown examples inside fenced code and HTML comments, reject unsafe or symlinked evidence paths, and do not open or execute evidence content. They validate structure and evidence existence, not mathematical correctness.

## Full versus Lite

KyMCM Full 1.0.0 is the separate review-gated workflow with structured mathematical records, approvals, Git binding, and figure support. Lite is a smaller Markdown handoff checker. Neither product guesses or converts the other's workspace.

## Known limitations

Lite does not provide solvers, model discovery, paper or figure generation, workflow approvals, JSON diagnostics, dynamic `add-problem`, native multi-OS certification, or mathematical-correctness validation. Git diagnostics are advisory.

## Upgrade and compatibility

This is the first standalone Lite v3 release. Historical Checkpoint Lite v2 workspaces are not automatically migrated. Full, Lite v2, Legacy, malformed, and unknown markers fail closed in Lite v3. Users must explicitly initialize or author a Lite v3 workspace. Full v1.0.0 remains separate and supported.

## Verification summary

The release candidate is checked by Lite unit, CLI, portability, protocol, release-tree, release-specific, and Full regression suites. CI covers Python 3.11–3.13. Final local test counts are recorded in the release review report rather than fixed in this document.
