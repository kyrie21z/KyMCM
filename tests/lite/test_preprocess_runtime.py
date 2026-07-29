from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "skills/kymcm-lite"
SCRIPTS = SKILL / "scripts"
FIXTURE = ROOT / "tests/fixtures/lite_synthetic_handoff"
sys.path.insert(0, str(SCRIPTS))

from kymcm_lite import cli
from kymcm_lite.contracts import (
    PREPROCESS_RESULT_HEADINGS, PREPROCESS_START_HEADINGS,
    check_preprocess_result, check_preprocess_start, check_result, check_start,
    doctor,
)


def ids(diagnostics):
    return {item.identifier for item in diagnostics}


class PreprocessRuntimeTests(unittest.TestCase):
    def fixture_copy(self):
        temporary = tempfile.TemporaryDirectory()
        workspace = Path(temporary.name) / "workspace"
        shutil.copytree(FIXTURE, workspace)
        return temporary, workspace

    def add_preprocess(self, workspace: Path) -> Path:
        pre = workspace / "problems/preprocess"
        for part in ("spec", "code", "data", "data/derived", "outputs", "notes", "result"):
            (pre / part).mkdir(parents=True, exist_ok=True)
        shutil.copy2(SKILL / "templates/START_PRE.template.md", pre / "spec/START_PRE.md")
        result = (SKILL / "templates/RESULT_PRE.template.md").read_text(encoding="utf-8")
        result = result.replace(
            "<!-- 示例：- E1 — `problems/preprocess/data/derived/cleaned_data.csv` — 冻结清洗数据 -->",
            "- E1 — `problems/preprocess/data/derived/cleaned_data.csv` — 冻结清洗数据",
        )
        (pre / "result/RESULT_PRE.md").write_text(result, encoding="utf-8")
        (pre / "data/derived/cleaned_data.csv").write_text("id,value\n1,2\n", encoding="utf-8")
        return pre

    def declare(self, workspace: Path, value: str = "PRE", problem: int = 1) -> Path:
        path = workspace / f"problems/q{problem}/spec/START_Q{problem}.md"
        text = path.read_text(encoding="utf-8")
        needle = next(line for line in text.splitlines() if line.startswith("**前问依赖：**"))
        path.write_text(
            text.replace(needle, f"**预处理依赖：** {value}\n\n{needle}", 1),
            encoding="utf-8",
        )
        return path

    def test_layout_absent_complete_and_invalid_forms(self):
        temporary, workspace = self.fixture_copy()
        try:
            info, diagnostics = doctor(workspace)
            self.assertNotIn("LITE-PREPROCESS-LAYOUT-001", ids(diagnostics))
            self.assertIn("INFO preprocess=absent", info)
            pre = self.add_preprocess(workspace)
            info, diagnostics = doctor(workspace)
            self.assertNotIn("LITE-PREPROCESS-LAYOUT-001", ids(diagnostics))
            self.assertIn("INFO preprocess=present start=yes result=yes", info)
            self.assertEqual(
                sorted(
                    item.name
                    for item in (workspace / "problems").iterdir()
                    if item.name.startswith("q")
                ),
                ["q1", "q2", "q3"],
            )
            (pre / "spec/START_PRE_1.md").write_text("# START PRE_1\n", encoding="utf-8")
            self.assertIn("LITE-PREPROCESS-LAYOUT-001", ids(doctor(workspace)[1]))
        finally:
            temporary.cleanup()

        for mode in ("missing", "file", "symlink", "misplaced"):
            with self.subTest(mode=mode):
                temporary, workspace = self.fixture_copy()
                try:
                    pre = self.add_preprocess(workspace)
                    if mode == "missing":
                        (pre / "outputs").rmdir()
                    elif mode == "file":
                        (pre / "outputs").rmdir()
                        (pre / "outputs").write_text("not a directory", encoding="utf-8")
                    elif mode == "symlink":
                        (pre / "outputs").rmdir()
                        (pre / "outputs").symlink_to(pre / "code", target_is_directory=True)
                    else:
                        shutil.move(pre / "result/RESULT_PRE.md", pre / "spec/RESULT_PRE.md")
                    self.assertIn("LITE-PREPROCESS-LAYOUT-001", ids(doctor(workspace)[1]))
                finally:
                    temporary.cleanup()

    def test_start_and_result_contract_failures_and_handoff_optional(self):
        temporary, workspace = self.fixture_copy()
        try:
            pre = self.add_preprocess(workspace)
            self.assertFalse([d for d in check_preprocess_start(workspace) if d.severity == "ERROR"])
            self.assertFalse([d for d in check_preprocess_result(workspace) if d.severity == "ERROR"])
            self.assertFalse((pre / "notes/HANDOFF_PRE.md").exists())
            self.assertEqual(len(PREPROCESS_START_HEADINGS), 8)
            self.assertEqual(len(PREPROCESS_RESULT_HEADINGS), 8)
            start = pre / "spec/START_PRE.md"
            original = start.read_text(encoding="utf-8")
            start.write_text(original.replace("## 3. 数据质量审计与处理规则", ""), encoding="utf-8")
            self.assertIn("LITE-PREPROCESS-START-HEADING-001", ids(check_preprocess_start(workspace)))
            start.write_text(original.replace("\n无\n", "\n待确认\n"), encoding="utf-8")
            self.assertIn("LITE-PREPROCESS-START-UNRESOLVED-001", ids(check_preprocess_start(workspace)))
            start.write_text(original, encoding="utf-8")
            result = pre / "result/RESULT_PRE.md"
            result_text = result.read_text(encoding="utf-8")
            result.write_text(result_text.replace("无偏差", "偏差待定"), encoding="utf-8")
            self.assertIn("LITE-PREPROCESS-RESULT-DEVIATION-001", ids(check_preprocess_result(workspace)))
            result.write_text(result_text, encoding="utf-8")
            old = time.time() - 10
            os.utime(result, (old, old))
            os.utime(start, None)
            self.assertIn("LITE-STALE-WARN-001", ids(check_preprocess_result(workspace)))
        finally:
            temporary.cleanup()

    def test_result_evidence_guards(self):
        mutations = {
            "format": ("- E1 — `problems/preprocess/data/derived/cleaned_data.csv` — 冻结清洗数据",
                       "- E1 `problems/preprocess/data/derived/cleaned_data.csv`", "LITE-EVIDENCE-FORMAT-001"),
            "duplicate": ("- E1 — `problems/preprocess/data/derived/cleaned_data.csv` — 冻结清洗数据",
                          "- E1 — `problems/preprocess/data/derived/cleaned_data.csv` — one\n- E1 — `problems/preprocess/data/derived/cleaned_data.csv` — two", "LITE-EVIDENCE-FORMAT-001"),
            "scope": ("problems/preprocess/data/derived/cleaned_data.csv",
                      "problems/q1/outputs/answer.csv", "LITE-EVIDENCE-SCOPE-001"),
            "missing": ("cleaned_data.csv", "missing.csv", "LITE-EVIDENCE-MISSING-001"),
            "traversal": ("problems/preprocess/data/derived/cleaned_data.csv",
                          "../outside.csv", "LITE-EVIDENCE-PATH-001"),
        }
        for name, (old, new, expected) in mutations.items():
            with self.subTest(name=name):
                temporary, workspace = self.fixture_copy()
                try:
                    pre = self.add_preprocess(workspace)
                    result = pre / "result/RESULT_PRE.md"
                    result.write_text(result.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")
                    self.assertIn(expected, ids(check_preprocess_result(workspace)))
                finally:
                    temporary.cleanup()
        temporary, workspace = self.fixture_copy()
        try:
            pre = self.add_preprocess(workspace)
            target = pre / "data/derived/cleaned_data.csv"
            target.unlink()
            target.symlink_to(pre / "outputs/real.csv")
            (pre / "outputs/real.csv").write_text("id\n1\n", encoding="utf-8")
            self.assertIn("LITE-EVIDENCE-SYMLINK-001", ids(check_preprocess_result(workspace)))
        finally:
            temporary.cleanup()

    def test_qn_dependency_compatibility_grammar_contract_and_staleness(self):
        temporary, workspace = self.fixture_copy()
        try:
            self.assertNotIn("LITE-START-PREPROCESS-WARN-001", ids(check_start(workspace, 1)))
            self.declare(workspace, "无")
            self.assertFalse([d for d in check_start(workspace, 1) if d.severity == "ERROR"])
        finally:
            temporary.cleanup()
        temporary, workspace = self.fixture_copy()
        try:
            self.declare(workspace, "PRE")
            self.assertIn("LITE-START-PREPROCESS-CONTRACT-001", ids(check_start(workspace, 1)))
            pre = self.add_preprocess(workspace)
            self.assertFalse([d for d in check_start(workspace, 1) if d.severity == "ERROR"])
            result_q1 = workspace / "problems/q1/result/RESULT_Q1.md"
            old = time.time() - 10
            os.utime(result_q1, (old, old))
            os.utime(pre / "result/RESULT_PRE.md", None)
            self.assertIn("LITE-PREPROCESS-STALE-WARN-001", ids(check_result(workspace, 1)))
        finally:
            temporary.cleanup()
        for value in ("pre", "Q0", "PRE ", ""):
            with self.subTest(value=value):
                temporary, workspace = self.fixture_copy()
                try:
                    self.declare(workspace, value)
                    self.assertIn("LITE-START-PREPROCESS-001", ids(check_start(workspace, 1)))
                finally:
                    temporary.cleanup()
        temporary, workspace = self.fixture_copy()
        try:
            self.add_preprocess(workspace)
            found = ids(check_start(workspace, 1))
            self.assertIn("LITE-START-PREPROCESS-WARN-001", found)
            self.assertFalse([d for d in check_start(workspace, 1) if d.severity == "ERROR"])
        finally:
            temporary.cleanup()
        temporary, workspace = self.fixture_copy()
        try:
            pre = self.add_preprocess(workspace)
            (pre / "spec/START_PRE.md").write_bytes(b"\xff\xfe")
            self.declare(workspace, "无")
            self.assertFalse([d for d in check_start(workspace, 1) if d.severity == "ERROR"])
        finally:
            temporary.cleanup()

        malformed = {
            "duplicate": (
                "**前问依赖：** 无",
                "**预处理依赖：** PRE\n**预处理依赖：** PRE\n\n**前问依赖：** 无",
            ),
            "spacing": (
                "**前问依赖：** 无",
                "**预处理依赖：**PRE\n\n**前问依赖：** 无",
            ),
            "wrong_section": (
                "## 8. 未决问题",
                "**预处理依赖：** PRE\n\n## 8. 未决问题",
            ),
            "pre_as_question": (
                "**前问依赖：** 无",
                "**前问依赖：** PRE",
            ),
        }
        for name, (old, new) in malformed.items():
            with self.subTest(name=name):
                temporary, workspace = self.fixture_copy()
                try:
                    start = workspace / "problems/q1/spec/START_Q1.md"
                    start.write_text(
                        start.read_text(encoding="utf-8").replace(old, new, 1),
                        encoding="utf-8",
                    )
                    found = ids(check_start(workspace, 1))
                    expected = (
                        "LITE-START-DEPENDENCY-001"
                        if name == "pre_as_question"
                        else "LITE-START-PREPROCESS-001"
                    )
                    self.assertIn(expected, found)
                finally:
                    temporary.cleanup()

    def test_preprocess_git_dirty_is_advisory(self):
        temporary, workspace = self.fixture_copy()
        try:
            pre = self.add_preprocess(workspace)
            subprocess.run(["git", "init", "-q", str(workspace)], check=True)
            subprocess.run(["git", "-C", str(workspace), "add", "."], check=True)
            subprocess.run(
                [
                    "git", "-C", str(workspace), "-c", "user.name=Test",
                    "-c", "user.email=test@example.invalid", "commit", "-qm", "fixture",
                ],
                check=True,
            )
            (pre / "code/clean.py").write_text("print('changed')\n", encoding="utf-8")
            found = ids(check_preprocess_result(workspace))
            self.assertIn("LITE-GIT-DIRTY-WARN-001", found)
            self.assertFalse([d for d in check_preprocess_result(workspace) if d.severity == "ERROR"])
        finally:
            temporary.cleanup()

    def test_invalid_utf8_returns_tool_error_without_traceback(self):
        temporary, workspace = self.fixture_copy()
        try:
            pre = self.add_preprocess(workspace)
            (pre / "spec/START_PRE.md").write_bytes(b"\xff\xfe")
            completed = subprocess.run(
                [
                    sys.executable, str(SKILL / "scripts/lite.py"),
                    "check-preprocess-start", "--workspace", str(workspace),
                ],
                text=True, capture_output=True,
            )
            self.assertEqual(completed.returncode, 2)
            self.assertIn("LITE-TOOL-001", completed.stderr)
            self.assertNotIn("Traceback", completed.stdout + completed.stderr)
        finally:
            temporary.cleanup()

    def test_preprocess_init_rollback(self):
        with tempfile.TemporaryDirectory() as raw:
            workspace = Path(raw) / "workspace"
            workspace.mkdir()
            with mock.patch.object(cli, "_write", side_effect=OSError("injected")):
                with self.assertRaises(OSError):
                    cli.initialize(workspace, 2, preprocess=True)
            for name in cli.MANAGED_ROOTS:
                self.assertFalse((workspace / name).exists(), name)


if __name__ == "__main__":
    unittest.main()
