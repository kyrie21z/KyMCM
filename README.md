# KyMCM Full

KyMCM Full is a Codex-native, review-gated mathematical-modeling workflow for CUMCM, MCM, and ICM. Version 1.0.0 preserves whole-problem definition, Model Spec v3, Result Record v2, deterministic review documents, evidence and Git binding, and reproducible paper figures.

## Install

KyMCM Full supports Python 3.11–3.13. Copy `skills/kymcm-full` into a Codex skills directory, then install the dependencies:

```bash
python -m pip install -r requirements.txt
python skills/kymcm-full/scripts/full_workspace.py init --workspace ./contest --contest CUMCM
git -C ./contest init -b main
python skills/kymcm-full/scripts/full_workspace.py doctor --workspace ./contest
```

The initializer creates an empty Q1–Q4 workspace. It does not add problem inputs, model code, results, figures, paper text, or a nested Git repository.

## Workflow

The canonical marker is `{"workflow":"kymcm_full","version":1}`. A complete Problem Definition must be reviewed and explicitly accepted before a question Start. Each Start binds a complete mathematical Model Spec and pre-start audit; each Result binds claims to artifacts and the contest repository commit. Formal review objects are rendered deterministically as `PROBLEM_DEFINITION.md`, `START_QN.md`, and `RESULT_QN.md`.

See [installation](docs/installation.md), [workflow](docs/full-workflow.md), [compatibility](docs/compatibility.md), [limitations](docs/known-limitations.md), and the standalone [Skill README](skills/kymcm-full/README.md).

## Product split

KyMCM Full is the installable product in this repository. Checkpoint Lite Pilot v2 remains a compatibility marker and state layout, not a separately installed Skill. Legacy Contract scripts are retained for existing marker-less workspaces; new workspaces use Full.

## Development

```bash
python -m compileall skills/kymcm-full tests
python -m unittest discover -s tests/full -v
python -m unittest tests.test_full_cli tests.test_full_portability tests.test_figure_system tests.test_markdown_format -v
```

No network service, OpenAI credential, proprietary font, or LaTeX installation is required for the test suite. Licensed under MIT; see [NOTICE](NOTICE.md) and [security policy](SECURITY.md).
