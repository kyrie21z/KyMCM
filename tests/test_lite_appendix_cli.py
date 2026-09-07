from __future__ import annotations

import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "skills/kymcm-lite/scripts/lite.py"
FIXTURE = ROOT / "tests/fixtures/lite_appendix_handoff"


def fingerprint(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        digest.update(path.relative_to(root).as_posix().encode())
        if path.is_file():
            digest.update(path.read_bytes())
    return digest.hexdigest()


class LiteAppendixCliTests(unittest.TestCase):
    def run_cli(self, *args: str, ok: int | None = None):
        env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        completed = subprocess.run(
            [sys.executable, str(CLI), *args],
            text=True, capture_output=True, env=env,
        )
        if ok is not None:
            self.assertEqual(completed.returncode, ok, completed.stdout + completed.stderr)
        return completed

    def fixture_copy(self):
        temporary = tempfile.TemporaryDirectory()
        workspace = Path(temporary.name) / "workspace"
        shutil.copytree(FIXTURE, workspace)
        return temporary, workspace

    def test_help_has_eight_commands_and_appendix_needs_no_problem(self):
        help_result = self.run_cli("--help", ok=0)
        for command in (
            "init", "doctor", "check-start", "check-result",
            "check-preprocess-start", "check-preprocess-result",
            "check-appendix-start", "check-appendix-result",
        ):
            self.assertIn(command, help_result.stdout)
        command_help = self.run_cli("check-appendix-start", "--help", ok=0)
        self.assertNotIn("--problem", command_help.stdout)

    def test_valid_commands_are_warning_only_and_read_only(self):
        temporary, workspace = self.fixture_copy()
        try:
            before = fingerprint(workspace)
            start = self.run_cli("check-appendix-start", "--workspace", str(workspace), ok=0)
            self.assertIn("SUMMARY errors=0", start.stdout)
            self.assertEqual(before, fingerprint(workspace))
            result = self.run_cli("check-appendix-result", "--workspace", str(workspace), ok=0)
            self.assertIn("SUMMARY errors=0", result.stdout)
            self.assertEqual(before, fingerprint(workspace))
            self.assertFalse(any(workspace.rglob("__pycache__")))
            self.assertFalse(any(workspace.rglob("*.pyc")))
        finally:
            temporary.cleanup()

    def test_malformed_contract_returns_one(self):
        temporary, workspace = self.fixture_copy()
        try:
            path = workspace / "reports/appendix/APPENDIX_START.md"
            path.write_text("# wrong\n", encoding="utf-8")
            completed = self.run_cli("check-appendix-start", "--workspace", str(workspace), ok=1)
            self.assertIn("LITE-APPENDIX-START-001", completed.stdout)
        finally:
            temporary.cleanup()

    def test_invalid_appendix_utf8_returns_two_without_traceback(self):
        temporary, workspace = self.fixture_copy()
        try:
            (workspace / "reports/appendix/APPENDIX_START.md").write_bytes(b"\xff\xfe")
            completed = self.run_cli("check-appendix-start", "--workspace", str(workspace), ok=2)
            self.assertIn("LITE-TOOL-001", completed.stderr)
            self.assertEqual(completed.stderr.count("SUMMARY errors=1 warnings=0"), 1)
            self.assertNotIn("Traceback", completed.stderr)
            self.assertEqual(completed.stdout, "")
        finally:
            temporary.cleanup()

    def test_invalid_legacy_and_optional_roots_do_not_affect_appendix_commands(self):
        temporary, workspace = self.fixture_copy()
        try:
            (workspace / "FROZEN_CONTEXT.md").write_bytes(b"\xff\xfe")
            legacy = workspace / "paper"
            legacy.mkdir(exist_ok=True)
            (legacy / "invalid.md").write_bytes(b"\xff\xfe")
            (legacy / "broken").symlink_to(legacy / "missing")
            figure = workspace / "figure"
            figure.mkdir()
            (figure / "invalid.bin").write_bytes(b"\xff\xfe")
            (figure / "broken").symlink_to(figure / "missing")
            before = fingerprint(workspace)
            for command in ("check-appendix-start", "check-appendix-result"):
                completed = self.run_cli(command, "--workspace", str(workspace), ok=0)
                self.assertNotIn("figure", completed.stdout + completed.stderr)
                self.assertEqual(before, fingerprint(workspace))
        finally:
            temporary.cleanup()

    def test_missing_and_extra_outputs_return_one(self):
        temporary, workspace = self.fixture_copy()
        try:
            (workspace / "appendix/problems/q1/result/formal.csv").unlink()
            completed = self.run_cli("check-appendix-result", "--workspace", str(workspace), ok=1)
            self.assertIn("LITE-APPENDIX-OUTPUT-MISSING-001", completed.stdout)
        finally:
            temporary.cleanup()

    def test_writer_is_not_blocked_but_copy_mismatch_is_and_checker_is_read_only(self):
        temporary, workspace = self.fixture_copy()
        try:
            source = workspace / "appendix/problems/q1/code/solve.py"
            source.write_text("from pathlib import Path\nPath('out').write_text('x')\n", encoding="utf-8")
            before = fingerprint(workspace)
            completed = self.run_cli(
                "check-appendix-result", "--workspace", str(workspace), ok=1
            )
            self.assertNotIn("LITE-APPENDIX-CODE-SIDE-EFFECT-001", completed.stdout)
            self.assertIn("LITE-APPENDIX-COPY-MISMATCH-001", completed.stdout)
            self.assertIn("appendix/problems/q1/code/solve.py:", completed.stdout)
            self.assertEqual(before, fingerprint(workspace))
        finally:
            temporary.cleanup()

    def test_internal_contract_sources_are_rejected_without_new_command(self):
        for relative in (
            "problems/q1/spec/SUPPLEMENT_START_Q1.md",
            "problems/q1/result/SUPPLEMENT_RESULT_Q1.md",
            "problems/q1/notes/HANDOFF_Q1.md",
            "problems/q2/notes/HANDOFF_Q2_1.md",
            "problems/preprocess/notes/HANDOFF_PRE.md",
        ):
            with self.subTest(relative=relative):
                temporary, workspace = self.fixture_copy()
                try:
                    source = workspace / relative
                    source.parent.mkdir(parents=True, exist_ok=True)
                    source.write_text(f"# {source.stem.replace('_', ' ')}\n", encoding="utf-8")
                    contract = workspace / "reports/appendix/APPENDIX_START.md"
                    contract.write_text(
                        contract.read_text(encoding="utf-8").replace(
                            "problems/q1/code/core.py", relative
                        ),
                        encoding="utf-8",
                    )
                    completed = self.run_cli(
                        "check-appendix-start", "--workspace", str(workspace), ok=1
                    )
                    self.assertIn("LITE-APPENDIX-SOURCE-PATH-001", completed.stdout)
                    self.assertIn("SUPPLEMENT, and HANDOFF internal documents", completed.stdout)
                finally:
                    temporary.cleanup()

    def test_figure_workspace_is_not_an_appendix_source(self):
        temporary, workspace = self.fixture_copy()
        try:
            source = workspace / "figure/final.py"
            source.parent.mkdir()
            source.write_text("print('display only')\n", encoding="utf-8")
            contract = workspace / "reports/appendix/APPENDIX_START.md"
            contract.write_text(
                contract.read_text(encoding="utf-8").replace(
                    "problems/q1/code/core.py", "figure/final.py"
                ),
                encoding="utf-8",
            )
            completed = self.run_cli(
                "check-appendix-start", "--workspace", str(workspace), ok=1
            )
            self.assertIn("LITE-APPENDIX-SOURCE-PATH-001", completed.stdout)
        finally:
            temporary.cleanup()


if __name__ == "__main__":
    unittest.main()
