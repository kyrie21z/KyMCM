import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "skills/kymcm-full/scripts"))

from checkpoint_full.storage import CheckpointStore, StorageError
from checkpoint_full.workflow import Workflow
from checkpoint_full.workflow import transition
from tests.full.helpers import model_spec, result


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.store = CheckpointStore(self.temporary.name)

    def test_round_trips_all_authoritative_artifacts(self):
        spec = model_spec()
        self.store.save_workflow(Workflow(1))
        self.store.save_model_spec(spec)
        self.store.save_result(result(spec))
        self.assertEqual(self.store.load_workflow(), Workflow(1))
        self.assertEqual(self.store.load_model_spec(), spec)
        self.assertEqual(self.store.load_result(), result(spec))

    def test_load_result_defaults_only_missing_optional_conclusions(self):
        payload = result().payload()
        payload.pop("statistical_conclusion")
        payload.pop("operational_conclusion")
        self.store._atomic_json("result_record.json", payload)
        loaded = self.store.load_result()
        self.assertIsNone(loaded.statistical_conclusion)
        self.assertIsNone(loaded.operational_conclusion)

        invalid = result().payload()
        invalid["statistical_conclusion"] = {"text": "", "evidence_ids": []}
        self.store._atomic_json("result_record.json", invalid)
        with self.assertRaises(StorageError):
            self.store.load_result()

    def test_round_trips_result_review_binding(self):
        spec = model_spec()
        start = transition(Workflow(1), "submit_start", {"spec": spec})
        running = transition(start, "accept_start", {"spec": spec})
        review = transition(running, "submit_result", {"spec": spec, "result": result(spec)})
        self.store.save_workflow(review)
        self.assertEqual(self.store.load_workflow(), review)

    def test_rejects_path_escape(self):
        with self.assertRaises(StorageError):
            self.store._path("../outside.json")
        with self.assertRaises(StorageError):
            self.store._path("nested/file.json")

    def test_failed_atomic_replace_preserves_old_snapshot(self):
        self.store.save_workflow(Workflow(1))
        path = Path(self.temporary.name) / "checkpoint" / "workflow.json"
        old = path.read_bytes()
        with patch("checkpoint_full.storage.os.replace", side_effect=OSError("boom")):
            with self.assertRaises(OSError):
                self.store.save_workflow(Workflow(2))
        self.assertEqual(path.read_bytes(), old)

    def test_reads_are_strict_and_events_are_append_only(self):
        checkpoint = Path(self.temporary.name) / "checkpoint"
        checkpoint.mkdir()
        (checkpoint / "workflow.json").write_text('{"state":"unknown"}', encoding="utf-8")
        with self.assertRaises(StorageError):
            self.store.load_workflow()
        self.store.append_event({"event": "first"})
        self.store.append_event({"event": "second"})
        lines = (checkpoint / "events.jsonl").read_text(encoding="utf-8").splitlines()
        self.assertEqual([json.loads(line)["event"] for line in lines], ["first", "second"])

    def test_rejects_internally_inconsistent_workflow(self):
        checkpoint = Path(self.temporary.name) / "checkpoint"
        checkpoint.mkdir()
        payload = Workflow(1).payload()
        payload.update({"state": "running", "spec_revision": None, "spec_hash": None})
        (checkpoint / "workflow.json").write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaises(StorageError):
            self.store.load_workflow()

    def test_rejects_checkpoint_directory_symlink(self):
        root = Path(self.temporary.name)
        outside = root.parent / f"{root.name}-outside"
        outside.mkdir()
        self.addCleanup(lambda: outside.rmdir())
        (root / "checkpoint").symlink_to(outside, target_is_directory=True)
        for operation in (
            lambda: self.store.save_workflow(Workflow(1)),
            lambda: self.store.load_workflow(),
            lambda: self.store.append_event({"event": "x"}),
        ):
            with self.subTest(operation=operation), self.assertRaises(StorageError):
                operation()
        self.assertEqual(list(outside.iterdir()), [])

    def test_rejects_storage_file_symlinks_for_read_and_write(self):
        root = Path(self.temporary.name)
        checkpoint = root / "checkpoint"
        checkpoint.mkdir()
        outside = root / "outside.json"
        outside.write_text("untouched", encoding="utf-8")
        (checkpoint / "workflow.json").symlink_to(outside)
        with self.assertRaises(StorageError):
            self.store.load_workflow()
        with self.assertRaises(StorageError):
            self.store.save_workflow(Workflow(1))
        self.assertEqual(outside.read_text(encoding="utf-8"), "untouched")
