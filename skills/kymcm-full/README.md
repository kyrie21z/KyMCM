# KyMCM Full Skill 1.0.0

This directory is a self-contained Codex Skill. Copy it as `kymcm-full`; its runtime does not import from the surrounding repository.

Initialize and inspect a contest workspace:

```bash
python scripts/full_workspace.py init --workspace /path/to/contest --contest MCM
git -C /path/to/contest init -b main
python scripts/full_workspace.py doctor --workspace /path/to/contest
```

Use `scripts/full_checkpoint.py` as the canonical checkpoint command. `scripts/lite_checkpoint.py` is a deprecated compatibility wrapper. Existing exact Lite v2 markers and `.kymcm/checkpoint_lite/**` state paths remain readable and are not rewritten automatically.

Read [SKILL.md](SKILL.md) for agent policy, [KyMCM_SOP.md](KyMCM_SOP.md) for operations, and [checkpoint core](docs/checkpoint-core.md) for state and hash semantics.
