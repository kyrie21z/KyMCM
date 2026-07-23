# KyMCM Lite 0.2.0

## Highlights

KyMCM Lite 0.2.0 preserves the first standalone Lite v3 modeling workflow from 0.1.0 and adds an optional independent appendix-organization stage. It provides deterministic read-only structural, evidence, exact-file-set, dependency, XLSX, and sensitive-information checks. Lite core uses only the Python standard library and remains independent of KyMCM Full.

## Install

Use Python 3.11, 3.12, or 3.13 and copy the complete `skills/kymcm-lite/` directory. Run `python scripts/lite.py --help` from the copied Skill or invoke the script by absolute path.

## Commands

- `init` creates the managed workspace skeleton for a fixed positive question count.
- `doctor` checks marker and layout integrity.
- `check-start` checks one START handoff.
- `check-result` checks START, RESULT, and declared evidence.
- `check-appendix-start` validates the whole-submission appendix whitelist without `--problem`.
- `check-appendix-result` validates the exact `appendix/` and root `code/` outputs without executing user code.

Exit code 0 means valid or warnings only, 1 means a contract or evidence failure, and 2 means an unexpected tool or environment failure.

## Protocol identity

The workspace marker remains exactly `{"workflow":"kymcm_lite","version":3}`. Product version 0.2.0 and protocol generation 3 are independent identifiers. Existing 0.1.0 modeling workspaces need no migration and create no appendix files unless authors explicitly add the optional contracts.

## Safety and validation scope

Checkers are read-only. They ignore Markdown examples inside fenced code and HTML comments, reject unsafe or symlinked paths, and never execute evidence or user code. Appendix checks never read `FROZEN_CONTEXT.md`; they validate structure and execution-provided evidence, not mathematical correctness.

## Full versus Lite

KyMCM Full 1.0.0 is the separate review-gated workflow with structured mathematical records, approvals, Git binding, and figure support. Lite is a smaller Markdown handoff checker. Neither product guesses or converts the other's workspace.

## Known limitations

Lite does not provide solvers, model discovery, paper or figure generation, workflow approvals, JSON diagnostics, dynamic `add-problem`, automatic appendix building/deletion, native multi-OS certification, or mathematical-correctness validation. It does not prove result equivalence, resolve every dynamic import, interpret all CMake, or verify Excel formula/format semantics. Git diagnostics are advisory.

## Upgrade and compatibility

Users who installed by copying must reinstall the complete Skill for 0.2.0. Symlink installations need only update the repository and restart Codex. Historical Checkpoint Lite v2 workspaces are not automatically migrated. Full, Lite v2, Legacy, malformed, and unknown markers fail closed in Lite v3. Full v1.0.0 remains separate and supported.

## Historical 0.1.0 release

KyMCM Lite 0.1.0 (2026-07-20) was the first standalone Lite v3 release, with variable-question initialization and the `init`, `doctor`, `check-start`, and `check-result` modeling commands.

## Verification summary

The release candidate is checked by Lite unit, CLI, portability, protocol, release-tree, release-specific, and Full regression suites. CI covers Python 3.11–3.13. Final local test counts are recorded in the release review report rather than fixed in this document.
