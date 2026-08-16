# KyMCM Lite flowchart content specification

Identifier: `kymcm-flowchart-content-v1`

## Authority and evidence

This is KyMCM Lite's evidence-derived **HOW MUCH INFORMATION** authority downstream of `kymcm-flowchart-selection-v1`. Its byte-identical repository mirror is `docs/lite-v3/kymcm-flowchart-content-v1.md`. It governs semantic node roles, node count, node-text density, line count, and overload restructuring. Its authority ends before final geometry and drawing.

The fixed census contains 73 strict flowcharts, 747 ordinary flow nodes, and 18 container titles counted separately. Text was reliably measurable for 726 ordinary nodes; 21 unlabeled or unreliably legible ordinary nodes are excluded from text-length distributions. Figure-level confidence is high 58 / medium 13 / low 2.

```text
node_count_total
= process + decision + terminal + io + subprocess + other_node
```

Container titles are separate from `node_count_total`.

## Evidence interpretation

- **Typical Range = Q1–Q3**, not a hard allowed interval.
- `N > type_Q3` is a node-count review trigger, not failure.
- Role text longer than Q3 triggers long-node/content review.
- Role text longer than P90 is a long-tail node when the evidence is sufficient.
- Strong Overload requires both structural-capacity pressure and text-density pressure.
- There is **no universal Hard Max** in v1.

A5 and A6 have low evidence. Their sparse or high-density observations are descriptive only and must not become automatic recommended targets or hard limits.

## Content principles

1. Use minimum sufficient information: a node contains only what is needed to understand process semantics.
2. One ordinary node expresses one principal action, state, or condition.
3. Explanatory prose belongs in the paper body when removing it does not alter process semantics.
4. Exchange complexity budgets: more nodes generally requires shorter node text; fewer nodes can tolerate somewhat longer text.
5. Compress text and content before layout. Never solve content overload by shrinking fonts, padding, or spacing.
6. Ordinary nodes prefer 1–2 text lines. Repeated ordinary nodes with at least 3 lines trigger density review; they are not automatically invalid.

Measured ordinary-node lines are approximately 1 line 63.5%, 2 lines 24.7%, and at least 3 lines 11.8%; median = 1 line and Q3 = 2 lines.

## Cross-type role fallbacks

- Macro process text is generally short, but a supported M-type profile takes priority over the pooled fallback.
- Core Algorithm A2–A4 process text is approximately 5–12 visible characters with a center around 8.
- Core Algorithm A2–A4 decision text is approximately 6–10 visible characters, with P90 about 13. A decision is a short condition, not a paragraph.
- Terminals are very short, typically “开始” or “结束”. A terminal carrying extensive output semantics should be reconsidered.
- Container-title guidance derives from the 18 observed titles; it is not an intuition-based fixed tiny range.

## Type-specific evidence profiles

Exact quartiles remain visible; rounded bands are only explanatory approximations.

| Type | Figures | Node Q1 / median / Q3 / P90 / max | Process n; Q1 / median / Q3 / P90 | Decision n; Q1 / median / Q3 / P90 | >=3 lines |
|---|---:|---|---|---|---:|
| M1 | 7 | 5 / 6 / 7.5 / 10.4 / 14 | 37; 4 / 6 / 8 / 16.4 | — | 2.1% |
| M2 | 11 | 6 / 7 / 8 / 10 / 10 | 62; 5 / 8 / 11.75 / 19 | — | 23.5% |
| M3 | 6 | 10.25 / 11.5 / 14.25 / 16.5 / 18 | 55; 3 / 4 / 6 / 8 | — | 0% |
| M4 | 8 | 12 / 14 / 19 / 22.3 / 30 | 100; 2 / 3 / 6 / 15 | 4; 14 / 16.5 / 22.25 / 28.1 (insufficient for a stable type-specific decision rule) | 4.8% |
| M5 | 4 | 9.5 / 10.5 / 11 / 11 / 11 | 29; 4 / 6 / 11 / 14.2 | — | 0% |
| M6 | 4 | 5.25 / 7.5 / 10 / 11.8 / 13 | 29; 4 / 6 / 16 / 24.4 | — | 6.5% |
| A1 | 6 | 5 / 5.5 / 6.75 / 8 / 9 | 28; 10.75 / 12.5 / 18.25 / 21.9 | — | 2.7% |
| A2 | 10 | 7 / 7.5 / 9 / 10 / 10 | 52; 5 / 7 / 12 / 18.9 | 15; 7 / 7 / 10.5 / 12.2 | 10.1% |
| A3 | 9 | 11 / 12 / 13 / 15 / 15 | 56; 3 / 8.5 / 13.5 / 24.5 | 26; 7 / 8 / 10 / 14 | 5.5% |
| A4 | 4 | 8.5 / 9.5 / 11.75 / 14.9 / 17 | 23; 7.5 / 9 / 11 / 12.8 | 9; 4 / 6 / 8 / 12.8 | 2.3% |
| A5 | 1 — LOW EVIDENCE, descriptive only | 19 / 19 / 19 / 19 / 19 | 11; 7 / 8 / 11.5 / 31 | 6; 6.25 / 7.5 / 11 / 17.5 | 0% |
| A6 | 3 — LOW EVIDENCE, descriptive only | 18.5 / 20 / 22 / 23.2 / 24 | 37; 17 / 24 / 31 / 40.8 | 21; 11 / 11 / 20 / 20 | 75.4% |

## Evidence-aware overload policy

```text
node-count-review:
  N > type_Q3

process-density-review:
  median_process_text > type_process_Q3   (when supported)

decision-density-review:
  median_decision_text > applicable_decision_Q3  (when supported)

multiline-density-review:
  repeated ordinary nodes with >=3 lines

strong-overload:
  node-count-review
  AND
  (process-density-review OR decision-density-review)
```

Strong Overload triggers semantic restructuring review, not automatic failure.

## Restructuring order

1. Remove explanatory prose or return it to body text.
2. Compress labels to short noun, verb–object, or condition phrases.
3. When one node contains multiple real sequential actions, split it into real nodes.
4. When several nodes form a meaningful named local process, extract a `subprocess` and optionally a local subflow.
5. When true stage boundaries exist, return to selection review for M4. Never invent stage groups merely to fit the page.
6. When overload exposes omitted structural semantics, return to selection-v1; for example M2→M3, A2→A3, or A3/A4→A6 only when genuinely required.
7. If the type remains correct and all semantics are necessary, use an overview plus a local subflow.
8. Only after the content audit passes does the human handle final layout and drawing.

A stage requires a real functional or semantic boundary. A subprocess requires a real encapsulatable process, not a hiding mechanism. Splitting into two diagrams requires Strong Overload or an independently meaningful local subflow, not arbitrary page cutting.

## Human-owned layout boundary

This specification may output the node list, roles, labels, directed connections and branch meanings, semantic groupings, stage or subprocess semantics, content-budget status, and overload actions. It must stop before orientation, coordinates, node dimensions, lane positions, edge bends, font size, visual style, or renderer parameters. Final spatial layout and manual drawing are owned by the user/human author.
