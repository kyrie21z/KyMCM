# KyMCM Lite 0.3.1

## Highlights

KyMCM Lite 0.3.1 lets each official question use either one unsuffixed START/RESULT pair or contiguous `QN_K` START units with matching RESULT units completed independently. Modes are mutually exclusive. Contract granularity follows modeling dependency and execution boundaries, not printed subquestion count; no aggregate contract, subproblem directory, manifest, or workflow state is added.

Only `check-start` and `check-result` gain optional positive `--subproblem K`. Dependencies may name exact earlier-question split units such as `Q1_2`; bare tokens address only single-mode questions, suffixed tokens never expand, and same-question dependencies remain forbidden. Appendix source exclusion and certification scanning now recognize every active single or split contract. Valid 0.3.0 single-mode workspaces continue to pass unchanged.

## Install

Use Python 3.11, 3.12, or 3.13 and copy the complete `skills/kymcm-lite/` directory. Run `python scripts/lite.py --help` from the copied Skill or invoke the script by absolute path.

## Commands

- `init` creates the managed workspace skeleton for a fixed positive question count.
- `doctor` checks marker, question layout, and single/split contract modes.
- `check-start` checks one selected START handoff; split mode requires `--subproblem K`.
- `check-result` checks the matching selected START, RESULT, and declared evidence.
- `check-appendix-start` validates the whole-submission appendix whitelist without `--problem`.
- `check-appendix-result` validates the exact `appendix/` and root `code/` outputs without executing user code.

Exit code 0 means valid or warnings only, 1 means a contract or evidence failure, and 2 means an unexpected tool or environment failure.

## Protocol identity

The workspace marker remains exactly `{"workflow":"kymcm_lite","version":3}`. Product version 0.3.1 and protocol generation 3 are independent identifiers. The eight START and seven RESULT headings are unchanged. START section 2 contains exactly one visible `**前问依赖：** 无` or strictly ordered exact earlier-unit list such as `**前问依赖：** Q1, Q2_1`.

## Safety and validation scope

Checkers are read-only. They ignore Markdown examples inside fenced code and HTML comments, reject unsafe or symlinked paths, and never execute evidence or user code. A legacy FROZEN_CONTEXT file is ignored even when malformed or invalid UTF-8. The active modeling workflow has no global context file, and appendix organization may reference but cannot copy single or split START/RESULT contracts.

Codex reads each declared upstream START and RESULT when authoring, materially revising, reviewing, or executing a dependent START. Authorized RESULT deviations form part of the effective upstream contract. A no-conflict review creates no report, JSON, approval, event, hash, or evidence artifact.

## Full versus Lite

KyMCM Full 1.0.0 is the separate review-gated workflow with structured mathematical records, approvals, Git binding, and figure support. Lite is a smaller Markdown handoff checker. Neither product guesses or converts the other's workspace.

## Known limitations

Lite does not provide solvers, model or contract-granularity discovery, automatic dependency discovery, transitive or wildcard expansion, sibling-unit comparison, automatic semantic reconciliation, paper or figure generation, workflow approvals, JSON diagnostics, dynamic `add-problem`, automatic appendix building/deletion, native multi-OS certification, or mathematical-correctness validation. Dependency completeness and contradiction decisions remain Codex/human responsibilities. Git diagnostics are advisory.

## Upgrade and compatibility

Users who installed by copying must reinstall the complete Skill for 0.3.1. Symlink installations need only update the repository and restart Codex. Existing 0.3.0 single-mode workspaces need no rewrite. To migrate 0.2.0, add one dependency declaration to section 2 of every START, ensure declared predecessors have completed START and RESULT files, optionally delete the legacy FROZEN_CONTEXT file, and rerun `doctor`, `check-start`, and `check-result`. Historical workspaces are not automatically migrated. Full, Lite v2, Legacy, malformed, and unknown markers fail closed in Lite v3. Full v1.0.0 remains separate and supported.

## Historical 0.3.0 release

KyMCM Lite 0.3.0 (2026-07-23) removed the global FROZEN_CONTEXT surface, added exact direct-dependency declarations and semantic contradiction review, and retained the appendix workflow.

## Historical 0.2.0 release

KyMCM Lite 0.2.0 (2026-07-23) added the independent appendix-organization stage and the `check-appendix-start` and `check-appendix-result` commands.

## Historical 0.1.0 release

KyMCM Lite 0.1.0 (2026-07-20) was the first standalone Lite v3 release, with variable-question initialization and the `init`, `doctor`, `check-start`, and `check-result` modeling commands.

## Verification summary

The canonical three-question 0.3.0 modeling fixture has six formal START/RESULT Markdown files totaling 10,569 bytes, plus the unchanged 38-byte marker. It has no FROZEN_CONTEXT or review snapshot.

The release candidate is checked by Lite unit, CLI, portability, protocol, release-tree, release-specific, and Full regression suites. CI covers Python 3.11–3.13. Final local test counts are recorded in the release review report rather than fixed in this document.
