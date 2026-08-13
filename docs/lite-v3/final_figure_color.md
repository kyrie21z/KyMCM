# KyMCM Lite `kymcm-figure-color-v1`

## Authority and scope

This is the frozen Lite color contract for Codex/Matplotlib data-driven final figures. Its byte-identical repository mirror is `docs/lite-v3/final_figure_color.md`. It depends on `final_figure_core_rules.md` and `final_figure_style.md`; `final_figure_typography.md` remains the independent font-family authority.

Use one stable palette across competitions. Priority is semantic correctness, cross-figure consistency, readability and reproducibility, visual attractiveness, then local customization. Color has fixed semantics. Keep qualitative, sequential, diverging, and semantic systems separate. Important comparisons always have redundant encoding through line style, marker, hatch, position, or facets.

Pt3 remains the normative color authority. The optional `figure_exec.py` exposes the frozen palette and semantic-color helpers for formal Codex/Matplotlib figures; local plotting code does not redeclare an ad-hoc palette. This parameterized executor adds no chart template, chart selection, command, manifest, or workflow state.

## Qualitative sequence

The frozen sequence contains at most seven equal-status categories in stable category order:

1. `#264653` — deep teal anchor;
2. `#E76F51` — coral/orange main warm comparison;
3. `#2A9D8F` — teal-green;
4. `#7A77B9` — soft purple;
5. `#8AB17D` — sage green;
6. `#E9C46A` — soft gold;
7. `#F4A261` — warm orange.

```text
KY_MCM_QUALITATIVE_V1 = ("#264653","#E76F51","#2A9D8F","#7A77B9","#8AB17D","#E9C46A","#F4A261")
```

In semantic-emphasis mode, use `#264653` for the primary object, `#E76F51` for the main comparison, and `#7A7A7A` plus line/marker variation for other baselines. In equal-status mode, use the frozen sequence. The first four are the priority core colors.

Above seven qualitative categories, merge noncritical categories, use facets/small multiples, neutralize minor categories, add line/marker/hatch structure, or move minor results to a table. Do not invent extra colors. `#E9C46A` and `#F4A261` are not used for figure text, thin threshold/reference lines, or as the sole encoding for a key object. A line using them also needs a marker or line style; they are better suited to bars, fills, large markers, and area elements.

## Semantic and neutral colors

| Role | Frozen encoding |
| --- | --- |
| primary/formal solution | `#264653` |
| main comparison | `#E76F51` |
| baseline/secondary | `#7A7A7A` |
| risk/anomaly/warning | `#A61B29` |
| infeasible | `#303030` plus hatch `///` or equivalent structural encoding |
| missing/unavailable | `#D9D9D9` |
| background | `#FFFFFF` |
| uncertainty | same color as main line, alpha 0.14–0.18, default 0.16 |

Comparison coral `#E76F51` and risk red `#A61B29` have different meanings. Risk red never enters the ordinary category cycle. Missing values are explicitly masked and are never zero or the low end of a continuous map.

The neutral skeleton is text `#303030`, spine `#303030`, reference `#7A7A7A`, and grid `#D9D9D9` at alpha 0.65. Axes, labels, and legend text use neutral dark colors; category colors do not decorate axes or text.

## Continuous maps

Use **batlow** for a monotonic continuous quantity such as intensity, density, probability, frequency, loss, or magnitude. Show a colorbar. Comparable panels for the same variable share `vmin`, `vmax`, and direction. Mask missing values to `#D9D9D9`. Use the original direction by default; use `batlow_r` only for an explicit semantic or domain reason and then consistently for that variable.

Obtain batlow through the bounded `cmcrameri` dependency used by `figure_exec.py`. Missing `cmcrameri` or a missing named map stops formal rendering; never silently fall back to viridis, jet, or another map.

Use **vik** only when a real center exists, such as zero, a baseline, a target, or a mean/median. Do not use a diverging map for one-way cost, probability, intensity, category codes, or an arbitrary aesthetic center. Center and symmetrize by default:

```text
limit = max(abs(vmin - center), abs(vmax - center))
vmin = center - limit
vmax = center + limit
normalization = TwoSlopeNorm(vcenter=center, vmin=vmin, vmax=vmax)
```

Use a nonsymmetric range only when the physical range is genuinely asymmetric and symmetry would severely lose useful resolution; record the reason. Comparable panels share center, `vmin`, `vmax`, direction, and colorbar.

## Chart-specific use

- **Line:** use the primary/comparison/baseline semantic map or the equal-status sequence with redundant markers/line styles. Keep at most seven main curves. Gold and warm orange are not the sole key thin-line encoding. Risk thresholds use `#A61B29`.
- **Bar/horizontal bar:** use qualitative or semantic colors. Risk uses `#A61B29`, infeasible uses `#303030` plus hatch, and missing uses `#D9D9D9`. Use no gradient, 3D, shadow, or risk red as an ordinary category.
- **Scatter:** discrete categories use the qualitative sequence; density uses batlow; anomalies use risk red plus a distinct marker; infeasible uses dark plus structural encoding. A key class is not color-only. High-density data moves to density/hexbin when required.
- **Box/violin:** equal groups use the qualitative sequence while edges, median, and whiskers remain neutral dark. Statistical boxplot fliers inherit their group by default; only business-risk anomalies use risk red.
- **Forest/interval/error bar:** primary, comparison, and other objects use semantic or qualitative colors; reference uses `#7A7A7A`; risks or violations use `#A61B29`; each estimate and its interval use the same color.
- **Heatmap/matrix:** monotone values use batlow, centered positive/negative values use vik, and a discrete category matrix uses the qualitative sequence. Missing values use `#D9D9D9`. Jet, rainbow, meaningless red-green gradients, and independent auto-scaling across comparable panels are prohibited.
- **Stacked/composition:** preserve category order and color across bars, panels, and figures; keep at most seven components. Risk, missing, and infeasible colors stay outside the ordinary stack sequence. A naturally ordered composition may use discretized batlow.
- **Uncertainty/background:** uncertainty uses the main line's color at default alpha 0.16. An ordinary background interval uses low-alpha baseline gray. Risk background uses low-alpha risk red only with real risk semantics.

## Cross-figure consistency and accessibility

The same object keeps the same color across panels, figure groups, and chapters. Legend order remains stable and argument-driven. Repeated objects share a legend; repeated views of one continuous variable share its scale and colorbar. Formal scripts do not define local ad-hoc palettes.

For every formal figure with at least three colors, inspect normal, grayscale, and approximate protan, deutan, and tritan views. Important objects must remain distinguishable through redundant encoding: primary and comparison do not collapse, risk does not collapse into an ordinary category, key curves remain visible on white, and missing does not resemble a low numeric value. CIEDE2000 and contrast measures are diagnostics rather than context-free pass thresholds. Okabe–Ito is an accessibility reference baseline, not KyMCM visual identity, and is not mixed into the final palette.

## Normative parameter summary and execution helpers

`KY_MCM_FIGURE_COLOR_V1` records:

```text
qualitative=("#264653","#E76F51","#2A9D8F","#7A77B9","#8AB17D","#E9C46A","#F4A261")
semantic.primary="#264653"
semantic.comparison="#E76F51"
semantic.baseline="#7A7A7A"
semantic.risk="#A61B29"
semantic.infeasible="#303030"
semantic.missing="#D9D9D9"
semantic.background="#FFFFFF"
neutral.text="#303030"
neutral.spine="#303030"
neutral.reference="#7A7A7A"
neutral.grid="#D9D9D9"
neutral.grid_alpha=0.65
continuous.sequential="batlow"
continuous.sequential_reversed="batlow_r"
continuous.diverging="vik"
uncertainty.default=0.16
uncertainty.min=0.14
uncertainty.max=0.18
max_qualitative_categories=7
priority_core_colors=4
infeasible_hatch="///"
```

`figure_exec.py` exposes the corresponding small interfaces, including `qualitative_colors(n)`, `semantic_color(role)`, `continuous_cmap(kind)`, and `diverging_norm(...)`. They mirror this authority and do not choose a chart family or color semantics.

## Acceptance checklist

Before accepting a formal data-driven figure, verify:

1. Every color comes from `kymcm-figure-color-v1`.
2. Semantic roles are correct.
3. Risk red stays outside the normal category cycle.
4. Missing values are not mapped as zero.
5. Important line and scatter distinctions use redundant encoding.
6. The same object keeps the same color.
7. Same-variable continuous panels share a range.
8. Sequential data uses batlow.
9. Vik is used only with a real center.
10. No jet, rainbow, or ad-hoc palette appears.
11. Key objects remain identifiable in degraded views.
12. Legend and colorbar order/direction stay stable.
13. No local override silently changes the system.
14. PDF and PNG use the same colors and layout.
