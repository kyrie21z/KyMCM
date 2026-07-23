from __future__ import annotations

import hashlib
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "skills/kymcm-lite/scripts"
FIXTURE = ROOT / "tests/fixtures/lite_appendix_handoff"
sys.path.insert(0, str(SCRIPTS))

from kymcm_lite.appendix_contracts import (
    APPENDIX_RESULT_HEADINGS, APPENDIX_START_HEADINGS, check_appendix_result,
    check_appendix_start,
)


def identifiers(diagnostics):
    return {item.identifier for item in diagnostics}


def fingerprint(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        digest.update(path.relative_to(root).as_posix().encode())
        if path.is_symlink():
            digest.update(os.readlink(path).encode())
        elif path.is_file():
            digest.update(path.read_bytes())
    return digest.hexdigest()


class AppendixRuntimeTests(unittest.TestCase):
    def fixture_copy(self):
        temporary = tempfile.TemporaryDirectory()
        workspace = Path(temporary.name) / "workspace"
        shutil.copytree(FIXTURE, workspace)
        return temporary, workspace

    def mutate_start(self, workspace: Path, old: str, new: str) -> None:
        path = workspace / "reports/appendix/APPENDIX_START.md"
        path.write_text(path.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")

    def mutate_result(self, workspace: Path, old: str, new: str) -> None:
        path = workspace / "reports/appendix/APPENDIX_RESULT.md"
        path.write_text(path.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")

    def test_exact_headings_and_valid_fixture(self):
        self.assertEqual(len(APPENDIX_START_HEADINGS), 9)
        self.assertEqual(len(APPENDIX_RESULT_HEADINGS), 10)
        self.assertFalse(any(item.severity == "ERROR" for item in check_appendix_start(FIXTURE)))
        self.assertFalse(any(item.severity == "ERROR" for item in check_appendix_result(FIXTURE)))

    def test_invalid_frozen_context_is_never_read_and_checks_are_read_only(self):
        temporary, workspace = self.fixture_copy()
        try:
            (workspace / "FROZEN_CONTEXT.md").write_bytes(b"\xff\xfe\x80")
            before = fingerprint(workspace)
            self.assertFalse(any(item.severity == "ERROR" for item in check_appendix_start(workspace)))
            self.assertEqual(before, fingerprint(workspace))
            self.assertFalse(any(item.severity == "ERROR" for item in check_appendix_result(workspace)))
            self.assertEqual(before, fingerprint(workspace))
        finally:
            temporary.cleanup()

    def test_heading_unresolved_and_visible_content_rules(self):
        cases = (
            ("## 3. appendix 目标结构", "", "LITE-APPENDIX-START-HEADING-001"),
            ("## 9. 未决问题\n\n无", "## 9. 未决问题\n\n待决定", "LITE-APPENDIX-UNRESOLVED-001"),
            ("提交最小复现附件和论文后的核心算法。", "<!-- only prompt -->", "LITE-APPENDIX-START-EMPTY-WARN-001"),
            ("按白名单构造 q1 Python、q2 C++、正式结果和最小环境。", "```md\nexample only\n```", "LITE-APPENDIX-START-EMPTY-WARN-001"),
        )
        for old, new, expected in cases:
            with self.subTest(expected=expected):
                temporary, workspace = self.fixture_copy()
                try:
                    self.mutate_start(workspace, old, new)
                    self.assertIn(expected, identifiers(check_appendix_start(workspace)))
                finally:
                    temporary.cleanup()

    def test_copy_curate_generate_and_duplicate_grammar(self):
        cases = (
            (
                "- C001 — COPY — `problems/q1/code/core.py` → `code/q1_core_algorithm.py` — q1 核心算法",
                "- C001 — CURATE — `problems/q1/code/core.py`; `problems/q1/code/helper.py` → `code/q1_core_algorithm.py` — q1 核心算法",
                None,
            ),
            (
                "- A001 — COPY — `problems/q1/code/solve.py` → `appendix/problems/q1/code/solve.py` — Python 正式入口",
                "- A001 — COPY — `problems/q1/code/solve.py`; `problems/q1/code/helper.py` → `appendix/problems/q1/code/solve.py` — invalid",
                "LITE-APPENDIX-WHITELIST-FORMAT-001",
            ),
            (
                "- C001 — COPY — `problems/q1/code/core.py` → `code/q1_core_algorithm.py` — q1 核心算法",
                "- A001 — COPY — `problems/q1/code/core.py` → `code/q1_core_algorithm.py` — duplicate",
                "LITE-APPENDIX-WHITELIST-DUPLICATE-001",
            ),
            (
                "- C001 — COPY — `problems/q1/code/core.py` → `code/q1_core_algorithm.py` — q1 核心算法",
                "- C001 — GENERATE — `code/q1_core_algorithm.py` — invalid",
                "LITE-APPENDIX-WHITELIST-FORMAT-001",
            ),
        )
        for old, new, expected in cases:
            with self.subTest(expected=expected):
                temporary, workspace = self.fixture_copy()
                try:
                    self.mutate_start(workspace, old, new)
                    found = identifiers(check_appendix_start(workspace))
                    if expected:
                        self.assertIn(expected, found)
                    else:
                        self.assertNotIn("LITE-APPENDIX-WHITELIST-FORMAT-001", found)
                finally:
                    temporary.cleanup()

    def test_unsafe_source_target_scope_and_symlinks(self):
        cases = (
            ("problems/q1/code/core.py", "../core.py", "LITE-APPENDIX-SOURCE-PATH-001"),
            ("problems/q1/code/core.py", r"C:\\Users\\x\\core.py", "LITE-APPENDIX-SOURCE-PATH-001"),
            ("problems/q1/code/core.py", "problems/q1/code/\tcore.py", "LITE-APPENDIX-SOURCE-PATH-001"),
            ("code/q1_core_algorithm.py", "code/nested/core.py", "LITE-APPENDIX-TARGET-PATH-001"),
            ("problems/q1/code/core.py", "paper/paper.md", "LITE-APPENDIX-SOURCE-PATH-001"),
        )
        for old, new, expected in cases:
            with self.subTest(new=new):
                temporary, workspace = self.fixture_copy()
                try:
                    self.mutate_start(workspace, old, new)
                    self.assertIn(expected, identifiers(check_appendix_start(workspace)))
                finally:
                    temporary.cleanup()
        if hasattr(os, "symlink"):
            temporary, workspace = self.fixture_copy()
            try:
                source = workspace / "problems/q1/code/core.py"
                real = workspace / "problems/q1/code/core-real.py"
                source.replace(real)
                source.symlink_to(real)
                self.assertIn("LITE-APPENDIX-SYMLINK-001", identifiers(check_appendix_start(workspace)))
            finally:
                temporary.cleanup()

    def test_declarations_and_environment_completeness(self):
        cases = (
            ("外部资料：无", "", "LITE-APPENDIX-DECLARATION-001"),
            ("强制结果文件：无", "强制结果文件：`appendix/Result.xlsx`", "LITE-APPENDIX-DECLARATION-001"),
            (
                "- A092 — GENERATE — `appendix/environment/system_info.txt` — 非敏感版本信息",
                "",
                "LITE-APPENDIX-WHITELIST-FORMAT-001",
            ),
        )
        for old, new, expected in cases:
            temporary, workspace = self.fixture_copy()
            try:
                self.mutate_start(workspace, old, new)
                self.assertIn(expected, identifiers(check_appendix_start(workspace)))
            finally:
                temporary.cleanup()

    def test_external_material_declaration_can_match_copy_whitelist(self):
        temporary, workspace = self.fixture_copy()
        try:
            source = workspace / "input/reference.txt"
            source.parent.mkdir(parents=True)
            source.write_text("synthetic reference\n")
            self.mutate_start(workspace, "外部资料：无", "外部资料：`appendix/input`")
            self.mutate_start(
                workspace,
                "强制结果文件：无",
                "资料来源：公开合成参考；用途：复核输入；必要性：评审环境不包含该资料。\n\n"
                "强制结果文件：无",
            )
            self.mutate_start(
                workspace,
                "- A090 — GENERATE",
                "- A006 — COPY — `input/reference.txt` → `appendix/input/reference.txt` — 必要外部资料\n"
                "- A090 — GENERATE",
            )
            found = identifiers(check_appendix_start(workspace))
            self.assertNotIn("LITE-APPENDIX-DECLARATION-001", found)
        finally:
            temporary.cleanup()

    def test_exact_file_set_copy_hash_forbidden_and_empty_directory(self):
        mutations = (
            ("missing", lambda root: (root / "appendix/problems/q1/result/formal.csv").unlink(), "LITE-APPENDIX-OUTPUT-MISSING-001"),
            ("extra", lambda root: (root / "appendix/extra.txt").write_text("x"), "LITE-APPENDIX-OUTPUT-EXTRA-001"),
            ("copy", lambda root: (root / "appendix/problems/q1/result/formal.csv").write_text("changed"), "LITE-APPENDIX-COPY-MISMATCH-001"),
            ("forbidden", lambda root: (root / "code/q1_core_algorithm.py").with_name("q1_core_algorithm.pyc").write_bytes(b"x"), "LITE-APPENDIX-OUTPUT-EXTRA-001"),
            ("empty", lambda root: (root / "appendix/problems/q1/empty").mkdir(), "LITE-APPENDIX-STRUCTURE-001"),
        )
        for name, mutate, expected in mutations:
            with self.subTest(name=name):
                temporary, workspace = self.fixture_copy()
                try:
                    mutate(workspace)
                    self.assertIn(expected, identifiers(check_appendix_result(workspace)))
                finally:
                    temporary.cleanup()

    def test_result_deviation_ids_evidence_and_integrity(self):
        cases = (
            ("无偏差", "需要偏差", "LITE-APPENDIX-DEVIATION-001"),
            ("A001、", "A999、", "LITE-APPENDIX-RESULT-001"),
            (
                "- E2 — `reports/appendix/evidence/python_compile.txt` — Python 编译验证",
                "- E2 — `../unsafe.txt` — Python 编译验证",
                "LITE-APPENDIX-EVIDENCE-001",
            ),
        )
        for old, new, expected in cases:
            temporary, workspace = self.fixture_copy()
            try:
                self.mutate_result(workspace, old, new)
                self.assertIn(expected, identifiers(check_appendix_result(workspace)))
            finally:
                temporary.cleanup()
        temporary, workspace = self.fixture_copy()
        try:
            integrity = workspace / "reports/appendix/evidence/source_integrity.csv"
            integrity.write_text(integrity.read_text().replace(",unchanged", ",changed", 1))
            self.assertIn("LITE-APPENDIX-INTEGRITY-001", identifiers(check_appendix_result(workspace)))
        finally:
            temporary.cleanup()

    def test_python_cpp_dependency_and_dynamic_import_checks(self):
        temporary, workspace = self.fixture_copy()
        try:
            (workspace / "appendix/problems/q1/code/solve.py").write_text("def broken(:\n")
            self.assertIn("LITE-APPENDIX-PYTHON-001", identifiers(check_appendix_result(workspace)))
        finally:
            temporary.cleanup()
        temporary, workspace = self.fixture_copy()
        try:
            self.mutate_start(
                workspace,
                "- A002 — COPY — `problems/q1/code/helper.py` → `appendix/problems/q1/code/helper.py` — Python 本地依赖\n",
                "",
            )
            self.mutate_result(workspace, "A001、A002、A003", "A001、A003")
            (workspace / "appendix/problems/q1/code/helper.py").unlink()
            self.assertIn("LITE-APPENDIX-PYTHON-001", identifiers(check_appendix_result(workspace)))
        finally:
            temporary.cleanup()
        temporary, workspace = self.fixture_copy()
        try:
            path = workspace / "appendix/problems/q1/code/solve.py"
            path.write_text(path.read_text() + '\n__import__("plugin")\n')
            found = identifiers(check_appendix_result(workspace))
            self.assertIn("LITE-APPENDIX-DEPENDENCY-WARN-001", found)
        finally:
            temporary.cleanup()
        temporary, workspace = self.fixture_copy()
        try:
            (workspace / "appendix/problems/q2/code/solver.hpp").unlink()
            found = identifiers(check_appendix_result(workspace))
            self.assertIn("LITE-APPENDIX-OUTPUT-MISSING-001", found)
        finally:
            temporary.cleanup()
        temporary, workspace = self.fixture_copy()
        try:
            source = workspace / "problems/q2/code/CMakeLists.txt"
            source.write_text("add_executable(solver solver.cpp missing.cpp)\n")
            target = workspace / "appendix/problems/q2/code/CMakeLists.txt"
            shutil.copy2(source, target)
            self.mutate_start(
                workspace,
                "- A090 — GENERATE",
                "- A006 — COPY — `problems/q2/code/CMakeLists.txt` → `appendix/problems/q2/code/CMakeLists.txt` — CMake 构建\n"
                "- A090 — GENERATE",
            )
            self.mutate_result(workspace, "A005、A090", "A005、A006、A090")
            found = identifiers(check_appendix_result(workspace))
            self.assertIn("LITE-APPENDIX-OUTPUT-MISSING-001", found)
        finally:
            temporary.cleanup()

    def test_duplicate_formal_results_and_executable_outputs(self):
        temporary, workspace = self.fixture_copy()
        try:
            source = workspace / "problems/q1/outputs/formal.csv"
            target = workspace / "appendix/problems/q1/result/formal-second.csv"
            shutil.copy2(source, target)
            self.mutate_start(
                workspace,
                "- A004 — COPY",
                "- A006 — COPY — `problems/q1/outputs/formal.csv` → `appendix/problems/q1/result/formal-second.csv` — 第二正式结果\n"
                "- A004 — COPY",
            )
            self.mutate_result(workspace, "A003、A004", "A003、A006、A004")
            self.assertIn("LITE-APPENDIX-DUPLICATE-001", identifiers(check_appendix_result(workspace)))
        finally:
            temporary.cleanup()
        temporary, workspace = self.fixture_copy()
        try:
            target = workspace / "code/q1_core_algorithm.py"
            target.chmod(0o755)
            self.assertIn("LITE-APPENDIX-FORBIDDEN-001", identifiers(check_appendix_result(workspace)))
        finally:
            temporary.cleanup()

    def test_valid_corrupt_and_missing_sheet_xlsx(self):
        def declare(workspace: Path) -> Path:
            source = workspace / "problems/q1/outputs/Result.xlsx"
            source.parent.mkdir(parents=True, exist_ok=True)
            line = "- A010 — COPY — `problems/q1/outputs/Result.xlsx` → `appendix/Result.xlsx` — 官方结果\n"
            self.mutate_start(
                workspace,
                "- A090 — GENERATE",
                line + "- A090 — GENERATE",
            )
            self.mutate_start(workspace, "强制结果文件：无", "强制结果文件：`appendix/Result.xlsx`")
            self.mutate_result(workspace, "A005、A090", "A005、A010、A090")
            return source

        for mode, expected in (("valid", None), ("corrupt", "LITE-APPENDIX-XLSX-001"), ("empty", "LITE-APPENDIX-XLSX-001")):
            with self.subTest(mode=mode):
                temporary, workspace = self.fixture_copy()
                try:
                    source = declare(workspace)
                    target = workspace / "appendix/Result.xlsx"
                    if mode == "corrupt":
                        source.write_bytes(b"not a zip")
                    else:
                        with zipfile.ZipFile(source, "w") as archive:
                            archive.writestr("[Content_Types].xml", "<Types/>")
                            sheets = "" if mode == "empty" else '<sheet name="Sheet1" sheetId="1"/>'
                            archive.writestr(
                                "xl/workbook.xml",
                                f'<workbook xmlns="x"><sheets>{sheets}</sheets></workbook>',
                            )
                    shutil.copy2(source, target)
                    digest = hashlib.sha256(source.read_bytes()).hexdigest()
                    integrity = workspace / "reports/appendix/evidence/source_integrity.csv"
                    with integrity.open("a", encoding="utf-8") as stream:
                        stream.write(f"problems/q1/outputs/Result.xlsx,{digest},{digest},unchanged\n")
                    diagnostics = check_appendix_result(workspace)
                    found = identifiers(diagnostics)
                    if expected:
                        self.assertIn(expected, found)
                    else:
                        self.assertNotIn("LITE-APPENDIX-XLSX-001", found)
                        self.assertFalse(
                            [item for item in diagnostics if item.severity == "ERROR"],
                            diagnostics,
                        )
                finally:
                    temporary.cleanup()

    def test_sensitive_redaction_certification_and_line_count_warning(self):
        temporary, workspace = self.fixture_copy()
        try:
            path = workspace / "appendix/environment/system_info.txt"
            token = "ghp_" + "A" * 26
            path.write_text(f"token: {token}\n")
            diagnostics = check_appendix_result(workspace)
            sensitive = [item for item in diagnostics if item.identifier == "LITE-APPENDIX-SENSITIVE-001"]
            self.assertTrue(sensitive)
            self.assertNotIn("ghp_", sensitive[0].message)
        finally:
            temporary.cleanup()
        temporary, workspace = self.fixture_copy()
        try:
            path = workspace / "appendix/problems/q1/result/formal.csv"
            path.write_text("claim\n全局最优\n")
            found = identifiers(check_appendix_result(workspace))
            self.assertIn("LITE-APPENDIX-CERTIFICATION-WARN-001", found)
            self.assertIn("LITE-APPENDIX-DEPENDENCY-WARN-001", found)
        finally:
            temporary.cleanup()


if __name__ == "__main__":
    unittest.main()
