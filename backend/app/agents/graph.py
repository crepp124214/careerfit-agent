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

REDACTED_EVIDENCE_KEYS = {
    "evidence",
    "jd_evidence",
    "resume_evidence",
    "projects",
    "messages",
    "prompt",
    "api_key",
}


def _redact_nested(value):
    if isinstance(value, dict):
        redacted = {}
        for key, nested in value.items():
            if key in {"raw_jd", "raw_resume"}:
                redacted[key] = "[redacted]"
            elif key in REDACTED_EVIDENCE_KEYS:
                redacted[key] = "[redacted evidence]"
            else:
                redacted[key] = _redact_nested(nested)
        return redacted
    if isinstance(value, list):
        return [_redact_nested(item) for item in value]
    return value


def redact_state(state: CareerFitState) -> dict:
    return _redact_nested(deepcopy(dict(state)))


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
