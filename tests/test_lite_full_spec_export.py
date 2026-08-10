from __future__ import annotations

import hashlib
import importlib.util
import getpass
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
EXPORTER_PATH = ROOT / "scripts/export_kymcm_lite_full_spec.py"
SPEC = ROOT / "docs/lite-v3/KyMCM_Lite_FULL_SPEC.md"


def load_exporter():
    module_spec = importlib.util.spec_from_file_location("kymcm_lite_full_exporter", EXPORTER_PATH)
    assert module_spec and module_spec.loader
    module = importlib.util.module_from_spec(module_spec)
    sys.modules[module_spec.name] = module
    module_spec.loader.exec_module(module)
    return module


exporter = load_exporter()


class LiteFullSpecExportTests(unittest.TestCase):
    def run_exporter(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(EXPORTER_PATH), *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )

    def copy_repository(self, target: Path) -> None:
        shutil.copytree(
            ROOT,
            target,
            ignore=shutil.ignore_patterns(".git", ".ai-bridge", "__pycache__", "*.pyc"),
        )

    def test_tracked_artifact_is_deterministic_and_checkable(self):
        first = exporter.build_document(ROOT)
        second = exporter.build_document(ROOT)
        self.assertEqual(first, second)
        self.assertEqual(first, SPEC.read_bytes())
        self.assertTrue(first.endswith(b"\n"))
        self.assertFalse(first.endswith(b"\n\n"))
        self.assertEqual(self.run_exporter("--output", str(SPEC), "--check").returncode, 0)

        text = first.decode("utf-8")
        preamble = text.split("## 1. Source manifest", 1)[0]
        self.assertNotIn(str(ROOT), text)
        self.assertNotRegex(preamble, r"20[0-9]{2}-[0-9]{2}-[0-9]{2}")
        self.assertNotIn(socket.gethostname(), preamble)
        self.assertNotIn(getpass.getuser(), preamble)
        for secret_marker in ("ghp_", "gho_", "Authorization:", "-----BEGIN"):
            self.assertNotIn(secret_marker, text)

    def test_normal_generation_and_stale_check_are_read_only(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "full-spec.md"
            generated = self.run_exporter(
                "--repo-root", str(ROOT), "--output", str(output)
            )
            self.assertEqual(generated.returncode, 0, generated.stderr)
            original = output.read_bytes()
            self.assertEqual(original, exporter.build_document(ROOT))
            unchanged = self.run_exporter(
                "--repo-root", str(ROOT), "--output", str(output)
            )
            self.assertEqual(unchanged.returncode, 0, unchanged.stderr)
            self.assertEqual(output.read_bytes(), original)

            output.write_bytes(b"stale\n")
            before = output.read_bytes()
            stale = self.run_exporter(
                "--repo-root", str(ROOT), "--output", str(output), "--check"
            )
            self.assertEqual(stale.returncode, 1, stale.stderr)
            self.assertIn("stale", stale.stdout)
            self.assertEqual(output.read_bytes(), before)

    def test_missing_output_check_is_stale_without_creating_parent(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "not-created" / "full-spec.md"
            result = self.run_exporter(
                "--repo-root", str(ROOT), "--output", str(output), "--check"
            )
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertFalse(output.parent.exists())

    def test_invalid_input_is_tool_error(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory) / "repo"
            self.copy_repository(fixture)
            mirror = fixture / "docs/lite-v3/appendix_organization.md"
            mirror.write_bytes(mirror.read_bytes() + b"\nchanged mirror\n")
            result = self.run_exporter("--repo-root", str(fixture))
            self.assertEqual(result.returncode, 2)
            self.assertIn("canonical and mirror differ", result.stderr)
            self.assertNotIn("Traceback", result.stderr)

    def test_new_unclassified_lite_document_blocks_export(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory) / "repo"
            self.copy_repository(fixture)
            (fixture / "docs/lite-v3/unclassified.md").write_text(
                "# Unclassified\n", encoding="utf-8"
            )
            result = self.run_exporter("--repo-root", str(fixture))
            self.assertEqual(result.returncode, 2)
            self.assertIn("unclassified", result.stderr)

    def test_manifest_and_canonical_completeness(self):
        sources = exporter.collect_sources(ROOT)
        document = SPEC.read_text(encoding="utf-8")
        self.assertEqual(len(sources), 40)
        self.assertEqual(
            {source.role for source in sources},
            {
                "identity", "core-skill", "protocol", "machine-contract",
                "diagnostic-catalog", "reference", "template", "agent-metadata",
                "product-documentation", "repository-maintenance",
            },
        )
        expected_fixed = {
            *exporter.CORE_SKILL_FILES,
            exporter.PROTOCOL_FILE,
            exporter.AGENT_FILE,
            exporter.SKILL_README,
            "docs/lite-v3/diagnostics.md",
            *(path for path, _role in exporter.REPOSITORY_NORMATIVE_DOCS if path != "docs/lite-v3/diagnostics.md"),
        }
        paths = {source.path for source in sources}
        self.assertTrue(expected_fixed <= paths)
        for directory in ("skills/kymcm-lite/references", "skills/kymcm-lite/templates"):
            ordinary = {
                path.relative_to(ROOT).as_posix()
                for path in (ROOT / directory).iterdir()
                if path.suffix in {".md", ".tex"}
                if path.is_file() and not path.is_symlink()
            }
            self.assertTrue(ordinary <= paths, directory)

        for index, source in enumerate(sources, 1):
            row = f"| {index} | `{source.path}` | `{source.role}` | {len(source.content)} | `{source.sha256}` |"
            self.assertIn(row, document, source.path)
            begin = f"<!-- BEGIN KYMCM-LITE SOURCE: {source.path} -->"
            end = f"<!-- END KYMCM-LITE SOURCE: {source.path} -->"
            self.assertEqual(document.count(begin), 1, source.path)
            self.assertEqual(document.count(end), 1, source.path)
            self.assertIn(source.content.decode("utf-8"), document, source.path)

    def test_docs_lite_v3_classification_and_exclusions(self):
        actual = {
            path.relative_to(ROOT).as_posix()
            for path in (ROOT / "docs/lite-v3").iterdir()
            if path.suffix in {".md", ".tex"}
            if path.is_file() and not path.is_symlink()
        }
        sources = exporter.collect_sources(ROOT)
        mirrors = {mirror for source in sources for mirror in source.mirrors}
        included = {
            path for path, _role in exporter.REPOSITORY_NORMATIVE_DOCS
            if path.startswith("docs/lite-v3/")
        } | mirrors
        excluded = set(exporter.EXCLUDED_LITE_V3_DOCS)
        self.assertFalse(included & excluded)
        self.assertTrue(included <= actual)
        self.assertTrue(actual <= included | excluded)
        document = SPEC.read_text(encoding="utf-8")
        for relative in excluded:
            self.assertNotIn(
                f"BEGIN KYMCM-LITE SOURCE: {relative}", document, relative
            )
        self.assertNotIn("BEGIN KYMCM-LITE SOURCE: docs/lite-v3/KyMCM_Lite_FULL_SPEC.md", document)

    def test_mirror_hashes_and_mapping(self):
        sources = exporter.collect_sources(ROOT)
        mirrored = [source for source in sources if source.mirrors]
        self.assertEqual(sum(len(source.mirrors) for source in mirrored), 25)
        for source in mirrored:
            for mirror in source.mirrors:
                path = ROOT / mirror
                self.assertEqual(path.read_bytes(), source.content, mirror)
                self.assertEqual(
                    hashlib.sha256(path.read_bytes()).hexdigest(), source.sha256, mirror
                )
        markdown_format = next(
            source for source in sources if source.path.endswith("/markdown_format.md")
        )
        self.assertFalse(markdown_format.mirrors)

    def test_machine_contract_covers_runtime_surface(self):
        contract = (ROOT / "skills/kymcm-lite/references/machine_contract.md").read_text(
            encoding="utf-8"
        )
        for required in (
            "marker", "mode.json", "managed roots", "figure/", "FROZEN_CONTEXT.md",
            "rollback", "START_PRE", "RESULT_PRE", "single", "split", "partial",
            "dependency", "evidence", "symlink", "Git", "read-only", "Supplement",
            "HANDOFF_QN.md", "Appendix", "source_integrity.csv", "XLSX", "Python",
            "init", "doctor", "check-preprocess-start", "check-preprocess-result",
            "check-start", "check-result", "check-appendix-start", "check-appendix-result",
            "0 = structure", "1 = a contract", "2 = an unexpected",
            "mathematical correctness", "human review",
            "editable/adopted boundary", "Start/Result invalidation",
            "artifact overwrite permission", "HANDOFF refresh alone",
            "Result acceptance", "HANDOFF authorization", "read-only HANDOFF",
        ):
            self.assertIn(required, contract, required)
        self.assertIn('{"workflow":"kymcm_lite","version":3}', contract)
        self.assertIn("LITE-APPENDIX-SOURCE-PATH-001", contract)

    def test_typography_reference_is_exported_without_full_ambiguity(self):
        reference = (ROOT / "skills/kymcm-lite/references/final_figure_typography.md").read_text(
            encoding="utf-8"
        )
        document = SPEC.read_text(encoding="utf-8")
        self.assertIn("skills/kymcm-lite/references/final_figure_typography.md", document)
        for exact in ("Noto Serif CJK SC", "Tinos", "STIX mathtext", "mathtext.fontset = stix"):
            self.assertIn(exact, reference)
            self.assertIn(exact, document)
        self.assertIn("stop the formal final-figure task", reference)
        self.assertIn("silent fallback", reference)
        self.assertIn("does not change, replace, or generalize that Full behavior", reference)

    def test_frozen_figure_references_are_exported(self):
        document = SPEC.read_text(encoding="utf-8")
        expected = {
            "final_figure_core_rules.md": ("4 columns × 3 rows", "PDF and PNG"),
            "final_figure_selection.md": ("kymcm-figure-selection-v1", "FIGURE_SELECTION_V1", "visual complexity != information value"),
            "final_figure_style.md": ("F-STANDARD", "FIGURE_STYLE_V1", "600 dpi"),
            "final_figure_color.md": ("KY_MCM_QUALITATIVE_V1", "batlow", "vik"),
        }
        for name, required in expected.items():
            path = ROOT / "skills/kymcm-lite/references" / name
            mirror = ROOT / "docs/lite-v3" / name
            self.assertEqual(path.read_bytes(), mirror.read_bytes(), name)
            self.assertIn(f"skills/kymcm-lite/references/{name}", document, name)
            text = path.read_text(encoding="utf-8")
            for phrase in required:
                self.assertIn(phrase, text, f"{name}: {phrase}")

    def test_release_surface_and_full_identity_unchanged(self):
        self.assertEqual((ROOT / "skills/kymcm-lite/VERSION").read_bytes(), b"0.9.8\n")
        self.assertEqual((ROOT / "skills/kymcm-full/VERSION").read_bytes(), b"1.0.0\n")
        tree = subprocess.check_output(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD:skills/kymcm-full"], text=True
        ).strip()
        self.assertEqual(tree, "d06f821c922986264f10f14910e51636e739aaa4")
        tag = subprocess.check_output(
            ["git", "-C", str(ROOT), "rev-parse", "full-v1.0.0"], text=True
        ).strip()
        self.assertEqual(tag, "8de8b146be09c5584cf63d7675d6cc36a3485ec8")
        self.assertEqual(
            subprocess.run(
                ["git", "-C", str(ROOT), "diff", "--name-only", "--", "skills/kymcm-full"],
                text=True,
                capture_output=True,
                check=False,
            ).stdout,
            "",
        )

    def test_init_does_not_create_the_external_export(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory) / "contest-lite"
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "skills/kymcm-lite/scripts/lite.py"),
                    "init",
                    "--workspace",
                    str(workspace),
                    "--questions",
                    "1",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertFalse(any(workspace.rglob("KyMCM_Lite_FULL_SPEC.md")))


if __name__ == "__main__":
    unittest.main()
