# KyMCM Lite v3 Phase 1 Benchmark Method

> Historical KyMCM Lite 0.1.0 benchmark method. Its FROZEN_CONTEXT inputs were removed from the canonical 0.3.0 fixture; the method is preserved for interpreting the original report.

## 1. Purpose and metric

The benchmark measures UTF-8 file bytes and formal artifact counts as a proxy for protocol overhead. It is not a token, reasoning-quality, or runtime benchmark. Measurements use ordinary file sizes from Python `Path.stat().st_size` on 2026-07-20.

## 2. Lite inclusion rules

Lifecycle alignment is part of a fair comparison: each product is measured after Q1 is complete and before Q2 execution introduces later frozen outcomes. The primary time-aligned Lite Q1 set therefore includes:

- `review_snapshots/before_q2/FROZEN_CONTEXT.md` as the context that was current at that lifecycle point;
- `problems/q1/spec/START_Q1.md`;
- `problems/q1/result/RESULT_Q1.md`.

A separate secondary **final-root-context Q1 view** substitutes the final root `FROZEN_CONTEXT.md` while retaining Q1 START and RESULT. Because the root file includes later Q2/Q3 frozen outcomes, this is a conservative upper-bound view after the complete fixture has advanced, not the lifecycle-equivalent primary denominator.

The ordinary Q1–Q3 workspace total includes root `FROZEN_CONTEXT.md` plus all three START and all three RESULT files. `.kymcm/mode.json` is required machine metadata and is reported separately.

Input data, code, ordinary evidence, `review_snapshots/**`, `.gitkeep`, reports, benchmark documents, Git internals, and caches are excluded from ordinary workspace totals. The single pre-Q2 snapshot is the deliberate exception only for the isolated primary Q1 comparison, where it substitutes for the root context at the matching lifecycle point. It remains historical reviewer-exercise material, not a production Lite artifact, hidden workflow state, or an additional formal workspace artifact.

## 3. Full comparison rules

The fair primary comparison uses one Q1 allocation handoff with the same ten units, A/B/C values, bounds, objective, answer `(5,4,1)`, and score 84. Full formal content/review objects are:

```text
problems/problem_definition/problem_definition.json
problems/problem_definition/PROBLEM_DEFINITION.md
problems/q1/spec/model_spec.json
problems/q1/spec/START_Q1.md
problems/q1/result/result_record.json
problems/q1/result/RESULT_Q1.md
```

Full `.kymcm/**` mode, workflow, binding, and event files are measured separately and excluded from the primary comparison. Ordinary evidence is excluded for both products. Approval transitions are counted separately.

## 4. Full generation procedure

The released `skills/kymcm-full/scripts/full_checkpoint.py` was run against a temporary directory inside the repository so its Git evidence guard could bind to the unchanged base HEAD. The temporary workspace contained the exact Full v1 marker, required Q1–Q4 empty layout, and a one-question Problem Definition. JSON was written as UTF-8 with `ensure_ascii=False` and compact separators.

The synthetic payload froze these Q1 semantics: objective `max 9x_A+8x_B+7x_C`; integer total 10; bounds A 1–5, B 1–4, C 1–3; tie preference more A then more B; direct result A=5, B=4, C=1 and score 84. It used one CSV evidence file outside the formal-byte count. The exact CLI transition sequence was:

```bash
python skills/kymcm-full/scripts/full_checkpoint.py --workspace "$TEMP" init-problem-definition
python skills/kymcm-full/scripts/full_checkpoint.py --workspace "$TEMP" --problem 1 init
python skills/kymcm-full/scripts/full_checkpoint.py --workspace "$TEMP" --problem 2 init
python skills/kymcm-full/scripts/full_checkpoint.py --workspace "$TEMP" --problem 3 init
python skills/kymcm-full/scripts/full_checkpoint.py --workspace "$TEMP" --problem 4 init
python skills/kymcm-full/scripts/full_checkpoint.py --workspace "$TEMP" submit-problem-definition
python skills/kymcm-full/scripts/full_checkpoint.py --workspace "$TEMP" accept-problem-definition --user-message "Accept synthetic benchmark definition."
python skills/kymcm-full/scripts/full_checkpoint.py --workspace "$TEMP" --problem 1 submit-start --recommendation "Execute the frozen integer allocation model."
python skills/kymcm-full/scripts/full_checkpoint.py --workspace "$TEMP" --problem 1 accept-start --recommendation "Execute the frozen integer allocation model." --user-message "Accept synthetic benchmark Start."
python skills/kymcm-full/scripts/full_checkpoint.py --workspace "$TEMP" --problem 1 submit-result
python skills/kymcm-full/scripts/full_checkpoint.py --workspace "$TEMP" --problem 1 accept-result --user-message "Accept synthetic benchmark Result."
```

The temporary directory was removed after byte counts were printed. No Full source or repository fixture was modified.

## 5. Recalculation commands

All Lite file bytes are recomputed from the repository rather than copied from a previous report. With `root` set to `tests/fixtures/lite_synthetic_handoff`, the two Q1 views and ordinary total are reproduced by:

```python
from pathlib import Path

root = Path("tests/fixtures/lite_synthetic_handoff")
q1_common = [root / "problems/q1/spec/START_Q1.md", root / "problems/q1/result/RESULT_Q1.md"]
q1_time_aligned = [root / "review_snapshots/before_q2/FROZEN_CONTEXT.md", *q1_common]
q1_final_context = [root / "FROZEN_CONTEXT.md", *q1_common]
all_lite = [root / "FROZEN_CONTEXT.md"] + [root / f"problems/q{q}/spec/START_Q{q}.md" for q in (1, 2, 3)] + [root / f"problems/q{q}/result/RESULT_Q{q}.md" for q in (1, 2, 3)]
print(len(q1_time_aligned), sum(path.stat().st_size for path in q1_time_aligned))
print(len(q1_final_context), sum(path.stat().st_size for path in q1_final_context))
print(len(all_lite), sum(path.stat().st_size for path in all_lite))
print((root / ".kymcm/mode.json").stat().st_size)
```

For either temporary Full file list or the Lite lists, category totals use:

```python
sum(path.stat().st_size for path in files if path.suffix == ".md")
sum(path.stat().st_size for path in files if path.suffix == ".json")
```

Evidence resolution is recomputed by the Phase 1 test: parse every RESULT evidence bullet, reject unsafe paths and symlinks, and count only paths that resolve to ordinary files under the same question's allowed directories.
