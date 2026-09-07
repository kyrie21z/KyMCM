from __future__ import annotations

import hashlib
import csv
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "skills/kymcm-lite/scripts"
FIXTURE = ROOT / "tests/fixtures/lite_appendix_handoff"
CORE_FIXTURE = ROOT / "tests/fixtures/lite_appendix_computation_core"
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

    def add_integrity_source(self, workspace: Path, relative: str) -> None:
        path = workspace / relative
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        integrity = workspace / "reports/appendix/evidence/source_integrity.csv"
        with integrity.open("a", encoding="utf-8") as stream:
            stream.write(f"{relative},{digest},{digest},unchanged\n")

    def replace_copy_source(self, workspace: Path, source: str, target: str, text: str) -> None:
        """Model an accepted synthetic source revision before packaging."""
        previous = hashlib.sha256((workspace / source).read_bytes()).hexdigest()
        (workspace / source).write_text(text, encoding="utf-8")
        (workspace / target).write_bytes((workspace / source).read_bytes())
        current = hashlib.sha256((workspace / source).read_bytes()).hexdigest()
        integrity = workspace / "reports/appendix/evidence/source_integrity.csv"
        integrity.write_text(
            integrity.read_text(encoding="utf-8").replace(previous, current),
            encoding="utf-8",
        )

    def test_display_excerpts_need_neither_standalone_syntax_nor_dependency_closure(self):
        for excerpt in ("from .helper import score\n", "    return score(values)\n"):
            with self.subTest(excerpt=excerpt), tempfile.TemporaryDirectory() as directory:
                workspace = Path(directory) / "workspace"
                shutil.copytree(FIXTURE, workspace)
                source = "problems/q1/code/core.py"
                target = "code/q1_core_algorithm.py"
                formal = "from .helper import score\n\ndef solve(values):\n    return score(values)\n"
                self.replace_copy_source(workspace, source, target, formal)
                (workspace / target).write_text(excerpt, encoding="utf-8")
                self.mutate_start(workspace, "- C001 — COPY", "- C001 — CURATE")
                self.mutate_start(
                    workspace, "— q1 核心算法",
                    "— 忠实连续行选录；省略其余函数和入口，不宣称独立运行",
                )
                before = fingerprint(workspace)
                diagnostics = check_appendix_result(workspace)
                self.assertFalse([d for d in diagnostics if d.severity == "ERROR"], diagnostics)
                self.assertEqual(before, fingerprint(workspace))
                # Removing the display header does not remove the A-class runtime header.
                self.mutate_start(
                    workspace,
                    "- C003 — COPY — `problems/q2/code/solver.hpp` → `code/solver.hpp` — q2 核心算法头文件\n",
                    "",
                )
                self.mutate_result(workspace, "、C003", "")
                (workspace / "code/solver.hpp").unlink()
                diagnostics = check_appendix_result(workspace)
                self.assertFalse([d for d in diagnostics if d.severity == "ERROR"], diagnostics)

    def test_accepted_runtime_readers_and_writers_pass_without_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory) / "workspace"
            shutil.copytree(FIXTURE, workspace)
            self.replace_copy_source(
                workspace, "problems/q1/code/solve.py", "appendix/problems/q1/code/solve.py",
                "import csv\nfrom pathlib import Path\n"
                "def solve(input_path, output_dir):\n"
                "    values = [int(row['value']) for row in csv.DictReader(open(input_path))]\n"
                "    Path(output_dir).mkdir(parents=True, exist_ok=True)\n"
                "    with (Path(output_dir) / 'result.csv').open('w') as stream:\n"
                "        csv.writer(stream).writerow([sum(values)])\n"
                "def workbook(frame, output_path):\n"
                "    frame.to_excel(output_path, index=False)\n"
                "raise RuntimeError('checker must never execute submitted code')\n",
            )
            before = fingerprint(workspace)
            diagnostics = check_appendix_result(workspace)
            self.assertFalse([d for d in diagnostics if d.severity == "ERROR"], diagnostics)
            self.assertEqual(before, fingerprint(workspace))

    def mixed_package(self, workspace: Path) -> Path:
        """Package accepted synthetic sources through the existing A/C mappings."""
        shutil.copytree(FIXTURE, workspace)
        files = ("reproduce.py", "search.cpp", "search.hpp", "settings.ini")
        for index, name in enumerate(files, 30):
            source = f"problems/q1/code/{name}"
            target = f"appendix/problems/q1/code/{name}"
            shutil.copy2(CORE_FIXTURE / name, workspace / source)
            shutil.copy2(workspace / source, workspace / target)
            self.add_integrity_source(workspace, source)
            self.mutate_start(workspace, "- A090 — GENERATE", (
                f"- A{index:03d} — COPY — `{source}` → `{target}` — 正式执行链\n"
                "- A090 — GENERATE"
            ))
            self.mutate_result(workspace, "A005、", f"A005、A{index:03d}、")
        self.declare_current_ai_usage(workspace, copy_target=True)
        self.mutate_result(workspace, "A005、", "A005、A093、")
        self.declare_root_results(workspace, ("appendix/official.csv",))
        self.replace_copy_source(
            workspace, "problems/q1/outputs/root_20.csv", "appendix/official.csv",
            "candidate,objective\n7,0\n",
        )
        source = "problems/q1/outputs/candidate.txt"
        target = "appendix/problems/q1/result/candidate.txt"
        shutil.copy2(CORE_FIXTURE / "candidate.txt", workspace / source)
        shutil.copy2(workspace / source, workspace / target)
        self.add_integrity_source(workspace, source)
        self.mutate_start(workspace, "- A090 — GENERATE", (
            f"- A034 — COPY — `{source}` → `{target}` — 冻结候选；仅用于声明的复算起点\n"
            "- A090 — GENERATE"
        ))
        self.mutate_result(workspace, "A005、", "A005、A034、")
        (workspace / "input").mkdir(exist_ok=True)
        shutil.copy2(CORE_FIXTURE / "input.csv", workspace / "input/values.csv")
        # Official raw data is supplied separately; no extra mapping is necessary.
        (workspace / "appendix/environment/README.md").write_text(
            "Synthetic reproduction only. Python stdlib + g++ C++17; input/values.csv "
            "contains value rows 2 and 4. Supply it alongside the extracted appendix.\n"
            "Run from the extraction root:\n"
            "python appendix/problems/q1/code/reproduce.py --compiler g++ "
            "--input input/values.csv --config appendix/problems/q1/code/settings.ini "
            "--output work/full\n"
            "Budget: 30 seconds. Full search 0..10 gives candidate=7, objective=0 exactly.\n"
            "Reduced acceptance: --steps 2 uses the real search; then --candidate "
            "appendix/problems/q1/result/candidate.txt recomputes the frozen candidate. "
            "Report both separately and full search not rerun. No stochastic process.\n",
            encoding="utf-8",
        )
        self.mutate_start(
            workspace, "执行静态语法、编译、COPY 哈希、敏感信息和源文件完整性验证；歧义交人工复核。",
            "声明输入 values.csv + settings.ini → README 入口 → 每次 30 秒 → "
            "完整搜索 candidate=7、objective=0 精确一致；失败立即停止。"
            "另测缩减范围：2 步短程搜索，然后固定候选复算，不称完整重跑。"
            "只写独立 work/；COPY、原始输入及正式源哈希不变。",
        )
        diagnostics = check_appendix_result(workspace)
        self.assertFalse([d for d in diagnostics if d.severity == "ERROR"], diagnostics)
        return workspace / "appendix"

    def run_mixed(self, isolated: Path, name: str, *extra: str):
        compiler = shutil.which("g++")
        if compiler is None:
            self.skipTest("g++ unavailable; real mixed-language reproduction NOT verified")
        work = isolated / "work"
        work.mkdir(exist_ok=True)
        # No inherited project/Python/compiler search paths or prebuilt binaries.
        environment = {"PATH": os.defpath, "LC_ALL": "C", "PYTHONDONTWRITEBYTECODE": "1"}
        return subprocess.run(
            [sys.executable, "-B", "-E", "-s",
             str(isolated / "appendix/problems/q1/code/reproduce.py"),
             "--compiler", compiler, "--input", str(isolated / "input/values.csv"),
             "--config", str(isolated / "appendix/problems/q1/code/settings.ini"),
             "--output", str(work / name), *extra],
            cwd=work, env=environment, capture_output=True, text=True, timeout=35,
        )

    def assert_mixed_result(self, path: Path, expected=(7, 0)):
        with path.open(newline="") as stream:
            reader = csv.DictReader(stream)
            self.assertEqual(reader.fieldnames, ["candidate", "objective"])
            rows = list(reader)
        self.assertEqual(len(rows), 1)
        self.assertEqual((int(rows[0]["candidate"]), int(rows[0]["objective"])), expected)

    def record_mixed_acceptance(self, workspace: Path, record: str) -> None:
        evidence = workspace / "reports/appendix/evidence/reproduction.txt"
        evidence.write_text(record, encoding="utf-8")
        self.mutate_result(
            workspace, "Python 静态编译和 C++ 构建均通过，本地依赖闭包完整。",
            record.strip(),
        )
        self.mutate_result(
            workspace, "## 10. 局限性与人工复核事项",
            "- E4 — `reports/appendix/evidence/reproduction.txt` — 实际构建、执行范围及精确比较\n\n"
            "## 10. 局限性与人工复核事项",
        )
        diagnostics = check_appendix_result(workspace)
        self.assertFalse([d for d in diagnostics if d.severity == "ERROR"], diagnostics)

    def test_isolated_python_cpp_full_reproduction_and_frozen_integrity(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workspace = root / "formal"
            package = self.mixed_package(workspace)
            before = fingerprint(workspace)
            isolated = root / "extracted"
            shutil.copytree(package, isolated / "appendix")
            shutil.copytree(workspace / "input", isolated / "input")
            for path in isolated.rglob("*"):
                if path.is_file():
                    path.chmod(0o444)
            frozen = fingerprint(isolated / "appendix")
            raw_input = fingerprint(isolated / "input")
            completed = self.run_mixed(isolated, "full")
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            self.assertIn("built-from-source\nfull-search", completed.stdout)
            self.assert_mixed_result(isolated / "work/full/result.csv")
            self.assert_mixed_result(isolated / "appendix/official.csv")
            self.assertEqual(frozen, fingerprint(isolated / "appendix"))
            self.assertEqual(raw_input, fingerprint(isolated / "input"))
            self.assertEqual(before, fingerprint(workspace))
            # A readable but numerically different output is not a successful comparison.
            with self.assertRaises(AssertionError):
                self.assert_mixed_result(isolated / "work/full/result.csv", expected=(6, 0))
            self.record_mixed_acceptance(
                workspace, completed.stdout
                + "full replay: candidate=7, objective=0, exact comparison passed; "
                "source/input/frozen package hashes unchanged; independent work/full output.\n",
            )

    def test_isolated_python_cpp_missing_source_or_configuration_fails(self):
        for missing in ("search.cpp", "search.hpp", "settings.ini", "configuration-drift"):
            with self.subTest(missing=missing), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                workspace = root / "formal"
                package = self.mixed_package(workspace)
                before = fingerprint(workspace)
                isolated = root / "extracted"
                shutil.copytree(package, isolated / "appendix")
                shutil.copytree(workspace / "input", isolated / "input")
                if missing == "configuration-drift":
                    config = isolated / "appendix/problems/q1/code/settings.ini"
                    config.write_text(
                        config.read_text().replace("offset = 1", "offset = 2"),
                        encoding="utf-8",
                    )
                else:
                    (isolated / "appendix/problems/q1/code" / missing).unlink()
                completed = self.run_mixed(isolated, "failure")
                if missing == "configuration-drift":
                    self.assertEqual(completed.returncode, 0, completed.stderr)
                    with self.assertRaises(AssertionError):
                        self.assert_mixed_result(isolated / "work/failure/result.csv")
                else:
                    self.assertNotEqual(completed.returncode, 0, completed.stdout)
                    self.assertFalse((isolated / "work/failure/result.csv").exists())
                self.assertEqual(before, fingerprint(workspace))

    def test_short_search_and_fixed_candidate_recalculation_are_not_full_replay(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workspace = root / "formal"
            package = self.mixed_package(workspace)
            before = fingerprint(workspace)
            isolated = root / "extracted"
            shutil.copytree(package, isolated / "appendix")
            shutil.copytree(workspace / "input", isolated / "input")
            short = self.run_mixed(isolated, "short", "--steps", "2")
            fixed = self.run_mixed(
                isolated, "fixed", "--candidate",
                str(isolated / "appendix/problems/q1/result/candidate.txt"),
            )
            self.assertEqual(short.returncode, 0, short.stderr)
            self.assertEqual(fixed.returncode, 0, fixed.stderr)
            self.assert_mixed_result(isolated / "work/short/result.csv", expected=(1, 36))
            with self.assertRaises(AssertionError):
                self.assert_mixed_result(isolated / "work/short/result.csv")
            self.assert_mixed_result(isolated / "work/fixed/result.csv")
            evidence = short.stdout + fixed.stdout + "full search not rerun\n"
            self.assertIn("short-search", evidence)
            self.assertIn("fixed-candidate-recalculation", evidence)
            self.assertNotIn("full-search", evidence)
            self.assertEqual(before, fingerprint(workspace))
            self.record_mixed_acceptance(
                workspace, evidence
                + "short: candidate=1, objective=36, not equivalent to formal result; "
                "fixed: candidate=7, objective=0, exact comparison passed.\n",
            )

    def declare_current_ai_usage(
        self, workspace: Path, *, copy_target: bool = False
    ) -> None:
        source_relative = "reports/ai-usage/AI 工具使用详情.pdf"
        source = workspace / source_relative
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_bytes(b"%PDF-1.4\nsynthetic test fixture\n%%EOF\n")
        self.mutate_start(
            workspace,
            "外部资料：无",
            "AI 工具使用详情：`appendix/AI 工具使用详情.pdf`\n\n外部资料：无",
        )
        self.mutate_start(
            workspace,
            "- A090 — GENERATE",
            "- A093 — COPY — `reports/ai-usage/AI 工具使用详情.pdf` → "
            "`appendix/AI 工具使用详情.pdf` — 已完成人工验收的 AI 使用详情\n"
            "- A090 — GENERATE",
        )
        if copy_target:
            (workspace / "appendix/AI 工具使用详情.pdf").write_bytes(source.read_bytes())
            self.add_integrity_source(workspace, source_relative)
            self.mutate_result(workspace, "A005、A090", "A005、A093、A090")

    def declare_root_results(
        self, workspace: Path, targets: tuple[str, ...], *, copy_targets: bool = True
    ) -> None:
        entries: list[str] = []
        declared: list[str] = []
        result_ids: list[str] = []
        for index, target in enumerate(targets, 20):
            suffix = Path(target).suffix.lower()
            source_relative = f"problems/q1/outputs/root_{index}{suffix}"
            source = workspace / source_relative
            if suffix == ".xlsx":
                with zipfile.ZipFile(source, "w") as archive:
                    archive.writestr("[Content_Types].xml", "<Types/>")
                    archive.writestr(
                        "xl/workbook.xml",
                        '<workbook xmlns="x"><sheets><sheet name="S" sheetId="1"/></sheets></workbook>',
                    )
            else:
                source.write_text(f"value\n{index}\n", encoding="utf-8")
            identifier = f"A{index:03d}"
            entries.append(
                f"- {identifier} — COPY — `{source_relative}` → `{target}` — 比赛强制提交结果"
            )
            declared.append(f"`{target}`")
            result_ids.append(identifier)
            self.add_integrity_source(workspace, source_relative)
            if copy_targets:
                destination = workspace / target
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
        self.mutate_start(
            workspace, "- A090 — GENERATE",
            "\n".join(entries) + "\n- A090 — GENERATE",
        )
        self.mutate_start(
            workspace, "强制结果文件：无",
            "强制结果文件：" + ", ".join(declared),
        )
        self.mutate_result(
            workspace, "、A090", "、" + "、".join(result_ids) + "、A090",
        )

    def test_exact_headings_and_valid_fixture(self):
        self.assertEqual(len(APPENDIX_START_HEADINGS), 9)
        self.assertEqual(len(APPENDIX_RESULT_HEADINGS), 10)
        self.assertFalse(any(item.severity == "ERROR" for item in check_appendix_start(FIXTURE)))
        self.assertFalse(any(item.severity == "ERROR" for item in check_appendix_result(FIXTURE)))

    def test_preprocess_sources_targets_and_contract_exclusion(self):
        temporary, workspace = self.fixture_copy()
        try:
            pre = workspace / "problems/preprocess"
            for part in ("spec", "code", "data/derived", "outputs", "notes", "result"):
                (pre / part).mkdir(parents=True, exist_ok=True)
            (pre / "code/clean.py").write_text("print('clean')\n", encoding="utf-8")
            (pre / "data/derived/clean.csv").write_text("id\n1\n", encoding="utf-8")
            (pre / "notes/schema.md").write_text("# Schema\n", encoding="utf-8")
            (pre / "spec/START_PRE.md").write_text("# START PRE\n", encoding="utf-8")
            additions = (
                "- A006 — COPY — `problems/preprocess/code/clean.py` → "
                "`appendix/problems/preprocess/code/clean.py` — 公共清洗\n"
                "- A007 — COPY — `problems/preprocess/data/derived/clean.csv` → "
                "`appendix/problems/preprocess/result/clean.csv` — 冻结数据\n"
                "- A008 — COPY — `problems/preprocess/notes/schema.md` → "
                "`appendix/problems/preprocess/result/schema.md` — 数据字典\n"
            )
            self.mutate_start(workspace, "- A090 — GENERATE", additions + "- A090 — GENERATE")
            self.mutate_start(
                workspace,
                "`problems/q1/code/core.py`",
                "`problems/preprocess/code/clean.py`",
            )
            diagnostics = check_appendix_start(workspace)
            self.assertFalse([item for item in diagnostics if item.severity == "ERROR"], diagnostics)
            self.mutate_start(
                workspace,
                "`problems/preprocess/notes/schema.md`",
                "`problems/preprocess/spec/START_PRE.md`",
            )
            self.assertIn(
                "LITE-APPENDIX-SOURCE-PATH-001",
                identifiers(check_appendix_start(workspace)),
            )
        finally:
            temporary.cleanup()

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
            ("提交完整正式求解附件和最终提交文档中的代表性真实代码。", "<!-- only prompt -->", "LITE-APPENDIX-START-EMPTY-WARN-001"),
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

        for current, legacy in (
            ("## 2. 正式结果与认证边界", "## 2. 论文引用、正式结果与认证边界"),
            ("## 5. 正式结果一致性", "## 5. 正式结果与论文一致性"),
        ):
            temporary, workspace = self.fixture_copy()
            try:
                contract = (
                    workspace / "reports/appendix/APPENDIX_START.md"
                    if "## 2." in current
                    else workspace / "reports/appendix/APPENDIX_RESULT.md"
                )
                contract.write_text(
                    contract.read_text(encoding="utf-8").replace(current, legacy),
                    encoding="utf-8",
                )
                checker = check_appendix_start if "## 2." in current else check_appendix_result
                expected = (
                    "LITE-APPENDIX-START-HEADING-001"
                    if "## 2." in current
                    else "LITE-APPENDIX-RESULT-HEADING-001"
                )
                self.assertIn(expected, identifiers(checker(workspace)))
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

    def test_operational_source_names_are_accepted_in_root_code(self):
        names = (
            "scheduler.py", "orchestrator.py", "checkpoint.py", "resume.py",
            "supervisor.py", "stage_ledger.py", "run_status.py",
            "resource_monitor.py", "audit.py",
        )
        old_entry = (
            "- C001 — COPY — `problems/q1/code/core.py` → "
            "`code/q1_core_algorithm.py` — q1 核心算法"
        )
        for name in names:
            with self.subTest(name=name):
                temporary, workspace = self.fixture_copy()
                try:
                    source_relative = f"problems/q1/code/{name}"
                    target_relative = f"code/{name}"
                    content = "def run_formal_stage():\n    return True\n"
                    source = workspace / source_relative
                    source.write_text(content, encoding="utf-8")
                    target = workspace / target_relative
                    target.write_text(content, encoding="utf-8")
                    (workspace / "code/q1_core_algorithm.py").unlink()
                    self.mutate_start(
                        workspace,
                        old_entry,
                        f"- C001 — COPY — `{source_relative}` → `{target_relative}` "
                        "— 正式流程中的真实代表性实现",
                    )
                    self.add_integrity_source(workspace, source_relative)
                    diagnostics = check_appendix_result(workspace)
                    self.assertFalse(
                        [item for item in diagnostics if item.severity == "ERROR"],
                        diagnostics,
                    )
                finally:
                    temporary.cleanup()

    def test_nested_appendix_operational_code_accepts_copy_and_curate(self):
        old_entry = (
            "- A001 — COPY — `problems/q1/code/solve.py` → "
            "`appendix/problems/q1/code/solve.py` — Python 正式入口"
        )
        for mode in ("COPY", "CURATE"):
            with self.subTest(mode=mode):
                temporary, workspace = self.fixture_copy()
                try:
                    source_relative = "problems/q1/code/pipeline/checkpoint.py"
                    target_relative = "appendix/problems/q1/code/pipeline/checkpoint.py"
                    source = workspace / source_relative
                    source.parent.mkdir(parents=True)
                    source.write_text("def resume():\n    return 0\n", encoding="utf-8")
                    target = workspace / target_relative
                    target.parent.mkdir(parents=True)
                    target.write_bytes(source.read_bytes())
                    (workspace / "appendix/problems/q1/code/solve.py").unlink()
                    self.mutate_start(
                        workspace,
                        old_entry,
                        f"- A001 — {mode} — `{source_relative}` → `{target_relative}` "
                        "— 正式断点恢复源码",
                    )
                    self.add_integrity_source(workspace, source_relative)
                    diagnostics = check_appendix_result(workspace)
                    self.assertFalse(
                        [item for item in diagnostics if item.severity == "ERROR"],
                        diagnostics,
                    )
                finally:
                    temporary.cleanup()

    def test_checkpoint_runtime_data_remains_forbidden(self):
        temporary, workspace = self.fixture_copy()
        try:
            source_relative = "problems/q1/code/checkpoint.ckpt"
            target_relative = "appendix/problems/q1/code/checkpoint.ckpt"
            source = workspace / source_relative
            source.write_bytes(b"runtime state")
            target = workspace / target_relative
            target.write_bytes(source.read_bytes())
            (workspace / "appendix/problems/q1/code/solve.py").unlink()
            self.mutate_start(
                workspace,
                "- A001 — COPY — `problems/q1/code/solve.py` → "
                "`appendix/problems/q1/code/solve.py` — Python 正式入口",
                f"- A001 — COPY — `{source_relative}` → `{target_relative}` "
                "— 运行 checkpoint 数据",
            )
            self.add_integrity_source(workspace, source_relative)
            self.assertIn(
                "LITE-APPENDIX-FORBIDDEN-001",
                identifiers(check_appendix_result(workspace)),
            )
        finally:
            temporary.cleanup()

    def test_cache_log_binary_and_temporary_code_targets_remain_forbidden(self):
        targets = (
            "run.log", "module.pyc", "bundle.zip", "native.so",
            "backup/solver.py", "tmp/solver.py", "tests/test_solver.py",
            "build/solver.py", "__pycache__/solver.py", "state.joblib",
            "features.npy", "features.npz", "model.pickle", "model.pkl",
            "model.sav", "model.pt", "model.pth", "result.csv", "notes.md",
            "Result.xlsx",
        )
        old_entry = (
            "- A001 — COPY — `problems/q1/code/solve.py` → "
            "`appendix/problems/q1/code/solve.py` — Python 正式入口"
        )
        for suffix in targets:
            with self.subTest(target=suffix):
                temporary, workspace = self.fixture_copy()
                try:
                    source_relative = f"problems/q1/code/{suffix}"
                    target_relative = f"appendix/problems/q1/code/{suffix}"
                    source = workspace / source_relative
                    source.parent.mkdir(parents=True, exist_ok=True)
                    source.write_bytes(b"artifact")
                    target = workspace / target_relative
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(source.read_bytes())
                    (workspace / "appendix/problems/q1/code/solve.py").unlink()
                    self.mutate_start(
                        workspace,
                        old_entry,
                        f"- A001 — COPY — `{source_relative}` → `{target_relative}` "
                        "— 禁止目标回归",
                    )
                    self.add_integrity_source(workspace, source_relative)
                    self.assertIn(
                        "LITE-APPENDIX-FORBIDDEN-001",
                        identifiers(check_appendix_result(workspace)),
                    )
                finally:
                    temporary.cleanup()

    def test_root_code_readme_and_data_remain_forbidden(self):
        old_entry = (
            "- C001 — COPY — `problems/q1/code/core.py` → "
            "`code/q1_core_algorithm.py` — q1 核心算法"
        )
        for name in ("README.md", "formal.csv", "state.json"):
            with self.subTest(name=name):
                temporary, workspace = self.fixture_copy()
                try:
                    source_relative = f"problems/q1/code/{name}"
                    target_relative = f"code/{name}"
                    source = workspace / source_relative
                    source.write_text("not paper code\n", encoding="utf-8")
                    target = workspace / target_relative
                    target.write_bytes(source.read_bytes())
                    (workspace / "code/q1_core_algorithm.py").unlink()
                    self.mutate_start(
                        workspace,
                        old_entry,
                        f"- C001 — COPY — `{source_relative}` → `{target_relative}` "
                        "— 禁止目标回归",
                    )
                    self.add_integrity_source(workspace, source_relative)
                    self.assertIn(
                        "LITE-APPENDIX-FORBIDDEN-001",
                        identifiers(check_appendix_result(workspace)),
                    )
                finally:
                    temporary.cleanup()

    def test_unsafe_source_target_scope_and_symlinks(self):
        cases = (
            ("problems/q1/code/core.py", "../core.py", "LITE-APPENDIX-SOURCE-PATH-001"),
            ("problems/q1/code/core.py", r"C:\\Users\\x\\core.py", "LITE-APPENDIX-SOURCE-PATH-001"),
            ("problems/q1/code/core.py", "problems/q1/code/\tcore.py", "LITE-APPENDIX-SOURCE-PATH-001"),
            ("code/q1_core_algorithm.py", "code/nested/core.py", "LITE-APPENDIX-TARGET-PATH-001"),
            ("problems/q1/code/core.py", "paper/paper.md", "LITE-APPENDIX-SOURCE-PATH-001"),
            ("problems/q1/code/core.py", "figure/final.py", "LITE-APPENDIX-SOURCE-PATH-001"),
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

    def test_contracts_and_handoffs_are_excluded_sources_and_scanned_for_limitations(self):
        for relative, title in (
            ("problems/q1/spec/START_Q1_1.md", "# START Q1_1"),
            ("problems/q1/result/RESULT_Q1_1.md", "# RESULT Q1_1"),
            ("problems/q1/spec/SUPPLEMENT_START_Q1.md", "# SUPPLEMENT START Q1"),
            ("problems/q1/result/SUPPLEMENT_RESULT_Q1.md", "# SUPPLEMENT RESULT Q1"),
            ("problems/q1/notes/HANDOFF_Q1.md", "# HANDOFF Q1"),
            ("problems/q1/notes/HANDOFF_Q1_1.md", "# HANDOFF Q1_1"),
            ("problems/preprocess/notes/HANDOFF_PRE.md", "# HANDOFF PRE"),
        ):
            with self.subTest(relative=relative):
                temporary, workspace = self.fixture_copy()
                try:
                    source = workspace / relative
                    source.parent.mkdir(parents=True, exist_ok=True)
                    source.write_text(f"{title}\n", encoding="utf-8")
                    self.mutate_start(
                        workspace,
                        "problems/q1/code/core.py",
                        relative,
                    )
                    self.assertIn(
                        "LITE-APPENDIX-SOURCE-PATH-001",
                        identifiers(check_appendix_start(workspace)),
                    )
                finally:
                    temporary.cleanup()

        temporary, workspace = self.fixture_copy()
        try:
            source = workspace / "problems/q1/notes/solver_note.md"
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_text("ordinary internal note\n", encoding="utf-8")
            self.mutate_start(workspace, "problems/q1/code/core.py", source.relative_to(workspace).as_posix())
            found = [
                item for item in check_appendix_start(workspace)
                if item.identifier == "LITE-APPENDIX-SOURCE-PATH-001"
                and item.location == source.relative_to(workspace).as_posix()
            ]
            self.assertTrue(found)
            self.assertTrue(all("internal references" not in item.message for item in found))
        finally:
            temporary.cleanup()

    def test_current_supplement_assets_use_existing_appendix_mappings(self):
        cases = (
            (
                "problems/q1/code/solve.py",
                "problems/q1/code/s1_validation.py",
                "print('supplement validation')\n",
            ),
            (
                "problems/q1/outputs/formal.csv",
                "problems/q1/outputs/s1_formal.csv",
                "value\n2\n",
            ),
            (
                "problems/q1/outputs/formal.csv",
                "problems/q1/data/derived/s1_formal.csv",
                "value\n2\n",
            ),
        )
        for old, relative, content in cases:
            with self.subTest(relative=relative):
                temporary, workspace = self.fixture_copy()
                try:
                    source = workspace / relative
                    source.parent.mkdir(parents=True, exist_ok=True)
                    source.write_text(content, encoding="utf-8")
                    self.mutate_start(workspace, old, relative)
                    self.assertNotIn(
                        "LITE-APPENDIX-SOURCE-PATH-001",
                        identifiers(check_appendix_start(workspace)),
                    )
                finally:
                    temporary.cleanup()

        temporary, workspace = self.fixture_copy()
        try:
            start = workspace / "problems/q1/spec/START_Q1.md"
            result = workspace / "problems/q1/result/RESULT_Q1.md"
            split_start = start.with_name("START_Q1_1.md")
            split_result = result.with_name("RESULT_Q1_1.md")
            start.rename(split_start)
            result.rename(split_result)
            split_start.write_text(
                "# START Q1_1\n\n有限搜索范围。\n",
                encoding="utf-8",
            )
            target = workspace / "appendix/problems/q1/result/formal.csv"
            target.write_text("claim\n全局最优\n", encoding="utf-8")
            found = identifiers(check_appendix_result(workspace))
            self.assertIn("LITE-APPENDIX-CERTIFICATION-WARN-001", found)
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

    def test_current_ai_usage_source_precedes_appendix_and_legacy_stays_valid(self):
        temporary, workspace = self.fixture_copy()
        try:
            self.declare_current_ai_usage(workspace)
            before = fingerprint(workspace)
            diagnostics = check_appendix_start(workspace)
            self.assertFalse([item for item in diagnostics if item.severity == "ERROR"], diagnostics)
            self.assertEqual(before, fingerprint(workspace))
        finally:
            temporary.cleanup()

        self.assertFalse(
            [item for item in check_appendix_start(FIXTURE) if item.severity == "ERROR"]
        )

    def test_current_ai_usage_rejects_missing_wrong_or_non_pdf_sources(self):
        cases = (
            ("missing", "reports/ai-usage/AI 工具使用详情.pdf", None),
            ("empty", "reports/ai-usage/AI 工具使用详情.pdf", b""),
            ("wrong-report", "reports/anything_else.pdf", b"%PDF\n"),
            ("tex", "reports/ai-usage/AI_TOOL_USAGE_DETAILS.tex", b"tex\n"),
            ("screenshot", "reports/ai-usage/figures/chatgpt_example.png", b"png\n"),
        )
        for name, replacement, content in cases:
            with self.subTest(name=name):
                temporary, workspace = self.fixture_copy()
                try:
                    self.declare_current_ai_usage(workspace)
                    original = workspace / "reports/ai-usage/AI 工具使用详情.pdf"
                    if name == "missing":
                        original.unlink()
                    elif name == "empty":
                        original.write_bytes(b"")
                    else:
                        candidate = workspace / replacement
                        candidate.parent.mkdir(parents=True, exist_ok=True)
                        candidate.write_bytes(content or b"")
                        self.mutate_start(
                            workspace,
                            "reports/ai-usage/AI 工具使用详情.pdf",
                            replacement,
                        )
                    found = identifiers(check_appendix_start(workspace))
                    expected = (
                        "LITE-APPENDIX-SOURCE-MISSING-001"
                        if name in {"missing", "empty"} else "LITE-APPENDIX-SOURCE-PATH-001"
                    )
                    self.assertIn(expected, found)
                finally:
                    temporary.cleanup()

    def test_current_ai_usage_declaration_whitelist_and_copy_mode_are_exact(self):
        mutations = (
            (
                "wrong-target",
                lambda root: self.mutate_start(
                    root, "appendix/AI 工具使用详情.pdf", "appendix/AI详情.pdf"
                ),
            ),
            (
                "curate",
                lambda root: self.mutate_start(root, "A093 — COPY", "A093 — CURATE"),
            ),
            (
                "generate",
                lambda root: self.mutate_start(
                    root,
                    "- A093 — COPY — `reports/ai-usage/AI 工具使用详情.pdf` → "
                    "`appendix/AI 工具使用详情.pdf` — 已完成人工验收的 AI 使用详情",
                    "- A093 — GENERATE — `appendix/AI 工具使用详情.pdf` — invalid",
                ),
            ),
            (
                "duplicate",
                lambda root: self.mutate_start(
                    root, "- A090 — GENERATE",
                    "- A094 — COPY — `reports/ai-usage/AI 工具使用详情.pdf` → "
                    "`appendix/AI 工具使用详情.pdf` — duplicate\n- A090 — GENERATE",
                ),
            ),
            (
                "declaration-only",
                lambda root: self.mutate_start(
                    root,
                    "- A093 — COPY — `reports/ai-usage/AI 工具使用详情.pdf` → "
                    "`appendix/AI 工具使用详情.pdf` — 已完成人工验收的 AI 使用详情\n",
                    "",
                ),
            ),
            (
                "whitelist-only",
                lambda root: self.mutate_start(
                    root,
                    "AI 工具使用详情：`appendix/AI 工具使用详情.pdf`\n\n",
                    "",
                ),
            ),
        )
        for name, mutate in mutations:
            with self.subTest(name=name):
                temporary, workspace = self.fixture_copy()
                try:
                    self.declare_current_ai_usage(workspace)
                    mutate(workspace)
                    self.assertTrue(
                        [item for item in check_appendix_start(workspace) if item.severity == "ERROR"]
                    )
                finally:
                    temporary.cleanup()

    def test_malformed_ai_usage_label_does_not_fall_back_to_legacy(self):
        malformed = (
            "AI 工具使用详情:`appendix/AI 工具使用详情.pdf`",
            "AI 工具使用详情 ：`appendix/AI 工具使用详情.pdf`",
            "AI工具使用详情：`appendix/AI 工具使用详情.pdf`",
        )
        for declaration in malformed:
            with self.subTest(declaration=declaration):
                temporary, workspace = self.fixture_copy()
                try:
                    self.mutate_start(
                        workspace, "外部资料：无",
                        f"{declaration}\n\n外部资料：无",
                    )
                    self.assertIn(
                        "LITE-APPENDIX-DECLARATION-001",
                        identifiers(check_appendix_start(workspace)),
                    )
                finally:
                    temporary.cleanup()

    def test_current_ai_usage_result_requires_byte_identical_root_copy(self):
        temporary, workspace = self.fixture_copy()
        try:
            self.declare_current_ai_usage(workspace, copy_target=True)
            before = fingerprint(workspace)
            diagnostics = check_appendix_result(workspace)
            self.assertFalse([item for item in diagnostics if item.severity == "ERROR"], diagnostics)
            self.assertEqual(before, fingerprint(workspace))
            (workspace / "appendix/AI 工具使用详情.pdf").write_bytes(b"changed")
            self.assertIn(
                "LITE-APPENDIX-COPY-MISMATCH-001",
                identifiers(check_appendix_result(workspace)),
            )
        finally:
            temporary.cleanup()

    def test_mandatory_root_results_support_one_multiple_and_legacy_name(self):
        for targets in (
            ("appendix/Result.xlsx",),
            ("appendix/Q2_result.xlsx",),
            ("appendix/Result.xlsx", "appendix/Q2_result.csv", "appendix/notes.txt"),
        ):
            with self.subTest(targets=targets):
                temporary, workspace = self.fixture_copy()
                try:
                    self.declare_root_results(workspace, targets)
                    diagnostics = check_appendix_result(workspace)
                    self.assertFalse(
                        [item for item in diagnostics if item.severity == "ERROR"], diagnostics
                    )
                finally:
                    temporary.cleanup()

    def test_current_ai_multiple_root_results_and_nested_support_compose(self):
        temporary, workspace = self.fixture_copy()
        try:
            self.declare_current_ai_usage(workspace, copy_target=True)
            self.declare_root_results(
                workspace,
                ("appendix/Result.xlsx", "appendix/Q2_result.csv"),
            )
            before = fingerprint(workspace)
            diagnostics = check_appendix_result(workspace)
            self.assertFalse(
                [item for item in diagnostics if item.severity == "ERROR"], diagnostics
            )
            self.assertEqual(before, fingerprint(workspace))
            self.assertTrue(
                (workspace / "appendix/problems/q1/result/formal.csv").is_file()
            )
        finally:
            temporary.cleanup()

    def test_mandatory_root_result_declaration_fails_closed(self):
        invalid = (
            "`appendix/Q.csv`, `appendix/Q.csv`",
            "`appendix/results/Q.csv`",
            "`appendix/Q.pdf`",
            "`appendix/AI 工具使用详情.pdf`",
            "`appendix/.hidden.csv`",
            "`appendix/Q_backup.csv`",
        )
        for payload in invalid:
            with self.subTest(payload=payload):
                temporary, workspace = self.fixture_copy()
                try:
                    self.mutate_start(
                        workspace, "强制结果文件：无", f"强制结果文件：{payload}"
                    )
                    self.assertIn(
                        "LITE-APPENDIX-DECLARATION-001",
                        identifiers(check_appendix_start(workspace)),
                    )
                finally:
                    temporary.cleanup()

    def test_root_result_declaration_and_whitelist_must_match_and_use_copy(self):
        cases = ("undeclared", "missing-entry", "curate", "generate")
        for case in cases:
            with self.subTest(case=case):
                temporary, workspace = self.fixture_copy()
                try:
                    self.declare_root_results(workspace, ("appendix/Q2_result.csv",))
                    if case == "undeclared":
                        self.mutate_start(
                            workspace,
                            "强制结果文件：`appendix/Q2_result.csv`",
                            "强制结果文件：无",
                        )
                    elif case == "missing-entry":
                        self.mutate_start(
                            workspace,
                            "- A020 — COPY — `problems/q1/outputs/root_20.csv` → "
                            "`appendix/Q2_result.csv` — 比赛强制提交结果\n",
                            "",
                        )
                    elif case == "curate":
                        self.mutate_start(workspace, "A020 — COPY", "A020 — CURATE")
                    else:
                        self.mutate_start(
                            workspace,
                            "- A020 — COPY — `problems/q1/outputs/root_20.csv` → "
                            "`appendix/Q2_result.csv` — 比赛强制提交结果",
                            "- A020 — GENERATE — `appendix/Q2_result.csv` — invalid",
                        )
                    self.assertTrue(
                        [item for item in check_appendix_start(workspace) if item.severity == "ERROR"]
                    )
                finally:
                    temporary.cleanup()

    def test_root_result_hash_text_structure_and_authoritative_copy(self):
        temporary, workspace = self.fixture_copy()
        try:
            self.declare_root_results(workspace, ("appendix/Q2_result.csv",))
            (workspace / "appendix/Q2_result.csv").write_text("changed\n", encoding="utf-8")
            self.assertIn(
                "LITE-APPENDIX-COPY-MISMATCH-001",
                identifiers(check_appendix_result(workspace)),
            )
            (workspace / "appendix/Q2_result.csv").write_bytes(b"\xff")
            self.assertIn(
                "LITE-APPENDIX-FORBIDDEN-001",
                identifiers(check_appendix_result(workspace)),
            )
            (workspace / "appendix/Q2_result.csv").write_bytes(b"")
            self.assertIn(
                "LITE-APPENDIX-FORBIDDEN-001",
                identifiers(check_appendix_result(workspace)),
            )
        finally:
            temporary.cleanup()

        temporary, workspace = self.fixture_copy()
        try:
            self.declare_root_results(workspace, ("appendix/Q2_result.xlsx",))
            source = workspace / "problems/q1/outputs/root_20.xlsx"
            source.write_bytes(b"not a workbook")
            shutil.copy2(source, workspace / "appendix/Q2_result.xlsx")
            self.assertIn(
                "LITE-APPENDIX-XLSX-001",
                identifiers(check_appendix_result(workspace)),
            )
        finally:
            temporary.cleanup()

        temporary, workspace = self.fixture_copy()
        try:
            source = "problems/q1/outputs/formal.csv"
            self.mutate_start(
                workspace, "- A090 — GENERATE",
                "- A020 — COPY — `problems/q1/outputs/formal.csv` → "
                "`appendix/Result.csv` — 官方根结果\n- A090 — GENERATE",
            )
            self.mutate_start(
                workspace, "强制结果文件：无",
                "强制结果文件：`appendix/Result.csv`",
            )
            self.mutate_result(workspace, "A005、A090", "A005、A020、A090")
            shutil.copy2(workspace / source, workspace / "appendix/Result.csv")
            self.assertIn(
                "LITE-APPENDIX-DUPLICATE-001",
                identifiers(check_appendix_result(workspace)),
            )
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

        temporary, workspace = self.fixture_copy()
        try:
            self.declare_current_ai_usage(workspace, copy_target=True)
            changed = b"%PDF-1.4\nchanged after integrity record\n%%EOF\n"
            (workspace / "reports/ai-usage/AI 工具使用详情.pdf").write_bytes(changed)
            (workspace / "appendix/AI 工具使用详情.pdf").write_bytes(changed)
            before = fingerprint(workspace)
            self.assertIn(
                "LITE-APPENDIX-INTEGRITY-001",
                identifiers(check_appendix_result(workspace)),
            )
            self.assertEqual(before, fingerprint(workspace))
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

    def test_sensitive_redaction_and_certification_warning(self):
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
            self.assertNotIn("LITE-APPENDIX-DEPENDENCY-WARN-001", found)
        finally:
            temporary.cleanup()

    def test_python_runtime_writers_are_allowed_but_copy_integrity_still_applies(self):
        fixture_writer = (CORE_FIXTURE / "core_write.py").read_text(encoding="utf-8")
        writers = (
            fixture_writer,
            "def solve(values):\n    return open('out.csv', 'w')\n",
            "from pathlib import Path\nPath('out.txt').write_text('x')\n",
            "from pathlib import Path\nPath('out.txt').open('w')\n",
            "from pathlib import Path\np = Path('out.txt')\np.open(mode='w')\n",
            "import io\nio.open('out.txt', 'w')\n",
            "from io import open as io_open\nio_open('out.txt', 'w')\n",
            "import pandas as pd\ndf.to_csv('out.csv')\n",
            "import pandas as pd\ndf.to_json(path_or_buf='out.json')\n",
            "import pandas as pd\ndf.to_markdown(buf='out.md')\n",
            "import numpy as np\nnp.save('out.npy', arr)\n",
            "from numpy import save as np_save\nnp_save('out.npy', arr)\n",
            "import scipy.sparse\nscipy.sparse.save_npz('out.npz', matrix)\n",
            "import joblib\njoblib.dump(obj, 'out.joblib')\n",
            "from joblib import dump as joblib_dump\njoblib_dump(obj, 'out.joblib')\n",
            "import pickle\npickle.dump(obj, fp)\n",
            "from pickle import dump as pickle_dump\npickle_dump(obj, fp)\n",
            "import json\njson.dump({}, fp)\n",
            "from json import dump as json_dump\njson_dump({}, fp)\n",
            "import yaml\nyaml.dump({}, fp)\n",
            "import yaml\nyaml.dump({}, stream)\n",
            "from yaml import dump as yaml_dump\nyaml_dump({}, fp)\n",
            "import tempfile\ntempfile.NamedTemporaryFile()\n",
            "from tempfile import mkstemp\nmkstemp()\n",
            "import shutil\nshutil.copy('a', 'b')\n",
            "from shutil import move\nmove('a', 'b')\n",
            "import os\nos.makedirs('out')\n",
            "from os import mkdir\nmkdir('out')\n",
            "import shelve\nshelve.open('out.db')\n",
            "from shelve import open as shelve_open\nshelve_open('out.db')\n",
            "import sqlite3\nsqlite3.connect('out.db')\n",
            "from sqlite3 import connect\nconnect('out.db')\n",
            "import torch\ntorch.save(model, 'out.pt')\n",
            "from torch import save as torch_save\ntorch_save(model, 'out.pt')\n",
            "model.save('out.pt')\n",
        )
        for source_text in writers:
            with self.subTest(source_text=source_text):
                temporary, workspace = self.fixture_copy()
                try:
                    path = workspace / "appendix/problems/q1/code/solve.py"
                    path.write_text(source_text, encoding="utf-8")
                    diagnostics = check_appendix_result(workspace)
                    side_effects = [
                        item for item in diagnostics
                        if item.identifier == "LITE-APPENDIX-CODE-SIDE-EFFECT-001"
                    ]
                    self.assertFalse(side_effects, diagnostics)
                    self.assertIn("LITE-APPENDIX-COPY-MISMATCH-001", identifiers(diagnostics))
                finally:
                    temporary.cleanup()

        temporary, workspace = self.fixture_copy()
        try:
            path = workspace / "appendix/problems/q1/code/solve.py"
            path.write_text(
                (CORE_FIXTURE / "core_read_only.py").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            found = identifiers(check_appendix_result(workspace))
            self.assertNotIn("LITE-APPENDIX-CODE-SIDE-EFFECT-001", found)
        finally:
            temporary.cleanup()

        allowed = (
            "open('input.csv')\n",
            "open('input.csv', 'rb')\n",
            "from pathlib import Path\nPath('input.csv').open('r')\n",
            "from pathlib import Path\np = Path('input.csv')\np.open()\n",
            "import io\nio.open('input.csv', 'rb')\n",
            "import pandas as pd\ndf.to_csv()\n",
            "import pandas as pd\ndf.to_csv(path_or_buf=None)\n",
            "import pandas as pd\ndf.to_json()\n",
            "import pandas as pd\ndf.to_markdown()\n",
            "import yaml\nyaml.dump({})\n",
            "import yaml\nyaml.dump({}, stream=None)\n",
            "import json\njson.dump({}, None)\n",
            "import sqlite3\nsqlite3.connect(':memory:')\n",
            "import sqlite3\nsqlite3.connect('file:memdb?mode=memory&cache=shared', uri=True)\n",
            "class Custom:\n    def write_text(self, value):\n        return value\n    def mkdir(self):\n        return None\n    def save(self):\n        return None\ncustom = Custom()\ncustom.write_text('x')\ncustom.mkdir()\ncustom.save()\n",
        )
        for source_text in allowed:
            with self.subTest(allowed_source_text=source_text):
                temporary, workspace = self.fixture_copy()
                try:
                    path = workspace / "appendix/problems/q1/code/solve.py"
                    path.write_text(source_text, encoding="utf-8")
                    found = identifiers(check_appendix_result(workspace))
                    self.assertNotIn("LITE-APPENDIX-CODE-SIDE-EFFECT-001", found)
                finally:
                    temporary.cleanup()

    def test_native_runtime_writers_are_allowed_but_copy_integrity_still_applies(self):
        fixture_writer = (CORE_FIXTURE / "core_write.cpp").read_text(encoding="utf-8")
        writers = (
            fixture_writer,
            'int run() { auto* f = fopen("out.csv", "w"); return f != nullptr; }\n',
            '#include <fstream>\nstd::ofstream out("out.csv");\n',
            '#include <fstream>\nstd::fstream out("out.csv", std::ios::out);\n',
            '#include <fcntl.h>\nint fd = open("out.bin", O_CREAT | O_WRONLY);\n',
            '#include <sys/stat.h>\nint run() { return mkdir("out", 0700); }\n',
        )
        target = "appendix/problems/q2/code/solver.cpp"
        for source_text in writers:
            with self.subTest(source_text=source_text):
                temporary, workspace = self.fixture_copy()
                try:
                    (workspace / target).write_text(source_text, encoding="utf-8")
                    found = identifiers(check_appendix_result(workspace))
                    self.assertNotIn("LITE-APPENDIX-CODE-SIDE-EFFECT-001", found)
                    self.assertIn("LITE-APPENDIX-COPY-MISMATCH-001", found)
                finally:
                    temporary.cleanup()

        temporary, workspace = self.fixture_copy()
        try:
            (workspace / target).write_text(
                '#include "solver.hpp"\nint best(int a, int b) { return a > b ? a : b; }\n',
                encoding="utf-8",
            )
            found = identifiers(check_appendix_result(workspace))
            self.assertNotIn("LITE-APPENDIX-CODE-SIDE-EFFECT-001", found)
        finally:
            temporary.cleanup()

        temporary, workspace = self.fixture_copy()
        try:
            (workspace / target).write_text(
                '/*\n'
                'std::ofstream out("x");\n'
                'fopen("x", "w");\n'
                '*/\n'
                'const char* text = "std::ofstream";\n'
                '// fopen("x", "w");\n'
                'int best(int a, int b) { return a > b ? a : b; }\n',
                encoding="utf-8",
            )
            found = identifiers(check_appendix_result(workspace))
            self.assertNotIn("LITE-APPENDIX-CODE-SIDE-EFFECT-001", found)
        finally:
            temporary.cleanup()


if __name__ == "__main__":
    unittest.main()
