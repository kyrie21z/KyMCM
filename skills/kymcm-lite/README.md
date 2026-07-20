# KyMCM Lite

KyMCM Lite 0.1.0 is a Markdown-first execution protocol for mathematical-modeling teams. It validates handoff structure and evidence integrity; it does not judge mathematical correctness.

## Installation

Copy the complete `kymcm-lite` directory into your Codex Skills directory. The copied directory is self-contained and the core requires only Python 3.11–3.13 standard library.

## Commands

```bash
python scripts/lite.py init --workspace PATH --questions 3
python scripts/lite.py doctor --workspace PATH
python scripts/lite.py check-start --workspace PATH --problem 1
python scripts/lite.py check-result --workspace PATH --problem 1
```

Exit code 0 means structurally valid (warnings may exist), 1 means contract or evidence invalid, and 2 means an unexpected tool or environment failure.

KyMCM Full is the review-gated end-to-end workflow. KyMCM Lite is a low-friction execution handoff. Users choose one Skill explicitly; neither guesses or converts the other workspace mode.

See `docs/protocol.md` for the complete standalone contract.
