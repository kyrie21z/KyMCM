# Chart Selection

Choose the simplest chart that directly tests the Figure Brief claim.

| Claim purpose | Default template | Required relationship |
|---|---|---|
| Ordered or temporal trend with uncertainty | `line_with_band` | ordered x, numeric y, optional lower/upper bounds |
| Compare several alternatives on common metrics | `grouped_bar_error` | categorical x, numeric y, optional group/error |
| Compare predictions with observations | `actual_vs_predicted` | paired actual and predicted values |
| Diagnose model errors | `residual_diagnostics` | paired predicted and residual, or actual and predicted |
| Inspect variable association | `correlation_heatmap` | at least two numeric variables |
| Test parameter robustness | `sensitivity_curve` | ordered parameter, numeric response, optional scenario |

Rules:

- Do not connect unordered categories with a line.
- Do not use a pie chart unless values form a meaningful whole.
- Show an interval or error when uncertainty is available.
- Use 3D only when the third dimension has irreducible spatial meaning.
- Do not use radar charts for precise high-dimensional comparison.
- Do not choose an advanced chart for decoration.
- When categories exceed the catalog limit, aggregate or select evidence-relevant categories before rendering.

`select_template(brief, data_profile)` returns a catalog template. An explicit supported `chart_family` wins. An `auto` brief uses profile hints such as `purpose`, `has_uncertainty`, and `numeric_columns`. An override must set `selection_reason` in the brief so the manifest preserves the decision.
