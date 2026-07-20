# KyMCM Lite v3 Phase 1 Benchmark Report

Date: 2026-07-20
Environment: Linux, Python 3 standard library, repository base HEAD `6c87056e967a3260de333d183909002d01413f6d`

Status: **Phase 1 benchmark validated**

## 1. Primary time-aligned Q1-equivalent comparison

The Lite side uses `review_snapshots/before_q2/FROZEN_CONTEXT.md`, the context current after Q1 and before Q2, together with Q1 START and RESULT.

| Metric | KyMCM Full v1 | KyMCM Lite v3 |
|---|---:|---:|
| Formal content/review files | 6 | 3 |
| Human-readable review Markdown files | 3 | 3 |
| Human-readable review Markdown bytes | 4,739 | 4,083 |
| Content-level JSON files | 3 | 0 |
| Content-level JSON bytes | 4,211 | 0 |
| Primary formal bytes | 8,950 | 4,083 |
| Duplicated authoritative semantic representations | 3 JSON/Markdown pairs | 0 |
| Blocking human approval transitions | 3 | 0 |

Time-aligned Lite removes 4,867 of 8,950 primary formal bytes, a measured reduction of **54.4%**. It also halves the formal file count. The Markdown-only byte difference is smaller because Lite keeps the handoff self-contained; the main reduction comes from eliminating content-level JSON duplicates.

## 2. Secondary final-root-context Q1 view

The **final-root-context Q1 view** uses the final root `FROZEN_CONTEXT.md` plus Q1 START and RESULT. It contains later Q2/Q3 frozen context, so it is not lifecycle-equivalent. Its three files total 4,485 bytes and reduce the Full denominator by 4,465 bytes, or **49.9%**.

The previously reported 49.9% was therefore conservative: it charged the isolated Q1 comparison for context added only after Q2 and Q3 completed.

## 3. Persistent machine metadata and state

| Product | Required machine files measured | Bytes | Primary comparison treatment |
|---|---:|---:|---|
| Lite | 1 exact mode marker | 38 | Reported separately |
| Full temporary flow | 13 mode/workflow/event/binding files | 4,905 | Reported separately and excluded |

Lite created no workflow state, event log, approval record, review binding, or content-level JSON. The Full state figure is diagnostic context, not added to the primary 8,950-byte denominator.

## 4. Lite Q1–Q3 fixture totals

The complete Lite fixture has seven formal Markdown files—one `FROZEN_CONTEXT.md`, three START files, and three RESULT files—totaling **12,359 bytes**. The exact 38-byte marker remains separate.

Stable values consumed by the fixture test:

| Key | Value |
|---|---:|
| `lite_q1_time_aligned_formal_files` | 3 |
| `lite_q1_time_aligned_formal_bytes` | 4083 |
| `lite_q1_final_context_formal_files` | 3 |
| `lite_q1_final_context_formal_bytes` | 4485 |
| `lite_all_formal_files` | 7 |
| `lite_all_formal_bytes` | 12359 |
| `lite_marker_files` | 1 |
| `lite_marker_bytes` | 38 |
| `lite_result_evidence_references` | 9 |
| `lite_safe_evidence_references` | 9 |

All 9 RESULT evidence references resolve to existing ordinary, non-symlinked files inside the current question's permitted directories: a **100% safe-resolution rate**.

## 5. Per-file audit

### Full temporary Q1 flow

| Formal object | Bytes |
|---|---:|
| `problem_definition.json` | 754 |
| `PROBLEM_DEFINITION.md` | 795 |
| `model_spec.json` | 1,564 |
| `START_Q1.md` | 1,799 |
| `result_record.json` | 1,893 |
| `RESULT_Q1.md` | 2,145 |

### Lite Q1 contexts

| Context view | Bytes |
|---|---:|
| Pre-Q2 time-aligned snapshot | 1,065 |
| Final root context | 1,467 |

### Lite Q1–Q3 ordinary formal fixture

| Formal object | Bytes |
|---|---:|
| `FROZEN_CONTEXT.md` | 1,467 |
| `START_Q1.md` | 1,874 |
| `RESULT_Q1.md` | 1,144 |
| `START_Q2.md` | 2,335 |
| `RESULT_Q2.md` | 1,582 |
| `START_Q3.md` | 2,182 |
| `RESULT_Q3.md` | 1,775 |

## 6. Interpretation limits

The comparison uses equivalent mathematical content but product-native representations, so it measures protocol overhead rather than identical prose. Byte count is only a reproducible proxy; it is not a direct token count or a claim about reasoning quality. The three-question Lite total is a fixture-size metric and is not compared with a one-question Full denominator.
