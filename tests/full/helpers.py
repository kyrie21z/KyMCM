from checkpoint_full.core import ModelSpec, ResultRecord


def model_spec(**changes):
    values = dict(
        schema_version=3,
        problem=1,
        revision=1,
        objective="Select the most reliable alternative.",
        data_semantics={
            "observation_unit": "one sampled bottle",
            "response": "score",
            "quality_control": "Build formal analysis data exactly as reviewed.",
            "prestart_audit": {
                "scope": "fixture input table",
                "checks": ("structure", "missingness", "range"),
                "findings": (),
                "unresolved": (),
            },
        },
        assumptions=("Samples are independent.",),
        model={
            "method": "weighted score", "formal_definition": "A weighted score ranks alternatives.",
            "symbols": ({"symbol": "S_i", "meaning": "score of alternative i", "unit": "index"},),
            "formulas": ({"name": "score", "latex": "S_i=\\sum_j w_jx_{ij}", "meaning": "weighted sum"},),
            "hypotheses": (),
            "procedures": ({"step": "1", "mathematical_action": "compute weighted sums", "output": "scores"},),
            "diagnostics": ({"target": "weights", "method": "sum check", "pass_rule": "sum equals one", "failure_action": "replan"},),
            "decision_logic": ({"condition": "S_i is maximal", "conclusion": "rank i first"},),
        },
        decision_rules=({"metric": "score", "rule": "larger is better"},),
        required_outputs=({"name": "ranking", "definition": "ordered alternatives", "unit": "rank"},),
    )
    if "model" in changes:
        values["model"] = {**values["model"], **changes.pop("model")}
    values.update(changes)
    return ModelSpec(**values)


def model_spec_with_alternatives(**changes):
    options = {
        "alternatives": (
            {"option": "weighted score", "mathematical_meaning": "weighted additive utility", "applicability": "criteria are compensatory", "advantages": "uses importance", "disadvantages": "depends on weights", "result_impact": "changes ranking when weights vary"},
            {"option": "unweighted score", "mathematical_meaning": "equal-weight additive utility", "applicability": "criteria have equal importance", "advantages": "transparent", "disadvantages": "ignores importance", "result_impact": "may change ranking"},
        ),
        "recommendation": {"option": "weighted score", "reason": "importance is part of the reviewed semantics"},
        "selection_rationale": "Use reviewed weights and test sensitivity.",
    }
    options.update(changes.pop("model", {}))
    return model_spec(model=options, **changes)


def result(spec=None, **changes):
    spec = spec or model_spec()
    values = dict(
        schema_version=2,
        problem=spec.problem,
        spec_revision=spec.revision,
        spec_hash=spec.hash,
        summary={
            "problem": "Rank the alternatives.",
            "method": "Use the reviewed weighted score.",
            "decision_basis": "The largest score ranks first.",
        },
        direct_answers=({
            "question": "Q1-1", "answer": "Alternative A ranks first.",
            "evidence_ids": ("summary_csv",),
        },),
        statistical_conclusion=None,
        operational_conclusion={
            "text": "Select Alternative A.", "evidence_ids": ("summary_csv",),
        },
        key_values=({
            "id": "primary_score", "label": "Top score", "value": 0.82391,
            "unit": "index", "format": {"decimals": 2},
        },),
        evidence_strength={"level": "moderate", "explanation": "The ranking passed the planned checks."},
        recommendation={"status": "accept", "reason": "The result answers the question and passes validation.", "required_actions": ()},
        summary_table_ids=(),
        tables=(),
        figures=(),
        technical_sections=({
            "title": "Ranking evidence", "analysis": "The reviewed scoring rule places A first.",
            "table_ids": (), "figure_ids": (), "evidence_ids": ("summary_csv",),
        },),
        validations=({
            "id": "ranking_complete", "name": "Ranking completeness", "status": "pass",
            "summary": "Every alternative is ranked.", "details": "No rank is missing.",
            "is_key": True, "evidence_ids": ("summary_csv",),
        },),
        limitations=({
            "id": "sample_scope", "summary": "Small sample.",
            "impact": "The ranking should not be generalized without new data.", "is_key": True,
        },),
        evidence={
            "input_hash": "a" * 64, "code_revision": "abc123", "result_hash": "b" * 64,
            "artifacts": ({
                "id": "summary_csv", "path": "problems/q1/outputs/summary.csv",
                "kind": "csv", "purpose": "Ranking evidence",
            },),
        },
    )
    values.update(changes)
    return ResultRecord(**values)
