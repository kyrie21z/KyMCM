from __future__ import annotations

import csv
from fractions import Fraction
import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/lite_synthetic_handoff"
DOCS = ROOT / "docs/lite-v3"

START_SECTIONS = (
    "## 1. 问题目标与直接交付",
    "## 2. 已冻结输入与前问继承",
    "## 3. 数据口径与预处理",
    "## 4. 数学模型、参数与判定规则",
    "## 5. Codex 执行边界",
    "## 6. 输出与证据清单",
    "## 7. 验证、求解预算与停止规则",
    "## 8. 未决问题",
)
RESULT_SECTIONS = (
    "## 1. 直接答案",
    "## 2. 实际执行方案与 START 偏差",
    "## 3. 关键结果",
    "## 4. 验证与审计",
    "## 5. 证据索引",
    "## 6. 局限性与风险",
    "## 7. 下游冻结输出",
)
HANDOFF_SECTIONS = (
    "## 1. 论文定位与可用结论",
    "## 2. 数据口径与实际执行",
    "## 3. 模型、参数与判定规则",
    "## 4. 完整关键结果",
    "## 5. 验证、敏感性与异常",
    "## 6. 图表、表格与素材索引",
    "## 7. 推荐论文表述与边界",
    "## 8. 前后问衔接与复核事项",
)
PERMITTED_SENTINELS = {"无", "None", "N/A"}
EVIDENCE = re.compile(r"^- E\d+ — `([^`]+)` — \S.*$")


def markdown_headings(path: Path) -> tuple[str, ...]:
    return tuple(line for line in path.read_text(encoding="utf-8").splitlines() if line.startswith("#"))


def section_text(path: Path, heading: str, following: tuple[str, ...]) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    start = lines.index(heading) + 1
    end = min((lines.index(item) for item in following if item in lines), default=len(lines))
    return "\n".join(lines[start:end]).strip()


def evidence_entries(path: Path) -> list[tuple[str, str]]:
    entries = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.startswith("- E"):
            continue
        matches = re.findall(r"`([^`]*)`", line)
        if len(matches) != 1:
            raise AssertionError(f"{path}: line {line_number} must contain exactly one backticked path")
        match = EVIDENCE.fullmatch(line)
        if not match:
            raise AssertionError(f"{path}: line {line_number} has malformed evidence syntax")
        entries.append((line, match.group(1)))
    return entries


class LiteV3Phase1Tests(unittest.TestCase):
    def test_marker_is_exact_and_only_fixture_json(self):
        marker = FIXTURE / ".kymcm/mode.json"
        self.assertEqual(marker.read_bytes(), b'{"workflow":"kymcm_lite","version":3}\n')
        self.assertEqual(json.loads(marker.read_text(encoding="utf-8")), {"workflow": "kymcm_lite", "version": 3})
        self.assertEqual([path.relative_to(FIXTURE) for path in FIXTURE.rglob("*.json")], [Path(".kymcm/mode.json")])

    def test_starts_have_exact_identity_headings_and_resolved_section(self):
        expected_dependencies = {1: "无", 2: "Q1", 3: "Q1, Q2"}
        for problem in (1, 2, 3):
            path = FIXTURE / f"problems/q{problem}/spec/START_Q{problem}.md"
            with self.subTest(problem=problem):
                self.assertEqual(markdown_headings(path), (f"# START Q{problem}", *START_SECTIONS))
                section = section_text(path, START_SECTIONS[1], START_SECTIONS[2:])
                self.assertEqual(
                    [line for line in section.splitlines() if line.startswith("**前问依赖：**")],
                    [f"**前问依赖：** {expected_dependencies[problem]}"],
                )
                unresolved = section_text(path, START_SECTIONS[-1], ())
                sentinel = unresolved.strip().strip("*_`").strip()
                self.assertIn(sentinel, PERMITTED_SENTINELS, f"{path}: unresolved section is {unresolved!r}")

    def test_results_have_exact_identity_headings_and_deviation_statement(self):
        for problem in (1, 2, 3):
            path = FIXTURE / f"problems/q{problem}/result/RESULT_Q{problem}.md"
            with self.subTest(problem=problem):
                self.assertEqual(markdown_headings(path), (f"# RESULT Q{problem}", *RESULT_SECTIONS))
                deviation = section_text(path, RESULT_SECTIONS[1], RESULT_SECTIONS[2:])
                self.assertTrue(
                    "无偏差" in deviation or ("授权偏差" in deviation and "授权" in deviation),
                    f"{path}: section 2 lacks deviation status",
                )

    def test_evidence_entries_are_safe_existing_question_files(self):
        total = 0
        for problem in (1, 2, 3):
            result = FIXTURE / f"problems/q{problem}/result/RESULT_Q{problem}.md"
            question = (FIXTURE / f"problems/q{problem}").resolve()
            allowed = tuple((question / part).resolve() for part in ("code", "data/derived", "outputs", "notes"))
            entries = evidence_entries(result)
            self.assertTrue(entries, f"{result}: no evidence entries")
            total += len(entries)
            for line, raw in entries:
                with self.subTest(problem=problem, evidence=line):
                    relative = Path(raw)
                    self.assertFalse(relative.is_absolute(), f"absolute evidence path: {raw}")
                    self.assertNotIn("..", relative.parts, f"traversal evidence path: {raw}")
                    path = FIXTURE / relative
                    self.assertTrue(path.is_file(), f"missing/non-file evidence: {raw}")
                    chain = [path, *path.parents]
                    self.assertFalse(any(item.is_symlink() for item in chain if item != FIXTURE.parent), f"symlink evidence: {raw}")
                    resolved = path.resolve()
                    self.assertTrue(any(root == resolved.parent or root in resolved.parents for root in allowed), f"out-of-scope evidence: {raw}")
                    self.assertIn(question, resolved.parents, f"cross-question evidence: {raw}")
        self.assertEqual(total, 9)

    def test_q2_q3_starts_do_not_copy_predecessor_results(self):
        for problem in (2, 3):
            start = (FIXTURE / f"problems/q{problem}/spec/START_Q{problem}.md").read_text(encoding="utf-8")
            with self.subTest(problem=problem):
                self.assertNotIn("# RESULT Q", start)
                self.assertNotIn("## 2. 实际执行方案与 START 偏差", start)
                for predecessor in range(1, problem):
                    complete = (FIXTURE / f"problems/q{predecessor}/result/RESULT_Q{predecessor}.md").read_text(encoding="utf-8")
                    self.assertNotIn(complete, start, f"Q{problem} copied complete RESULT_Q{predecessor}")

    def test_q3_discloses_authorized_extra_sensitivity_point(self):
        result = FIXTURE / "problems/q3/result/RESULT_Q3.md"
        text = result.read_text(encoding="utf-8")
        self.assertIn("额外加入 `λ=3`", text)
        self.assertIn("problems/q3/notes/authorized_deviation.txt", text)
        note = FIXTURE / "problems/q3/notes/authorized_deviation.txt"
        self.assertIn("does not change the primary coefficient 2", note.read_text(encoding="utf-8"))

    def test_fixture_arithmetic_is_internally_consistent(self):
        scenarios = {
            row["scenario"]: tuple(int(row[key]) for key in "ABC")
            for row in csv.DictReader((FIXTURE / "input/uncertainty_scenarios.csv").read_text(encoding="utf-8").splitlines())
        }
        comparison = list(csv.DictReader((FIXTURE / "problems/q2/outputs/risk_comparison.csv").read_text(encoding="utf-8").splitlines()))
        for row in comparison:
            allocation = tuple(int(row[key]) for key in "ABC")
            values = [sum(x * value for x, value in zip(allocation, scenario)) for scenario in scenarios.values()]
            risk = Fraction(3, 5) * Fraction(sum(values), 3) + Fraction(2, 5) * min(values)
            self.assertEqual(values, [int(row[f"{name}_score"]) for name in ("low", "base", "high")], row["candidate"])
            self.assertEqual(risk, Fraction(row["risk_score"]), row["candidate"])
        self.assertEqual(max(comparison, key=lambda row: Fraction(row["risk_score"]))["candidate"], "robust")

        sensitivity = list(csv.DictReader((FIXTURE / "problems/q3/outputs/interaction_sensitivity.csv").read_text(encoding="utf-8").splitlines()))
        candidates = {"q1_baseline": (5, 4, 1), "q2_robust": (4, 4, 2), "balanced_candidate": (4, 3, 3)}
        for row in sensitivity:
            coefficient = int(row["interaction_coefficient"])
            for name, (a, b, c) in candidates.items():
                expected = 9 * a + 8 * b + 7 * c + coefficient * min(b, c) - max(a - 4, 0)
                self.assertEqual(int(row[name]), expected, f"lambda={coefficient}, candidate={name}")
        primary = next(row for row in sensitivity if row["interaction_coefficient"] == "2")
        self.assertEqual(primary["winner"], "balanced_candidate")

    def test_fixture_has_no_full_state_private_or_forbidden_files(self):
        forbidden_names = {
            "problem_definition.json", "model_spec.json", "result_record.json", "workflow.json",
            "events.jsonl", "approval.json", "review_hash.json",
        }
        forbidden_suffixes = {".pyc", ".pyo", ".ttf", ".otf", ".woff", ".woff2", ".pdf"}
        forbidden_text = re.compile(
            r"/home/kyrie|P1C|2012_cumcm|wine_lite|BEGIN (?:OPENSSH|RSA) PRIVATE KEY|api[_-]?key|exported conversation",
            re.IGNORECASE,
        )
        for path in FIXTURE.rglob("*"):
            with self.subTest(path=path.relative_to(FIXTURE)):
                self.assertFalse(path.is_symlink(), f"fixture symlink: {path}")
                if not path.is_file():
                    continue
                self.assertNotIn(path.name, forbidden_names)
                self.assertNotIn(path.suffix.lower(), forbidden_suffixes)
                self.assertLessEqual(path.stat().st_size, 1024 * 1024)
                if path.suffix.lower() in {".md", ".txt", ".csv", ".json"}:
                    self.assertIsNone(forbidden_text.search(path.read_text(encoding="utf-8")), f"forbidden text in {path}")

    def test_template_headings_exactly_match_rfc_contracts(self):
        self.assertFalse((DOCS / "FROZEN_CONTEXT.template.md").exists())
        self.assertEqual(markdown_headings(DOCS / "START_QN.template.md"), ("# START QN", *START_SECTIONS))
        self.assertEqual(markdown_headings(DOCS / "RESULT_QN.template.md"), ("# RESULT QN", *RESULT_SECTIONS))
        rfc = (ROOT / "docs/lite-v3-rfc.md").read_text(encoding="utf-8")
        for sequence in (("# START QN", *START_SECTIONS), ("# RESULT QN", *RESULT_SECTIONS)):
            block = sequence[0] + "\n\n" + "\n".join(sequence[1:])
            self.assertIn(block, rfc, f"RFC lacks exact heading block beginning {sequence[0]}")

    def test_start_template_has_execution_first_guidance_without_contract_change(self):
        template = (DOCS / "START_QN.template.md").read_text(encoding="utf-8")
        for required in (
            "最小直接结论", "冒烟测试", "可恢复执行阶段",
            "嵌套拟合/求解/情景总次数", "L0", "L1", "L2",
        ):
            self.assertIn(required, template)
        self.assertEqual(template.count("**前问依赖：** 无"), 1)
        self.assertEqual(markdown_headings(DOCS / "START_QN.template.md"), ("# START QN", *START_SECTIONS))

    def test_handoff_template_has_exact_identity_headings_and_authority(self):
        template = DOCS / "HANDOFF_QN.template.md"
        text = template.read_text(encoding="utf-8")
        self.assertEqual(markdown_headings(template), ("# HANDOFF QN", *HANDOFF_SECTIONS))
        self.assertIn("**正式上游：** `problems/qN/result/RESULT_QN.md`", text)
        self.assertIn("正式范围以匹配 RESULT 为准", text)
        self.assertIn("具体数值以真实机器证据为准", text)
        self.assertIn("拆分模式不得创建无后缀汇总 HANDOFF", text)

    def test_reviewer_record_has_no_missing_or_ambiguous_items(self):
        record = (DOCS / "reviewer-record.md").read_text(encoding="utf-8")
        statuses = re.findall(r"^\| [^|]+ \| (sufficient|missing|ambiguous) \|", record, re.MULTILINE)
        self.assertEqual(len(statuses), 18, "reviewer record must assess 10 implementer and 8 reviewer items")
        self.assertEqual(set(statuses), {"sufficient"}, f"non-sufficient reviewer assessments: {statuses}")

    def test_benchmark_lite_counts_match_fixture(self):
        report = (DOCS / "benchmark-report.md").read_text(encoding="utf-8")
        self.assertIn("Historical KyMCM Lite 0.1.0 benchmark", report)
        formal = [FIXTURE / f"problems/q{q}/{part}/{name}_Q{q}.md"
                  for q in (1, 2, 3)
                  for part, name in (("spec", "START"), ("result", "RESULT"))]
        evidence_count = sum(len(evidence_entries(FIXTURE / f"problems/q{q}/result/RESULT_Q{q}.md")) for q in (1, 2, 3))
        self.assertEqual(len(formal), 6)
        self.assertTrue(all(path.is_file() for path in formal))
        self.assertEqual(sum(path.stat().st_size for path in formal), 10569)
        self.assertIn("six formal START/RESULT Markdown files totaling 10,569 bytes", (ROOT / "docs/lite-v3-release-notes.md").read_text(encoding="utf-8"))
        self.assertEqual(evidence_count, 9)
        self.assertFalse(any(FIXTURE.rglob("FROZEN_CONTEXT.md")))

    def test_phase1_artifacts_are_independent_of_production_runtime(self):
        paths = [path for path in FIXTURE.rglob("*") if path.is_file()]
        paths.extend(DOCS / name for name in ("START_QN.template.md", "RESULT_QN.template.md"))
        for path in paths:
            if path.suffix.lower() not in {".md", ".txt", ".csv", ".json"}:
                continue
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("from kymcm_lite", text, str(path))
            self.assertNotIn("import kymcm_lite", text, str(path))


if __name__ == "__main__":
    unittest.main()
