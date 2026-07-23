# Changelog

## 0.3.1 - 2026-07-24

- Allow each official question to use either one unsuffixed START/RESULT pair or contiguous suffixed START units with independently completed RESULT units.
- Add exact `QN_K` dependency tokens, `--subproblem` selection on the two modeling checks, layout diagnostics, and split-aware appendix references.
- Preserve the Lite v3 marker, headings, six commands, standard-library runtime, and compatibility with valid 0.3.0 single-mode workspaces.

## 0.3.0 - 2026-07-23

- Remove `FROZEN_CONTEXT.md` from initialization, managed layout, runtime checks, and active templates.
- Require one exact direct-dependency declaration in START section 2 and validate declared upstream START/RESULT structure.
- Add mandatory Codex semantic contradiction review without consistency state or artifacts; preserve appendix behavior.

## 0.2.0 - 2026-07-23

- Add optional, independent APPENDIX_START/APPENDIX_RESULT contracts and two read-only appendix commands.
- Enforce whitelist-first exact output sets, COPY hashes, source-integrity records, dependency closure, XLSX structure, and sensitive-data checks.
- Keep Lite v3 marker and existing modeling contracts/checker behavior unchanged; appendix commands never read `FROZEN_CONTEXT.md`.

## 0.1.0 - 2026-07-20

- Ship a standalone, Markdown-first Lite v3 Skill with variable-question initialization.
- Provide read-only doctor, START, RESULT, and evidence checks with stable diagnostics and exit codes.
- Reject unsafe evidence paths and symlinks without opening or executing evidence content.
- Support standalone copying on Python 3.11–3.13 using only the standard library and no Full runtime modules.
