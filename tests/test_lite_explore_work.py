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
SKILL = ROOT / "skills/kymcm-lite"
CLI = SKILL / "scripts/lite.py"
SINGLE_FIXTURE = ROOT / "tests/fixtures/lite_synthetic_handoff"
SPLIT_FIXTURE = ROOT / "tests/fixtures/lite_split_handoff"
APPENDIX_FIXTURE = ROOT / "tests/fixtures/lite_appendix_handoff"

sys.path.insert(0, str(SKILL / "scripts"))

from kymcm_lite.cli import parser
from kymcm_lite.paths import EVIDENCE_DIRS, MARKER_BYTES, QUESTION_DIRS


def fingerprint(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        if path.is_file() and not path.is_symlink():
            digest.update(path.read_bytes())
    return digest.hexdigest()


class LiteExploreWorkTests(unittest.TestCase):
    def run_cli(self, *args: str, ok: int | None = None):
        completed = subprocess.run(
            [sys.executable, str(CLI), *args],
            text=True,
            capture_output=True,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        if ok is not None:
            self.assertEqual(completed.returncode, ok, completed.stdout + completed.stderr)
        return completed

    def copy_fixture(self, fixture: Path):
        temporary = tempfile.TemporaryDirectory()
        workspace = Path(temporary.name) / "workspace"
        shutil.copytree(fixture, workspace)
        return temporary, workspace

    def add_explore(self, workspace: Path, question: int = 1) -> None:
        explore = workspace / f"problems/q{question}/explore"
        (explore / "code").mkdir(parents=True)
        (explore / "outputs").mkdir()
        (explore / f"EXPLORE_Q{question}.md").write_text(
            "# EXPLORE Q1\n\n## T1 — route\n\nHypothesis\nA is faster.\n\n"
            "Test\nOne microbenchmark.\n\nBudget\n<= 1 min\n\n"
            "Decision rule\nLower elapsed time.\n\nResult\nPending.\n\nDecision\nPending.\n",
            encoding="utf-8",
        )
        (explore / "code/t1_probe.py").write_text("print('scratch')\n", encoding="utf-8")
        (explore / "outputs/t1_result.csv").write_text("route,time\nA,1\n", encoding="utf-8")

    def test_reference_template_and_mirrors(self):
        reference = SKILL / "references/explore_work.md"
        template = SKILL / "templates/EXPLORE_QN.template.md"
        self.assertTrue(reference.is_file())
        self.assertEqual(reference.read_bytes(), (ROOT / "docs/lite-v3/explore_work.md").read_bytes())
        self.assertEqual(template.read_bytes(), (ROOT / "docs/lite-v3/EXPLORE_QN.template.md").read_bytes())
        template_text = template.read_text(encoding="utf-8")
        for required in (
            "EXPLORE QN", "Hypothesis", "Test", "Budget", "Decision rule",
            "Result", "Decision", "PROMOTE", "DROP", "NEXT", "STOP",
        ):
            self.assertIn(required, template_text)

    def test_active_guidance_freezes_optional_stop_and_formal_boundary(self):
        texts = [
            (SKILL / "references/explore_work.md").read_text(encoding="utf-8"),
            (SKILL / "SKILL.md").read_text(encoding="utf-8"),
            (SKILL / "docs/protocol.md").read_text(encoding="utf-8"),
        ]
        combined = "\n".join(texts)
        for required in (
            "optional", "route clear", "minimum useful", "hard budget", "STOP",
            "PROMOTE", "DROP", "NEXT", "not formally accepted", "formal evidence",
            "Appendix", "problems/qN/explore/",
        ):
            self.assertIn(required, combined)
        self.assertNotIn("EXPLORE_RESULT", combined)
        self.assertNotIn("EXPLORE START", combined)
        self.assertNotIn("E1/E2", combined)

    def test_runtime_surface_and_marker_are_unchanged(self):
        subparsers = next(
            action for action in parser()._actions
            if hasattr(action, "choices") and action.choices
        )
        self.assertEqual(
            set(subparsers.choices),
            {
                "init", "doctor", "check-start", "check-result",
                "check-preprocess-start", "check-preprocess-result",
                "check-appendix-start", "check-appendix-result",
            },
        )
        self.assertEqual(MARKER_BYTES, b'{"workflow":"kymcm_lite","version":3}\n')
        self.assertNotIn("explore", QUESTION_DIRS)
        self.assertNotIn("explore", EVIDENCE_DIRS)
        runtime = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (SKILL / "scripts/kymcm_lite").glob("*.py")
        )
        for forbidden in (
            "check-explore", "EXPLORE_RESULT", "init --explore",
            "explore_manifest", "explore_state", "explore_approval",
        ):
            self.assertNotIn(forbidden, runtime)

    def test_fresh_init_does_not_create_explore(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory) / "workspace"
            self.run_cli("init", "--workspace", str(workspace), "--questions", "2", ok=0)
            self.assertFalse(any(workspace.glob("problems/q*/explore")))

    def test_optional_explore_does_not_change_single_formal_checks(self):
        temporary, workspace = self.copy_fixture(SINGLE_FIXTURE)
        try:
            baseline = {}
            for command in ("doctor", "check-start", "check-result"):
                args = (command, "--workspace", str(workspace))
                if command != "doctor":
                    args += ("--problem", "1")
                baseline[command] = self.run_cli(*args).returncode
            self.add_explore(workspace)
            (workspace / "problems/q1/explore/outputs/binary.bin").write_bytes(b"\xff\x00")
            before = fingerprint(workspace)
            for command in ("doctor", "check-start", "check-result"):
                args = (command, "--workspace", str(workspace))
                if command != "doctor":
                    args += ("--problem", "1")
                completed = self.run_cli(*args)
                self.assertEqual(completed.returncode, baseline[command])
                self.assertNotIn("EXPLORE", completed.stdout + completed.stderr)
                self.assertEqual(before, fingerprint(workspace))
        finally:
            temporary.cleanup()

    def test_one_problem_level_explore_does_not_change_split_checks(self):
        temporary, workspace = self.copy_fixture(SPLIT_FIXTURE)
        try:
            self.add_explore(workspace, question=2)
            self.assertTrue((workspace / "problems/q2/explore/EXPLORE_Q2.md").is_file())
            self.assertFalse(any((workspace / "problems/q2/explore").glob("EXPLORE_Q2_*.md")))
            for subproblem in (1, 2):
                self.run_cli(
                    "check-start", "--workspace", str(workspace),
                    "--problem", "2", "--subproblem", str(subproblem), ok=0,
                )
                self.run_cli(
                    "check-result", "--workspace", str(workspace),
                    "--problem", "2", "--subproblem", str(subproblem), ok=0,
                )
        finally:
            temporary.cleanup()

    def test_explore_output_is_rejected_as_formal_result_evidence(self):
        temporary, workspace = self.copy_fixture(SINGLE_FIXTURE)
        try:
            self.add_explore(workspace)
            result = workspace / "problems/q1/result/RESULT_Q1.md"
            result.write_text(
                result.read_text(encoding="utf-8").replace(
                    "problems/q1/outputs/baseline_allocation.csv",
                    "problems/q1/explore/outputs/t1_result.csv",
                ),
                encoding="utf-8",
            )
            completed = self.run_cli(
                "check-result", "--workspace", str(workspace), "--problem", "1", ok=1,
            )
            self.assertIn("LITE-EVIDENCE-SCOPE-001", completed.stdout)
        finally:
            temporary.cleanup()

    def test_explore_source_is_rejected_by_appendix_mapping(self):
        temporary, workspace = self.copy_fixture(APPENDIX_FIXTURE)
        try:
            self.add_explore(workspace)
            start = workspace / "reports/appendix/APPENDIX_START.md"
            start.write_text(
                start.read_text(encoding="utf-8").replace(
                    "problems/q1/code/solve.py",
                    "problems/q1/explore/code/t1_probe.py",
                    1,
                ),
                encoding="utf-8",
            )
            completed = self.run_cli(
                "check-appendix-start", "--workspace", str(workspace), ok=1,
            )
            self.assertIn("LITE-APPENDIX-SOURCE-PATH-001", completed.stdout)
        finally:
            temporary.cleanup()


if __name__ == "__main__":
    unittest.main()
