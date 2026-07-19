# KyMCM Standard Operating Procedure

## 1. Initialize

Create one workspace and initialize schema v4. `pipeline.json` is authoritative; `events.jsonl` is audit-only.

## 2. Approve the Problem Contract

Document interpretation, subproblems, shared symbols/data, ambiguities, and the dependency DAG. Reject cycles. The stable topological order is for display and deterministic suggestions, not a strict question-number gate. Obtain the exact versioned approval phrase before any Solution Contract.

Resolve every pending human approval before starting a problem. Approval rechecks Contract type, version, status, and Solution problem identity; approved Contracts are then bound by identity and hash.

## 3. Solve One Problem at a Time

Choose one ready problem. Independent problems may be selected in any order, but only one problem may be running or blocked:

1. Read the Problem Contract and completed predecessor outputs.
2. Draft and approve `Solution Contract Qi`.
3. Generate a non-approval Implementation Plan.
4. Start Qi only when its Contract snapshot is current and dependencies have completed with valid evidence.
5. Execute the Implementation Plan; schema v4 has no `run-stage` or micro-stage state.
6. Record `results/qN/validation.json` with executable evidence.
7. Complete Qi only when validation status is `pass`, contract snapshots match, the report hash matches, and every evidence file remains available.

## 4. Handle Validation Outcomes

- `pass`: freeze outputs and continue.
- `repairable`: repair implementation and rerun validation.
- `contract_change_required`: draft and approve a new Solution Contract version.
- `decision_required`: pause and ask the user for the unresolved decision.

## 5. Handle Upstream Defects

Use `invalidate-problem` for implementation defects. The target and DAG successors become stale, validation pointers and current focus are cleared, and unrelated problems remain unchanged. A new Solution Contract invalidates its problem and successors; downstream Solution Contracts must be renewed when dependency snapshots change. Any new Problem Contract version conservatively invalidates all existing work, even when the DAG is unchanged.

## 6. Build Paper Figures

After result data is available, create Figure Briefs in `figures/figure_plan.yaml`. Every Figure uses exactly one workspace-local CSV evidence file; modeling code must merge multiple sources and export a named intermediate CSV. Render SVG/PDF/PNG through `figure_manager.py`, run the deterministic audit, and inspect `figures/gallery.html`. Use only passing manifests in the paper. Figure planning and audit are stateless and do not create Contract approvals.

## 7. Final Paper

After all problems complete, record global consistency with per-problem validation hashes, draft the paper, and request the Final Paper Checkpoint. Submission and approval both revalidate all upstream evidence. Require exact approval `批准 Final Paper vN` before final export.

## 8. Prohibitions

- No concurrent problem execution.
- No parallel Contract approval.
- No prose self-approval in place of executable validation.
- No in-place edits to approved Contracts.
- No problem completion without evidence-bearing validation.
- No final export before Final Paper approval.
- No Figure Contract, Figure approval status, or lifecycle change.
