from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from tests.full.helpers import model_spec, result


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/kymcm-full"
SCRIPTS = SKILL / "scripts"
sys.path.insert(0, str(SCRIPTS))

from full_checkpoint import _git_guard, _result
from workflow_mode import WorkflowModeError, workspace_mode


def fingerprint(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


class FullPortabilityTests(unittest.TestCase):
    def run_cli(self, script: Path, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(script), *args], cwd=cwd, text=True,
            capture_output=True,
        )

    def git(self, root: Path, *args: str) -> str:
        return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()

    def test_mode_marker_is_explicit_and_unknown_versions_fail(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self.assertEqual(workspace_mode(root), "legacy")
            marker = root / ".kymcm/mode.json"
            marker.parent.mkdir()
            marker.write_text('{"workflow":"kymcm_full","version":1}\n', encoding="utf-8")
            self.assertEqual(workspace_mode(root), "kymcm_full")
            marker.write_text('{"workflow":"checkpoint_lite","version":2}\n', encoding="utf-8")
            self.assertEqual(workspace_mode(root), "checkpoint_lite")
            marker.write_text('{"workflow":"kymcm_full","version":99}\n', encoding="utf-8")
            with self.assertRaises(WorkflowModeError):
                workspace_mode(root)

    def test_skill_copy_runs_without_source_repository(self):
        with tempfile.TemporaryDirectory() as raw:
            copied = Path(raw) / "kymcm-full"
            shutil.copytree(SKILL, copied, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            completed = self.run_cli(copied / "scripts/full_checkpoint.py", "--help", cwd=Path(raw))
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn("validate-layout", completed.stdout)
            wrapper = self.run_cli(copied / "scripts/lite_checkpoint.py", "--help", cwd=Path(raw))
            self.assertEqual(wrapper.returncode, 0, wrapper.stderr)
            self.assertIn("validate-layout", wrapper.stdout)
            self.assertIn("submit-result", wrapper.stdout)

    def test_initializer_is_fresh_and_refuses_nonempty_target(self):
        with tempfile.TemporaryDirectory() as raw:
            workspace = Path(raw) / "contest"
            init = self.run_cli(SCRIPTS / "full_workspace.py", "init", "--workspace", str(workspace), "--contest", "CUMCM")
            self.assertEqual(init.returncode, 0, init.stderr)
            self.assertEqual(workspace_mode(workspace), "kymcm_full")
            for q in range(1, 5):
                state = json.loads((workspace / f".kymcm/checkpoint_lite/q{q}/checkpoint/workflow.json").read_text())
                self.assertEqual(state["state"], "exploring")
                self.assertFalse((workspace / f"problems/q{q}/spec/START_Q{q}.md").exists())
                self.assertFalse((workspace / f"problems/q{q}/result/RESULT_Q{q}.md").exists())
            definition = json.loads((workspace / ".kymcm/checkpoint_lite/problem_definition/workflow.json").read_text())
            self.assertEqual(definition["state"], "draft")
            again = self.run_cli(SCRIPTS / "full_workspace.py", "init", "--workspace", str(workspace), "--contest", "CUMCM")
            self.assertNotEqual(again.returncode, 0)

    def test_doctor_is_read_only_in_external_git_repository(self):
        with tempfile.TemporaryDirectory() as raw:
            workspace = Path(raw) / "contest"
            self.assertEqual(self.run_cli(SCRIPTS / "full_workspace.py", "init", "--workspace", str(workspace), "--contest", "MCM").returncode, 0)
            self.git(workspace, "init", "-b", "main")
            self.git(workspace, "config", "user.name", "Fixture")
            self.git(workspace, "config", "user.email", "fixture@example.invalid")
            self.git(workspace, "add", ".")
            self.git(workspace, "commit", "-m", "fixture")
            before = fingerprint(workspace)
            completed = self.run_cli(SCRIPTS / "full_workspace.py", "doctor", "--workspace", str(workspace))
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            self.assertTrue(json.loads(completed.stdout)["read_only"])
            self.assertEqual(before, fingerprint(workspace))

    def test_git_guard_scopes_dirty_check_to_current_problem(self):
        with tempfile.TemporaryDirectory() as raw:
            workspace = Path(raw) / "contest"
            self.assertEqual(self.run_cli(SCRIPTS / "full_workspace.py", "init", "--workspace", str(workspace), "--contest", "ICM").returncode, 0)
            self.git(workspace, "init", "-b", "main")
            self.git(workspace, "config", "user.name", "Fixture")
            self.git(workspace, "config", "user.email", "fixture@example.invalid")
            artifact = workspace / "problems/q1/outputs/a.json"
            artifact.write_text("{}", encoding="utf-8")
            self.git(workspace, "add", ".")
            self.git(workspace, "commit", "-m", "fixture")
            payload = result(model_spec()).payload()
            payload["evidence"]["artifacts"][0]["path"] = "problems/q1/outputs/a.json"
            payload["evidence"]["code_revision"] = self.git(workspace, "rev-parse", "HEAD")
            record = _result(payload)
            (workspace / "README.md").write_text("unrelated dirty file\n", encoding="utf-8")
            _git_guard(workspace, 1, record)
            code = workspace / "problems/q1/code/model.py"
            code.write_text("x = 1\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "uncommitted changes"):
                _git_guard(workspace, 1, record)

    def test_git_guard_rejects_workspace_without_repository(self):
        with tempfile.TemporaryDirectory() as raw:
            workspace = Path(raw)
            payload = result(model_spec()).payload()
            payload["evidence"]["code_revision"] = "0" * 40
            with self.assertRaisesRegex(ValueError, "Git repository"):
                _git_guard(workspace, 1, _result(copy.deepcopy(payload)))


if __name__ == "__main__":
    unittest.main()
