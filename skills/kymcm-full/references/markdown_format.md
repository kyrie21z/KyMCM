# KyMCM Markdown Format

## Scope

Apply this reference whenever creating or modifying a contest Markdown Artifact, including Problem Definition, Start, Result, notes, and reports.

Use standard Markdown and LaTeX that render predictably in common Markdown viewers and downstream document conversion. This is a writing check, not a new workflow state, approval, or formatter.

## Mathematical notation

- Put mathematical variables, symbols, subscripts, sets, statistics, parameters, and short expressions in inline delimiters `$...$`.
- Put a display equation in `$$...$$`, with each `$$` delimiter on its own line.
- Put multiline derivations in a standard LaTeX environment such as `aligned`, enclosed by display delimiters.
- Do not mechanically wrap every single letter. Use math delimiters only when a token has mathematical meaning.
- Keep ordinary abbreviations, filenames, field names, and prose outside math delimiters.
- Bare LaTeX commands are forbidden in prose. Commands such as `\alpha`, `\Phi`, and `\sum` must be inside math delimiters.
- Do not put mathematics that should render in backticks or a code block. Use code formatting only when showing the literal source text.

Wrong:

```markdown
The significance level is \alpha=0.05.
```

Correct:

```markdown
The significance level is $\alpha=0.05$.
```

Wrong: `` `G=\sigma_p^2/\sigma_e^2` ``

Correct: $G=\sigma_p^2/\sigma_e^2$

Display equation:

```markdown
$$
G=\frac{\sigma_\tau^2}{\sigma_\tau^2+\sigma_\delta^2}
$$
```

Multiline derivation:

```markdown
$$
\begin{aligned}
\bar{x} &= \frac{1}{n}\sum_{i=1}^{n}x_i,\\
s^2 &= \frac{1}{n-1}\sum_{i=1}^{n}(x_i-\bar{x})^2.
\end{aligned}
$$
```

## Headings, paragraphs, and lists

- Use `#`, `##`, and `###` headings without skipping levels.
- Leave a blank line after every heading.
- Do not use bold text as a substitute for a heading.
- Give each paragraph one main idea and keep connected reasoning together.
- Use lists for genuinely parallel items, not to fragment a continuous argument.
- Keep list marker and indentation styles consistent within a list.

## Tables

- Keep mathematical quantities in inline delimiters `$...$` inside cells and headings.
- Right-align numeric columns with `---:`.
- Put units in column headings rather than repeating them in every cell.
- Do not put display equations, nested lists, or long derivations in table cells.
- Use `\mid` for conditional probability or set conditions; a bare `|` can break Markdown column boundaries.
- Keep cell text short. Move qualifications and derivations to prose below the table.

```markdown
| Metric | Group 1 | Group 2 | Conclusion |
|---|---:|---:|---|
| Mean score $\bar{x}$ | 73.11 | 70.51 | Group 1 is higher |
```

Write $P(A\mid B)$ in a table, not a mathematical expression containing a bare vertical bar.

## Code, paths, and field names

- Put filenames, paths, JSON fields, CLI commands, and program identifiers in backticks.
- Examples include `model_spec.json`, `problems/q1/outputs/`, and `prestart_audit`.
- Add a language identifier to every fenced code block, such as `python`, `json`, `bash`, or `markdown`.
- Do not use code formatting for a variable or formula that is meant to render mathematically.
- Mathematical source may appear in a code block only when the source syntax itself is the subject.

## Images and links

Use standard Markdown image and link syntax:

```markdown
![Figure 1. Score difference comparison](figures/q1_score_difference.png)
[Reference title](https://example.com)
```

- Give every figure a concise descriptive alt text.
- Prefer workspace-relative paths for contest artifacts.
- Use ordinary external links with descriptive labels rather than bare URLs when practical.
- Do not use wikilinks such as `[[note]]` or embeds such as `![[figure.png]]`.

## Pre-output check

- Are mathematical variables and symbols enclosed in `$...$`?
- Are display equations enclosed in `$$...$$`, with delimiters on separate lines?
- Does prose contain a bare command such as `\alpha`, `\Phi`, or `\sum`?
- Was any mathematics that should render mistakenly written as code?
- Does any table formula contain a bare `|` instead of `\mid`?
- Are headings, fenced code blocks, tables, and math delimiters properly closed?

## Excluded Obsidian features

Do not introduce YAML properties or frontmatter, wikilinks, note embeds, callouts, tags, block IDs, Obsidian comments, aliases, CSS classes, vault management, task management, Obsidian CLI instructions, or Obsidian media/PDF embed syntax.

Mermaid is outside this reference and remains governed by the existing Figure and visualization system.
