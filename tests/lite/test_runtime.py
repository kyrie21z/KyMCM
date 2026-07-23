from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "skills/kymcm-lite/scripts"
sys.path.insert(0, str(SCRIPTS))

from kymcm_lite import cli
from kymcm_lite.contracts import START_HEADINGS, meaningful, parse_markdown
from kymcm_lite.diagnostics import error, exit_code, render, warning
from kymcm_lite.paths import (
    MARKER_BYTES, discover_questions, evidence_path_diagnostics, marker_diagnostics,
    safe_relative_path,
)


class DiagnosticTests(unittest.TestCase):
    def test_render_and_exit_selection(self):
        items = [warning("W", ".", "warn"), error("E", "x", "bad")]
        self.assertEqual(render(items), ["WARNING W .: warn", "ERROR E x: bad", "SUMMARY errors=1 warnings=1"])
        self.assertEqual(exit_code(items), 1)
        self.assertEqual(exit_code(items[:1]), 0)
        tool = error("LITE-TOOL-001", ".", "failure")
        self.assertEqual(exit_code([tool]), 2)
        self.assertEqual(exit_code([items[1], tool]), 2)


class PathTests(unittest.TestCase):
    def test_marker_is_exact_and_fails_closed(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); (root / ".kymcm").mkdir()
            marker = root / ".kymcm/mode.json"
            marker.write_bytes(MARKER_BYTES)
            self.assertEqual(marker_diagnostics(root), [])
            for value in ({"workflow": "kymcm_full", "version": 1}, {"workflow": "checkpoint_lite", "version": 2}, {"workflow": "kymcm_lite", "version": 4}):
                marker.write_text(json.dumps(value), encoding="utf-8")
                self.assertEqual(marker_diagnostics(root)[0].identifier, "LITE-MODE-001")
            marker.write_text("not-json", encoding="utf-8")
            self.assertEqual(marker_diagnostics(root)[0].identifier, "LITE-MODE-001")

    def test_question_discovery_requires_contiguity(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); (root / "problems/q1").mkdir(parents=True); (root / "problems/q3").mkdir()
            numbers, diagnostics = discover_questions(root)
            self.assertEqual(numbers, [1, 3])
            self.assertEqual(diagnostics[0].identifier, "LITE-LAYOUT-001")

    def test_cross_platform_safe_relative_paths(self):
        for unsafe in ("", "\x00", "x\x00y", "x\ny", "x\ry", "/tmp/x", "../x", "a/../x", r"C:\\temp\\x", r"\\server\\x"):
            self.assertFalse(safe_relative_path(unsafe), unsafe)
        self.assertTrue(safe_relative_path("problems/q1/outputs/x.csv"))

    def test_evidence_path_parser_is_total_for_malicious_text(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            for unsafe in ("", "\x00", "x\x00y", "x\ny", "x\ry", "/tmp/x", r"C:\\temp\\x", r"\\server\\x", "../x", "a/../../x"):
                with self.subTest(raw=repr(unsafe)):
                    diagnostics = evidence_path_diagnostics(root, 1, unsafe)
                    self.assertEqual(diagnostics[0].identifier, "LITE-EVIDENCE-PATH-001")

    def test_evidence_scope_and_symlink_guards(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); allowed = root / "problems/q1/outputs"; allowed.mkdir(parents=True)
            target = allowed / "x.txt"; target.write_text("x", encoding="utf-8")
            self.assertEqual(evidence_path_diagnostics(root, 1, "problems/q1/outputs/x.txt"), [])
            self.assertEqual(evidence_path_diagnostics(root, 1, "problems/q2/outputs/x.txt")[0].identifier, "LITE-EVIDENCE-SCOPE-001")
            link = allowed / "link.txt"; link.symlink_to(target)
            self.assertEqual(evidence_path_diagnostics(root, 1, "problems/q1/outputs/link.txt")[0].identifier, "LITE-EVIDENCE-SYMLINK-001")
            broken = allowed / "broken.txt"; broken.symlink_to(allowed / "missing")
            self.assertEqual(evidence_path_diagnostics(root, 1, "problems/q1/outputs/broken.txt")[0].identifier, "LITE-EVIDENCE-SYMLINK-001")


class MarkdownTests(unittest.TestCase):
    def test_fenced_heading_text_is_ignored(self):
        text = "# START Q1\n\n```md\n## 1. 问题目标与直接交付\n```\n~~~\n## fake\n~~~\n## 1. 问题目标与直接交付\n"
        parsed = parse_markdown(text)
        self.assertEqual([item for item, _ in parsed.headings], ["# START Q1", START_HEADINGS[0]])

    def test_sections_and_meaningful_content(self):
        text = "# START Q1\n\n## 1. 问题目标与直接交付\nanswer\n\n## 2. 已冻结输入与前问继承\n<!-- prompt -->\n"
        parsed = parse_markdown(text)
        self.assertEqual(parsed.section(START_HEADINGS[0], START_HEADINGS), "answer")
        self.assertFalse(meaningful(parsed.section(START_HEADINGS[1], START_HEADINGS)))

    def test_fenced_and_commented_examples_are_not_meaningful(self):
        self.assertFalse(meaningful("<!-- example -->"))
        self.assertFalse(meaningful("```md\nexample\n```"))
        self.assertFalse(meaningful("~~~\nexample\n~~~"))
        self.assertTrue(meaningful("<!-- example -->\nactive prose"))
        self.assertTrue(meaningful("```md\nexample\n```\nactive prose"))


class InitializationTests(unittest.TestCase):
    def test_init_rollback_preserves_unrelated_content(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); unrelated = root / "keep.txt"; unrelated.write_text("keep", encoding="utf-8")
            original = cli._write
            calls = 0
            def fail_first(path, content):
                nonlocal calls
                calls += 1
                if calls == 1:
                    raise OSError("simulated")
                original(path, content)
            with mock.patch.object(cli, "_write", side_effect=fail_first), self.assertRaises(OSError):
                cli.initialize(root, 3)
            self.assertEqual(unrelated.read_text(encoding="utf-8"), "keep")
            for managed in (".kymcm", "FROZEN_CONTEXT.md", "input", "paper", "reports", "problems"):
                self.assertFalse((root / managed).exists(), managed)

    def test_init_rollback_removes_new_ancestors_but_preserves_existing_parent(self):
        for failure_call in (1,):
            with self.subTest(failure_call=failure_call), tempfile.TemporaryDirectory() as raw:
                parent = Path(raw) / "existing"
                parent.mkdir()
                keep = parent / "keep.txt"
                keep.write_text("keep", encoding="utf-8")
                workspace = parent / "new ancestor" / "深层" / "workspace"
                original = cli._write
                calls = 0

                def fail_at_call(path, content):
                    nonlocal calls
                    calls += 1
                    if calls == failure_call:
                        raise OSError("simulated")
                    original(path, content)

                with mock.patch.object(cli, "_write", side_effect=fail_at_call), self.assertRaises(OSError):
                    cli.initialize(workspace, 1)
                self.assertTrue(parent.is_dir())
                self.assertEqual(keep.read_text(encoding="utf-8"), "keep")
                self.assertFalse((parent / "new ancestor").exists())


if __name__ == "__main__":
    unittest.main()
