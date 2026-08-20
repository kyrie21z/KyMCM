# KyMCM Lite `kymcm-figure-3d-v1`

## Authority and scope

This reference is the normative HOW authority for formal intrinsic-3D data figures. Its byte-identical repository mirror is `docs/lite-v3/final_figure_3d.md`; the executable authority is `skills/kymcm-lite/figure_3d_exec.py` under `kymcm-figure-3d-exec-v1`.

It applies only after `final_figure_selection.md` has established that the selected information structure passes the intrinsic-3D gate. It is not a generic illustration specification, a stylistic upgrade, or a flowchart contract. Ordinary 2D/Cartesian figures remain on the Matplotlib `figure_exec.py` route. Formal intrinsic 3D does not use Matplotlib `mplot3d` and does not silently fall back when PyVista/VTK is unavailable.

Apply authorities in this order:

```text
final_figure_selection.md -> WHAT/WHEN and intrinsic-3D eligibility
final_figure_core_rules.md -> universal in-image/title/bundle boundaries
final_figure_color.md      -> semantic and continuous-color intent
final_figure_3d.md         -> 3D scene/camera/lighting/depth HOW
figure_3d_exec.py          -> machine-safe PyVista execution and hard audit
figure_bundle.py           -> same-stem PDF/PNG/PY/TXT delivery audit
ChatGPT/user               -> semantic and visual acceptance
```

`final_figure_style.md` remains the ordinary Matplotlib Pt2 authority. Its Cartesian axes, spines, ticks, bars, boxes, and line geometry do not silently govern VTK scenes.

## Physical templates and output meaning

Reuse exactly the existing physical templates:

```text
F-WIDE     = 160 x 60 mm   ~= 3780 x 1417 px
F-STANDARD = 160 x 80 mm   ~= 3780 x 1890 px
F-TALL     = 160 x 105 mm  ~= 3780 x 2480 px
M-STANDARD = 128 x 80 mm   ~= 3024 x 1890 px
```

Pixel dimensions are computed from `round(mm / 25.4 * 600)` and accepted within ±1 px. The authoritative 3D scene is the direct PyVista/VTK 600 dpi-equivalent PNG: it is not a lower-resolution image enlarged afterward and is not cropped. The matching PDF is an exact-physical-size formal paper container that embeds this raster scene; it is not a promise of vector 3D geometry. Its MediaBox must match the selected template within 0.25 pt.

Every formal programmatic 3D figure is complete only as one same-stem bundle:

```text
<stem>.pdf  paper-placement container
<stem>.png  authoritative high-resolution VTK render
<stem>.py   reproducible figure-specific entrypoint
<stem>.txt  paper-facing 图题 and 图注
```

## Scientific scene defaults

Use pure white with no gradient background. Add no title, extruded text decoration, decorative floor/wall box, cinematic perspective exaggeration, depth-of-field/bokeh, glossy material, environment map, reflection, or photorealistic ray-traced effect. A reference plane is allowed only when the scientific geometry needs it.

Use smooth shading for continuous surfaces when geometrically appropriate. Show mesh edges only when topology is evidence. Use explicit scalar ranges and controlled maps. Avoid transparency unless it reveals otherwise hidden scientific structure and the figure-specific entrypoint explicitly justifies it.

The default depth hierarchy is:

```text
geometry + normals/smooth shading
+ restrained PyVista light kit
+ SSAA anti-aliasing
```

Shadows and screen-space ambient occlusion (SSAO) are opt-in only when they materially clarify geometry. They are not defaults because they may distort quantitative color or height reading. The v1 final anti-aliasing default is SSAA. Failure to enable SSAA stops formal rendering; there is no silent disabled state or MSAA fallback in this release.

## Reproducible camera

Interactive mouse placement is never the sole source of a formal camera. The same-stem PY must call `apply_camera()` with finite explicit values for:

```text
position
focal_point
view_up
projection = perspective | parallel
```

Position and focal point must differ; view-up must be non-zero and nonparallel to the view direction. Use parallel projection when perspective distortion would interfere with quantitative shape comparison. Perspective is allowed for genuinely spatial geometry when it improves depth interpretation. There is no universal frozen camera angle and no automatic data-derived camera in v1.

## Scalar color

For a surface or mesh carrying a numeric scalar, use the Pt3 semantics where applicable:

- sequential values use controlled `batlow`;
- diverging values with a meaningful center use controlled `vik`;
- specify a finite increasing scalar range explicitly;
- use shared ranges for comparable scenes;
- use height/depth and color as mutually consistent evidence, not contradictory encodings.

`continuous_cmap_3d()` and `surface_kwargs()` expose only the approved maps. Rainbow and uncontrolled palettes are outside the formal route.

## Typography boundary

Do not claim that the Matplotlib Tinos/Noto per-`Text` hard audit applies to VTK-native text actors. Custom text APIs that accept a local font file should use approved locally installed fonts when technically supported, without copying, downloading, or bundling font files. Required text remains readable and follows the existing language semantics; no title belongs inside the scene.

VTK axes and scalar-bar APIs do not expose reliable exact Tinos/Noto routing for every component. `figure_3d_exec.py` audits only inspectable machine-safe properties, and ChatGPT/user performs final mixed-text visual review. If required CJK text would render as boxes/tofu, fail or omit that actor and move the explanation to the same-stem TXT caption. This limitation does not weaken the existing exact Matplotlib typography contract.

## Executable sequence

The figure-specific same-stem PY follows this conceptual sequence:

```python
stem = Path(__file__).with_suffix("")
plotter = create_formal_plotter("F-WIDE")
# add scientific geometry, using surface_kwargs() for scalar surfaces
apply_camera(plotter, position=..., focal_point=..., view_up=..., projection="perspective")
save_formal_3d_figure(plotter, stem, template="F-WIDE")
write_figure_note(stem, title="...", caption="...")
validate_figure_bundle(stem, source_path=__file__)
```

The executor uses `Plotter(off_screen=True)` at exact final pixels, pure white background, restrained lighting, SSAA, explicit camera metadata, direct PNG rendering, and one deterministic Matplotlib raster-packaging path for exact-size PDF. Matplotlib is only the non-3D PDF container layer. The executor verifies PNG header/dimensions and PDF MediaBox before atomically replacing the accepted visual pair.

## Machine and human audit boundary

`audit_3d_contract()` fails closed on known template, off-screen mode, window pixels, white background, helper-enabled SSAA, explicit camera metadata, projection consistency, helper-owned-title absence, approved helper scalar map/range, suffix-free output stem, and forbidden same-stem image formats.

It does not pretend to decide whether the camera is semantically best, whether 3D was the right chart, whether transparency or SSAO is justified, whether lighting reveals the conclusion fairly, or whether every VTK glyph came from an exact font file. Those remain ChatGPT/user semantic and visual review. Passing the executor audit without passing `validate_figure_bundle()` and that review is not final acceptance.

## Product boundary

The optional requirements are isolated in `requirements-figure-3d.txt`. Linux/WSL/server rendering requires a working VTK headless EGL/OpenGL environment. Missing PyVista, VTK, Matplotlib packaging support, `cmcrameri`, SSAA, or headless rendering stops the intrinsic-3D task.

This route adds no public command, checker, state, manifest, content JSON, approval/hash ledger, managed figure root, chart-template API, downloaded dataset, font/mesh fixture, migration, or KyMCM Full behavior. The Lite v3 marker and exactly eight commands remain unchanged. Flowcharts retain their semantic-plan-to-human-layout path and never acquire a Python renderer from this reference.
