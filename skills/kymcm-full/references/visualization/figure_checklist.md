# Figure Audit Checklist

## Automatic Errors

- Manifest, exactly one workspace-local CSV evidence file, SVG, PDF, and PNG exist and are ordinary files.
- Multiple source files were merged by modeling code and exported as a named intermediate CSV before rendering.
- Source files remain inside the workspace and match recorded SHA-256 values.
- SVG/PDF/PNG hashes and sizes match the manifest.
- PDF has a PDF header and EOF marker; SVG parses with an `svg` root; PNG verifies and decodes as PNG.
- PNG dimensions match the manifest and satisfy the selected physical width at 300 DPI.
- `preferred_asset` equals the validated PDF output path.
- Manifest includes claim, template, paper section, label, caption draft, and preferred asset.
- Required axis-label metadata exists for the selected template.
- Input numeric values are finite.
- Template category, series, variable, and point limits are respected.

## Automatic Warnings

- Preferred CJK font was unavailable for a Chinese brief.
- A title option was requested even though captions belong in the paper.

## Human Gallery Review

- The visual emphasis supports the stated claim.
- Labels, units, and annotations remain readable at final paper width.
- Legend and annotations do not hide important data.
- Legend, category, series, and variable counts remain readable rather than merely below hard renderer limits.
- Important series remain distinguishable without color alone.
- Output aspect ratio supports the intended evidence at the target paper width.
- The caption describes evidence without adding an unsupported conclusion.
- The figure is referenced and explained in the target paper section.
- Black-and-white output remains interpretable.

The audit cannot guarantee absence of every text overlap or misleading interpretation. Gallery review remains required, but it creates no approval state.
