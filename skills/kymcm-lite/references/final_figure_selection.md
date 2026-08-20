# KyMCM Lite figure-selection hierarchy

## Authority and scope

This reference is the single authoritative Lite source for choosing **what** data-driven final figure to use and **when** to increase its information structure. Its identifier is KyMCM Lite `kymcm-figure-selection-v1`, and its byte-identical repository mirror is `docs/lite-v3/final_figure_selection.md`.

Apply it only to explicitly requested data-driven final-figure work after the existing final-figure entry gate has been satisfied. It does not select macro or algorithm flowcharts. Flowcharts use `kymcm-flowchart-selection-v1.md` followed by `kymcm-flowchart-content-v1.md`, and final layout and drawing remain human-owned.

This hierarchy is evidence-derived, not a chart-complexity ranking:

```text
basic chart --[real additional information need]--> enhanced chart
```

Visual complexity is not information value. Prefer the least complex expression that answers the actual question accurately.

## Decision levels

- **L0 — prose or table:** do not draw a chart when a short statement or small table communicates the required exact values more directly.
- **L1 — base chart:** use the lowest-complexity chart that correctly expresses the core conclusion.
- **L2 — enhanced chart:** upgrade only when a named trigger adds real, necessary, interpretable information or restores readability.
- **L3 — Figure Group:** organize multiple complementary, low-decoding-cost panels that jointly support one conclusion.

L3 is an information-organization level, not a chart type, workflow, state, manifest, or fixed panel quota.

## Upgrade rule

Upgrade if and only if the added effective information justifies the added reading and layout cost. This is a semantic judgment, not a numeric scorer.

An upgrade is justified when it adds a necessary comparison, model relationship, sample distribution, statistical uncertainty, density or spatial structure, substantively important continuous dimension, diagnostic evidence, or a readable separation of crowded content. Decoration, novelty, gradients, pseudo-depth, or an appearance of sophistication never justify an upgrade.

When a table or L1 chart remains more accurate and direct, retain it.

## Enhancement triggers

The only automatic v1 trigger vocabulary is:

```text
comparison
model_relation
distribution
uncertainty
density_or_spatial_structure
extra_continuous_dimension
diagnostic
crowding
```

- `comparison`: add same-scale comparison among multiple objects, methods, scenarios, or periods.
- `model_relation`: add a fitted line, theoretical curve, or model-predicted relationship.
- `distribution`: move from a representative value to the structure of a sample distribution.
- `uncertainty`: add a confidence interval, prediction interval, or meaningful stochastic variation.
- `density_or_spatial_structure`: reveal hotspots, local density, or continuous spatial structure.
- `extra_continuous_dimension`: show a second continuous explanatory variable whose joint response is substantively important.
- `diagnostic`: test model assumptions, residual behavior, or error structure.
- `crowding`: use facets or small multiples to restore readability without inventing a new variable.

Do not infer additional automatic triggers in v1.

## Intrinsic-3D execution gate

3D is an execution/expression route after semantic chart selection, not a ninth enhancement trigger. The PyVista route is allowed only when at least one condition is true:

- the data or scientific geometry itself lives in `x,y,z` space;
- a third continuous response dimension `z=f(x,y)` is substantively part of the conclusion;
- three-dimensional geometry, topology, or occlusion is itself evidence;
- a 3D feasible region or spatial surface cannot be represented without materially losing the required structure.

Reject 3D bars, pseudo-depth on ordinary category or trend charts, surfaces created only to look advanced, 3D for one-factor sensitivity, and 3D when a contour, aligned slices, heatmap, or small multiples communicates the same claim more accurately and directly. Backend availability never drives semantic selection. After an eligible information structure is selected:

```text
2D expression adequate                  -> Matplotlib + figure_exec.py
intrinsic 3D information genuinely required -> PyVista + figure_3d_exec.py
```

If PyVista/VTK is unavailable, fail closed; do not fall back to Matplotlib `mplot3d`.

## Core selection branches

### Trend and continuous change

Use this progression:

```text
few exact values                            -> L0 table
one object over a continuous variable       -> L1 single line
few same-scale objects                      -> L2 multi-line [comparison]
too many lines, long legends, or overlap    -> L2/L3 facets or small multiples [crowding]
two substantive continuous inputs z=f(x,y)  -> conditional L2 response surface or contour
                                                [extra_continuous_dimension]
```

A 3D surface is not a generally superior line chart. Use a response surface or contour only when two continuous inputs truly exist and the complete joint response is part of the argument. Prefer a 2D contour when height is not itself necessary; route a true intrinsic-3D response surface to PyVista only when height/depth materially carries the conclusion. If a few fixed slices answer the question, retain two-dimensional curves. Resolve crowded lines with small multiples before adding more colors or thinner lines.

Stop at the first level that answers the question without hiding material differences.

### Category and alternative comparison

Use this progression:

```text
few exact results                                  -> L0 table
ordinary category comparison                       -> L1 bar chart
explicit rank or order                             -> L2 sorted horizontal bar [comparison]
few methods/years within the same categories       -> L2 grouped bar [comparison]
sample batch behind every category, spread matters -> L2 boxplot [distribution]
```

The `bar -> boxplot` transition is valid only when the target changes from representative-value comparison to location, dispersion, quartiles, and outliers. A boxplot is not a stylistic upgrade to a bar chart.

Stop at a table or ordinary bar chart when distribution evidence is absent or irrelevant.

### Bivariate relation

Use this progression:

```text
raw relation between two variables             -> L1 scatter
fit, theory, or model relation must be tested   -> L2 scatter + fitted/theoretical/model curve
                                                   [model_relation]
few discrete categories                        -> L2 color + marker redundant encoding [comparison]
too many categories or difficult decoding      -> L2/L3 facets [crowding]
severe overlap and hotspot structure matters   -> L2 density or heat representation
                                                   [density_or_spatial_structure]
```

Important categories must not be distinguished by color alone; apply the redundant-encoding requirements of `final_figure_color.md`. Hexbin and joint KDE are possible density representations, not automatic upgrades for every scatter plot.

Stop at scatter when the raw relationship is the complete claim.

### Distribution

Use this progression:

```text
one sample; frequency, modes, or skew matter       -> L1 histogram
continuous density or shape comparison also matters -> L2 histogram + KDE, KDE, or faceted density
                                                       [distribution/comparison]
multiple sampled conditions; location and spread matter -> L2 boxplot [distribution/comparison]
```

KDE must represent actual sample information and use defensible smoothing. `violin`, `raincloud`, `ECDF`, and `ridgeline` do not enter the default v1 hierarchy.

Stop when the chosen view shows the distribution feature used by the conclusion; do not add redundant distribution layers for decoration.

### Matrix and higher-dimensional relation

Use this progression:

```text
exact values are primary                          -> L0 numeric table
high/low pattern, blocks, or correlation matters  -> L2 heatmap [density_or_spatial_structure]
small matrix; pattern and exact values both matter -> L2 annotated heatmap
same-variable, same-scale matrices must be compared -> L3 aligned heatmaps + shared colorbar
                                                      [comparison]
```

Comparable panels must use a shared scale and must not autoscale independently. Sequential and diverging maps, normalization, colorbar semantics, and missing-value treatment follow `final_figure_color.md`, including its `batlow` and `vik` rules.

Stop at a numeric table when color encoding would make exact lookup harder.

### Spatial data

Use this progression:

```text
only locations matter                              -> L1 map + points
categories or states across space matter           -> L2 categorized spatial scatter [comparison]
hotspots, density, or continuous intensity matters -> L2 heat/density map
                                                      [density_or_spatial_structure]
conditions, periods, or states must be compared    -> L3 same-basemap small multiples
                                                      [comparison/crowding]
continuous 2D density and meaningful height matter -> conditional L2 2D density or 3D density surface
                                                      [extra_continuous_dimension]
```

This branch chooses the expression level only. Ordinary 2D spatial expressions remain on their suitable 2D route; spatial geometry or topology that passes the intrinsic-3D gate routes to PyVista. It does not choose a mapping library or vector editor.

Stop at map + points when location is the only information required.

### Sensitivity and robustness

Use this progression:

```text
one parameter -> one metric                       -> L1 sensitivity line
one parameter -> few metrics                      -> L2 multi-line or aligned small panels [comparison]
separate one-factor changes for multiple parameters -> L3 shared-structure small multiples
                                                      [comparison/crowding]
two continuous parameters jointly affect the target -> conditional L2 response surface, contour,
                                                       or feasible-region view
                                                       [extra_continuous_dimension]
```

Separate one-factor perturbations do not justify forcing a high-dimensional 3D chart. For two continuous parameters, choose a contour, aligned slices, or heatmap unless height/depth is genuinely required; only then use a PyVista response surface.

Stop when the view reveals the sensitivity or robustness claim at the tested parameter dimensionality.

### Forecasting and uncertainty

Use this progression:

```text
historical trend                                  -> L1 observation line
history plus point forecast                       -> L2 observed + predicted line [model_relation]
forecast uncertainty affects the conclusion       -> L2 observed + predicted + confidence/prediction band
                                                     [uncertainty]
multiple forecast variables or scenarios          -> L3 aligned small multiples [comparison/crowding]
few forecasting methods                           -> L2 few prediction lines in one panel [comparison]
too many methods for one readable panel            -> L2/L3 method facets [crowding]
```

Every confidence or prediction band must have real statistical meaning under `final_figure_style.md`; never add one as decoration.

Stop at a point forecast when uncertainty is neither available nor part of the claim.

### Model fit and diagnostics

Use this progression:

```text
show that fitted and observed values are close     -> L1/L2 observed vs fitted [model_relation]
test assumptions or residual structure             -> L2 residual diagnostic [diagnostic]
test a residual normality assumption                -> conditional L2 Q-Q plot [diagnostic]
test heteroscedasticity or systematic bias          -> conditional L2 residual vs fitted [diagnostic]
```

A diagnostic chart is evidence for an assumption or error structure, not a prettier result chart. Use it only when that diagnostic question must be answered.

Stop after the smallest diagnostic set that addresses the named model risk.

## Figure Group rule

When one conclusion needs multiple complementary kinds of evidence, group simple or enhanced panels with low decoding cost instead of making one panel increasingly complex. A possible evidence sequence is:

```text
(a) source data or trend
(b) model relation or fit
(c) principal result
(d) validation, sensitivity, or robustness
```

This is an example, not a required four-panel template. Combine panels only when they jointly support one core conclusion. Canvas dimensions, grid choice, gaps, and panel markers remain governed by `final_figure_core_rules.md` and `final_figure_style.md`.

## Conditions that block automatic upgrade

- Keep prose or a table for a few exact values when it is more direct.
- Keep a single line when it answers the question; do not promote it to 3D.
- Keep an ordinary bar chart for a simple category comparison; do not mechanically replace it with a radar chart.
- Use no Sankey diagram without real flow semantics.
- Use no response surface without a real two-continuous-input response.
- Use no boxplot or violin plot without sample-distribution information.
- Add no confidence interval band without statistical uncertainty.
- Add no Q-Q or residual plot without a model-assumption or error-structure question.
- Do not make a chart a default merely because it appeared in an excellent prior submission.

```text
visual complexity != information value
```

## Pending and not-covered branches

The evidence base does not support automatic v1 selection rules for:

```text
violin plot
raincloud plot
ECDF
forest plot
Pareto front
PR curve
calibration curve
classification-evaluation hierarchy
ridgeline
```

The classification-evaluation entry includes the full ROC/PR/confusion/calibration decision hierarchy. A confusion matrix or ROC view may still be used when explicitly required, but it is not an automatic basic-to-enhanced branch in v1. Any pending chart may be discussed or drawn when the user explicitly requests it. Promote a pending branch only through a future evidence review and a new identifier such as `kymcm-figure-selection-v2`.

## Authority boundaries and order

Apply final-figure authorities in this order for a data-driven figure:

1. `final_figure_selection.md` decides **WHAT / WHEN**: L0–L3, chart family, enhancement trigger, and grouping need.
2. `final_figure_core_rules.md` applies core in-figure boundaries and routes separate flowchart requests.
3. For ordinary 2D expression, `final_figure_style.md` and `final_figure_execution.md` decide Matplotlib HOW and execution.
4. For intrinsic-3D expression, `final_figure_3d.md` and `figure_3d_exec.py` decide scene, camera, lighting, depth, and execution without inheriting 2D axes geometry.
5. `final_figure_color.md` decides qualitative, semantic, continuous-map, missing-value, and accessibility color behavior where applicable.
6. `final_figure_typography.md` decides Matplotlib font families and missing-font behavior; `final_figure_3d.md` states the honest VTK-native text limit.

Selection cannot override a visual hard constraint in the other four authorities. Style, color, and typography cannot select a chart because it looks more sophisticated. Complete selection before applying rendering details.

## Machine-oriented normative summary

This is a documentation-level summary for future reasoning. It is not JSON, a runtime configuration, a contract, or a manifest.

```text
FIGURE_SELECTION_V1
identifier = kymcm-figure-selection-v1
levels = [L0, L1, L2, L3]
upgrade_triggers = [comparison, model_relation, distribution, uncertainty,
                    density_or_spatial_structure, extra_continuous_dimension,
                    diagnostic, crowding]
branches = [trend, category_comparison, bivariate_relation, distribution,
            matrix, spatial, sensitivity, forecasting, diagnostics]
execution_route = matplotlib_2d | pyvista_intrinsic_3d
intrinsic_3d_is_not_an_upgrade_trigger = true

trend:
  base_choice = table | single_line
  enhancement_trigger = comparison | crowding | extra_continuous_dimension
  enhanced_choice = multi_line | small_multiples | conditional_surface_or_contour
  stop_condition = lowest level answers the continuous-change question

category_comparison:
  base_choice = table | bar
  enhancement_trigger = comparison | distribution
  enhanced_choice = sorted_horizontal_bar | grouped_bar | boxplot
  stop_condition = distribution evidence is required before boxplot

bivariate_relation:
  base_choice = scatter
  enhancement_trigger = model_relation | comparison | crowding | density_or_spatial_structure
  enhanced_choice = relation_overlay | redundant_category_encoding | facets | density_representation
  stop_condition = raw scatter already expresses the complete relation

distribution:
  base_choice = histogram
  enhancement_trigger = distribution | comparison
  enhanced_choice = histogram_plus_KDE | KDE_or_faceted_density | boxplot
  stop_condition = added layer answers a named distribution question

matrix:
  base_choice = numeric_table
  enhancement_trigger = density_or_spatial_structure | comparison
  enhanced_choice = heatmap | annotated_heatmap | shared_scale_heatmap_group
  stop_condition = exact lookup remains primary

spatial:
  base_choice = map_plus_points
  enhancement_trigger = comparison | density_or_spatial_structure | crowding | extra_continuous_dimension
  enhanced_choice = categorized_scatter | density_map | same_basemap_small_multiples | conditional_density_surface
  stop_condition = location alone answers the question

sensitivity:
  base_choice = sensitivity_line
  enhancement_trigger = comparison | crowding | extra_continuous_dimension
  enhanced_choice = multi_line | small_multiples | conditional_response_or_feasible_region
  stop_condition = tested parameter dimensionality is represented directly

forecasting:
  base_choice = observation_line
  enhancement_trigger = model_relation | uncertainty | comparison | crowding
  enhanced_choice = prediction_line | interval_band | small_multiples_or_facets
  stop_condition = no unsupported uncertainty or excess method overlay

diagnostics:
  base_choice = observed_vs_fitted
  enhancement_trigger = diagnostic
  enhanced_choice = residual_diagnostic | conditional_QQ | conditional_residual_vs_fitted
  stop_condition = smallest set resolves the named assumption or error risk
```

Selection-v1 itself adds no plotting runtime, chart-template API, automatic visual checker, Figure contract, manifest, workflow state, content JSON, CLI, special-chart tool route, or final-figure workflow. The separate optional execution-v1 layer implements only accepted HOW constants and does not change this WHAT/WHEN authority.
