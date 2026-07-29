from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import hashlib


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/kymcm-lite"
FIXTURE = ROOT / "tests/fixtures/lite_synthetic_handoff"
APPENDIX_FIXTURE = ROOT / "tests/fixtures/lite_appendix_handoff"
SPLIT_FIXTURE = ROOT / "tests/fixtures/lite_split_handoff"


class LitePortabilityTests(unittest.TestCase):
    def test_copied_skill_runs_without_repository_imports(self):
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw); copied = base / "kymcm-lite"; shutil.copytree(SKILL, copied)
            workspace = base / "workspace"
            env = {**os.environ, "PYTHONPATH": "", "PYTHONDONTWRITEBYTECODE": "1"}
            command = [sys.executable, str(copied / "scripts/lite.py")]
            def run(*args: str) -> subprocess.CompletedProcess[str]:
                return subprocess.run([*command, *args], cwd=base, env=env, text=True, capture_output=True)
            self.assertEqual(run("--help").returncode, 0)
            self.assertEqual(run(
                "init", "--workspace", str(workspace), "--questions", "3", "--preprocess"
            ).returncode, 0)
            shutil.copy2(
                copied / "templates/START_PRE.template.md",
                workspace / "problems/preprocess/spec/START_PRE.md",
            )
            result_pre = (copied / "templates/RESULT_PRE.template.md").read_text(encoding="utf-8").replace(
                "<!-- 示例：- E1 — `problems/preprocess/data/derived/cleaned_data.csv` — 冻结清洗数据 -->",
                "- E1 — `problems/preprocess/data/derived/cleaned_data.csv` — 冻结清洗数据",
            )
            (workspace / "problems/preprocess/result/RESULT_PRE.md").write_text(result_pre, encoding="utf-8")
            (workspace / "problems/preprocess/data/derived/cleaned_data.csv").write_text(
                "id,value\n1,2\n", encoding="utf-8"
            )
            (workspace / "FROZEN_CONTEXT.md").write_bytes(b"\xff\xfe")
            for question in (1, 2, 3):
                for part, name in (("spec", f"START_Q{question}.md"), ("result", f"RESULT_Q{question}.md")):
                    shutil.copy2(FIXTURE / f"problems/q{question}/{part}/{name}", workspace / f"problems/q{question}/{part}/{name}")
                for part in ("code", "data/derived", "outputs", "notes"):
                    source = FIXTURE / f"problems/q{question}/{part}"
                    for path in source.rglob("*"):
                        if path.is_file():
                            target = workspace / path.relative_to(FIXTURE); target.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(path, target)
            self.assertEqual(run("doctor", "--workspace", str(workspace)).returncode, 0)
            self.assertEqual(run("check-preprocess-start", "--workspace", str(workspace)).returncode, 0)
            self.assertEqual(run("check-preprocess-result", "--workspace", str(workspace)).returncode, 0)
            for question in (1, 2, 3):
                self.assertEqual(run("check-start", "--workspace", str(workspace), "--problem", str(question)).returncode, 0)
                result = run("check-result", "--workspace", str(workspace), "--problem", str(question))
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            split_workspace = base / "split workspace"
            shutil.copytree(SPLIT_FIXTURE, split_workspace)
            for command_name in ("check-start", "check-result"):
                for unit in ("1", "2"):
                    result = run(
                        command_name, "--workspace", str(split_workspace),
                        "--problem", "2", "--subproblem", unit,
                    )
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            appendix_workspace = base / "appendix workspace"
            shutil.copytree(APPENDIX_FIXTURE, appendix_workspace)
            for appendix_command in ("check-appendix-start", "check-appendix-result"):
                result = run(appendix_command, "--workspace", str(appendix_workspace))
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            for path in (copied / "scripts").rglob("*.py"):
                text = path.read_text(encoding="utf-8")
                self.assertNotIn("kymcm-full", text)
                self.assertNotIn("checkpoint_full", text)
                self.assertNotIn(str(ROOT), text)

    def test_read_only_copied_skill_runs_from_unrelated_directory(self):
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            copied = base / "只读 skill with spaces"
            shutil.copytree(SKILL, copied, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            workspace = base / "可写 workspace with spaces"
            unrelated = base / "unrelated cwd"
            unrelated.mkdir()
            for path in copied.rglob("*"):
                if path.is_file():
                    path.chmod(0o444)
                elif path.is_dir():
                    path.chmod(0o555)
            copied.chmod(0o555)

            def fingerprint(root: Path) -> str:
                digest = hashlib.sha256()
                for path in sorted(root.rglob("*")):
                    digest.update(path.relative_to(root).as_posix().encode("utf-8"))
                    if path.is_file():
                        digest.update(path.read_bytes())
                return digest.hexdigest()

            env = {**os.environ, "PATH": os.path.dirname(sys.executable), "PYTHONPATH": "", "PYTHONDONTWRITEBYTECODE": "1"}
            command = [sys.executable, str(copied / "scripts/lite.py")]
            before_skill = fingerprint(copied)
            initialized = subprocess.run([*command, "init", "--workspace", str(workspace), "--questions", "3"], cwd=unrelated, env=env, text=True, capture_output=True)
            self.assertEqual(initialized.returncode, 0, initialized.stdout + initialized.stderr)
            (workspace / "FROZEN_CONTEXT.md").write_bytes(b"\xff\xfe")
            for question in (1, 2, 3):
                for part, name in (("spec", f"START_Q{question}.md"), ("result", f"RESULT_Q{question}.md")):
                    shutil.copy2(FIXTURE / f"problems/q{question}/{part}/{name}", workspace / f"problems/q{question}/{part}/{name}")
                for part in ("code", "data/derived", "outputs", "notes"):
                    for source in (FIXTURE / f"problems/q{question}/{part}").rglob("*"):
                        if source.is_file():
                            target = workspace / source.relative_to(FIXTURE)
                            target.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(source, target)
            for args in (("doctor",), ("check-start", "--problem", "1"), ("check-result", "--problem", "1")):
                before_workspace = fingerprint(workspace)
                completed = subprocess.run([*command, args[0], "--workspace", str(workspace), *args[1:]], cwd=unrelated, env=env, text=True, capture_output=True)
                self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
                self.assertEqual(fingerprint(workspace), before_workspace)
            self.assertEqual(fingerprint(copied), before_skill)
            self.assertFalse(any(copied.rglob("__pycache__")))


if __name__ == "__main__":
    unittest.main()
