from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "skills/kymcm-lite/scripts/lite.py"
FIXTURE = ROOT / "tests/fixtures/lite_synthetic_handoff"
SPLIT_FIXTURE = ROOT / "tests/fixtures/lite_split_handoff"
LITE_TEMPLATES = ROOT / "skills/kymcm-lite/templates"


def fingerprint(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        digest.update(path.relative_to(root).as_posix().encode())
        if path.is_symlink():
            digest.update(os.readlink(path).encode())
        elif path.is_file():
            digest.update(path.read_bytes())
    return digest.hexdigest()


class LiteCliTests(unittest.TestCase):
    def run_cli(self, *args: str, ok: int | None = None) -> subprocess.CompletedProcess[str]:
        env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        completed = subprocess.run([sys.executable, str(CLI), *args], text=True, capture_output=True, env=env)
        if ok is not None:
            self.assertEqual(completed.returncode, ok, completed.stdout + completed.stderr)
        return completed

    def fixture_copy(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temporary = tempfile.TemporaryDirectory()
        workspace = Path(temporary.name) / "workspace"
        shutil.copytree(FIXTURE, workspace)
        return temporary, workspace

    def split_fixture_copy(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temporary = tempfile.TemporaryDirectory()
        workspace = Path(temporary.name) / "workspace"
        shutil.copytree(SPLIT_FIXTURE, workspace)
        return temporary, workspace

    def add_preprocess(self, workspace: Path) -> None:
        root = workspace / "problems/preprocess"
        for part in ("spec", "code", "data", "data/derived", "outputs", "notes", "result"):
            (root / part).mkdir(parents=True, exist_ok=True)
        shutil.copy2(LITE_TEMPLATES / "START_PRE.template.md", root / "spec/START_PRE.md")
        result = (LITE_TEMPLATES / "RESULT_PRE.template.md").read_text(encoding="utf-8")
        result = result.replace(
            "<!-- 示例：- E1 — `problems/preprocess/data/derived/cleaned_data.csv` — 冻结清洗数据 -->",
            "- E1 — `problems/preprocess/data/derived/cleaned_data.csv` — 冻结清洗数据",
        )
        (root / "result/RESULT_PRE.md").write_text(result, encoding="utf-8")
        (root / "data/derived/cleaned_data.csv").write_text("id,value\\n1,2\\n", encoding="utf-8")

    def test_optional_preprocess_init_commands_dependency_and_read_only_checks(self):
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            plain = base / "plain"
            self.run_cli("init", "--workspace", str(plain), "--questions", "1", ok=0)
            self.assertFalse((plain / "problems/preprocess").exists())
            enabled = base / "enabled"
            initialized = self.run_cli(
                "init", "--workspace", str(enabled), "--questions", "1",
                "--preprocess", ok=0,
            )
            self.assertIn("START_PRE", initialized.stdout)
            self.assertIn("No PRE contracts were created", initialized.stdout)
            self.assertIn("templates/RESULT_PRE.template.md", initialized.stdout)
            self.assertIn("no HANDOFF checker", initialized.stdout)
            pre = enabled / "problems/preprocess"
            for part in ("spec", "code", "data", "data/derived", "outputs", "notes", "result"):
                self.assertTrue((pre / part).is_dir(), part)
            self.assertFalse(any(pre.rglob("*PRE*.md")))
            self.assertIn("preprocess=present start=no result=no", self.run_cli(
                "doctor", "--workspace", str(enabled), ok=0
            ).stdout)
            missing = self.run_cli(
                "check-preprocess-start", "--workspace", str(enabled), ok=1
            )
            self.assertIn("LITE-PREPROCESS-START-001", missing.stdout)

        temporary, workspace = self.fixture_copy()
        try:
            self.add_preprocess(workspace)
            q1 = workspace / "problems/q1/spec/START_Q1.md"
            q1.write_text(q1.read_text(encoding="utf-8").replace(
                "**前问依赖：** 无",
                "**预处理依赖：** PRE\n\n**前问依赖：** 无",
            ), encoding="utf-8")
            for command in ("check-preprocess-start", "check-preprocess-result"):
                before = fingerprint(workspace)
                completed = self.run_cli(command, "--workspace", str(workspace), ok=0)
                self.assertEqual(before, fingerprint(workspace), completed.stdout)
            self.run_cli(
                "check-start", "--workspace", str(workspace), "--problem", "1", ok=0
            )
            bad = workspace / "problems/preprocess/result/RESULT_PRE_1.md"
            bad.write_text("# RESULT PRE_1\\n", encoding="utf-8")
            self.assertIn("LITE-PREPROCESS-LAYOUT-001", self.run_cli(
                "doctor", "--workspace", str(workspace), ok=1
            ).stdout)
        finally:
            temporary.cleanup()

    def test_help_exposes_exact_public_commands(self):
        completed = self.run_cli("--help", ok=0)
        for command in (
            "init", "doctor", "check-preprocess-start",
            "check-preprocess-result", "check-start", "check-result",
        ):
            self.assertIn(command, completed.stdout)
        self.assertNotIn("add-problem", completed.stdout)
        for command in ("check-start", "check-result"):
            self.assertIn("--subproblem", self.run_cli(command, "--help", ok=0).stdout)
        for command in (
            "init", "doctor", "check-preprocess-start", "check-preprocess-result",
            "check-appendix-start", "check-appendix-result",
        ):
            self.assertNotIn("--subproblem", self.run_cli(command, "--help", ok=0).stdout)

    def test_split_selection_titles_missing_result_and_doctor_output(self):
        before = fingerprint(SPLIT_FIXTURE)
        completed = self.run_cli("doctor", "--workspace", str(SPLIT_FIXTURE), ok=0)
        self.assertIn("INFO q1 mode=single starts=Q1 results=Q1", completed.stdout)
        self.assertIn(
            "INFO q2 mode=split starts=Q2_1,Q2_2 results=Q2_1,Q2_2",
            completed.stdout,
        )
        for unit in ("1", "2"):
            self.run_cli(
                "check-start", "--workspace", str(SPLIT_FIXTURE),
                "--problem", "2", "--subproblem", unit, ok=0,
            )
            self.run_cli(
                "check-result", "--workspace", str(SPLIT_FIXTURE),
                "--problem", "2", "--subproblem", unit, ok=0,
            )
        self.assertIn(
            "LITE-CONTRACT-SELECT-001",
            self.run_cli(
                "check-start", "--workspace", str(SPLIT_FIXTURE),
                "--problem", "2", ok=1,
            ).stdout,
        )
        unknown = self.run_cli(
            "check-result", "--workspace", str(SPLIT_FIXTURE),
            "--problem", "2", "--subproblem", "3", ok=1,
        )
        self.assertIn("LITE-CONTRACT-SELECT-001", unknown.stdout)
        self.assertEqual(unknown.stdout.count("SUMMARY "), 1)
        self.assertIn(
            "LITE-CONTRACT-SELECT-001",
            self.run_cli(
                "check-start", "--workspace", str(SPLIT_FIXTURE),
                "--problem", "1", "--subproblem", "1", ok=1,
            ).stdout,
        )
        temporary, workspace = self.split_fixture_copy()
        try:
            (workspace / "problems/q2/result/RESULT_Q2_2.md").unlink()
            partial = self.run_cli("doctor", "--workspace", str(workspace), ok=0)
            self.assertIn(
                "INFO q2 mode=split starts=Q2_1,Q2_2 results=Q2_1",
                partial.stdout,
            )
            missing = self.run_cli(
                "check-result", "--workspace", str(workspace),
                "--problem", "2", "--subproblem", "2", ok=1,
            )
            self.assertIn("LITE-RESULT-001", missing.stdout)
            self.assertIn("RESULT_Q2_2.md", missing.stdout)
        finally:
            temporary.cleanup()
        temporary, workspace = self.split_fixture_copy()
        try:
            selected = workspace / "problems/q2/spec/START_Q2_1.md"
            selected.write_text(
                selected.read_text(encoding="utf-8").replace(
                    "# START Q2_1", "# START Q2_2", 1
                ),
                encoding="utf-8",
            )
            invalid_title = self.run_cli(
                "check-start", "--workspace", str(workspace),
                "--problem", "2", "--subproblem", "1", ok=1,
            )
            self.assertIn("LITE-START-001", invalid_title.stdout)
        finally:
            temporary.cleanup()
        self.assertEqual(before, fingerprint(SPLIT_FIXTURE))

    def test_split_layout_failures_are_blocking_without_traceback(self):
        mutations = {
            "mixed": lambda root: shutil.copy2(
                root / "problems/q2/spec/START_Q2_1.md",
                root / "problems/q2/spec/START_Q2.md",
            ),
            "gap": lambda root: (
                root / "problems/q2/spec/START_Q2_2.md"
            ).rename(root / "problems/q2/spec/START_Q2_3.md"),
            "orphan": lambda root: (
                root / "problems/q2/result/RESULT_Q2_2.md"
            ).rename(root / "problems/q2/result/RESULT_Q2_3.md"),
        }
        for name, mutate in mutations.items():
            temporary, workspace = self.split_fixture_copy()
            try:
                mutate(workspace)
                completed = self.run_cli(
                    "doctor", "--workspace", str(workspace), ok=1
                )
                self.assertIn("LITE-CONTRACT-LAYOUT-001", completed.stdout, name)
                self.assertNotIn("Traceback", completed.stdout + completed.stderr, name)
            finally:
                temporary.cleanup()

    def test_split_dependency_mode_and_exact_pair_rules(self):
        temporary, workspace = self.split_fixture_copy()
        try:
            q1_start = workspace / "problems/q1/spec/START_Q1.md"
            q1_result = workspace / "problems/q1/result/RESULT_Q1.md"
            split_start = q1_start.with_name("START_Q1_1.md")
            split_result = q1_result.with_name("RESULT_Q1_1.md")
            q1_start.rename(split_start)
            q1_result.rename(split_result)
            split_start.write_text(
                split_start.read_text(encoding="utf-8").replace(
                    "# START Q1", "# START Q1_1", 1
                ),
                encoding="utf-8",
            )
            split_result.write_text(
                split_result.read_text(encoding="utf-8").replace(
                    "# RESULT Q1", "# RESULT Q1_1", 1
                ),
                encoding="utf-8",
            )
            second_start = split_start.with_name("START_Q1_2.md")
            second_result = split_result.with_name("RESULT_Q1_2.md")
            shutil.copy2(split_start, second_start)
            shutil.copy2(split_result, second_result)
            second_start.write_text(
                second_start.read_text(encoding="utf-8").replace(
                    "# START Q1_1", "# START Q1_2", 1
                ),
                encoding="utf-8",
            )
            second_result.write_text(
                second_result.read_text(encoding="utf-8").replace(
                    "# RESULT Q1_1", "# RESULT Q1_2", 1
                ),
                encoding="utf-8",
            )
            current = workspace / "problems/q2/spec/START_Q2_1.md"
            current.write_text(
                current.read_text(encoding="utf-8").replace(
                    "**前问依赖：** Q1", "**前问依赖：** Q1_1, Q1_2"
                ),
                encoding="utf-8",
            )
            valid = self.run_cli(
                "check-start", "--workspace", str(workspace),
                "--problem", "2", "--subproblem", "1", ok=0,
            )
            self.assertNotIn("LITE-START-DEPENDENCY", valid.stdout)
            current.write_text(
                current.read_text(encoding="utf-8").replace(
                    "**前问依赖：** Q1_1, Q1_2", "**前问依赖：** Q1"
                ),
                encoding="utf-8",
            )
            bare = self.run_cli(
                "check-start", "--workspace", str(workspace),
                "--problem", "2", "--subproblem", "1", ok=1,
            )
            self.assertIn("LITE-START-DEPENDENCY-SCOPE-001", bare.stdout)
            current.write_text(
                current.read_text(encoding="utf-8").replace(
                    "**前问依赖：** Q1", "**前问依赖：** Q1_1, Q1_2"
                ),
                encoding="utf-8",
            )
            second_result.unlink()
            missing = self.run_cli(
                "check-result", "--workspace", str(workspace),
                "--problem", "2", "--subproblem", "1", ok=1,
            )
            self.assertEqual(
                missing.stdout.count("LITE-START-DEPENDENCY-CONTRACT-001"), 1
            )
        finally:
            temporary.cleanup()

        temporary, workspace = self.split_fixture_copy()
        try:
            current = workspace / "problems/q2/spec/START_Q2_1.md"
            current.write_text(
                current.read_text(encoding="utf-8").replace(
                    "**前问依赖：** Q1", "**前问依赖：** Q1_1"
                ),
                encoding="utf-8",
            )
            completed = self.run_cli(
                "check-start", "--workspace", str(workspace),
                "--problem", "2", "--subproblem", "1", ok=1,
            )
            self.assertIn("LITE-START-DEPENDENCY-SCOPE-001", completed.stdout)
        finally:
            temporary.cleanup()

    def test_init_variable_counts_unrelated_root_and_only_mode_json(self):
        for count in (1, 3, 6):
            with self.subTest(count=count), tempfile.TemporaryDirectory() as raw:
                workspace = Path(raw); (workspace / "unrelated.txt").write_text("keep", encoding="utf-8")
                self.run_cli("init", "--workspace", str(workspace), "--questions", str(count), ok=0)
                self.assertEqual((workspace / "unrelated.txt").read_text(), "keep")
                self.assertEqual((workspace / ".kymcm/mode.json").read_bytes(), b'{"workflow":"kymcm_lite","version":3}\n')
                self.assertEqual(len(list((workspace / "problems").glob("q*"))), count)
                self.assertEqual([p.relative_to(workspace) for p in workspace.rglob("*.json")], [Path(".kymcm/mode.json")])
                self.assertFalse((workspace / "FROZEN_CONTEXT.md").exists())
                self.assertFalse((workspace / "paper").exists())
                self.assertFalse(any(workspace.rglob("START_*.md")))
                self.assertFalse(any(workspace.rglob("RESULT_*.md")))

    def test_init_conflict_is_all_or_nothing(self):
        with tempfile.TemporaryDirectory() as raw:
            workspace = Path(raw); conflict = workspace / "input"; conflict.mkdir(); keep = conflict / "keep"; keep.write_text("x")
            before = fingerprint(workspace)
            completed = self.run_cli("init", "--workspace", str(workspace), "--questions", "3", ok=1)
            self.assertIn("LITE-LAYOUT-001", completed.stdout)
            self.assertEqual(before, fingerprint(workspace))

    def test_doctor_is_read_only_and_unknown_roots_are_info(self):
        temporary, workspace = self.fixture_copy()
        try:
            (workspace / "extra.txt").write_text("allowed", encoding="utf-8")
            before = fingerprint(workspace)
            completed = self.run_cli("doctor", "--workspace", str(workspace), ok=0)
            self.assertIn("INFO unknown-root-entries=extra.txt", completed.stdout)
            self.assertEqual(before, fingerprint(workspace))
        finally:
            temporary.cleanup()

    def test_phase1_fixture_q1_to_q3_passes_read_only(self):
        before = fingerprint(FIXTURE)
        for problem in (1, 2, 3):
            self.run_cli("check-start", "--workspace", str(FIXTURE), "--problem", str(problem), ok=0)
            self.run_cli("check-result", "--workspace", str(FIXTURE), "--problem", str(problem), ok=0)
        self.assertEqual(before, fingerprint(FIXTURE))

    def test_absent_full_old_malformed_and_unknown_markers_fail_closed(self):
        values = (None, {"workflow": "kymcm_full", "version": 1}, {"workflow": "checkpoint_lite", "version": 2}, {"workflow": "kymcm_lite", "version": 99}, "bad")
        for value in values:
            temporary, workspace = self.fixture_copy()
            try:
                marker = workspace / ".kymcm/mode.json"
                if value is None: marker.unlink()
                elif value == "bad": marker.write_text("{bad", encoding="utf-8")
                else: marker.write_text(json.dumps(value) + "\n", encoding="utf-8")
                completed = self.run_cli("check-start", "--workspace", str(workspace), "--problem", "1", ok=1)
                self.assertIn("LITE-MODE-001", completed.stdout)
            finally:
                temporary.cleanup()

    def test_start_heading_failures_and_unresolved_are_blocking(self):
        variants = {
            "missing": lambda text: text.replace("## 3. 数据口径与预处理\n", ""),
            "duplicate": lambda text: text.replace("## 3. 数据口径与预处理\n", "## 3. 数据口径与预处理\n## 3. 数据口径与预处理\n"),
            "reordered": lambda text: text.replace("## 2. 已冻结输入与前问继承", "## X").replace("## 3. 数据口径与预处理", "## 2. 已冻结输入与前问继承").replace("## X", "## 3. 数据口径与预处理"),
            "fenced": lambda text: text.replace("## 3. 数据口径与预处理", "```md\n## 3. 数据口径与预处理\n```"),
            "unresolved": lambda text: text[:-2] + "需要决定\n",
        }
        for name, mutate in variants.items():
            temporary, workspace = self.fixture_copy()
            try:
                path = workspace / "problems/q1/spec/START_Q1.md"; path.write_text(mutate(path.read_text(encoding="utf-8")), encoding="utf-8")
                completed = self.run_cli("check-start", "--workspace", str(workspace), "--problem", "1", ok=1)
                expected = "LITE-START-UNRESOLVED-001" if name == "unresolved" else "LITE-START-HEADING-001"
                self.assertIn(expected, completed.stdout)
            finally: temporary.cleanup()

    def test_result_deviation_and_evidence_format_failures(self):
        mutations = {
            "deviation": ("无偏差", "执行一致"),
            "no_evidence": ("- E1 — `problems/q1/outputs/baseline_allocation.csv` — 冻结分配与贡献表\n- E2 — `problems/q1/outputs/validation.txt` — 可行性与目标值审计", ""),
            "malformed": ("- E1 — `problems/q1/outputs/baseline_allocation.csv` — 冻结分配与贡献表", "- E1 `problems/q1/outputs/baseline_allocation.csv` bad"),
            "duplicate": ("- E2 — `problems/q1/outputs/validation.txt` — 可行性与目标值审计", "- E1 — `problems/q1/outputs/validation.txt` — 可行性与目标值审计"),
        }
        for name, (old, new) in mutations.items():
            temporary, workspace = self.fixture_copy()
            try:
                path = workspace / "problems/q1/result/RESULT_Q1.md"; path.write_text(path.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")
                completed = self.run_cli("check-result", "--workspace", str(workspace), "--problem", "1", ok=1)
                self.assertIn("LITE-RESULT-DEVIATION-001" if name == "deviation" else "LITE-EVIDENCE-FORMAT-001", completed.stdout)
            finally: temporary.cleanup()

    def test_commented_and_fenced_result_examples_are_inactive(self):
        evidence = "- E1 — `problems/q1/outputs/baseline_allocation.csv` — 冻结分配与贡献表\n- E2 — `problems/q1/outputs/validation.txt` — 可行性与目标值审计"
        cases = {
            "commented_deviation": ("按 START 的整数线性目标和全部约束进行小规模枚举，并以手工边际价值论证复核。无偏差。", "<!-- 无偏差 -->", "LITE-RESULT-DEVIATION-001"),
            "fenced_deviation": ("按 START 的整数线性目标和全部约束进行小规模枚举，并以手工边际价值论证复核。无偏差。", "```md\n无偏差\n```", "LITE-RESULT-DEVIATION-001"),
            "commented_authorized": ("按 START 的整数线性目标和全部约束进行小规模枚举，并以手工边际价值论证复核。无偏差。", "<!-- 授权偏差 `problems/q1/notes/authorization.md` -->", "LITE-RESULT-DEVIATION-001"),
            "fenced_authorized": ("按 START 的整数线性目标和全部约束进行小规模枚举，并以手工边际价值论证复核。无偏差。", "~~~md\n授权偏差 `problems/q1/notes/authorization.md`\n~~~", "LITE-RESULT-DEVIATION-001"),
            "commented_evidence": (evidence, f"<!--\n{evidence}\n-->", "LITE-EVIDENCE-FORMAT-001"),
            "fenced_evidence": (evidence, f"```md\n{evidence}\n```", "LITE-EVIDENCE-FORMAT-001"),
            "fenced_validation": ("分配均为整数且总和为 10；三个上下限全部满足。", "```md\nvalidation example\n```", "LITE-RESULT-VALIDATION-WARN-001"),
            "commented_downstream": ("后续问题可继承 A=5、B=4、C=1 和基准分数 84。Q2 使用的正式接口为 `problems/q2/data/derived/q1_baseline_snapshot.csv`；枚举过程仅限本题。", "<!-- 无后续问题 -->", "LITE-RESULT-DOWNSTREAM-WARN-001"),
        }
        for name, (old, new, expected) in cases.items():
            temporary, workspace = self.fixture_copy()
            try:
                result = workspace / "problems/q1/result/RESULT_Q1.md"
                result.write_text(result.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")
                completed = self.run_cli("check-result", "--workspace", str(workspace), "--problem", "1")
                self.assertIn(expected, completed.stdout, name)
            finally:
                temporary.cleanup()

    def test_active_result_content_after_examples_still_passes(self):
        temporary, workspace = self.fixture_copy()
        try:
            result = workspace / "problems/q1/result/RESULT_Q1.md"
            text = result.read_text(encoding="utf-8")
            text = text.replace("按 START 的整数线性目标和全部约束进行小规模枚举，并以手工边际价值论证复核。无偏差。", "<!-- 无偏差 -->\n```md\n授权偏差 `../unsafe`\n```\n实际执行与 START 一致，无偏差。")
            result.write_text(text, encoding="utf-8")
            completed = self.run_cli("check-result", "--workspace", str(workspace), "--problem", "1", ok=0)
            self.assertNotIn("LITE-RESULT-DEVIATION-001", completed.stdout)
        finally:
            temporary.cleanup()

    def test_unsafe_evidence_categories_are_blocking(self):
        cases = {
            "traversal": "../outside.txt", "absolute": "/tmp/outside.txt", "windows": r"C:\\outside.txt",
            "cross_question": "problems/q2/outputs/risk_comparison.csv", "directory": "problems/q1/outputs", "missing": "problems/q1/outputs/missing.txt",
        }
        for name, raw_path in cases.items():
            temporary, workspace = self.fixture_copy()
            try:
                result = workspace / "problems/q1/result/RESULT_Q1.md"
                text = result.read_text(encoding="utf-8")
                text = text.replace("problems/q1/outputs/baseline_allocation.csv", raw_path)
                result.write_text(text, encoding="utf-8")
                completed = self.run_cli("check-result", "--workspace", str(workspace), "--problem", "1", ok=1)
                self.assertRegex(completed.stdout, r"LITE-EVIDENCE-(PATH|SCOPE|MISSING)-001", name)
            finally: temporary.cleanup()

    def test_file_directory_broken_and_escape_symlinks_are_blocking(self):
        temporary, workspace = self.fixture_copy()
        try:
            target = workspace / "problems/q1/outputs/baseline_allocation.csv"
            real = workspace / "real.csv"; target.replace(real); target.symlink_to(real)
            completed = self.run_cli("check-result", "--workspace", str(workspace), "--problem", "1", ok=1)
            self.assertIn("LITE-EVIDENCE-SYMLINK-001", completed.stdout)
        finally: temporary.cleanup()
        temporary, workspace = self.fixture_copy()
        try:
            outputs = workspace / "problems/q1/outputs"; shutil.rmtree(outputs); outputs.symlink_to(Path(temporary.name), target_is_directory=True)
            completed = self.run_cli("check-result", "--workspace", str(workspace), "--problem", "1", ok=1)
            self.assertIn("LITE-LAYOUT-SYMLINK-001", completed.stdout)
        finally: temporary.cleanup()
        temporary, workspace = self.fixture_copy()
        try:
            target = workspace / "problems/q1/outputs/baseline_allocation.csv"; target.unlink(); target.symlink_to(workspace / "missing")
            completed = self.run_cli("check-result", "--workspace", str(workspace), "--problem", "1", ok=1)
            self.assertIn("LITE-EVIDENCE-SYMLINK-001", completed.stdout)
        finally: temporary.cleanup()

    def test_warnings_return_zero_and_legacy_roots_are_never_read(self):
        with tempfile.TemporaryDirectory() as raw:
            workspace = Path(raw) / "workspace"
            self.run_cli("init", "--workspace", str(workspace), "--questions", "1", ok=0)
            completed = self.run_cli("doctor", "--workspace", str(workspace), ok=0)
            self.assertIn("LITE-GIT-WARN-001", completed.stdout)
        temporary, workspace = self.fixture_copy()
        try:
            (workspace / "FROZEN_CONTEXT.md").write_bytes(b"\xff\xfe")
            legacy = workspace / "paper"
            legacy.mkdir(exist_ok=True)
            (legacy / "invalid.md").write_bytes(b"\xff\xfe")
            (legacy / "broken").symlink_to(legacy / "missing")
            before = fingerprint(workspace)
            for args in (
                ("doctor",),
                ("check-start", "--problem", "1"),
                ("check-result", "--problem", "1"),
            ):
                completed = self.run_cli(args[0], "--workspace", str(workspace), *args[1:], ok=0)
                self.assertNotIn("FROZEN_CONTEXT", completed.stdout + completed.stderr)
                self.assertNotIn("paper", completed.stdout + completed.stderr)
                self.assertEqual(fingerprint(workspace), before)
        finally: temporary.cleanup()

    def test_dependency_declaration_valid_forms(self):
        for problem in (1, 2, 3):
            completed = self.run_cli(
                "check-start", "--workspace", str(FIXTURE), "--problem", str(problem), ok=0
            )
            self.assertNotIn("LITE-START-DEPENDENCY", completed.stdout)
        temporary, workspace = self.fixture_copy()
        try:
            start = workspace / "problems/q2/spec/START_Q2.md"
            start.write_text(
                start.read_text(encoding="utf-8").replace("**前问依赖：** Q1", "**前问依赖：** 无"),
                encoding="utf-8",
            )
            self.run_cli("check-start", "--workspace", str(workspace), "--problem", "2", ok=0)
        finally:
            temporary.cleanup()

    def test_dependency_declaration_missing_duplicate_and_inactive_examples(self):
        mutations = {
            "missing": "",
            "duplicate": "**前问依赖：** Q1\n**前问依赖：** Q1",
            "comment": "<!-- **前问依赖：** Q1 -->",
            "fence": "```md\n**前问依赖：** Q1\n```",
        }
        for name, replacement in mutations.items():
            temporary, workspace = self.fixture_copy()
            try:
                start = workspace / "problems/q2/spec/START_Q2.md"
                start.write_text(
                    start.read_text(encoding="utf-8").replace("**前问依赖：** Q1", replacement),
                    encoding="utf-8",
                )
                completed = self.run_cli(
                    "check-start", "--workspace", str(workspace), "--problem", "2", ok=1
                )
                self.assertIn("LITE-START-DEPENDENCY-001", completed.stdout, name)
            finally:
                temporary.cleanup()

    def test_dependency_grammar_and_scope_failures(self):
        cases = {
            "separator": (3, "Q1,Q2", "LITE-START-DEPENDENCY-001"),
            "lowercase": (2, "q1", "LITE-START-DEPENDENCY-001"),
            "leading-zero": (2, "Q01", "LITE-START-DEPENDENCY-001"),
            "duplicate": (3, "Q1, Q1", "LITE-START-DEPENDENCY-SCOPE-001"),
            "unsorted": (3, "Q2, Q1", "LITE-START-DEPENDENCY-SCOPE-001"),
            "self": (2, "Q2", "LITE-START-DEPENDENCY-SCOPE-001"),
            "forward": (2, "Q3", "LITE-START-DEPENDENCY-SCOPE-001"),
            "zero": (2, "Q0", "LITE-START-DEPENDENCY-SCOPE-001"),
            "negative": (2, "Q-1", "LITE-START-DEPENDENCY-SCOPE-001"),
        }
        for name, (problem, value, identifier) in cases.items():
            temporary, workspace = self.fixture_copy()
            try:
                start = workspace / f"problems/q{problem}/spec/START_Q{problem}.md"
                old = "Q1, Q2" if problem == 3 else "Q1"
                start.write_text(
                    start.read_text(encoding="utf-8").replace(
                        f"**前问依赖：** {old}", f"**前问依赖：** {value}"
                    ),
                    encoding="utf-8",
                )
                completed = self.run_cli(
                    "check-start", "--workspace", str(workspace), "--problem", str(problem), ok=1
                )
                self.assertIn(identifier, completed.stdout, name)
            finally:
                temporary.cleanup()

        temporary, workspace = self.fixture_copy()
        try:
            start = workspace / "problems/q1/spec/START_Q1.md"
            start.write_text(
                start.read_text(encoding="utf-8").replace("**前问依赖：** 无", "**前问依赖：** Q1"),
                encoding="utf-8",
            )
            completed = self.run_cli(
                "check-start", "--workspace", str(workspace), "--problem", "1", ok=1
            )
            self.assertIn("LITE-START-DEPENDENCY-SCOPE-001", completed.stdout)
        finally:
            temporary.cleanup()

        temporary, workspace = self.fixture_copy()
        try:
            shutil.rmtree(workspace / "problems/q1")
            completed = self.run_cli(
                "check-start", "--workspace", str(workspace), "--problem", "2", ok=1
            )
            self.assertIn("LITE-START-DEPENDENCY-SCOPE-001", completed.stdout)
        finally:
            temporary.cleanup()

    def test_dependency_upstream_contract_availability_and_structure(self):
        cases = ("missing-start", "symlink-result", "invalid-utf8", "invalid-heading")
        for name in cases:
            temporary, workspace = self.fixture_copy()
            try:
                start = workspace / "problems/q1/spec/START_Q1.md"
                result = workspace / "problems/q1/result/RESULT_Q1.md"
                if name == "missing-start":
                    start.unlink()
                elif name == "symlink-result":
                    target = workspace / "q1-result-copy.md"
                    result.replace(target)
                    result.symlink_to(target)
                elif name == "invalid-utf8":
                    result.write_bytes(b"\xff\xfe")
                else:
                    start.write_text(
                        start.read_text(encoding="utf-8").replace(
                            "## 3. 数据口径与预处理", "## 3. wrong"
                        ),
                        encoding="utf-8",
                    )
                completed = self.run_cli(
                    "check-start", "--workspace", str(workspace), "--problem", "2", ok=1
                )
                self.assertIn("LITE-START-DEPENDENCY-CONTRACT-001", completed.stdout, name)
            finally:
                temporary.cleanup()

    def test_upstream_dependency_validation_is_lightweight_and_result_inherits_it(self):
        temporary, workspace = self.fixture_copy()
        try:
            upstream = workspace / "problems/q1/spec/START_Q1.md"
            upstream.write_text(
                upstream.read_text(encoding="utf-8").replace("**前问依赖：** 无", ""),
                encoding="utf-8",
            )
            completed = self.run_cli(
                "check-start", "--workspace", str(workspace), "--problem", "2", ok=0
            )
            self.assertNotIn("LITE-START-DEPENDENCY-001", completed.stdout)

            current = workspace / "problems/q2/spec/START_Q2.md"
            current.write_text(
                current.read_text(encoding="utf-8").replace(
                    "**前问依赖：** Q1", "**前问依赖：** q1"
                ),
                encoding="utf-8",
            )
            completed = self.run_cli(
                "check-result", "--workspace", str(workspace), "--problem", "2", ok=1
            )
            self.assertEqual(completed.stdout.count("LITE-START-DEPENDENCY-001"), 1)
        finally:
            temporary.cleanup()

    def test_output_order_is_deterministic(self):
        args = ("doctor", "--workspace", str(FIXTURE))
        first = self.run_cli(*args, ok=0).stdout
        second = self.run_cli(*args, ok=0).stdout
        self.assertEqual(first, second)

    def test_git_unavailable_and_question_scoped_dirty_state_are_advisory(self):
        temporary, workspace = self.fixture_copy()
        try:
            env = {**os.environ, "PATH": os.path.dirname(sys.executable), "PYTHONDONTWRITEBYTECODE": "1"}
            completed = subprocess.run(
                [sys.executable, str(CLI), "doctor", "--workspace", str(workspace)],
                text=True, capture_output=True, env=env,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            self.assertIn("LITE-GIT-WARN-001", completed.stdout)
        finally:
            temporary.cleanup()

        mutations = {
            "clean": None,
            "code": "problems/q1/code/solve.py",
            "derived": "problems/q1/data/derived/candidates.csv",
            "unrelated": "problems/q1/notes/review.txt",
        }
        for name, relative in mutations.items():
            temporary, workspace = self.fixture_copy()
            try:
                subprocess.run(["git", "init", "-q", str(workspace)], check=True)
                subprocess.run(["git", "-C", str(workspace), "config", "user.name", "Lite Test"], check=True)
                subprocess.run(["git", "-C", str(workspace), "config", "user.email", "lite@example.invalid"], check=True)
                subprocess.run(["git", "-C", str(workspace), "add", "."], check=True)
                subprocess.run(["git", "-C", str(workspace), "commit", "-qm", "fixture"], check=True)
                if relative:
                    path = workspace / relative
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(path.read_text(encoding="utf-8") + "\nchanged\n" if path.exists() else "changed\n", encoding="utf-8")
                completed = self.run_cli("check-result", "--workspace", str(workspace), "--problem", "1", ok=0)
                if name in {"code", "derived"}:
                    self.assertIn("LITE-GIT-DIRTY-WARN-001", completed.stdout, name)
                else:
                    self.assertNotIn("LITE-GIT-DIRTY-WARN-001", completed.stdout, name)
            finally:
                temporary.cleanup()


if __name__ == "__main__":
    unittest.main()
