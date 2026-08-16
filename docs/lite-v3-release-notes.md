# KyMCM Lite 0.9.11

KyMCM Lite 0.9.11 adds two evidence-derived flowchart authorities. `kymcm-flowchart-selection-v1` uses the fixed corpus of 73 strict CUMCM main-evidence flowcharts (Macro 40, Algorithm 33) to qualify flowchart use, split Macro from Algorithm, and select one minimum-sufficient-complexity type from M1–M6 or A1–A6. `kymcm-flowchart-content-v1` uses 747 ordinary nodes, including 726 reliably measurable text nodes, to review node roles, node counts, text density, line count, and overload restructuring.

The authority split is deliberate: selection-v1 decides WHAT/WHEN; content-v1 decides HOW MUCH INFORMATION. Typical Range means Q1–Q3 rather than a hard allowed interval, and the content specification has no universal Hard Max. Strong Overload requires node-count pressure plus supported process or decision text-density pressure, and it triggers semantic restructuring review rather than automatic failure. Sparse A5/A6 evidence remains descriptive only.

The old fixed 4×3 macro template and default two-row serpentine algorithm layout are retired. The corpus does not support algorithm serpentine as a default. Both specifications stop before orientation, coordinates, geometry, routing, styling, or renderer parameters: final layout judgment and manual drawing are explicitly owned by the user/human author. This release adds no flowchart layout/style/execution specification, renderer, Graphviz/Mermaid/TikZ route, diagram runtime, dependency, CLI, checker, state, or manifest.

The data-driven figure system remains separate and unchanged: `kymcm-figure-selection-v1`, Pt1/Pt2/Pt3/Typography, and `kymcm-figure-exec-v1` continue to govern formal Matplotlib work, and `nature-figure` retains its 0.9.10 optional read-only advisory boundary. The Lite v3 marker and eight commands are unchanged, 0.9.10 and earlier contest workspaces need no migration, and KyMCM Full remains unchanged.

# KyMCM Lite 0.9.10

KyMCM Lite 0.9.10 removes the dual-authority ambiguity from the normal formal Matplotlib pipeline. `kymcm-figure-selection-v1` remains the WHAT/WHEN authority; Pt1/Pt2/Pt3/Typography remain the normative visual contract; `kymcm-figure-exec-v1` remains the sole normal formal rendering and hard-audit executor; Codex implements the selected figure; ChatGPT/user owns semantic and visual acceptance. Passing `figure_exec.py` remains necessary but is not final acceptance.

Ordinary formal figures no longer depend on or automatically invoke `nature-figure`. The separately installed specialist may participate only when the user explicitly requests a read-only advisory second opinion on an already-rendered PDF/PNG. It cannot choose or reclassify the chart, apply its own contract/theme/rcParams/palette/font/canvas/export defaults, rerender, restyle, export, overwrite, replace the KyMCM artifact, or become the final authority. Suggestions return to Codex, are implemented through KyMCM code and `figure_exec.py`, pass the hard audit again, and return to ChatGPT/user review.

The compatible `font_kwargs(role, script=...)` interface now declares `latin` as Tinos, `cjk` as Noto Serif CJK SC, and `mixed` as both. The hard audit strips `$...$` fragments for ordinary-text classification and checks declared Matplotlib `Text` families against visible script classes while preserving STIX mathtext. This closes the normal typography ownership gap without claiming exact physical per-glyph font-file forensics. Required fonts and controlled `cmcrameri` remain fail-closed; accepted Pt2/Pt3 values are unchanged.

The Lite core CLI remains exactly eight commands and standard-library-only. This release adds no state, manifest, content JSON, CLI, chart-template library, automatic chart selection, or special-tool routing system. Existing 0.9.9 workspaces require no migration, and KyMCM Full remains unchanged.

# KyMCM Lite 0.9.9

KyMCM Lite 0.9.9 retains `kymcm-figure-selection-v1` unchanged in purpose for WHAT/WHEN reasoning and adds `kymcm-figure-exec-v1` for exact HOW constants. The optional `skills/kymcm-lite/figure_exec.py` centralizes accepted canvas, typography, line/tick/grid, marker, bar, box, error-bar, palette, continuous-map, and output parameters so formal Codex/Matplotlib figures no longer depend on manually retyping them.

The helper fails closed on its machine-safe subset: strict local `Noto Serif CJK SC` and `Tinos` availability, STIX mathtext base configuration, titles, text below 8 pt, unstyled applicable axes, ordinary lines above 2 pt, unknown common artist colors, uncontrolled continuous maps, exact physical geometry, and same-layout PDF plus 600 dpi PNG saving. `batlow` and `vik` come only from bounded `cmcrameri`; there is no color-map or font fallback. Accepted Pt2/Pt3 numeric and color values remain unchanged, and the typography contract remains exactly Noto Serif CJK SC / Tinos / STIX.

The hard audit does not decide whether English or prose is necessary, whether a semantic role or confidence band is conceptually correct, whether a chart family is appropriate, or whether complex mixed Chinese/Latin glyph routing and the whole composition are visually sound. Those remain `nature-figure` plus ChatGPT/user review responsibilities. The Lite core CLI remains exactly eight commands and standard-library-only; optional figure execution adds no managed state, manifest, content JSON, CLI, automatic chart selection, or tool-routing workflow. Existing 0.9.8 workspaces require no migration, and the historical 0.9.8 entry below remains the merged-main baseline.

## KyMCM Lite 0.9.8

KyMCM Lite 0.9.8 adds the evidence-derived `kymcm-figure-selection-v1` canonical reference and byte-identical `docs/lite-v3/` mirror. It freezes L0 prose/table, L1 lowest-complexity base chart, L2 evidence-triggered enhancement, and L3 coherent Figure Group organization. Enhancement is permitted only for `comparison`, `model_relation`, `distribution`, `uncertainty`, `density_or_spatial_structure`, `extra_continuous_dimension`, `diagnostic`, or `crowding`; visual complexity alone is never an upgrade criterion.

The hierarchy covers nine core branches: trend, category comparison, bivariate relation, distribution, matrix, spatial data, sensitivity, forecasting, and diagnostics. Violin, raincloud, ECDF, forest, Pareto, PR, calibration, full classification-evaluation, and ridgeline branches remain explicitly pending rather than being inferred from general visualization knowledge. Data-driven final-figure work now chooses WHAT/WHEN through selection. Pt1 core receives only the required selection cross-reference and review/spatial-boundary update; Pt2 style, Pt3 color, and typography remain byte-unchanged from 0.9.7.

This release adds no plotting runtime, chart-template library, shared style/color module, runtime dependency, checker, CLI, contract, manifest, state, content JSON, special-chart tool route, or final-figure workflow. The Lite v3 marker, exact eight commands, optional non-managed `figure/`, RESULT/HANDOFF/PRE/Supplement/Appendix gates, fixed AI-use package, standard-library runtime, and KyMCM Full remain unchanged. Pt1 semantics are preserved with the minimal integration update described above; the 0.9.7 Pt2 style, Pt3 color, and typography contracts remain byte-unchanged. Existing 0.9.7 workspaces require no migration.

## KyMCM Lite 0.9.7

KyMCM Lite 0.9.7 integrates the frozen Pt1 core figure rules, Pt2 `kymcm-figure-style-v1`, and Pt3 `kymcm-figure-color-v1` as canonical Lite references with byte-identical `docs/lite-v3/` mirrors. Final-figure instructions and reviews now load the core rules; Codex/Matplotlib data-driven figures and general figure specifications/reviews also load the style, color, and independent typography authorities before invoking external `nature-figure`.

The frozen documentation defines PDF/PNG-only formal output, no internal figure title or explanatory prose, final physical-size templates, ≥8 pt text, geometry and layout rules, semantic/qualitative colors, batlow and vik continuous maps, redundant accessibility encoding, and the existing exact `Noto Serif CJK SC` / `Tinos` / `STIX mathtext` routing. The earlier typography reference's SVG audit language is replaced by the accepted PDF/PNG contract. The complete ChatGPT Project Source, mirror classification, release tree, and protected hashes are refreshed accordingly.

This is a documentation and integration release. It adds no plotting runtime, chart-template library, color/style Python module, `cmcrameri` dependency, visual checker, CLI, contract, manifest, state, content JSON, or tool-routing workflow. The basic/enhanced chart hierarchy, special-chart/tool routing, and final-figure workflow remain paused. Existing 0.9.6 workspaces require no migration; the Lite v3 marker, eight commands, RESULT/HANDOFF/PRE/Supplement/Appendix semantics, fixed AI-use package, standard-library runtime, and KyMCM Full remain unchanged.

## KyMCM Lite 0.9.6

KyMCM Lite 0.9.6 adds a fixed final-submission AI-tool disclosure package for the 2026 trial regulation. The canonical `AI_TOOL_USAGE_DETAILS.template.tex` has exactly five sections, a two-column table fixed to ChatGPT/GPT-5.6 Thinking and Codex CLI/GPT-5.6 Codex, two fixed real-screenshot paths/captions, conservative adoption/review and overall declaration prose, and fail-closed missing-image checks. The only competition-time content replacements are the two real screenshots; XeLaTeX writes the exact `AI 工具使用详情.pdf` output. `AI_TOOL_USAGE_DECLARATION.template.tex` is a fixed non-numbered snippet for placement before paper references.

This is a final-submission documentation/template release. Using KyMCM Lite is AI-tool usage, but the material is outside RESULT, Supplement, HANDOFF, Appendix, evidence, modeling dependencies, and final-figure work. Lite adds no command, checker, diagnostic, state, JSON, manifest, approval, runtime PDF generation, screenshot/chat-log reader, or automatic inference from RESULT/HANDOFF. XeLaTeX/TeX Live is optional and not a Lite runtime dependency; no fonts, screenshots, PDFs, or LaTeX intermediates enter the repository. Existing 0.9.5 workspaces need no migration, and Full and all existing modeling workflow behavior remain unchanged.

## KyMCM Lite 0.9.5

KyMCM Lite 0.9.5 refocuses optional submission-appendix curation on an auditable computation core. `appendix/problems/*/code/` and direct root `code/` targets retain input/feature construction, model and optimization logic, statistics, prediction, constraints, validation, and audit paths, while result tables, interface/report prose, export writers, caches, checkpoints, temporary files, databases, and model persistence remain outside the code surface. Formal result assets are independent COPY/CURATE targets and are never regenerated by the checker or by submitted code.

`check-appendix-result` adds the high-confidence static Error `LITE-APPENDIX-CODE-SIDE-EFFECT-001` for Python and C/C++ file/directory writers and persistence APIs, and code-target suffix rules reject common runtime data (`.joblib`, `.npy`, `.npz`, `.pickle`, `.pkl`, `.sav`, `.ckpt`, `.pt`, `.pth`). Read-only opens and in-memory assembly remain allowed; dynamic wrappers, indirect writes, and semantic equivalence remain human-review limits. The Lite v3 marker, eight commands, frozen Appendix headings, standard-library runtime, existing 0.9.4 workspaces, final-figure typography, and KyMCM Full remain unchanged.

This is a computation-core curation and static-audit release. It adds no workspace migration, state, JSON, manifest, approval object, command, result regeneration, or automatic rewrite.

## KyMCM Lite 0.9.4

KyMCM Lite 0.9.4 freezes one Lite-only typography contract for explicitly requested final display figures. After the relevant RESULT and Supplement Result entries are accepted and any requested HANDOFF task is complete, Lite reads `skills/kymcm-lite/references/final_figure_typography.md` and passes its exact requirements to the external `nature-figure` Skill:

```text
Chinese/CJK punctuation  -> Noto Serif CJK SC
English/Arabic numerals  -> Tinos
Formulas and symbols     -> STIX mathtext
Matplotlib setting        -> mathtext.fontset = stix
```

`nature-figure` discovers fonts, renders, and audits actual output. If any required font is unavailable, formal rendering stops and reports the missing item; silent fallback, approximate-font substitution, font downloads, font copying, and font binaries in the repository are forbidden. A user-requested preview must be marked non-final and report any fallback. Lite does not render, import, vendor, or runtime-depend on `nature-figure`, and it adds no figure command, checker, state, JSON, manifest, or approval file.

The contract covers semantic routing of mixed Chinese, English, numeric, punctuation, and mathtext content and a minimum external audit for PNG/PDF/SVG output. The byte-identical reference mirror is included in the generated complete Project Source. Existing 0.9.3 workspaces need no migration; historical figures are not redrawn or retroactively declared compliant. KyMCM Full's built-in renderer and Microsoft YaHei/CJK sans-serif behavior remain unchanged.

This is a documentation and external-figure-contract release. The Lite v3 marker, eight commands, frozen templates, RESULT acceptance/HANDOFF timing, Supplement/PRE behavior, standard-library runtime, and Full boundary remain unchanged.

## KyMCM Lite 0.9.3

KyMCM Lite 0.9.3 gates every technical HANDOFF on explicit post-execution acceptance of the corresponding RESULT by the user or responsible ChatGPT. Codex executes through RESULT/RESULT_PRE plus the applicable machine check, then stops and reports that semantic acceptance is pending; `check-result`, tests, CI, commits, or stable evidence do not authorize HANDOFF.

Only a new independent HANDOFF task after acceptance may create or refresh `HANDOFF_QN.md` or `HANDOFF_PRE.md`, and that task is read-only: it does not run new computation or modify code, data, START, RESULT, or Supplement contracts. A pending Supplement Result or RESULT_PRE leaves the existing HANDOFF snapshot unchanged; acceptance adopts the Result, while HANDOFF refresh is no longer the adoption trigger. The marker, eight commands, frozen contract headings, stateless runtime, Full, and 0.9.2 workspace compatibility remain unchanged.

This is a documentation and semantic-review release. It adds no approval file, state machine, JSON, manifest, checker, command, or runtime acceptance state. Python cannot enforce the human gate; the complete Project Source export is regenerated and checked.

## KyMCM Lite 0.9.2

KyMCM Lite 0.9.2 changes the semantic lifecycle of the optional question-level Supplement pair while keeping the Lite v3 runtime surface unchanged. The latest numbered Sx is editable and rerunnable in place only while it has not been adopted, has no later Sy, and has no downstream or formal-delivery use. A material Start change first removes or invalidates its same-number Result; the revised execution then writes a replacement Result and refreshes HANDOFF.

Adopted Sx entries remain frozen and append-only. Adoption may be established by explicit user acceptance, completed downstream use, a later Sy inheritance baseline, formal submission/appendix delivery, or a change that would invalidate completed downstream or certification boundaries. Refreshing HANDOFF, committing, or ordinary local execution alone does not adopt Sx. Base START/RESULT, adopted history, and non-latest Sx artifacts remain protected; only the latest unadopted Sx may rebuild its own `sN_` artifacts.

This is a documentation and semantic-review release. It does not add a checker, command, state, JSON, manifest, approval, dependency token, PRE Supplement, or runtime adoption decision. Existing 0.9.0 and 0.9.1 workspaces require no migration. The marker, eight commands, base/PRE/HANDOFF/Appendix/Figure contracts, Full, and generated complete Project Source boundary remain unchanged except for the updated normative text.

## KyMCM Lite 0.9.1

KyMCM Lite 0.9.1 adds a deterministic complete single-file specification export for ChatGPT Project Sources at `docs/lite-v3/KyMCM_Lite_FULL_SPEC.md`, generated by `scripts/export_kymcm_lite_full_spec.py`. The exporter reads canonical Skill, protocol, reference, template, machine-contract, diagnostic, and current repository documentation sources; records bytes and SHA-256 values; validates byte-identical mirrors; classifies every `docs/lite-v3/*.md`; and supports read-only `--check` stale-artifact detection.

This is a documentation and repository-maintenance release. It does not change the Lite v3 marker, eight public commands, workspace layout, frozen headings, dependency grammar, evidence scope, Supplement/HANDOFF/figure/appendix runtime behavior, or Full. The generated file is intentionally long, is not hand-edited, and still requires human review for mathematical correctness.

The 0.9.0 runtime surface remains below for complete release context:

## KyMCM Lite 0.9.0 runtime surface

KyMCM Lite 0.9.0 adds optional question-level Supplement contracts for work discovered after a base question is formally complete. Instead of overwriting the visible base START/RESULT identity, each official question may use one append-only pair:

```text
problems/qN/spec/SUPPLEMENT_START_QN.md
problems/qN/result/SUPPLEMENT_RESULT_QN.md
```

Single and split modes share that pair. Each S1/S2/... plan is written and semantically reviewed before its execution; the matching result is appended afterward. Completed entries and their evidence are not overwritten. The supported types are `补充验证`, `方案修订`, and `实现修复`; impact is stated exactly as `追加证据`, `局部替代`, `完全替代`, or `不改变正式状态`.

Current effective technical state is the base RESULT set plus completed Supplement Result entries applied in order and only within explicit scope. Failed or aborted entries preserve technical history and risks but create no new formal numeric conclusion. Supplement-specific implementation and evidence remain in existing QN directories, preferably at new `sN_` paths.

Dependency grammar is unchanged: later START files still name exact base tokens such as `Q1` or `Q2_1`. Semantic review also reads applicable Supplement entries and treats an unmatched material plan as a pending risk. Material completed changes trigger downstream impact review; affected downstream work uses that question's own Supplement rather than overwriting its base RESULT.

The one problem-level `HANDOFF_QN.md` is refreshed after every Supplement Result. Its formal-upstream list names base RESULT files first and the question-level Supplement Result next. It preserves base-unit and Sx provenance and distinguishes current effective, superseded, failed, and auxiliary material. HANDOFF remains derived, non-formal, and never becomes a dependency.

Supplement Markdown contracts are internal documents and are rejected as appendix sources with existing `LITE-APPENDIX-SOURCE-PATH-001`. Current effective Supplement code, derived data, outputs, and representative code remain eligible under the existing source roots and mapping rules. Superseded assets are excluded unless a competition explicitly requires historical comparison.

The marker remains exactly `{"workflow":"kymcm_lite","version":3}`. The eight public commands, base START/RESULT and PRE discovery, partial split legality, dependency tokens, evidence scope, all frozen START/RESULT/PRE/HANDOFF/APPENDIX headings, figure behavior, and standalone standard-library runtime remain unchanged. The only runtime change extends appendix internal-document rejection to the two Supplement paths.

The commands remain exactly `init`, `doctor`, `check-preprocess-start`, `check-preprocess-result`, `check-start`, `check-result`, `check-appendix-start`, and `check-appendix-result`, supported on Python 3.11, 3.12, and 3.13. The mirrored `supplement_work.md` and `technical_handoff.md` references define formal versus auxiliary and current versus superseded content. The one `HANDOFF_QN.md` replaces no legacy `HANDOFF_QN_K.md`; those notes are not automatically migrated. Dependencies keep exact tokens.

The optional `figure/` known optional root and separate `nature-figure` boundary are unchanged. Appendix still selects a complete formal solve code package and authentic representative root code while excluding internal contracts and display-only plotting.

No Supplement checker, CLI option, state, JSON, manifest, approval, hash ledger, new dependency token, `followups/`, per-Sx directory, aggregate RESULT, or PRE Supplement is added. Python does not enforce Sx continuity, plan-before-execution, replacement scope, mathematical correctness, or HANDOFF currency; these remain agent semantic-review and human-review responsibilities.

Existing 0.8.1 workspaces need no migration and need not create Supplement files. Existing user-created files with the new names are not rewritten automatically. Full 1.0.0 remains separate and unchanged.
Historical Lite v2 remains a separate Full compatibility marker and is not accepted as Lite v3.

## Historical releases

- 0.8.1 (2026-07-30) made QN HANDOFF official-question-scoped.
- 0.8.0 (2026-07-30) made formal work non-visual by default and added the optional request-driven figure workspace.
- 0.7.0 (2026-07-30) refocused Lite on programming-side execution and neutral technical handoffs.
- 0.6.0 (2026-07-29) added optional fixed PRE contracts, commands, dependencies, and appendix mappings.
- 0.5.1 (2026-07-29) defined the complete formal solve code package and expanded authentic representative-code eligibility.
- 0.5.0 (2026-07-29) introduced the original writing-oriented HANDOFF layer.
- 0.4.0 (2026-07-29) added the execution-first modeling-plan standard.
- 0.3.1 (2026-07-24) added independent split units and exact dependency tokens.
- 0.3.0 (2026-07-23) removed the active FROZEN_CONTEXT surface and introduced direct dependency review.
- 0.2.0 (2026-07-23) added independent appendix contracts and checks.
- 0.1.0 (2026-07-20) introduced standalone Lite v3.
