# KyMCM Lite v3 Provisional Diagnostic Catalog

Status: Normative for planned Phase 2 implementation. Phase 1 defines these diagnostics but implements no Lite checker.

Exit codes remain `0` for structurally valid contracts (warnings allowed), `1` for contract or evidence invalidity, and `2` for unexpected tool or environment failure. Every emitted message should include the workspace-relative path and, when relevant, the question number, heading, section, or evidence entry.

| Identifier | Severity | Commands | Precise trigger | Blocking | Message intent and required location |
|---|---|---|---|---|---|
| `LITE-MODE-001` | Error | all | `.kymcm/mode.json` is missing, malformed, or not exactly Lite v3 | Yes | Show marker path, observed value/error, and exact expected marker |
| `LITE-LAYOUT-001` | Error | `doctor` | Required managed directory or marker path is missing | Yes | Name each missing workspace-relative managed path |
| `LITE-LAYOUT-SYMLINK-001` | Error | all | Any traversed managed path is a symlink or escapes the workspace | Yes | Name the unsafe component and managed path |
| `LITE-CONTEXT-001` | Error | `check-start`, `check-result` | `FROZEN_CONTEXT.md` is missing, not an ordinary file, or unreadable | Yes | Name the context path and read failure |
| `LITE-CONTEXT-SPARSE-WARN-001` | Warning | `check-start`, `check-result` | Q2+ context has no usable cross-question interface content | No | Name context path and expected inherited-interface section |
| `LITE-START-001` | Error | `check-start`, `check-result` | START is missing, unreadable, or title is not exactly `# START QN` | Yes | Name START path and expected question identity |
| `LITE-START-HEADING-001` | Error | `check-start`, `check-result` | A required START heading is missing, duplicated, or reordered | Yes | Name START path, first mismatch, and expected heading order |
| `LITE-START-EMPTY-WARN-001` | Warning | `check-start`, `check-result` | A required START section has no meaningful author content | No | Name START path and section number |
| `LITE-START-UNRESOLVED-001` | Error | `check-start`, `check-result` | Trimmed section 8 is not exactly `无`, `None`, or `N/A` | Yes | Name START path, section 8, and permitted sentinels |
| `LITE-RESULT-001` | Error | `check-result` | RESULT is missing, unreadable, or title is not exactly `# RESULT QN` | Yes | Name RESULT path and expected question identity |
| `LITE-RESULT-HEADING-001` | Error | `check-result` | A required RESULT heading is missing, duplicated, or reordered | Yes | Name RESULT path, first mismatch, and expected heading order |
| `LITE-RESULT-DEVIATION-001` | Error | `check-result` | RESULT section 2 contains neither `无偏差` nor an explicit authorized-deviation record | Yes | Name RESULT path and section 2 requirement |
| `LITE-RESULT-VALIDATION-WARN-001` | Warning | `check-result` | RESULT section 4 lacks problem-applicable validation detail | No | Name RESULT path and validation section; avoid demanding inapplicable categories |
| `LITE-RESULT-DOWNSTREAM-WARN-001` | Warning | `check-result` | RESULT section 7 states neither inheritable outputs nor an explicit absence | No | Name RESULT path and downstream section |
| `LITE-EVIDENCE-FORMAT-001` | Error | `check-result` | An evidence bullet has zero/multiple backticked paths or invalid bullet syntax | Yes | Name RESULT path, line/entry, and required syntax |
| `LITE-EVIDENCE-PATH-001` | Error | `check-result` | Evidence path is absolute, empty, or contains a `..` segment | Yes | Show the rejected path and safe relative-path rule |
| `LITE-EVIDENCE-SCOPE-001` | Error | `check-result` | Evidence resolves outside the current question's `code`, `data/derived`, `outputs`, or `notes` | Yes | Show resolved question-relative scope and allowed directories |
| `LITE-EVIDENCE-MISSING-001` | Error | `check-result` | Evidence is missing or not an ordinary file | Yes | Name the evidence entry and unresolved path |
| `LITE-EVIDENCE-SYMLINK-001` | Error | `check-result` | Evidence or a traversed evidence component is a symlink | Yes | Name the evidence entry and unsafe component |
| `LITE-GIT-WARN-001` | Warning | `doctor`, `check-start`, `check-result` | Git executable or workspace repository is unavailable | No | State that revision diagnostics are unavailable, not that the contract is invalid |
| `LITE-GIT-DIRTY-WARN-001` | Warning | `check-result` | Current-question `code` or `data/derived` has Git changes | No | List affected question-scoped paths without changing Git state |
| `LITE-STALE-WARN-001` | Warning | `check-result` | RESULT modification time is older than START | No | Name both paths/times and label this an advisory heuristic |
| `LITE-TOOL-001` | Error | all | An unexpected I/O, encoding, subprocess, or environment failure prevents diagnosis | Tool failure | Name operation and safe error context; return exit code 2 |
