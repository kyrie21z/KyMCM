from __future__ import annotations

import ast
import builtins
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "skills/kymcm-lite/figure_bundle.py"


def load_module():
    spec = importlib.util.spec_from_file_location("kymcm_lite_figure_bundle", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


figure_bundle = load_module()


class FigureBundleTests(unittest.TestCase):
    def make_bundle(self, directory: str, name: str = "formal") -> Path:
        stem = Path(directory) / name
        stem.with_suffix(".pdf").write_bytes(b"%PDF-1.4\nnon-empty")
        stem.with_suffix(".png").write_bytes(b"\x89PNG\r\n\x1a\nnon-empty")
        stem.with_suffix(".py").write_text(
            "from pathlib import Path\nstem = Path(__file__).with_suffix(\"\")\n",
            encoding="utf-8",
        )
        figure_bundle.write_figure_note(stem, title="响应面", caption="颜色表示响应值。")
        return stem

    def assert_invalid(self, mutate, pattern: str) -> None:
        with tempfile.TemporaryDirectory() as directory:
            stem = self.make_bundle(directory)
            mutate(stem)
            with self.assertRaisesRegex(figure_bundle.FigureBundleError, pattern):
                figure_bundle.validate_figure_bundle(stem, source_path=stem.with_suffix(".py"))

    def test_module_is_standard_library_only(self):
        allowed = set(sys.stdlib_module_names)
        tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                imported.add(node.module.split(".", 1)[0])
        self.assertTrue(imported <= allowed, imported - allowed)
        self.assertNotIn("json", imported)

    def test_valid_same_stem_bundle_and_multiline_caption_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            stem = self.make_bundle(directory)
            figure_bundle.write_figure_note(
                stem,
                title="三维可行域",
                caption="(a) 表示基准情景。\n(b) 表示约束收紧情景。",
            )
            result = figure_bundle.validate_figure_bundle(
                stem,
                source_path=Path(__file__).with_name("unused.py") if False else stem.with_suffix(".py"),
            )
            self.assertEqual(set(result), {"pdf", "png", "py", "txt"})
            self.assertEqual(result["py"], stem.with_suffix(".py"))
            self.assertEqual(
                result["txt"].read_text(encoding="utf-8"),
                "图题：三维可行域\n图注：\n(a) 表示基准情景。\n(b) 表示约束收紧情景。\n",
            )

    def test_each_required_file_is_enforced(self):
        for suffix, role in ((".pdf", "PDF"), (".png", "PNG"), (".py", "PY"), (".txt", "TXT")):
            with self.subTest(suffix=suffix):
                self.assert_invalid(lambda stem, suffix=suffix: stem.with_suffix(suffix).unlink(), role)

    def test_source_must_be_same_stem(self):
        with tempfile.TemporaryDirectory() as directory:
            stem = self.make_bundle(directory)
            other = Path(directory) / "other.py"
            other.write_text("pass\n", encoding="utf-8")
            with self.assertRaisesRegex(figure_bundle.FigureBundleError, "same-stem"):
                figure_bundle.validate_figure_bundle(stem, source_path=other)

    def test_empty_and_non_utf8_source_fail(self):
        self.assert_invalid(lambda stem: stem.with_suffix(".py").write_bytes(b""), "empty")
        self.assert_invalid(lambda stem: stem.with_suffix(".py").write_bytes(b"\xff\xfe"), "UTF-8")
        self.assert_invalid(lambda stem: stem.with_suffix(".py").write_bytes(b"pass\x00binary"), "opaque")
        self.assert_invalid(lambda stem: stem.with_suffix(".txt").write_bytes(b"\xff\xfe"), "UTF-8")

    def test_validation_does_not_require_matplotlib_or_pyvista(self):
        with tempfile.TemporaryDirectory() as directory:
            stem = self.make_bundle(directory)
            real_import = builtins.__import__

            def fail_optional(name, *args, **kwargs):
                if name.split(".", 1)[0] in {"matplotlib", "pyvista", "vtk"}:
                    raise AssertionError(f"unexpected optional import: {name}")
                return real_import(name, *args, **kwargs)

            with mock.patch("builtins.__import__", side_effect=fail_optional):
                figure_bundle.validate_figure_bundle(stem, source_path=stem.with_suffix(".py"))

    def test_note_grammar_is_fail_closed(self):
        cases = {
            "wrong title field": "标题：响应面\n图注：\n说明。\n",
            "blank title": "图题：   \n图注：\n说明。\n",
            "multiline title": "图题：响应面\n额外标题行\n图注：\n说明。\n",
            "wrong caption field": "图题：响应面\n说明：\n说明。\n",
            "blank caption": "图题：响应面\n图注：\n",
            "blank caption line": "图题：响应面\n图注：\n第一行\n\n第二行\n",
            "no trailing newline": "图题：响应面\n图注：\n说明。",
        }
        for name, note in cases.items():
            with self.subTest(name=name):
                self.assert_invalid(
                    lambda stem, note=note: stem.with_suffix(".txt").write_text(note, encoding="utf-8"),
                    "figure note|title|caption|图注|图题",
                )

    def test_note_writer_rejects_placeholders_numbering_and_multiline_title(self):
        with tempfile.TemporaryDirectory() as directory:
            stem = Path(directory) / "figure"
            for title, caption in (
                ("图 1 响应面", "说明。"),
                ("Figure 2 Response surface", "说明。"),
                ("响应面", "TODO"),
                ("响应面", "TBD"),
                ("响应面", "待补充"),
                ("第一行\n第二行", "说明。"),
            ):
                with self.subTest(title=title, caption=caption):
                    with self.assertRaises(figure_bundle.FigureBundleError):
                        figure_bundle.write_figure_note(stem, title=title, caption=caption)

    def test_forbidden_same_stem_format_fails_without_deleting_files(self):
        with tempfile.TemporaryDirectory() as directory:
            stem = self.make_bundle(directory)
            for suffix in figure_bundle.FORBIDDEN_IMAGE_SUFFIXES:
                with self.subTest(suffix=suffix):
                    forbidden = stem.with_suffix(suffix)
                    forbidden.write_bytes(b"keep")
                    with self.assertRaisesRegex(figure_bundle.FigureBundleError, "forbidden"):
                        figure_bundle.validate_figure_bundle(stem, source_path=stem.with_suffix(".py"))
                    self.assertEqual(forbidden.read_bytes(), b"keep")
                    forbidden.unlink()
            uppercase = stem.with_suffix(".SVG")
            uppercase.write_bytes(b"keep")
            with self.assertRaisesRegex(figure_bundle.FigureBundleError, "forbidden"):
                figure_bundle.validate_figure_bundle(stem, source_path=stem.with_suffix(".py"))

    def test_atomic_note_failure_preserves_accepted_note(self):
        with tempfile.TemporaryDirectory() as directory:
            stem = Path(directory) / "formal"
            note = figure_bundle.write_figure_note(stem, title="原图题", caption="原图注。")
            accepted = note.read_bytes()
            real_replace = os.replace

            def fail_install(source, destination):
                source_path = Path(source)
                destination_path = Path(destination)
                if destination_path == note and "accepted" not in source_path.name:
                    raise OSError("injected replacement failure")
                return real_replace(source, destination)

            with mock.patch.object(figure_bundle.os, "replace", side_effect=fail_install):
                with self.assertRaisesRegex(figure_bundle.FigureBundleError, "write failed"):
                    figure_bundle.write_figure_note(stem, title="新图题", caption="新图注。")
            self.assertEqual(note.read_bytes(), accepted)

    def test_validation_creates_no_state_manifest_or_json(self):
        with tempfile.TemporaryDirectory() as directory:
            stem = self.make_bundle(directory)
            before = {path.name for path in Path(directory).iterdir()}
            figure_bundle.validate_figure_bundle(stem, source_path=stem.with_suffix(".py"))
            self.assertEqual({path.name for path in Path(directory).iterdir()}, before)
            self.assertFalse(any(Path(directory).glob("*.json")))


if __name__ == "__main__":
    unittest.main()
