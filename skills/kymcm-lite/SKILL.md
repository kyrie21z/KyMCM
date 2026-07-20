---
name: kymcm-lite
description: Execute and review Markdown-first mathematical-modeling handoffs with structural and evidence checks, without workflow state or content JSON.
---

# KyMCM Lite

Resolve the explicit contest workspace before acting. Require exactly `{"workflow":"kymcm_lite","version":3}` in `.kymcm/mode.json`; fail closed for Full, Lite v2, Legacy, malformed, absent, or unknown modes.

Treat `FROZEN_CONTEXT.md`, the current `START_QN.md`, the current `RESULT_QN.md`, and RESULT-declared evidence as the only formal Lite surfaces. Read the complete context and START before implementation, and the complete RESULT plus evidence before external review. Use `scripts/lite.py` for initialization and read-only checks, and follow `references/markdown_format.md`.

Preserve mathematical meaning, parameters, constraints, decision rules, data semantics, budgets, and fallback rules. Choose implementation details independently only when they cannot alter conclusions. Ask one highest-impact question and stop when semantic uncertainty remains. Stop when a discovered data issue changes values, missingness, sample membership, pairing, or model input. Repair parser, path, syntax, cache, logging, and plotting mechanics locally when semantics do not change.

Disclose every authorized START deviation in RESULT. Never create Full JSON artifacts, workflow state, approvals, events, review hashes, or content-level JSON. Never self-approve mathematical conclusions.
