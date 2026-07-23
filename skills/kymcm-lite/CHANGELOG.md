# Changelog

## 0.2.0 - 2026-07-23

- Add optional, independent APPENDIX_START/APPENDIX_RESULT contracts and two read-only appendix commands.
- Enforce whitelist-first exact output sets, COPY hashes, source-integrity records, dependency closure, XLSX structure, and sensitive-data checks.
- Keep Lite v3 marker and existing modeling contracts/checker behavior unchanged; appendix commands never read `FROZEN_CONTEXT.md`.

## 0.1.0 - 2026-07-20

- Ship a standalone, Markdown-first Lite v3 Skill with variable-question initialization.
- Provide read-only doctor, START, RESULT, and evidence checks with stable diagnostics and exit codes.
- Reject unsafe evidence paths and symlinks without opening or executing evidence content.
- Support standalone copying on Python 3.11–3.13 using only the standard library and no Full runtime modules.
