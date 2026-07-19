---
name: kymcm
description: >
  KyMCM is a Codex-native math modeling workflow for CUMCM, MCM, and ICM.
  It supports the legacy Contract workflow and Checkpoint Lite Pilot v2 with
  whole-problem definition and complete mathematical review.
---

# KyMCM

Resolve the explicit contest workspace before acting and run `workflow_mode.py`. An absent `.kymcm/mode.json` selects the legacy Contract workflow. Exactly `{"workflow":"checkpoint_lite","version":2}` selects Lite Pilot v2. Invalid or unknown markers fail closed. Never infer the contest workspace from the development repository or mix modes.

## Legacy Contract

Legacy behavior remains Problem Contract, Solution Contract Qi, single-focus dependency DAG, `state/pipeline.json`, executable validation, deterministic stale propagation, and Final Paper Checkpoint. Use the existing `pipeline_manager.py` commands and do not create Lite artifacts.

## Checkpoint Lite Pilot v2

Start Codex from the contest workspace. Lite v2 has three semantic objects:

1. Problem Definition for whole-problem meaning, data, subproblems, shared semantics, dependencies, and resolved ambiguities.
2. Model Spec v3 for one problem's complete structured mathematics.
3. Result Record for claims, outputs, validation, evidence, and limitations.

The sequence is Problem Definition draft → complete Markdown review → explicit user acceptance → Q1 Start, then Q1→Q4 serially according to reviewed dependencies. No Start is permitted before Problem Definition acceptance.

### Embedded Brainstorming

Brainstorming is a writing policy used while forming Problem Definition and every Start. It is not a state, checkpoint, artifact, log, authorization protocol, or separate approval, and it does not depend on an external brainstorming Skill.

Before submitting Problem Definition or Start:

1. Check for non-unique choices that materially affect the model, evaluation meaning, or conclusions.
2. Do not silently decide such a choice. When needed, present 2–3 reasonable options, their main impact, and a clear recommendation.
3. Ask only the single highest-impact question at a time.
4. After the user answers, write the conclusion directly into the Problem Definition or Model Spec's mathematical fields.
5. Resolve every key question before submitting the complete Markdown for approval.
6. When the interpretation and mathematical route are objectively clear, do not manufacture questions or fictional alternatives.

Ask about concept definitions, competing model routes, metric priorities, weights, aggregation rules, interpretation without ground truth, and data treatments that change conclusions. Do not ask about library choice, code organization, parser repair, plotting implementation, or other engineering details that do not change mathematical semantics. For example, “可信度如何定义” is a high-impact question; “使用哪个 Excel 解析库” is an implementation detail.

### Pre-Start data audit

Before every Start, perform a read-only audit limited to the data actually used by that problem: readability, table and identifier structure, observation units, duplicate keys and pairing, missing/non-numeric/out-of-range values, and problem-defined ranges or identities. This is part of Model Spec `data_semantics`, not a new state or Checkpoint, and it must not fit models, test significance, select features, or create paper figures.

Record harmless formatting normalization that does not change numerical meaning without interrupting the user. Before submitting Start, group and explain any findings whose treatment changes a value, missingness, sample set, pairing, or model input; resolve the highest-impact question with the user and write the actual finding and agreed treatment into the Model Spec. Do not mechanically interrupt for every cell. Never submit while `prestart_audit.unresolved` is non-empty.

If execution reveals a new anomaly that changes data meaning or model input, stop and use the existing replan path, update the complete Model Spec, and submit a new Start review. Parser libraries, paths, caches, syntax, and other purely implementation-level repairs use normal rerun recovery and do not trigger replan.

### Natural Modeling Interaction

Advance real contest modeling as a natural modeling conversation, not as a user-facing test protocol. Do not announce invented numbered stages, test steps, numbered stopping points, or acceptance checklists, and do not treat the user as a tester. Checkpoint Lite state, hashes, CLI commands, and Approval mechanics are internal details by default. When review is needed, naturally explain that the whole-problem interpretation, current problem's modeling plan, or completed result is ready for the user to inspect before continuing. Ask at most one genuinely consequential Brainstorm question at a time, and accept experience feedback in ordinary language at any point. A real-problem exercise does not justify lower modeling quality, an artificially narrow scope, or a forced Q1-only limit; whether to continue to another question follows the user's instruction and reviewed problem dependencies.

JSON is the machine object. Deterministically rendered Markdown is the formal human review object:

- `problems/problem_definition/PROBLEM_DEFINITION.md`
- `problems/qN/spec/START_QN.md`
- `problems/qN/result/RESULT_QN.md`

Read every formal review document completely. A chat message may navigate and summarize but must never replace the document or request acceptance from a compressed summary alone. JSON and Markdown are hash-bound and both are revalidated at acceptance.

### Markdown output

Whenever creating or modifying a Markdown Artifact, follow `references/markdown_format.md`. This applies to Problem Definition, Start, Result, notes, and reports. Put mathematical variables and symbols in `$...$`, put display equations in `$$...$$`, never emit bare LaTeX commands in prose, and do not format mathematics that should render as code.

### Figure output

For CUMCM and other Chinese-language papers, set `language: zh` in every Figure Brief. Use Chinese by default for all human-readable natural-language figure text, including axis labels, legend labels, subplot titles, in-figure annotations, and `caption_draft`.

Keep established proper names, model names, abbreviations, variables, formulas, and units in their conventional English or Latin form when appropriate, including RMSE, R², ICC, AUC, ARIMA, LSTM, and Spearman. Prefer professional mixed expressions such as `$G$ 系数`, `Spearman 相关系数`, `LSTM 预测值`, and `RMSE` rather than mechanical translation.

Do not add a large title to every figure; the paper caption remains responsible for the figure title. Prefer Microsoft YaHei for Chinese text, then use the existing CJK sans-serif fallbacks when unavailable. Never download or commit font files for a figure.

### Human control policy

- Approval blocks at Problem Definition, Start, any semantic-change Start, and Result.
- Do not submit Problem Definition or Start while a key modeling question remains unresolved in the conversation.
- Notification does not block for library choice, file naming, objective parsing repairs, syntax/cache failures, and implementation details that do not change conclusions.

Reduce mechanical approvals, never meaningful modeling discussion. Never accept a checkpoint without explicit non-empty user wording.

### Workspace protocol

Normal commands read fixed paths; do not pass arbitrary root-level files:

```bash
python "$KYMCM_ROOT/scripts/lite_checkpoint.py" submit-problem-definition
python "$KYMCM_ROOT/scripts/lite_checkpoint.py" accept-problem-definition --user-message "用户原话"
python "$KYMCM_ROOT/scripts/lite_checkpoint.py" --problem 1 submit-start --recommendation "Agent 建议"
python "$KYMCM_ROOT/scripts/lite_checkpoint.py" --problem 1 accept-start --recommendation "同一建议" --user-message "用户原话"
python "$KYMCM_ROOT/scripts/lite_checkpoint.py" --problem 1 submit-result
python "$KYMCM_ROOT/scripts/lite_checkpoint.py" --problem 1 accept-result --user-message "用户原话"
```

Write ResultRecord schema v2 as a two-layer review: a self-contained summary followed by Agent-written technical analysis, full validation, limitations, evidence index, and review metadata. Keep raw key values in JSON with optional display formats; prepare display tables as CSV evidence; register PNG figures explicitly; and use stable internal evidence IDs. The renderer formats and embeds declared artifacts but never derives conclusions. The recommendation inside `result_record.json` is the single source of truth for Result review.

All Qn specs, code, derived data, outputs, notes, and results belong under `problems/qN/`. The workspace root is allowlisted. Result evidence must be existing non-symlink files in the current problem's allowed directories and must bind the actual clean Git code revision. Never hand-edit `.kymcm` JSON.

Implementation bugs use rerun recovery. Mathematical or semantic changes require replan, a changed v3 Model Spec, complete new Start Markdown, and new Approval. A whole-problem semantic change makes Problem Definition stale; a problem-level semantic change returns the question to exploration.

## Safety

- Never generate solver artifacts before applicable Problem Definition and Start acceptance.
- Never self-approve or treat events and notifications as approval.
- Never use a failed-trial archive or legacy workspace output as formal evidence.
- Never complete work without current passing, revision-bound evidence and formal Result review.
