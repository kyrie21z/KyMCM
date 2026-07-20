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

CONTEXT_HEADINGS = (
    "# FROZEN CONTEXT",
    "## 1. 共享定义与符号",
    "## 2. 全局数据口径",
    "## 3. 已冻结参数与规则",
    "## 4. 跨题输出与文件接口",
    "## 5. 当前限制与注意事项",
)
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

    def test_context_has_exact_heading_order(self):
        self.assertEqual(markdown_headings(FIXTURE / "FROZEN_CONTEXT.md"), CONTEXT_HEADINGS)

    def test_starts_have_exact_identity_headings_and_resolved_section(self):
        for problem in (1, 2, 3):
            path = FIXTURE / f"problems/q{problem}/spec/START_Q{problem}.md"
            with self.subTest(problem=problem):
                self.assertEqual(markdown_headings(path), (f"# START Q{problem}", *START_SECTIONS))
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
        self.assertEqual(markdown_headings(DOCS / "FROZEN_CONTEXT.template.md"), CONTEXT_HEADINGS)
        self.assertEqual(markdown_headings(DOCS / "START_QN.template.md"), ("# START QN", *START_SECTIONS))
        self.assertEqual(markdown_headings(DOCS / "RESULT_QN.template.md"), ("# RESULT QN", *RESULT_SECTIONS))
        rfc = (ROOT / "docs/lite-v3-rfc.md").read_text(encoding="utf-8")
        for sequence in (CONTEXT_HEADINGS, ("# START QN", *START_SECTIONS), ("# RESULT QN", *RESULT_SECTIONS)):
            block = sequence[0] + "\n\n" + "\n".join(sequence[1:])
            self.assertIn(block, rfc, f"RFC lacks exact heading block beginning {sequence[0]}")

    def test_reviewer_record_has_no_missing_or_ambiguous_items(self):
        record = (DOCS / "reviewer-record.md").read_text(encoding="utf-8")
        statuses = re.findall(r"^\| [^|]+ \| (sufficient|missing|ambiguous) \|", record, re.MULTILINE)
        self.assertEqual(len(statuses), 18, "reviewer record must assess 10 implementer and 8 reviewer items")
        self.assertEqual(set(statuses), {"sufficient"}, f"non-sufficient reviewer assessments: {statuses}")

    def test_benchmark_lite_counts_match_fixture(self):
        report = (DOCS / "benchmark-report.md").read_text(encoding="utf-8")
        recorded = {key: int(value) for key, value in re.findall(r"^\| `(lite_[a-z0-9_]+)` \| (\d+) \|$", report, re.MULTILINE)}
        all_formal = [FIXTURE / "FROZEN_CONTEXT.md"]
        all_formal += [FIXTURE / f"problems/q{q}/spec/START_Q{q}.md" for q in (1, 2, 3)]
        all_formal += [FIXTURE / f"problems/q{q}/result/RESULT_Q{q}.md" for q in (1, 2, 3)]
        q1_common = [FIXTURE / "problems/q1/spec/START_Q1.md", FIXTURE / "problems/q1/result/RESULT_Q1.md"]
        q1_time_aligned = [FIXTURE / "review_snapshots/before_q2/FROZEN_CONTEXT.md", *q1_common]
        q1_final_context = [FIXTURE / "FROZEN_CONTEXT.md", *q1_common]
        self.assertEqual(q1_time_aligned[0].relative_to(FIXTURE), Path("review_snapshots/before_q2/FROZEN_CONTEXT.md"))
        self.assertEqual(q1_final_context[0].relative_to(FIXTURE), Path("FROZEN_CONTEXT.md"))
        self.assertEqual(len(q1_time_aligned), 3)
        self.assertEqual(len(q1_final_context), 3)
        evidence_count = sum(len(evidence_entries(FIXTURE / f"problems/q{q}/result/RESULT_Q{q}.md")) for q in (1, 2, 3))
        expected = {
            "lite_q1_time_aligned_formal_files": len(q1_time_aligned),
            "lite_q1_time_aligned_formal_bytes": sum(path.stat().st_size for path in q1_time_aligned),
            "lite_q1_final_context_formal_files": len(q1_final_context),
            "lite_q1_final_context_formal_bytes": sum(path.stat().st_size for path in q1_final_context),
            "lite_all_formal_files": len(all_formal),
            "lite_all_formal_bytes": sum(path.stat().st_size for path in all_formal),
            "lite_marker_files": 1,
            "lite_marker_bytes": (FIXTURE / ".kymcm/mode.json").stat().st_size,
            "lite_result_evidence_references": evidence_count,
            "lite_safe_evidence_references": evidence_count,
        }
        self.assertEqual(recorded, expected)
        self.assertLessEqual(expected["lite_q1_time_aligned_formal_bytes"], expected["lite_q1_final_context_formal_bytes"])

        full_match = re.search(r"\| Primary formal bytes \| ([\d,]+) \| ([\d,]+) \|", report)
        time_reduction = re.search(r"Time-aligned Lite removes ([\d,]+) of [\d,]+ primary formal bytes, a measured reduction of \*\*([\d.]+)%\*\*", report)
        final_reduction = re.search(r"Its three files total [\d,]+ bytes and reduce the Full denominator by ([\d,]+) bytes, or \*\*([\d.]+)%\*\*", report)
        self.assertIsNotNone(full_match, "benchmark report lacks primary formal byte row")
        self.assertIsNotNone(time_reduction, "benchmark report lacks time-aligned reduction")
        self.assertIsNotNone(final_reduction, "benchmark report lacks final-context reduction")
        full_bytes = int(full_match.group(1).replace(",", ""))
        self.assertEqual(int(full_match.group(2).replace(",", "")), expected["lite_q1_time_aligned_formal_bytes"])
        for match, lite_bytes in (
            (time_reduction, expected["lite_q1_time_aligned_formal_bytes"]),
            (final_reduction, expected["lite_q1_final_context_formal_bytes"]),
        ):
            reduction = full_bytes - lite_bytes
            self.assertEqual(int(match.group(1).replace(",", "")), reduction)
            self.assertEqual(float(match.group(2)), round(100 * reduction / full_bytes, 1))

    def test_phase1_artifacts_are_independent_of_production_runtime(self):
        paths = [path for path in FIXTURE.rglob("*") if path.is_file()]
        paths.extend(DOCS / name for name in ("FROZEN_CONTEXT.template.md", "START_QN.template.md", "RESULT_QN.template.md"))
        for path in paths:
            if path.suffix.lower() not in {".md", ".txt", ".csv", ".json"}:
                continue
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("from kymcm_lite", text, str(path))
            self.assertNotIn("import kymcm_lite", text, str(path))


if __name__ == "__main__":
    unittest.main()
