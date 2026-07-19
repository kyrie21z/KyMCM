# KyMCM Full operating procedure

## 1. Establish the workspace

Run `full_workspace.py init`, initialize the contest directory as an independent Git repository, add original problem inputs, and run the read-only `doctor`. Version 1 fixes the protocol to Q1–Q4.

## 2. Define the whole problem

Draft `problems/problem_definition/problem_definition.json`. Resolve only mathematically consequential ambiguity with the user. Submit it to render `PROBLEM_DEFINITION.md`, read the complete document, and record explicit user acceptance. A summary is never a substitute for the review document.

## 3. Start one problem

Follow reviewed dependencies. Perform a read-only audit of inputs used by that problem, record semantics and agreed treatments in Model Spec v3, submit Start, read `START_QN.md`, and record explicit acceptance. Start approval authorizes implementation only for that reviewed specification.

## 4. Execute and review

Keep code and derived data under the current `problems/qN/` tree. Commit code and derived evidence to the independent contest repository. Build Result Record v2 with direct answers, validation, limitations, artifacts, and `evidence.code_revision`. Submit Result, read the complete `RESULT_QN.md`, then record explicit acceptance.

Implementation-only failure uses repair/rerun. A change to meaning, inputs, assumptions, equations, decision rules, or conclusions requires semantic replan and a new Start review.

## 5. Figures and paper

Use Figure Briefs and workspace-local evidence. Render, inspect manifests, audit, and gallery outputs before paper use. Do not bundle fonts; Chinese rendering prefers Microsoft YaHei and uses documented CJK fallbacks.

## 6. Completion

Finish all dependency-required questions, recheck deterministic documents and evidence hashes, run paper quality/security checks, and request the final human review before export.
