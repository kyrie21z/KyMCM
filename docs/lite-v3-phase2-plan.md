# KyMCM Lite v3 Phase 2 — Standalone MVP

> Historical KyMCM Lite 0.1.0 plan. Superseded by the 0.3.0 direct-dependency workflow; context behavior below is retained as release history.

## Objective

Implement a self-contained Python-standard-library Skill that initializes variable-question Lite v3 workspaces and performs read-only workspace, START, RESULT, and evidence checks.

## Product boundary

Lite validates Markdown structure and evidence integrity. It does not judge mathematical correctness, discover models, manage approvals or hidden state, execute user code, or depend on KyMCM Full.

## Deliverables

- `skills/kymcm-lite/` with identity, templates, standalone protocol documentation, and `scripts/lite.py`.
- Public commands: `init`, `doctor`, `check-start`, and `check-result`.
- Stable plain-text diagnostics and exit codes 0, 1, and 2.
- Unit, CLI integration, standalone-copy portability, performance, release-tree, and Full-isolation tests.
- Repository documentation that presents Full and Lite as explicit sibling products.

## Command behavior

`init` creates the exact Lite v3 marker, minimal context, and contiguous q1–qN managed directories without Git or workflow state. `doctor` diagnoses layout, mode, Python, symlinks, Git availability, and document discovery. `check-start` validates the frozen contract and unresolved sentinel. `check-result` adds deviation and safe evidence validation. All checkers are read-only.

## Testing and isolation

Lite tests cover positive fixtures, malformed contracts, path traversal, cross-question evidence, symlinks, warning/error/tool exits, deterministic output, copied-Skill execution, and sub-second local checks. Full sources remain hash-identical and all Full regression groups must pass.

## Non-goals and stop condition

Phase 2 does not add migration, `add-problem`, JSON output, paper/figure generation, solvers, agent scheduling, or release automation. Stop with uncommitted reviewable changes after every local gate is green; release work belongs to a later phase.
