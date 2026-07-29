# KyMCM Lite 0.5.1

## Highlights

KyMCM Lite 0.5.1 corrects the two appendix code surfaces. `appendix/` now means the complete formal solve code package with plotting excluded; root `code/` means authentic representative implementation for the paper PDF and may include scheduling, recovery, audit, and other paper-relevant non-core execution code.

The change is not a similarity-evasion mechanism. Copying, obfuscation, junk/dead code, arbitrary renaming or control-flow changes, and code unrelated to the formal workflow are forbidden. Selecting distinctive authentic engineering code reduces false alarms caused by naturally similar generic core implementations while preserving traceability.

No external similarity service, originality score, plotting classifier, command, state, JSON, manifest, approval, or new whitelist mode is added. The six public commands, Lite v3 marker, START/RESULT/HANDOFF templates, APPENDIX_START/RESULT headings and declaration grammar, dependency/evidence grammar, and modeling checker behavior are unchanged from 0.5.0.

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

The workspace marker remains exactly `{"workflow":"kymcm_lite","version":3}`. Product version 0.5.1 and protocol generation 3 are independent identifiers. The eight START and seven RESULT headings are unchanged. START section 2 contains exactly one visible `**前问依赖：** 无` or strictly ordered exact earlier-unit list such as `**前问依赖：** Q1, Q2_1`.

## Appendix code surfaces

APPENDIX_START remains the sole source-to-target whitelist using the existing COPY, CURATE, and GENERATE grammar. For `appendix/problems/qN/code/`, list every source used by the formal solve pipeline and its runtime/build closure, including applicable scheduling, batch execution, checkpoint/resume source, failure isolation, status readback, audit, and local configuration. Exclude plotting, tests, caches, logs, obsolete experiments, runtime checkpoint/status data, binaries, credentials, and unrelated infrastructure.

Root `code/` still contains direct files only, but they are selected for truthful paper explanation rather than constrained to generic core algorithms. Each C entry identifies real source paths, formal responsibility, paper value, and COPY/CURATE boundaries. Formal calculation and plotting that cannot be separated mechanically must stop for human review.

The checker now permits operational source names such as `scheduler.py`, `orchestrator.py`, `checkpoint.py`, `resume.py`, `supervisor.py`, `stage_ledger.py`, `run_status.py`, `resource_monitor.py`, and `audit.py`. It continues to reject runtime data and unsafe/binary/cache/log targets. It does not judge formal-code completeness, plotting responsibility, originality, external similarity, or CURATE semantic equivalence.

## Paper-writing HANDOFF

Create HANDOFF only after the exact matching RESULT passes `check-result` and formal plus paper-relevant auxiliary evidence is stable. Single mode uses `HANDOFF_QN.md`; split mode uses exact `HANDOFF_QN_K.md` documents and never an unsuffixed aggregate.

RESULT controls formal scope, machine evidence controls actual values and assets, and HANDOFF remains the paper writer's sole complete collaboration document that organizes them for writing. Every important item is labeled `正式` or `辅助`, maps to real workspace-relative evidence, and states both usable interpretation and forbidden causal, absolute, or extrapolative language. Critical numbers are rechecked against evidence before finalization. HANDOFF cannot expand RESULT, serve as a downstream modeling dependency, or enter appendix outputs.

## Safety and validation scope

Checkers are read-only. They ignore Markdown examples inside fenced code and HTML comments, reject unsafe or symlinked paths, and never execute evidence or user code. A legacy FROZEN_CONTEXT file is ignored even when malformed or invalid UTF-8. The active modeling workflow has no global context file, and appendix organization may reference but cannot copy single or split START/RESULT contracts or matching HANDOFF collaboration documents.

Codex reads each declared upstream START and RESULT when authoring, materially revising, reviewing, or executing a dependent START. Authorized RESULT deviations form part of the effective upstream contract. A no-conflict review creates no report, JSON, approval, event, hash, or evidence artifact.

Before formal execution, Codex performs environment and data preflight, checks dependency contradictions separately from final plan quality, and runs a smallest representative smoke test. Formal work proceeds in recoverable stages with intermediate persistence and explicit failure/repair records. Every execution receives a basic L0 audit; L1 sensitivity or robustness checks are required when conclusions depend on uncertain assumptions or parameters; L2 independent or alternative-method checks are used when warranted by risk and cost. These semantic duties are not mechanically certified by the Lite checker.

## Full versus Lite

KyMCM Full 1.0.0 is the separate review-gated workflow with structured mathematical records, approvals, Git binding, and figure support. Lite is a smaller Markdown handoff checker. Neither product guesses or converts the other's workspace.

## Known limitations

Lite does not provide solvers, model or contract-granularity discovery, automatic dependency discovery, transitive or wildcard expansion, sibling-unit comparison, automatic semantic reconciliation, automatic cost measurement, automatic recovery, automatic paper or figure generation, workflow approvals, JSON diagnostics, dynamic `add-problem`, automatic appendix building/deletion, plotting classification, originality or external-similarity checking, native multi-OS certification, or mathematical-correctness validation. HANDOFF completeness, appendix coverage, CURATE equivalence, code authenticity, and writing quality remain Codex/ChatGPT and human responsibilities. Final paper numbers still require evidence-level review. Git diagnostics are advisory.

## Upgrade and compatibility

Users who installed by copying must reinstall the complete Skill for 0.5.1. Symlink installations need only update the repository and restart Codex. Existing 0.5.0 workspaces and appendix contracts need no rewrite. Apply the corrected code-selection policy when an appendix is next reorganized or resubmitted; historical packages are not automatically migrated or rewritten. Full, Lite v2, Legacy, malformed, and unknown markers fail closed in Lite v3. Full v1.0.0 remains separate and supported.

## Historical 0.5.0 release

KyMCM Lite 0.5.0 (2026-07-29) added the exact single/split paper-writing HANDOFF layer while preserving RESULT as the formal boundary and only downstream modeling inheritance surface.

## Historical 0.4.0 release

KyMCM Lite 0.4.0 (2026-07-29) added the mirrored execution-first modeling-plan design standard, including preflight, smoke testing, staged recovery, explicit nested cost, and L0/L1/L2 validation guidance. Its preserved canonical source SHA-256 is `3c508dc1a48a697efcc8b220cde5187727b8b49ba4b81570ca3ab8750e09120b`.

## Historical 0.3.1 release

KyMCM Lite 0.3.1 (2026-07-24) added independent split units with exact dependency tokens while preserving the single-mode workspace contract.

## Historical 0.3.0 release

KyMCM Lite 0.3.0 (2026-07-23) removed the global FROZEN_CONTEXT surface, added exact direct-dependency declarations and semantic contradiction review, and retained the appendix workflow.

## Historical 0.2.0 release

KyMCM Lite 0.2.0 (2026-07-23) added the independent appendix-organization stage and the `check-appendix-start` and `check-appendix-result` commands.

## Historical 0.1.0 release

KyMCM Lite 0.1.0 (2026-07-20) was the first standalone Lite v3 release, with variable-question initialization and the `init`, `doctor`, `check-start`, and `check-result` modeling commands.

## Verification summary

The canonical three-question 0.3.0 modeling fixture has six formal START/RESULT Markdown files totaling 10,569 bytes, plus the unchanged 38-byte marker. It has no FROZEN_CONTEXT or review snapshot.

The release candidate is checked by Lite unit, CLI, portability, protocol, release-tree, release-specific, and Full regression suites. CI covers Python 3.11–3.13. Final local test counts are recorded in the release review report rather than fixed in this document.
