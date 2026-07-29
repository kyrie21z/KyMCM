# KyMCM

KyMCM provides two explicit, sibling Codex Skills for mathematical modeling.

- **KyMCM Full 1.0.0** is the stable, review-gated end-to-end workflow. It preserves whole-problem definition, Model Spec v3, Result Record v2, deterministic review documents, evidence and Git binding, and reproducible paper figures.
- **KyMCM Lite 0.6.0** is the Markdown-first execution protocol with an optional shared-data PRE stage, execution-first plan design, evidence-linked paper-writing HANDOFF documents, and appendix curation without workflow state or content JSON.

## Install

Copy the Skill you intend to use. Full supports Python 3.11–3.13 and uses the repository requirements:

```bash
python -m pip install -r requirements.txt
python skills/kymcm-full/scripts/full_workspace.py init --workspace ./contest --contest CUMCM
git -C ./contest init -b main
python skills/kymcm-full/scripts/full_workspace.py doctor --workspace ./contest
```

Lite core uses only Python 3.11–3.13 standard library:

```bash
cp -R skills/kymcm-lite /path/to/codex/skills/
python skills/kymcm-lite/scripts/lite.py init --workspace ./contest-lite --questions 3 --preprocess
python skills/kymcm-lite/scripts/lite.py check-preprocess-start --workspace ./contest-lite
python skills/kymcm-lite/scripts/lite.py check-preprocess-result --workspace ./contest-lite
python skills/kymcm-lite/scripts/lite.py doctor --workspace ./contest-lite
python skills/kymcm-lite/scripts/lite.py check-appendix-start --workspace ./contest-lite
python skills/kymcm-lite/scripts/lite.py check-appendix-result --workspace ./contest-lite
```

The Full initializer creates an empty Q1–Q4 workspace. Neither initializer adds problem inputs, model code, results, figures, paper text, or a nested Git repository.

## Workflow

The canonical marker is `{"workflow":"kymcm_full","version":1}`. A complete Problem Definition must be reviewed and explicitly accepted before a question Start. Each Start binds a complete mathematical Model Spec and pre-start audit; each Result binds claims to artifacts and the contest repository commit. Formal review objects are rendered deterministically as `PROBLEM_DEFINITION.md`, `START_QN.md`, and `RESULT_QN.md`.

See [installation](docs/installation.md), [Full workflow](docs/full-workflow.md), [compatibility](docs/compatibility.md), [limitations](docs/known-limitations.md), the [Full Skill README](skills/kymcm-full/README.md), and the [Lite Skill README](skills/kymcm-lite/README.md).

## Product split

Users explicitly choose Full or Lite; neither Skill guesses, converts, or silently accepts the other's mode. Historical Checkpoint Lite Pilot v2 remains an internal Full compatibility marker and is not Lite v3.

## Development

```bash
python -m compileall skills/kymcm-full skills/kymcm-lite tests
python -m unittest discover -s tests/lite -v
python -m unittest tests.test_lite_cli tests.test_lite_portability tests.test_lite_appendix_cli tests.test_lite_v3_phase1 tests.test_lite_release -v
python -m unittest discover -s tests/full -v
python -m unittest tests.test_full_cli tests.test_full_portability tests.test_figure_system tests.test_markdown_format -v
```

No network service, OpenAI credential, proprietary font, or LaTeX installation is required for the test suite. Licensed under MIT; see [NOTICE](NOTICE.md) and [security policy](SECURITY.md).
