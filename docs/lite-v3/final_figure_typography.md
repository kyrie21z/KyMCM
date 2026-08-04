# KyMCM Lite final-figure typography

## Authority and scope

This reference is the authoritative Lite-only typography contract for final display figures. The byte-identical repository mirror is `docs/lite-v3/final_figure_typography.md`. It applies only after the relevant RESULT and Supplement Result entries have been accepted, any requested HANDOFF task has completed, and the user explicitly requests a final figure.

KyMCM Lite does not render figures. It reads this contract, passes it to the external `nature-figure` Skill, and reviews the returned font audit. Lite does not import, vendor, copy, download, or otherwise depend on `nature-figure`; it adds no figure command, checker, contract, manifest, state, JSON, or font ledger.

The required final-figure sequence is:

```text
accepted RESULT / accepted Supplement Result
→ current HANDOFF completed in a separate explicit task
→ explicit user request for the final figure
→ Lite reads this reference and passes the exact typography contract
→ nature-figure discovers fonts, renders, and audits the output
→ only an audited output may be called final
```

When a user says only “draw a figure” or “generate the final figure”, these requirements are the default project constraint. A user-requested different font is an explicit project-level deviation: Lite must identify the difference, obtain clear confirmation, pass and record the deviation, and must not silently replace the default contract.

## Exact font contract

The three required names are exact and are not interchangeable with approximate families:

| Content semantics | Required font/family or configuration |
| --- | --- |
| Chinese Han characters, Chinese full-width punctuation, and CJK punctuation | `Noto Serif CJK SC` |
| Latin letters, Arabic numerals, ASCII punctuation, English units, and ordinary English text | `Tinos` |
| Math formulas, Greek letters, operators, superscripts/subscripts, and mathematical symbols | `STIX mathtext` |

The exact mathtext configuration name is:

```text
mathtext.fontset = stix
```

The following are not equivalent formal Lite choices: `Noto Sans CJK SC`, `Source Han Serif SC`, `Microsoft YaHei`, `Times New Roman`, `DejaVu Serif`, or `STIXGeneral` used as an ordinary global font. Microsoft YaHei remains an existing KyMCM Full内置 renderer rule where documented; this Lite reference does not change, replace, or generalize that Full behavior.

## Mixed-text routing

Do not set one global font for an entire figure and assume that fallback produces the contract. Route content by semantic character class:

- Chinese characters and Chinese/CJK punctuation use `Noto Serif CJK SC`.
- Latin text, numbers, English abbreviations, ordinary units, and ASCII punctuation use `Tinos`.
- Every mathematical expression belongs inside Matplotlib mathtext boundaries such as `$...$` and uses STIX mathtext.
- Mathematical Greek letters, operators, subscripts, superscripts, and formula symbols must not depend on accidental Unicode coverage in Tinos or Noto.
- Mixed titles, axis labels, legends, annotations, table cells, and text boxes preserve this split. ASCII letters and numbers embedded in Chinese text still use Tinos; an English/numeric text element does not become wholly Noto merely because the figure also contains Chinese.

The following is a non-runtime semantic example, not Lite configuration or a dependency:

```python
{
    "font.family": ["Tinos", "Noto Serif CJK SC"],
    "mathtext.fontset": "stix",
    "axes.unicode_minus": False,
    "pdf.fonttype": 42,
    "svg.fonttype": "none",
}
```

This example only communicates a basic font stack and mathtext setting. For Chinese punctuation and complex mixed text, fallback alone may be insufficient; `nature-figure` must use explicit font properties, text segmentation, or its existing routing mechanism so the actual rendered fonts satisfy this contract. Lite does not execute, import, or maintain this example. If `axes.unicode_minus` conflicts with the external implementation, it must not weaken the typography contract: mathematical minus signs remain in mathtext and are rendered by STIX mathtext, with the deviation documented in the external audit.

## Missing-font stop rule

Formal final rendering must stop when any requirement is unavailable:

```text
Noto Serif CJK SC missing
or Tinos missing
or STIX mathtext unavailable
→ stop the formal final-figure task
→ report the exact missing item
→ do not produce or label a final-compliant figure
```

There is no silent fallback to a system default, an approximate family, or a missing-glyph substitution. Do not download a font, copy it from another directory, put a font file in the repository, or claim that a preview satisfies the final contract. A temporary preview is permitted only when the user explicitly requests one; it must be marked `preview/non-final`, report the actual fallback, fail final typography acceptance, and never overwrite an accepted final output. Lite does not proactively create such previews.

## External audit minimum

`nature-figure` is responsible for font discovery, actual rendering, output, and the final font audit. At minimum, the audit must verify:

1. Chinese title/axis/legend/annotation text actually uses `Noto Serif CJK SC`.
2. English, numerals, percentages, scientific notation, and units actually use `Tinos`.
3. `$...$` expressions actually use STIX mathtext.
4. Mixed samples are not rendered as one incorrectly unified Noto or Tinos block.
5. There are no missing-glyph, font-fallback, or font-family-not-found warnings.
6. Required PNG/PDF/SVG outputs remain visually consistent.
7. PDF/SVG embedding does not corrupt, replace, or distort Chinese or mathematical glyphs.
8. The output directory contains no font binary.
9. The delivery note records all three checks and any explicitly authorized deviation.

The minimum routing probe covers equivalent character classes; it is not a required figure or Lite test asset:

```text
中文：模型结果（测试），样本量：
英文/数字：Model Accuracy = 87.5%, n = 1024
数学：$f(x)=\alpha x^2+\beta$, $R^2$, $\mu\pm\sigma$
混合：模型 Accuracy = 87.5%，$R^2=0.92$
```

If any audit item fails, typography acceptance fails. Keep existing accepted output unchanged, report the element, expected font, actual font, and missing/fallback detail, and wait for environment repair or an explicitly confirmed project deviation. Visual similarity is not evidence of compliance.

## Installation and product boundary

Users install the three required fonts locally and carry their own licensing responsibility. KyMCM does not contain, distribute, share, download, or commit font files. CI does not need these fonts because Lite has no renderer; font availability is checked by the external `nature-figure` final-figure task.

This contract does not change the Lite v3 marker, the eight commands, `figure/` boundaries, RESULT acceptance, HANDOFF timing, Supplement/PRE behavior, or the standard-library-only Lite runtime. Historical figures are not redrawn or retroactively declared compliant. Existing 0.9.3 workspaces need no migration; new 0.9.4 final-figure requests use this contract by default.

KyMCM Full remains separate. Its built-in renderer and existing Microsoft YaHei/CJK sans-serif behavior are unchanged, and this Lite reference must not be used to reinterpret Full files or tests.
