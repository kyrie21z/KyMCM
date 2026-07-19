"""Natural-language views that hide Checkpoint Lite mechanics."""

from __future__ import annotations

import csv
import math
import os
from pathlib import Path
from typing import Mapping, Sequence

from .core import ModelSpec, ResultRecord
from .problem_definition import ProblemDefinition
from .workflow import StaleReason, Workflow, WorkflowState


def _joined(values: Sequence[str], empty: str = "无") -> str:
    return "；".join(str(value) for value in values) if values else empty


def _cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _render_prestart_audit(spec: ModelSpec) -> str:
    audit = spec.data_semantics.get("prestart_audit")
    quality_control = spec.data_semantics.get(
        "quality_control", "按原始数据语义执行并完整记录。"
    )
    if not isinstance(audit, Mapping):
        audit_text = "尚未提供 Start 前数据审计摘要；该旧版 Model Spec 不得提交新的 Start。"
    else:
        scope = audit.get("scope") if isinstance(audit.get("scope"), str) else "（未提供）"
        checks_value = audit.get("checks")
        checks = checks_value if isinstance(checks_value, (list, tuple)) else ()
        findings_value = audit.get("findings")
        findings = findings_value if isinstance(findings_value, (list, tuple)) else ()
        unresolved_value = audit.get("unresolved")
        unresolved = unresolved_value if isinstance(unresolved_value, (list, tuple)) else ("格式无效",)
        if findings:
            rows = []
            for finding in findings:
                if not isinstance(finding, Mapping):
                    rows.append("| （格式无效） | （格式无效） | （格式无效） | （格式无效） |")
                    continue
                impact = (
                    "会改变分析输入" if finding.get("changes_analysis_input") is True
                    else "不改变分析输入"
                )
                rows.append(
                    f"| {_cell(finding.get('location', '（未提供）'))} | "
                    f"{_cell(finding.get('issue', '（未提供）'))} | {impact} | "
                    f"{_cell(finding.get('treatment', '（未提供）'))} |"
                )
            findings_text = (
                "| 位置 | 问题 | 对分析输入的影响 | 处理方案 |\n"
                "|---|---|---|---|\n" + "\n".join(rows)
            )
        else:
            findings_text = "未发现需要单独处理的数据异常。"
        audit_text = (
            f"**审计范围**：{scope}\n\n"
            f"**已执行检查**：{_joined(checks, '（未提供）')}\n\n"
            f"### 实际发现\n\n{findings_text}\n\n"
            f"**未决问题**：{_joined(unresolved)}"
        )
    return (
        f"{audit_text}\n\n### 正式分析数据生成规则\n\n{quality_control}"
    )


def render_start_brief(spec: ModelSpec, recommendation: str) -> str:
    rules = [f"{rule['metric']}：{rule['rule']}" for rule in spec.decision_rules]
    confirmations = ["确认上述问题理解与方法即可开始计算"]
    return "\n".join((
        "## 方案确认",
        f"1. 我对问题的理解：{spec.objective}",
        f"2. 建议采用的方法：{spec.model['method']}。{spec.model['formal_definition']}",
        f"3. 最关键的数学或评价规则：{_joined(rules)}",
        f"4. 需要确认的内容：{_joined(confirmations)}",
        f"5. 我的建议：{recommendation}",
    ))


def _format_number(value: int | float, rule: Mapping[str, object] | None = None) -> str:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError("displayed values must be finite numbers")
    rule = rule or {}
    scaled = value * rule.get("scale", 1)
    if "decimals" in rule:
        return f"{scaled:.{rule['decimals']}f}"
    if isinstance(scaled, int):
        return str(scaled)
    return format(scaled, ".6g")


def _format_value(item: Mapping[str, object]) -> str:
    display = _format_number(item["value"], item.get("format"))
    unit = str(item.get("unit", ""))
    return f"{display}{unit}" if unit == "%" else f"{display} {unit}".rstrip()


def render_result_brief(result: ResultRecord) -> str:
    answers = [f"{item['question']}：{item['answer']}" for item in result.direct_answers]
    values = [f"{item['label']}={_format_value(item)}" for item in result.key_values]
    key_limits = [item["summary"] for item in result.limitations if item["is_key"]]
    recommendation = result.recommendation
    return "\n".join((
        "## 结果验收",
        f"直接答案：{_joined(answers)}",
        f"关键数值：{_joined(values)}",
        f"证据强度：{result.evidence_strength['explanation']}",
        f"限制与风险：{_joined(key_limits)}",
        f"建议：{recommendation['reason']}",
    ))


def public_status(workflow: Workflow) -> str:
    if workflow.state is WorkflowState.STALE:
        return ("结果需要重新计算" if workflow.stale_reason is StaleReason.RERUN_REQUIRED
                else "方案需要重新梳理")
    return {
        WorkflowState.EXPLORING: "正在分析",
        WorkflowState.AWAITING_START_REVIEW: "方案待确认",
        WorkflowState.RUNNING: "正在计算",
        WorkflowState.AWAITING_RESULT_REVIEW: "结果待验收",
        WorkflowState.COMPLETED: "已完成",
    }[workflow.state]


def render_problem_definition(definition: ProblemDefinition) -> str:
    sources = "\n".join(f"- **{x['name']}**：{x['role']}（范围：{x['scope']}）" for x in definition.source_data)
    problems = "\n".join(
        f"### Q{x['problem']}\n\n题意：{x['statement']}\n\n目标：{x['objective']}\n\n"
        f"输入：{_joined(x['inputs'])}\n\n输出：{_joined(x['outputs'])}"
        for x in definition.subproblems
    )
    dependencies = "\n".join(
        f"- Q{key} ← {_joined([f'Q{x}' for x in value], '无直接前驱')}"
        for key, value in sorted(definition.dependencies.items(), key=lambda item: int(item[0]))
    )
    outputs = "\n".join(f"- **{x['name']}**：{x['definition']}" for x in definition.shared_outputs) or "无"
    semantics = "\n".join(f"- **{key}**：{value}" for key, value in sorted(definition.shared_semantics.items())) or "无"
    tradeoffs = "\n".join(
        f"- **{x['issue']}**：最终口径：{x['resolution']}；后续影响：{x['impact']}"
        for x in definition.ambiguities
    ) or "本阶段未发现需要用户裁决的关键建模歧义。"
    tradeoff_heading = "已冻结的关键建模取舍" if definition.ambiguities else "关键取舍与未决问题"
    return (
        f"# {definition.title}\n\n## 1. 全题目标\n\n{definition.overall_objective}\n\n"
        f"## 2. 原始数据及作用\n\n{sources}\n\n## 3. 子问题定义\n\n{problems}\n\n"
        f"## 4. 共享语义\n\n{semantics}\n\n## 5. 依赖关系\n\n{dependencies}\n\n"
        f"稳定执行顺序：{_joined([f'Q{x}' for x in definition.topological_order])}\n\n"
        f"## 6. 跨题共享输出\n\n{outputs}\n\n## 7. {tradeoff_heading}\n\n{tradeoffs}\n"
    )


def render_start_document(spec: ModelSpec, definition: ProblemDefinition, recommendation: str) -> str:
    subproblem = next(x for x in definition.subproblems if x["problem"] == spec.problem)
    predecessors = definition.dependencies[str(spec.problem)]
    symbols = "\n".join(
        f"| {x['symbol']} | {x['meaning']} | {x.get('index_scope', '')} | {x.get('unit', '')} |"
        for x in spec.model["symbols"]
    )
    formulas = "\n\n".join(f"### {x['name']}\n\n$${x['latex']}$$\n\n{x['meaning']}" for x in spec.model["formulas"])
    hypotheses = "\n".join(
        f"- **{x['name']}**：$H_0$: {x['null']}；$H_1$: {x['alternative']}；范围：{x['scope']}"
        for x in spec.model["hypotheses"]
    ) or "不适用"
    procedures = "\n".join(f"{x['step']}. {x['mathematical_action']} → {x['output']}" for x in spec.model["procedures"])
    diagnostics = "\n".join(f"- **{x['target']}**：{x['method']}；通过：{x['pass_rule']}；失败：{x['failure_action']}" for x in spec.model["diagnostics"])
    alternatives = "\n".join(
        f"### {x['option']}\n\n数学含义：{x['mathematical_meaning']}；适用条件：{x['applicability']}；"
        f"优点：{x['advantages']}；缺点：{x['disadvantages']}；结果影响：{x['result_impact']}"
        for x in spec.model.get("alternatives", ())
    )
    if alternatives:
        recommendation_item = spec.model["recommendation"]
        tradeoffs = (
            f"{alternatives}\n\n### 最终采用方案\n\n**{recommendation_item['option']}**："
            f"{recommendation_item['reason']}\n\n选择理由：{spec.model['selection_rationale']}"
        )
    else:
        tradeoffs = "本阶段未发现需要用户裁决的关键建模歧义。"
    logic = "\n".join(f"- {x if isinstance(x, str) else x['condition'] + ' → ' + x['conclusion']}" for x in spec.model["decision_logic"])
    outputs = "\n".join(f"- **{x['name']}**：{x['definition']}（{x['unit']}）" for x in spec.required_outputs)
    audit = _render_prestart_audit(spec)
    return (
        f"# START Q{spec.problem}\n\n## 1. 问题理解\n\n{spec.objective}\n\n"
        f"## 2. 与 Problem Definition 的关系及前驱\n\n{subproblem['statement']}\n\n直接前驱：{_joined([f'Q{x}' for x in predecessors], '无')}\n\n"
        f"## 3. 数据结构与观测单位\n\n{spec.data_semantics['observation_unit']}\n\n"
        f"## 4. 数学符号表\n\n| 符号 | 含义 | 索引范围 | 单位 |\n|---|---|---|---|\n{symbols}\n\n"
        f"## 5. 核心数学模型与 LaTeX 公式\n\n{spec.model['formal_definition']}\n\n{formulas}\n\n"
        f"## 6. 假设与检验假设\n\n建模假设：{_joined(spec.assumptions)}\n\n{hypotheses}\n\n"
        f"## 7. 建模步骤\n\n{procedures}\n\n## 8. Start 前数据审计与处理规则\n\n{audit}\n\n"
        f"## 9. 诊断、稳健性和敏感性计划\n\n{diagnostics}\n\n## 10. 判定逻辑\n\n{logic}\n\n"
        f"## 11. 关键取舍与未决问题\n\n{tradeoffs}\n\n"
        f"## 12. 输出清单、风险和局限\n\n{outputs}\n\n{_joined(spec.model.get('limitations', spec.assumptions))}\n\n"
        f"## 13. Agent 导航建议\n\n{recommendation}\n"
    )


_EVIDENCE_STRENGTH = {
    "strong": "强证据", "moderate": "中等证据", "limited": "有限证据",
    "insufficient": "证据不足", "not_applicable": "不适用",
}
_RECOMMENDATIONS = {"accept": "建议接受", "revise": "建议返工", "reject": "建议拒绝"}
_VALIDATION_STATUS = {"pass": "通过", "warning": "警告", "fail": "失败", "not_applicable": "不适用"}


def _evidence_numbers(result: ResultRecord) -> tuple[dict[str, str], dict[str, Mapping[str, object]]]:
    artifacts = result.evidence["artifacts"]
    return (
        {item["id"]: f"E{index}" for index, item in enumerate(artifacts, 1)},
        {item["id"]: item for item in artifacts},
    )


def _evidence_refs(ids: Sequence[str], numbers: Mapping[str, str]) -> str:
    try:
        references = [f"[{numbers[item]}]" for item in ids]
    except KeyError as exc:
        raise ValueError(f"unknown evidence id: {exc.args[0]}") from exc
    return " ".join(references)


def _relative_link(workspace: Path, result: ResultRecord, artifact: Mapping[str, object]) -> str:
    document_parent = workspace / f"problems/q{result.problem}/result"
    return Path(os.path.relpath(workspace / str(artifact["path"]), document_parent)).as_posix()


def _render_csv_table(
    table: Mapping[str, object], workspace: Path, artifact: Mapping[str, object],
) -> str:
    if artifact["kind"] != "csv":
        raise ValueError(f"table {table['id']} must reference CSV evidence")
    path = workspace / str(artifact["path"])
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        columns = list(table["columns"])
        missing = [column for column in columns if column not in fieldnames]
        if missing:
            raise ValueError(f"CSV for table {table['id']} lacks columns: {', '.join(missing)}")
        rows = list(reader)
    sort = table.get("sort")
    if sort:
        column = sort["column"]
        if column not in columns:
            raise ValueError(f"table {table['id']} sort column is not displayed")

        def sort_key(row: Mapping[str, str]) -> tuple[int, object]:
            raw = row[column]
            try:
                return (0, float(raw))
            except ValueError:
                return (1, raw)

        rows.sort(key=sort_key, reverse=sort.get("descending", False))
    rows = rows[:table["max_rows"]]
    formats = table.get("formats", {})
    rendered_rows: list[str] = []
    for row in rows:
        cells: list[str] = []
        for column in columns:
            raw = row[column]
            if column in formats and raw != "":
                try:
                    raw = _format_number(float(raw), formats[column])
                except ValueError as exc:
                    raise ValueError(f"table {table['id']} column {column} contains non-numeric data") from exc
            cells.append(_cell(raw))
        rendered_rows.append("| " + " | ".join(cells) + " |")
    header = "| " + " | ".join(_cell(column) for column in columns) + " |"
    separator = "|" + "|".join("---" for _ in columns) + "|"
    return f"### {table['title']}\n\n{header}\n{separator}\n" + "\n".join(rendered_rows)


def render_result_document(result: ResultRecord, workspace_root: str | Path) -> str:
    workspace = Path(workspace_root).expanduser().resolve()
    numbers, artifacts = _evidence_numbers(result)
    tables = {item["id"]: item for item in result.tables}
    figures = {item["id"]: item for item in result.figures}

    def table_text(table_id: str) -> str:
        try:
            table = tables[table_id]
            artifact = artifacts[table["source_evidence_id"]]
        except KeyError as exc:
            raise ValueError(f"unknown table or evidence id: {exc.args[0]}") from exc
        return _render_csv_table(table, workspace, artifact)

    def figure_text(figure_id: str) -> str:
        try:
            figure = figures[figure_id]
            artifact = artifacts[figure["source_evidence_id"]]
        except KeyError as exc:
            raise ValueError(f"unknown figure or evidence id: {exc.args[0]}") from exc
        if artifact["kind"] != "png":
            raise ValueError(f"figure {figure_id} must reference PNG evidence")
        link = _relative_link(workspace, result, artifact)
        return (f"### {figure['caption']}\n\n![{figure['caption']}]({link})\n\n"
                f"**图注**：{figure['caption']}\n\n{figure['interpretation']}")

    navigation = "\n".join((
        "- [2. 结果摘要](#2-结果摘要)", "- [3. 技术分析](#3-技术分析)",
        "- [4. 完整验证与敏感性分析](#4-完整验证与敏感性分析)",
        "- [5. 局限与适用范围](#5-局限与适用范围)",
        "- [6. 证据索引](#6-证据索引)", "- [7. 审阅信息](#7-审阅信息)",
    ))
    answers = "\n".join(
        f"> **{item['question']}：** {item['answer']}"
        + (f" {_evidence_refs(item.get('evidence_ids', ()), numbers)}" if item.get("evidence_ids") else "")
        for item in result.direct_answers
    )
    summary_parts = [
        f"### 问题与方法\n\n{result.summary['problem']}\n\n{result.summary['method']}\n\n"
        f"**决策依据**：{result.summary['decision_basis']}",
        f"### 直接答案\n\n{answers}",
    ]
    for title, conclusion in (
        ("统计结论", result.statistical_conclusion), ("操作性结论", result.operational_conclusion),
    ):
        if conclusion is not None:
            refs = _evidence_refs(conclusion.get("evidence_ids", ()), numbers)
            summary_parts.append(f"### {title}\n\n{conclusion['text']}" + (f" {refs}" if refs else ""))
    key_results = [table_text(table_id) for table_id in result.summary_table_ids]
    if result.key_values:
        key_results.append("\n".join(f"- **{item['label']}**：{_format_value(item)}" for item in result.key_values))
    summary_parts.append("### 关键结果\n\n" + ("\n\n".join(key_results) or "未登记需要单列的关键数值或摘要表。"))
    strength = result.evidence_strength
    summary_parts.append(
        f"### 证据强度\n\n**{_EVIDENCE_STRENGTH[strength['level']]}**：{strength['explanation']}"
    )
    recommendation = result.recommendation
    recommendation_text = f"**{_RECOMMENDATIONS[recommendation['status']]}**：{recommendation['reason']}"
    if recommendation["required_actions"]:
        recommendation_text += "\n\n必须完成：\n\n" + "\n".join(
            f"- {item}" for item in recommendation["required_actions"]
        )
    summary_parts.append(f"### 接受或返工建议\n\n{recommendation_text}")
    key_validations = [item for item in result.validations if item["is_key"]]
    key_limits = [item for item in result.limitations if item["is_key"]]
    validation_lines = [
        f"- **{item['name']}（{_VALIDATION_STATUS[item['status']]}）**：{item['summary']}"
        + (f" {_evidence_refs(item.get('evidence_ids', ()), numbers)}" if item.get("evidence_ids") else "")
        for item in key_validations
    ]
    limit_lines = [f"- **{item['summary']}**：{item['impact']}" for item in key_limits]
    summary_parts.append(
        "### 核心验证与局限\n\n" + "\n".join(validation_lines + limit_lines or ["无摘要层核心项。"])
    )

    technical_parts: list[str] = []
    for section in result.technical_sections:
        refs = _evidence_refs(section.get("evidence_ids", ()), numbers)
        body = section["analysis"] + (f" {refs}" if refs else "")
        embedded = [table_text(item) for item in section.get("table_ids", ())]
        embedded.extend(figure_text(item) for item in section.get("figure_ids", ()))
        technical_parts.append(f"### {section['title']}\n\n{body}" +
                               ("\n\n" + "\n\n".join(embedded) if embedded else ""))
    technical = "\n\n".join(technical_parts) or "本结果无需补充独立技术小节。"

    validation_rows = "\n".join(
        f"| {_cell(item['name'])} | {_VALIDATION_STATUS[item['status']]} | "
        f"{_cell(item['summary'])} | "
        f"{_evidence_refs(item.get('evidence_ids', ()), numbers) or '—'} |"
        for item in result.validations
    ) or "| 无 | 不适用 | 未登记验证项 | — |"
    validation_details = []
    for item in result.validations:
        if item.get("details"):
            refs = _evidence_refs(item.get("evidence_ids", ()), numbers)
            validation_details.append(f"### {item['name']}\n\n{item['details']}" + (f" {refs}" if refs else ""))
    validation_section = (
        "| 验证项 | 状态 | 核心结果 | 证据 |\n|---|---|---|---|\n" + validation_rows
        + ("\n\n" + "\n\n".join(validation_details) if validation_details else "")
    )
    limitations = "\n".join(
        f"- **{item['summary']}**：{item['impact']}" for item in result.limitations
    ) or "未识别出需要单列的适用范围限制。"
    evidence_rows = "\n".join(
        f"| {numbers[item['id']]} | {_cell(item['kind'])} | "
        f"[{_cell(item['path'])}]({_relative_link(workspace, result, item)}) | {_cell(item['purpose'])} |"
        for item in result.evidence["artifacts"]
    ) or "| — | — | — | 未登记证据文件 |"
    review = (
        f"- Result Schema 版本：{result.schema_version}\n"
        f"- 问题编号：Q{result.problem}\n"
        f"- Model Spec revision：{result.spec_revision}\n"
        f"- Model Spec hash：`{result.spec_hash}`\n"
        f"- Result hash：`{result.evidence.get('result_hash', '')}`\n"
        f"- 当前建议状态：{_RECOMMENDATIONS[result.recommendation['status']]}"
    )
    return (
        f"# RESULT Q{result.problem}\n\n## 1. 内容导航\n\n{navigation}\n\n"
        f"## 2. 结果摘要\n\n{'\n\n'.join(summary_parts)}\n\n"
        f"## 3. 技术分析\n\n{technical}\n\n"
        f"## 4. 完整验证与敏感性分析\n\n{validation_section}\n\n"
        f"## 5. 局限与适用范围\n\n{limitations}\n\n"
        f"## 6. 证据索引\n\n| 编号 | 类型 | 路径 | 用途 |\n|---|---|---|---|\n{evidence_rows}\n\n"
        f"## 7. 审阅信息\n\n{review}\n"
    )
