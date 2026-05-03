from collections.abc import Callable
from copy import deepcopy
from datetime import datetime, timezone

from app.agents import nodes
from app.agents.state import CareerFitState

Node = Callable[[CareerFitState], CareerFitState]

NODE_SEQUENCE: list[tuple[str, Node]] = [
    ("jd_parser", nodes.jd_parser),
    ("resume_parser", nodes.resume_parser),
    ("match_scorer", nodes.match_scorer),
    ("gap_analyzer", nodes.gap_analyzer),
    ("resume_optimizer", nodes.resume_optimizer),
    ("interview_coach", nodes.interview_coach),
    ("learning_planner", nodes.learning_planner),
    ("next_best_action", nodes.next_best_action),
]


def redact_state(state: CareerFitState) -> dict:
    snapshot = deepcopy(dict(state))
    if "raw_jd" in snapshot:
        snapshot["raw_jd"] = "[redacted]"
    if "raw_resume" in snapshot:
        snapshot["raw_resume"] = "[redacted]"
    return snapshot


def run_workflow(initial_state: CareerFitState) -> tuple[CareerFitState, list[dict]]:
    state = dict(initial_state)
    trace = []
    for node_name, node in NODE_SEQUENCE:
        started_at = datetime.now(timezone.utc)
        input_snapshot = redact_state(state)
        output = node(state)
        state.update(output)
        finished_at = datetime.now(timezone.utc)
        trace.append(
            {
                "node_name": node_name,
                "status": "success",
                "input_snapshot": input_snapshot,
                "output_snapshot": redact_state(output),
                "started_at": started_at,
                "finished_at": finished_at,
            }
        )
    return state, trace
