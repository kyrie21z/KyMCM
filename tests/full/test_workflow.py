from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "skills/kymcm-full/scripts"))

from checkpoint_full.workflow import (
    StaleReason, Workflow, WorkflowError, WorkflowState, transition,
)
from tests.full.helpers import model_spec, result


class WorkflowTests(unittest.TestCase):
    def start(self):
        spec = model_spec()
        review = transition(Workflow(1), "submit_start", {"spec": spec, "review_document_hash": "a" * 64})
        return spec, review

    def running(self):
        spec, review = self.start()
        return spec, transition(review, "accept_start", {"spec": spec})

    def test_start_requires_review_acceptance(self):
        spec, review = self.start()
        self.assertEqual(review.state, WorkflowState.AWAITING_START_REVIEW)
        self.assertEqual(transition(review, "accept_start", {"spec": spec}).state, WorkflowState.RUNNING)
        with self.assertRaises(WorkflowError):
            transition(Workflow(1), "accept_start", {"spec": spec})

    def test_submit_start_requires_resolved_prestart_audit_atomically(self):
        missing = model_spec(data_semantics={"observation_unit": "one row"})
        unresolved_semantics = model_spec().payload()["data_semantics"]
        unresolved_semantics["prestart_audit"]["unresolved"] = ["resolve duplicate key"]
        unresolved = model_spec(data_semantics=unresolved_semantics)
        flow = Workflow(1)
        before = flow.payload()
        for spec, code in ((missing, "missing_prestart_audit"),
                           (unresolved, "unresolved_data_issue")):
            with self.subTest(code=code), self.assertRaisesRegex(WorkflowError, code):
                transition(flow, "submit_start", {"spec": spec})
            self.assertEqual(flow.payload(), before)

    def test_accept_start_revalidates_prestart_audit(self):
        invalid = model_spec(data_semantics={"observation_unit": "one row"})
        review = Workflow(
            1, state=WorkflowState.AWAITING_START_REVIEW,
            spec_revision=invalid.revision, spec_hash=invalid.hash,
            review_document_hash="a" * 64,
        )
        before = review.payload()
        with self.assertRaisesRegex(WorkflowError, "missing_prestart_audit"):
            transition(review, "accept_start", {"spec": invalid})
        self.assertEqual(review.payload(), before)

    def test_review_document_hash_is_required_and_cleared(self):
        spec = model_spec()
        with self.assertRaises(WorkflowError):
            transition(Workflow(1), "submit_start", {"spec": spec, "review_document_hash": "bad"})
        _, review = self.start()
        self.assertEqual(review.review_document_hash, "a" * 64)
        self.assertIsNone(transition(review, "accept_start", {"spec": spec}).review_document_hash)

    def test_result_review_and_acceptance(self):
        spec, running = self.running()
        record = result(spec)
        review = transition(running, "submit_result", {"spec": spec, "result": record, "review_document_hash": "c" * 64})
        self.assertEqual(review.state, WorkflowState.AWAITING_RESULT_REVIEW)
        self.assertEqual(transition(review, "accept_result", {"spec": spec, "result": record}).state, WorkflowState.COMPLETED)

    def test_result_cannot_be_submitted_before_start_acceptance(self):
        spec, review = self.start()
        with self.assertRaises(WorkflowError):
            transition(review, "submit_result", {"spec": spec, "result": result(spec)})

    def test_runtime_semantic_change_replans_to_exploring(self):
        spec, running = self.running()
        stale = transition(running, "mark_stale", {"reason": "replan_required", "source": "metric meaning changed"})
        self.assertEqual(stale.state, WorkflowState.STALE)
        exploring = transition(stale, "recover")
        self.assertEqual(exploring.state, WorkflowState.EXPLORING)
        revised = model_spec(revision=2, objective="Use the clarified metric.")
        self.assertEqual(transition(exploring, "submit_start", {"spec": revised}).state, WorkflowState.AWAITING_START_REVIEW)

    def test_implementation_repair_preserves_approved_spec(self):
        spec, running = self.running()
        stale = transition(running, "mark_stale", {"reason": "rerun_required", "source": "parser bug"})
        recovered = transition(stale, "recover")
        self.assertEqual(recovered.state, WorkflowState.RUNNING)
        self.assertEqual((recovered.spec_revision, recovered.spec_hash), (spec.revision, spec.hash))

    def test_revised_start_must_change_revision_and_semantics(self):
        spec, running = self.running()
        stale = transition(running, "mark_stale", {"reason": "replan_required", "source": "semantic change"})
        exploring = transition(stale, "recover")
        with self.assertRaises(WorkflowError):
            transition(exploring, "submit_start", {"spec": spec})
        with self.assertRaises(WorkflowError):
            transition(exploring, "submit_start", {"spec": model_spec(revision=2)})

    def test_removed_decision_actions_are_unknown(self):
        for action in ("open_decision", "resolve_decision"):
            with self.subTest(action=action), self.assertRaises(WorkflowError):
                transition(Workflow(1), action)

    def test_invalid_transitions_are_atomic(self):
        flow = Workflow(1)
        before = flow.payload()
        with self.assertRaises(WorkflowError):
            transition(flow, "accept_result", {})
        self.assertEqual(flow.payload(), before)

    def test_constructor_rejects_contradictory_state(self):
        with self.assertRaises(WorkflowError):
            Workflow(1, state=WorkflowState.RUNNING)
        with self.assertRaises(WorkflowError):
            Workflow(1, stale_reason=StaleReason.REPLAN_REQUIRED, stale_source="x")


if __name__ == "__main__":
    unittest.main()
