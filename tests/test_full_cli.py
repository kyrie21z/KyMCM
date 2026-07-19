from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from tests.full.helpers import model_spec, result
from tests.full.test_problem_definition import payload as definition_payload


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills/kymcm-full/scripts"
FULL = SCRIPTS / "full_checkpoint.py"
MODE = SCRIPTS / "workflow_mode.py"
sys.path.insert(0, str(SCRIPTS))
from full_checkpoint import _evidence_guard, _git_guard, _result, result_review_hash
from checkpoint_full.core import LiteValidationError
from checkpoint_full.render import render_result_document


class FullV1CliTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(dir=ROOT)
        self.workspace = Path(self.temporary.name)
        (self.workspace / ".kymcm").mkdir()
        self.write(".kymcm/mode.json", {"workflow": "kymcm_full", "version": 1})
        for name in ("input", "paper", "reports"):
            (self.workspace / name).mkdir()
        (self.workspace / "AGENTS.md").write_text("synthetic", encoding="utf-8")
        (self.workspace / "README.md").write_text("synthetic", encoding="utf-8")
        (self.workspace / "problems/problem_definition").mkdir(parents=True)
        for q in range(1, 5):
            for part in ("spec", "code", "data/derived", "outputs", "notes", "result"):
                (self.workspace / f"problems/q{q}/{part}").mkdir(parents=True, exist_ok=True)
        self.cli("init-problem-definition")
        for q in range(1, 5): self.cli("--problem", str(q), "init")

    def tearDown(self): self.temporary.cleanup()

    def write(self, relative, payload):
        path = self.workspace / relative; path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8"); return path

    def cli(self, *arguments, ok=True):
        completed = subprocess.run([sys.executable, str(FULL), "--workspace", str(self.workspace), *arguments], cwd=self.workspace, text=True, capture_output=True)
        if ok and completed.returncode: self.fail(completed.stderr)
        return completed

    def fingerprint(self):
        digest=hashlib.sha256()
        for path in sorted(p for p in self.workspace.rglob("*") if p.is_file() and not p.is_symlink()):
            digest.update(str(path.relative_to(self.workspace)).encode()); digest.update(path.read_bytes())
        return digest.hexdigest()

    def accept_definition(self):
        self.write("problems/problem_definition/problem_definition.json", definition_payload())
        self.cli("submit-problem-definition")
        self.cli("accept-problem-definition", "--user-message", "I accept the synthetic whole problem.")

    def accept_start(self):
        self.accept_definition()
        self.write("problems/q1/spec/model_spec.json", model_spec().payload())
        self.cli("--problem", "1", "submit-start", "--recommendation", "Use it")
        self.cli("--problem", "1", "accept-start", "--recommendation", "Use it", "--user-message", "I approve the Start.")

    def test_mode_layout_and_definition_gate(self):
        self.assertEqual(subprocess.check_output([sys.executable, str(MODE), "--workspace", str(self.workspace)], text=True).strip(), "kymcm_full")
        self.cli("validate-layout")
        self.write("problems/q1/spec/model_spec.json", model_spec().payload())
        self.assertNotEqual(self.cli("--problem", "1", "submit-start", "--recommendation", "Use it", ok=False).returncode, 0)
        self.accept_definition()
        self.cli("--problem", "1", "submit-start", "--recommendation", "Use it")
        start = self.workspace / "problems/q1/spec/START_Q1.md"
        text = start.read_text(encoding="utf-8")
        self.assertIn("数学符号表", text); self.assertIn("S_i=\\sum_j", text)
        start.write_text(text + "tamper", encoding="utf-8")
        self.assertNotEqual(self.cli("--problem", "1", "accept-start", "--recommendation", "Use it", "--user-message", "approve", ok=False).returncode, 0)

    def test_submit_start_requires_prestart_audit_without_partial_write(self):
        self.accept_definition()
        incomplete = model_spec().payload()
        del incomplete["data_semantics"]["prestart_audit"]
        self.write("problems/q1/spec/model_spec.json", incomplete)
        workflow_path = self.workspace / ".kymcm/checkpoint_lite/q1/checkpoint/workflow.json"
        before = workflow_path.read_bytes()
        failed = self.cli(
            "--problem", "1", "submit-start", "--recommendation", "Use it",
            ok=False,
        )
        self.assertNotEqual(failed.returncode, 0)
        self.assertEqual(before, workflow_path.read_bytes())
        self.assertFalse((self.workspace / "problems/q1/spec/START_Q1.md").exists())

        self.write("problems/q1/spec/model_spec.json", model_spec().payload())
        self.cli("--problem", "1", "submit-start", "--recommendation", "Use it")
        self.assertTrue((self.workspace / "problems/q1/spec/START_Q1.md").is_file())

    def test_accepted_definition_or_start_json_mutation_is_rejected(self):
        self.accept_definition()
        definition = definition_payload(overall_objective="Mutated after acceptance.")
        self.write("problems/problem_definition/problem_definition.json", definition)
        self.write("problems/q1/spec/model_spec.json", model_spec().payload())
        self.assertNotEqual(self.cli("--problem", "1", "submit-start", "--recommendation", "Use it", ok=False).returncode, 0)
        self.write("problems/problem_definition/problem_definition.json", definition_payload())
        self.cli("--problem", "1", "submit-start", "--recommendation", "Use it")
        changed = model_spec(objective="Changed after review.").payload()
        self.write("problems/q1/spec/model_spec.json", changed)
        self.assertNotEqual(self.cli("--problem", "1", "accept-start", "--recommendation", "Use it", "--user-message", "approve", ok=False).returncode, 0)

    def test_definition_revision_only_mutation_is_rejected_atomically(self):
        self.write("problems/problem_definition/problem_definition.json", definition_payload(revision=1))
        self.cli("submit-problem-definition")
        self.write("problems/problem_definition/problem_definition.json", definition_payload(revision=2))
        before = self.fingerprint()
        failed = self.cli("accept-problem-definition", "--user-message", "approve", ok=False)
        self.assertNotEqual(failed.returncode, 0)
        self.assertEqual(before, self.fingerprint())
        flow = json.loads((self.workspace / ".kymcm/checkpoint_lite/problem_definition/workflow.json").read_text())
        self.assertEqual((flow["state"], flow["revision"]), ("awaiting_review", 1))

    def test_result_artifact_only_mutation_is_rejected_atomically(self):
        self.accept_start()
        for name in ("a.json", "b.json"):
            (self.workspace / f"problems/q1/outputs/{name}").write_text("{}", encoding="utf-8")
        revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        record = result(model_spec()).payload()
        record["evidence"] = {"input_hash":"a"*64, "code_revision":revision,
                              "result_hash":"", "artifacts":[{
                                  "id": "summary_csv", "path": "problems/q1/outputs/a.json",
                                  "kind": "json", "purpose": "fixture evidence",
                              }]}
        self.write("problems/q1/result/result_record.json", record)
        self.cli("--problem", "1", "submit-result")
        submitted = json.loads((self.workspace / "problems/q1/result/result_record.json").read_text())
        submitted["evidence"]["artifacts"][0]["path"] = "problems/q1/outputs/b.json"
        submitted["evidence"]["result_hash"] = ""
        self.write("problems/q1/result/result_record.json", submitted)
        before = self.fingerprint()
        failed = self.cli("--problem", "1", "accept-result", "--user-message", "approve", ok=False)
        self.assertNotEqual(failed.returncode, 0)
        self.assertEqual(before, self.fingerprint())
        flow = json.loads((self.workspace / ".kymcm/checkpoint_lite/q1/checkpoint/workflow.json").read_text())
        self.assertEqual(flow["state"], "awaiting_result_review")

    def test_root_allowlist_rejects_trial_style_files(self):
        for relative in ("q1_analysis.py", "MODEL_SPEC_Q1.json", "outputs/q1/x.csv", "__pycache__/x.pyc"):
            path = self.workspace / relative; path.parent.mkdir(parents=True, exist_ok=True); path.write_text("x")
            with self.subTest(relative=relative): self.assertNotEqual(self.cli("validate-layout", ok=False).returncode, 0)
            if path.is_file(): path.unlink()
            while path.parent != self.workspace and not any(path.parent.iterdir()): parent=path.parent; parent.rmdir(); path=parent

    def test_resolved_ambiguity_is_rendered_as_frozen_tradeoff(self):
        self.write("problems/problem_definition/problem_definition.json", definition_payload(
            ambiguities=[{"issue":"Reliability meaning", "resolution":"Use absolute agreement", "impact":"Changes Q1 decision logic"}],
        ))
        self.cli("submit-problem-definition")
        markdown = (self.workspace / "problems/problem_definition/PROBLEM_DEFINITION.md").read_text()
        self.assertIn("已冻结的关键建模取舍", markdown)
        self.assertIn("Use absolute agreement", markdown)
        self.assertNotIn("用户原话", markdown)

    def test_parser_exposes_no_consultation_or_decision_commands(self):
        help_text = subprocess.check_output([sys.executable, str(FULL), "--help"], text=True)
        for command in ("open-problem-consultation", "record-problem-consultation", "open-consultation", "resolve-consultation", "open-decision", "resolve-decision"):
            with self.subTest(command=command):
                self.assertNotIn(command, help_text)
                self.assertNotEqual(self.cli(command, ok=False).returncode, 0)

    def test_skill_classifies_modeling_question_and_implementation_detail(self):
        skill = (ROOT / "skills/kymcm-full/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("可信度如何定义", skill)
        self.assertIn("使用哪个 Excel 解析库", skill)
        self.assertIn("do not manufacture questions or fictional alternatives", skill)

    def test_normal_workflow_generates_no_brainstorm_infrastructure(self):
        self.accept_definition()
        self.write("problems/q1/spec/model_spec.json", model_spec().payload())
        self.cli("--problem", "1", "submit-start", "--recommendation", "Use it")
        forbidden = {"pending_choice.json", "decisions.jsonl", "consultations.jsonl", "brainstorm.json", "BRAINSTORM.md"}
        self.assertFalse(forbidden & {path.name for path in self.workspace.rglob("*")})

    def test_evidence_guards_and_result_hash(self):
        spec = model_spec(); base = result(spec).payload(); base["evidence"]["artifacts"][0]["path"] = "problems/q1/outputs/a.json"
        output = self.workspace / "problems/q1/outputs/a.json"; output.write_text("{}")
        from full_checkpoint import _result
        record = _result(base); _evidence_guard(self.workspace, 1, record)
        for bad in ("../x", "/tmp/x", "problems/q2/outputs/x", "reports/phase1_trials/x"):
            changed=copy.deepcopy(base); changed["evidence"]["artifacts"][0]["path"] = bad
            with self.subTest(bad=bad), self.assertRaises(ValueError): _evidence_guard(self.workspace, 1, _result(changed))
        link=self.workspace/"problems/q1/outputs/link"; link.symlink_to(output)
        changed=copy.deepcopy(base); changed["evidence"]["artifacts"][0]["path"] = "problems/q1/outputs/link"
        with self.assertRaises(ValueError): _evidence_guard(self.workspace,1,_result(changed))
        stable=result_review_hash(base); changed=copy.deepcopy(base); changed["limitations"][0]["impact"]="changed"
        self.assertNotEqual(stable,result_review_hash(changed))

    def test_result_loader_accepts_truly_missing_optional_conclusions(self):
        payload = result(model_spec()).payload()
        payload.pop("statistical_conclusion")
        payload.pop("operational_conclusion")
        record = _result(payload)
        self.assertIsNone(record.statistical_conclusion)
        self.assertIsNone(record.operational_conclusion)
        rendered = render_result_document(record, self.workspace)
        self.assertNotIn("### 统计结论", rendered)
        self.assertNotIn("### 操作性结论", rendered)

        invalid = copy.deepcopy(payload)
        invalid["operational_conclusion"] = {"text": "", "evidence_ids": []}
        with self.assertRaises(LiteValidationError):
            _result(invalid)

    def test_result_review_hash_covers_complete_evidence_without_mutating_input(self):
        payload = result(model_spec()).payload()
        payload["evidence"]["artifacts"][0]["path"] = "problems/q1/outputs/a.json"
        payload["evidence"]["extension"] = {"source":"fixture"}
        original = copy.deepcopy(payload)
        stable = result_review_hash(payload)
        self.assertEqual(stable, result_review_hash(copy.deepcopy(payload)))
        changed_hash = copy.deepcopy(payload); changed_hash["evidence"]["result_hash"] = "f" * 64
        self.assertEqual(stable, result_review_hash(changed_hash))
        changed_artifact = copy.deepcopy(payload); changed_artifact["evidence"]["artifacts"][0]["path"] = "problems/q1/outputs/b.json"
        self.assertNotEqual(stable, result_review_hash(changed_artifact))
        changed_extension = copy.deepcopy(payload); changed_extension["evidence"]["extension"]["source"] = "other"
        self.assertNotEqual(stable, result_review_hash(changed_extension))
        self.assertEqual(payload, original)
        nonfinite = copy.deepcopy(payload); nonfinite["evidence"]["extension"]["value"] = float("nan")
        with self.assertRaises(ValueError):
            result_review_hash(nonfinite)

    def test_dirty_relevant_code_is_rejected(self):
        code = self.workspace / "problems/q1/code/model.py"; code.write_text("print('synthetic')")
        record = result(model_spec(), evidence={"input_hash":"a"*64,"code_revision":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),"result_hash":"b"*64,"artifacts":[{"id":"summary_csv","path":"problems/q1/code/model.py","kind":"py","purpose":"fixture code"}]})
        with self.assertRaises(ValueError): _git_guard(self.workspace, 1, record)


if __name__ == "__main__": unittest.main()
