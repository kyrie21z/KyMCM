"""Static, manifest-driven figure gallery generation."""

from __future__ import annotations

import html
import json
from pathlib import Path


def _asset_link(workspace: Path, value: object) -> str:
    if not isinstance(value, str) or not value.startswith("figures/"):
        return ""
    figures = (workspace / "figures").resolve()
    path = (workspace / value).resolve()
    if not path.is_relative_to(figures) or not path.is_file():
        return ""
    return str(path.relative_to(figures))


def generate_gallery(workspace: Path) -> Path:
    workspace = workspace.resolve()
    manifest_dir = workspace / "figures" / "manifests"
    manifests = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(manifest_dir.glob("*.json"))
    ] if manifest_dir.is_dir() else []
    cards: list[str] = []
    for manifest in manifests:
        outputs = manifest.get("output_paths", {})
        outputs = outputs if isinstance(outputs, dict) else {}
        preview = _asset_link(workspace, outputs.get("png"))
        vector = _asset_link(workspace, outputs.get("svg"))
        pdf = _asset_link(workspace, outputs.get("pdf"))
        warnings = manifest.get("audit_warnings", manifest.get("warnings", []))
        warning_html = "".join(f"<li>{html.escape(str(item))}</li>" for item in warnings)
        cards.append(f"""
<article class="figure-card">
  <img src="{html.escape(preview)}" alt="Preview of {html.escape(manifest.get('figure_id', 'figure'))}">
  <div class="body">
    <div class="status {html.escape(manifest.get('audit_status', 'pending'))}">{html.escape(manifest.get('audit_status', 'pending'))}</div>
    <h2>{html.escape(manifest.get('figure_id', ''))}</h2>
    <p><strong>Claim:</strong> {html.escape(manifest.get('claim', ''))}</p>
    <dl>
      <dt>Template</dt><dd>{html.escape(manifest.get('template', ''))}</dd>
      <dt>Source</dt><dd>{html.escape(', '.join(manifest.get('source_data', [])))}</dd>
      <dt>Paper section</dt><dd>{html.escape(manifest.get('paper_section', ''))}</dd>
      <dt>Caption</dt><dd>{html.escape(manifest.get('caption_draft', ''))}</dd>
    </dl>
    <p class="links"><a href="{html.escape(vector)}">SVG</a><a href="{html.escape(pdf)}">PDF</a></p>
    <ul>{warning_html}</ul>
  </div>
</article>""")
    document = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>KyMCM Figure Gallery</title>
<style>
:root {{ color-scheme: light; font-family: system-ui, sans-serif; color: #17202a; background: #f4f6f7; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; }}
header {{ background: #ffffff; border-bottom: 1px solid #d5d8dc; padding: 20px max(24px, 5vw); }}
h1 {{ margin: 0; font-size: 24px; }}
main {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 360px), 1fr)); gap: 18px; padding: 24px max(24px, 5vw); }}
.figure-card {{ background: #ffffff; border: 1px solid #d5d8dc; border-radius: 6px; overflow: hidden; }}
.figure-card img {{ width: 100%; aspect-ratio: 16 / 9; object-fit: contain; background: #ffffff; border-bottom: 1px solid #e5e7e9; }}
.body {{ padding: 16px; }}
h2 {{ margin: 4px 0 12px; font-size: 18px; }}
.status {{ display: inline-block; font-size: 12px; font-weight: 700; text-transform: uppercase; }}
.status.pass {{ color: #117864; }} .status.fail {{ color: #b03a2e; }} .status.pending {{ color: #7d6608; }}
dl {{ display: grid; grid-template-columns: 110px 1fr; gap: 6px 10px; font-size: 14px; }}
dt {{ font-weight: 700; }} dd {{ margin: 0; overflow-wrap: anywhere; }}
.links {{ display: flex; gap: 14px; }} a {{ color: #006a9b; }}
</style>
</head>
<body><header><h1>KyMCM Figure Gallery</h1></header><main>{''.join(cards)}</main></body>
</html>
"""
    output = workspace / "figures" / "gallery.html"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(document, encoding="utf-8")
    return output
