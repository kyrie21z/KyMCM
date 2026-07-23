# KyMCM Lite v3 Diagnostic Catalog

Status: Normative for KyMCM Lite 0.3.0.

Exit codes remain `0` for structurally valid contracts (warnings allowed), `1` for contract or evidence invalidity, and `2` for unexpected tool or environment failure. Every emitted message should include the workspace-relative path and, when relevant, the question number, heading, section, or evidence entry.

| Identifier | Severity | Commands | Precise trigger | Blocking | Message intent and required location |
|---|---|---|---|---|---|
| `LITE-MODE-001` | Error | all | `.kymcm/mode.json` is missing, malformed, or not exactly Lite v3 | Yes | Show marker path, observed value/error, and exact expected marker |
| `LITE-LAYOUT-001` | Error | `doctor` | Required managed directory or marker path is missing | Yes | Name each missing workspace-relative managed path |
| `LITE-LAYOUT-SYMLINK-001` | Error | all | Any traversed managed path is a symlink or escapes the workspace | Yes | Name the unsafe component and managed path |
| `LITE-START-001` | Error | `check-start`, `check-result` | START is missing, unreadable, or title is not exactly `# START QN` | Yes | Name START path and expected question identity |
| `LITE-START-HEADING-001` | Error | `check-start`, `check-result` | A required START heading is missing, duplicated, or reordered | Yes | Name START path, first mismatch, and expected heading order |
| `LITE-START-DEPENDENCY-001` | Error | `check-start`, `check-result` | Section 2 dependency declaration is missing, duplicated, malformed, comment-only, or fenced-only | Yes | Name START path and exact `**前问依赖：**` grammar |
| `LITE-START-DEPENDENCY-SCOPE-001` | Error | `check-start`, `check-result` | Dependency is self, forward, zero, negative, unknown, duplicated, or unsorted; or Q1 does not use `无` | Yes | Name START path and strict predecessor rule |
| `LITE-START-DEPENDENCY-CONTRACT-001` | Error | `check-start`, `check-result` | A declared upstream START/RESULT is missing, unsafe, unreadable, or structurally invalid | Yes | Name exact upstream path and required title/headings |
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

## Appendix diagnostics

The modeling workflow has no FROZEN_CONTEXT surface. Appendix organization may reference START and RESULT only. All paths below are workspace-relative, and secret diagnostics redact matched values.

| Identifier | Severity | Precise trigger |
|---|---|---|
| `LITE-APPENDIX-START-001` | Error | APPENDIX_START is missing, unsafe, or has the wrong title |
| `LITE-APPENDIX-START-HEADING-001` | Error | APPENDIX_START headings are missing, duplicated, or reordered |
| `LITE-APPENDIX-START-EMPTY-WARN-001` | Warning | One of APPENDIX_START sections 1–8 lacks visible author content |
| `LITE-APPENDIX-UNRESOLVED-001` | Error | APPENDIX_START section 9 is not exactly cleared |
| `LITE-APPENDIX-DECLARATION-001` | Error | External-material or mandatory-result declaration is missing, duplicated, malformed, or inconsistent |
| `LITE-APPENDIX-WHITELIST-FORMAT-001` | Error | Whitelist ID, mode, source list, purpose, environment set, or bullet grammar is invalid |
| `LITE-APPENDIX-WHITELIST-DUPLICATE-001` | Error | A whitelist ID or target is duplicated |
| `LITE-APPENDIX-SOURCE-PATH-001` | Error | A source is unsafe, outside permitted roots/mapping, or is a START/RESULT reference |
| `LITE-APPENDIX-SOURCE-MISSING-001` | Error | A declared source is not an existing ordinary file |
| `LITE-APPENDIX-TARGET-PATH-001` | Error | A target is unsafe or outside its exact appendix/code surface |
| `LITE-APPENDIX-SYMLINK-001` | Error | A source, target, evidence, or traversed component is a symlink |
| `LITE-APPENDIX-RESULT-001` | Error | APPENDIX_RESULT is missing/invalid, omits an approved ID, or names an unknown whitelist-like ID |
| `LITE-APPENDIX-RESULT-HEADING-001` | Error | APPENDIX_RESULT headings are missing, duplicated, or reordered |
| `LITE-APPENDIX-DEVIATION-001` | Error | APPENDIX_RESULT section 2 lacks `无偏差` or an authorized deviation with safe evidence |
| `LITE-APPENDIX-EVIDENCE-001` | Error | Evidence syntax, ID, path, existence, symlink safety, or required integrity index is invalid |
| `LITE-APPENDIX-OUTPUT-MISSING-001` | Error | A declared output or static local dependency is missing |
| `LITE-APPENDIX-OUTPUT-EXTRA-001` | Error | An undeclared file exists in `appendix/` or root `code/` |
| `LITE-APPENDIX-STRUCTURE-001` | Error | An output root/directory is forbidden, undeclared, empty, or structurally misplaced |
| `LITE-APPENDIX-FORBIDDEN-001` | Error | A submitted name/type is cache, build, log, internal, duplicate-like, or non-core root-code material |
| `LITE-APPENDIX-COPY-MISMATCH-001` | Error | A COPY target SHA-256 differs from its source |
| `LITE-APPENDIX-INTEGRITY-001` | Error | `source_integrity.csv` is missing or structurally/hash/status invalid |
| `LITE-APPENDIX-DUPLICATE-001` | Error | Two declared formal-result files are byte-identical |
| `LITE-APPENDIX-PYTHON-001` | Error | Submitted Python has invalid syntax or a missing obvious local module |
| `LITE-APPENDIX-DEPENDENCY-WARN-001` | Warning | Dynamic loading/CMake prevents closure proof, or root core code is outside the 150–400 line guideline |
| `LITE-APPENDIX-XLSX-001` | Error | Declared Result.xlsx is not a valid basic workbook ZIP/XML structure |
| `LITE-APPENDIX-SENSITIVE-001` | Error | A high-confidence local path, credential, private key, authorization value, or machine identity is detected |
| `LITE-APPENDIX-CERTIFICATION-WARN-001` | Warning | Unqualified global-certification wording conflicts with visible finite/partial limitations |
| `LITE-APPENDIX-STALE-WARN-001` | Warning | APPENDIX_START validation finds pre-existing nonempty output roots |
