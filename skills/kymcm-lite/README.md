# KyMCM Lite

KyMCM Lite 0.2.0 is a Markdown-first execution protocol for mathematical-modeling teams. It validates handoff structure and evidence integrity and adds an optional, independent appendix-organization stage; it does not judge mathematical correctness.

## Installation

Copy the complete `kymcm-lite` directory into your Codex Skills directory. The copied directory is self-contained and the core requires only Python 3.11–3.13 standard library.

## Commands

```bash
python scripts/lite.py init --workspace PATH --questions 3
python scripts/lite.py doctor --workspace PATH
python scripts/lite.py check-start --workspace PATH --problem 1
python scripts/lite.py check-result --workspace PATH --problem 1
python scripts/lite.py check-appendix-start --workspace PATH
python scripts/lite.py check-appendix-result --workspace PATH
```

Exit code 0 means structurally valid (warnings may exist), 1 means contract or evidence invalid, and 2 means an unexpected tool or environment failure.

The appendix stage begins only after modeling is complete. `APPENDIX_START.md` is the sole whitelist, `APPENDIX_RESULT.md` is the execution report, `appendix/` is the minimal reproducibility/result attachment, and root `code/` contains only concise core algorithms. Appendix checks are read-only, standard-library-only, and never read `FROZEN_CONTEXT.md`.

KyMCM Full is the review-gated end-to-end workflow. KyMCM Lite is a low-friction execution handoff. Users choose one Skill explicitly; neither guesses or converts the other workspace mode.

See `docs/protocol.md` for the complete standalone contract.
