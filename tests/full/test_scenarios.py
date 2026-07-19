from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "skills/kymcm-full/scripts"))

from checkpoint_full.render import render_result_brief, render_start_brief
from checkpoint_full.workflow import Workflow, WorkflowError, WorkflowState
from checkpoint_full.workflow import transition
from tests.full.helpers import model_spec, result


class ScenarioTests(unittest.TestCase):
    def complete_ordinary_problem(self, method, definition, output_name):
        spec = model_spec(
            model={"method": method, "formal_definition": definition},
            required_outputs=({"name": output_name, "definition": "primary answer", "unit": "index"},),
        )
        record = result(spec)
        flow = Workflow(spec.problem)
        blocking_views = []
        flow = transition(flow, "submit_start", {"spec": spec})
        blocking_views.append(render_start_brief(spec, "采用该方案"))
        flow = transition(flow, "accept_start", {"spec": spec})
        flow = transition(flow, "submit_result", {"spec": spec, "result": record})
        blocking_views.append(render_result_brief(record))
        flow = transition(flow, "accept_result", {"spec": spec, "result": record})
        return flow, blocking_views

    def test_unambiguous_problem_can_complete_without_consultation(self):
        fixtures = (
            ("统计评价", "S=sum(w_i*x_i)", "ranking"),
            ("约束优化", "min c(x), subject to g(x)<=0", "solution"),
            ("预测微分方程", "dy/dt=f(t,y)", "forecast"),
        )
        for fixture in fixtures:
            with self.subTest(family=fixture[0]):
                flow, blocking_views = self.complete_ordinary_problem(*fixture)
                self.assertEqual(flow.state, WorkflowState.COMPLETED)
                self.assertEqual(len(blocking_views), 2)

    def test_bug_reruns_without_start_but_math_change_requires_start(self):
        flow = Workflow(1)
        original = model_spec()
        flow = transition(flow, "submit_start", {"spec": original})
        flow = transition(flow, "accept_start", {"spec": original})
        bug = transition(flow, "mark_stale", {"reason": "rerun_required", "source": "implementation bug"})
        rerun = transition(bug, "recover")
        self.assertEqual(rerun.state, WorkflowState.RUNNING)
        self.assertEqual(rerun.spec_hash, original.hash)

        semantic = transition(flow, "mark_stale", {"reason": "replan_required", "source": "metric definition"})
        revised = model_spec(revision=2, objective="Minimize expected loss.")
        replanning = transition(semantic, "recover")
        self.assertEqual(replanning.state, WorkflowState.EXPLORING)
        self.assertEqual(replanning.spec_hash, original.hash)
        before = replanning.payload()
        for rejected in (original, model_spec(revision=2)):
            with self.assertRaises(WorkflowError):
                transition(replanning, "submit_start", {"spec": rejected})
            self.assertEqual(replanning.payload(), before)
        review = transition(replanning, "submit_start", {"spec": revised})
        self.assertEqual(review.state, WorkflowState.AWAITING_START_REVIEW)
        self.assertNotEqual(review.spec_hash, original.hash)

    def test_bug_can_rerun_from_each_authorized_nonblocking_phase(self):
        spec = model_spec()
        start = transition(Workflow(1), "submit_start", {"spec": spec})
        running = transition(start, "accept_start", {"spec": spec})
        review = transition(running, "submit_result", {"spec": spec, "result": result(spec)})
        completed = transition(review, "accept_result", {"spec": spec, "result": result(spec)})
        for source in (running, review, completed):
            stale = transition(source, "mark_stale", {"reason": "rerun_required", "source": "bug"})
            recovered = transition(stale, "recover")
            with self.subTest(source=source.state):
                self.assertEqual(recovered.state, WorkflowState.RUNNING)
                self.assertEqual(recovered.spec_hash, spec.hash)
                self.assertIsNone(recovered.review_result_hash)
