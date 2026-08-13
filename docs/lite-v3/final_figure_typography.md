# KyMCM Lite final-figure typography

## Authority and scope

This reference is the authoritative Lite-only typography contract for final display figures. The byte-identical repository mirror is `docs/lite-v3/final_figure_typography.md`. It applies only after the relevant RESULT and Supplement Result entries have been accepted, any requested HANDOFF task has completed, and the user explicitly requests a final figure.

The KyMCM Lite core CLI/runtime does not render figures. The optional `figure_exec.py` performs strict font-availability preflight, fixed Matplotlib rc configuration, hard title/text-size checks, and formal PDF/PNG saving for Codex/Matplotlib figures. Lite does not import, vendor, copy, download, or otherwise depend on the external `nature-figure` Skill; the helper adds no figure command, manifest, workflow state, JSON, or font ledger.

The required final-figure sequence is:

```text
accepted RESULT / accepted Supplement Result
→ current HANDOFF completed in a separate explicit task
→ explicit user request for the final figure
→ Lite reads this reference and configures the exact base contract with figure_exec.py
→ Codex declares latin/cjk/mixed routing with font_kwargs() for content it creates
→ figure_exec.py preflights fonts, audits declared routing and other machine-safe rules, and saves PDF + PNG
→ ChatGPT/user visually and semantically reviews the rendered artifact
→ only an accepted output may be called final
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

The optional execution helper configures this exact base stack:

```python
{
    "font.family": ["Tinos", "Noto Serif CJK SC"],
    "mathtext.fontset": "stix",
    "axes.unicode_minus": False,
    "pdf.fonttype": 42,
}
```

The compatible helper interface is `font_kwargs(role, script="mixed")`: `script="latin"` declares Tinos, `script="cjk"` declares Noto Serif CJK SC, and `script="mixed"` declares both in that order. The default keeps the existing mixed-family call form valid. The hard audit strips `$...$` mathtext fragments from ordinary-text classification, requires CJK-only visible text to include Noto Serif CJK SC, Latin/digit/ASCII-only visible text to include Tinos, and mixed visible text to include both. All declared ordinary families remain inside the approved pair.

This declared-family audit does not prove the exact physical font file used for each glyph in a complex mixed-script Matplotlib `Text` object. Codex uses explicit helper properties for the content it creates, and ChatGPT/user visually inspects the final artifact. Mathematical minus signs remain in mathtext and use STIX mathtext. Unusually strict forensic verification may be requested explicitly as an optional read-only specialist second opinion; it is not part of the normal required pipeline.

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

## Normal audit and review minimum

`figure_exec.py` is responsible for strict required-font lookup, the fixed base rc stack, minimum text size, title checks, declared Matplotlib `Text`-family routing, and formal save. Codex is responsible for using the script-aware helper on content it creates. ChatGPT/user owns final visual and semantic review. At minimum, the normal combined review verifies:

1. Chinese axis/legend/annotation/panel-label text declares `Noto Serif CJK SC` and renders without visible glyph problems.
2. English, numerals, percentages, scientific notation, and units declare `Tinos` and render correctly.
3. `$...$` expressions use the frozen STIX mathtext configuration.
4. Mixed samples declare both approved families and render legibly.
5. There are no missing-glyph, font-fallback, or font-family-not-found warnings.
6. Required PDF and PNG outputs remain visually consistent.
7. PDF font embedding does not corrupt, replace, or distort Chinese or mathematical glyphs.
8. The output directory contains no font binary.
9. The delivery note records the three-family/configuration checks and any explicitly authorized deviation.

The minimum routing probe covers equivalent character classes; it is not a required figure or Lite test asset:

```text
中文：模型结果（测试），样本量：
英文/数字：Model Accuracy = 87.5%, n = 1024
数学：$f(x)=\alpha x^2+\beta$, $R^2$, $\mu\pm\sigma$
混合：模型 Accuracy = 87.5%，$R^2=0.92$
```

If any item fails, typography acceptance fails. Keep existing accepted output unchanged, report the element, expected declaration/configuration, and missing/fallback detail, and wait for environment repair or an explicitly confirmed project deviation. Visual similarity alone is not evidence of compliance.

When the user explicitly requests an independent specialist review, `nature-figure` may inspect the already-rendered PDF/PNG read-only and advise on unusually strict font/glyph concerns. It cannot rerender, restyle, export, overwrite, or apply its own typography/theme defaults to the KyMCM artifact. Any proposed change returns to Codex, uses this contract and `figure_exec.py`, passes the hard audit again, and returns to ChatGPT/user acceptance.

## Installation and product boundary

Users install the required fonts locally and carry their own licensing responsibility. KyMCM does not contain, distribute, share, download, or commit font files. Repository tests use the narrow injected resolver seam to test fail-closed behavior without bundling fonts; real formal rendering performs strict local lookup and stops when either named family is unavailable.

This contract does not change the Lite v3 marker, the eight commands, `figure/` boundaries, RESULT acceptance, HANDOFF timing, Supplement/PRE behavior, or the standard-library-only Lite core runtime. Historical figures are not redrawn or retroactively declared compliant. Existing 0.9.9 workspaces need no migration; new 0.9.10 formal Codex/Matplotlib final-figure requests use the optional execution helper by default and do not require `nature-figure`.

KyMCM Full remains separate. Its built-in renderer and existing Microsoft YaHei/CJK sans-serif behavior are unchanged, and this Lite reference must not be used to reinterpret Full files or tests.
