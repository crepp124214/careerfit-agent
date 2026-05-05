from collections.abc import Callable
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

from app.agents import nodes
from app.agents.state import CareerFitState

Node = Callable[[CareerFitState], CareerFitState]

NODE_SEQUENCE: list[tuple[str, Node]] = [
    ("jd_parser", nodes.jd_parser),
    ("resume_parser", nodes.resume_parser),
    ("rag_retriever", nodes.rag_retriever),
    ("match_scorer", nodes.match_scorer),
    ("gap_analyzer", nodes.gap_analyzer),
    ("resume_optimizer", nodes.resume_optimizer),
    ("interview_coach", nodes.interview_coach),
    ("learning_planner", nodes.learning_planner),
    ("next_best_action", nodes.next_best_action),
]

NODE_LABELS: dict[str, str] = {
    "jd_parser": "JD 解析",
    "resume_parser": "简历解析",
    "rag_retriever": "知识库检索",
    "match_scorer": "匹配评分",
    "gap_analyzer": "缺口分析",
    "resume_optimizer": "简历优化",
    "interview_coach": "面试题生成",
    "learning_planner": "学习计划",
    "next_best_action": "下一步行动",
}

LLM_NODES = {"resume_optimizer", "interview_coach", "learning_planner", "next_best_action"}

REDACTED_EVIDENCE_KEYS = {
    "evidence",
    "jd_evidence",
    "resume_evidence",
    "knowledge_evidence",
    "projects",
    "messages",
    "prompt",
    "api_key",
    "rag_results",
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


def _make_event(
    event_type: str,
    task_id: int,
    node_name: str,
    **kwargs: Any,
) -> dict[str, Any]:
    event: dict[str, Any] = {
        "type": event_type,
        "task_id": task_id,
        "node_name": node_name,
        "node_label": NODE_LABELS.get(node_name, node_name),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    event.update(kwargs)
    return event


def run_workflow(
    initial_state: CareerFitState,
    *,
    task_id: int = 0,
    on_event: Callable[[dict[str, Any]], None] | None = None,
    on_node_complete: Callable[[dict[str, Any]], None] | None = None,
) -> tuple[CareerFitState, list[dict]]:
    state = dict(initial_state)
    trace = []
    total = len(NODE_SEQUENCE)
    workflow_started_at = datetime.now(timezone.utc)

    for idx, (node_name, node) in enumerate(NODE_SEQUENCE):
        node_index = idx + 1
        is_llm = node_name in LLM_NODES

        if on_event:
            on_event(
                _make_event(
                    "node_started",
                    task_id,
                    node_name,
                    node_index=node_index,
                    total_nodes=total,
                    execution_mode="llm" if is_llm else "deterministic",
                )
            )

        if is_llm and on_event:
            on_event(
                _make_event(
                    "llm_connecting",
                    task_id,
                    node_name,
                    node_index=node_index,
                    total_nodes=total,
                )
            )

        started_at = datetime.now(timezone.utc)
        input_snapshot = redact_state(state)
        llm_connected = False
        llm_error: str | None = None
        llm_connection_started_at: datetime | None = None

        if is_llm:
            llm_connection_started_at = datetime.now(timezone.utc)

        try:
            output = node(state)
            state.update(output)
            finished_at = datetime.now(timezone.utc)

            execution_meta = output.pop("_execution_meta", {
                "agent_role": node_name,
                "execution_mode": "llm" if is_llm else "deterministic",
                "model_name": None,
                "fallback_used": False,
                "schema_valid": True,
                "retry_count": 0,
            })
            summary = output.pop("_summary", "")
            execution_meta["summary"] = summary

            if is_llm and on_event:
                model_name = execution_meta.get("model_name")
                fallback_used = execution_meta.get("fallback_used", False)
                connection_duration_ms = None
                if llm_connection_started_at:
                    connection_duration_ms = int(
                        (datetime.now(timezone.utc) - llm_connection_started_at).total_seconds() * 1000
                    )
                if fallback_used:
                    on_event(
                        _make_event(
                            "llm_failed",
                            task_id,
                            node_name,
                            node_index=node_index,
                            total_nodes=total,
                            model_name=model_name,
                            error=llm_error or "LLM 不可用，回退到规则引擎",
                            fallback_used=True,
                            connection_duration_ms=connection_duration_ms,
                        )
                    )
                else:
                    on_event(
                        _make_event(
                            "llm_connected",
                            task_id,
                            node_name,
                            node_index=node_index,
                            total_nodes=total,
                            model_name=model_name,
                            connection_duration_ms=connection_duration_ms,
                        )
                    )

            duration_ms = int((finished_at - started_at).total_seconds() * 1000)
            trace_item = {
                "node_name": node_name,
                "status": "success",
                "input_snapshot": input_snapshot,
                "output_snapshot": redact_state(output),
                "execution_meta": execution_meta,
                "started_at": started_at,
                "finished_at": finished_at,
            }

            if on_event:
                on_event(
                    _make_event(
                        "node_completed",
                        task_id,
                        node_name,
                        node_index=node_index,
                        total_nodes=total,
                        status="success",
                        duration_ms=duration_ms,
                        execution_mode=execution_meta.get("execution_mode", "deterministic"),
                        summary=summary,
                    )
                )

            if on_node_complete:
                on_node_complete(trace_item)

            trace.append(trace_item)

        except Exception as exc:
            finished_at = datetime.now(timezone.utc)
            duration_ms = int((finished_at - started_at).total_seconds() * 1000)

            if is_llm and on_event:
                connection_duration_ms = None
                if llm_connection_started_at:
                    connection_duration_ms = int(
                        (datetime.now(timezone.utc) - llm_connection_started_at).total_seconds() * 1000
                    )
                on_event(
                    _make_event(
                        "llm_failed",
                        task_id,
                        node_name,
                        node_index=node_index,
                        total_nodes=total,
                        error=str(exc),
                        fallback_used=False,
                        connection_duration_ms=connection_duration_ms,
                    )
                )

            if on_event:
                on_event(
                    _make_event(
                        "node_failed",
                        task_id,
                        node_name,
                        node_index=node_index,
                        total_nodes=total,
                        error=str(exc),
                        duration_ms=duration_ms,
                    )
                )

            trace_item = {
                "node_name": node_name,
                "status": "failed",
                "input_snapshot": input_snapshot,
                "output_snapshot": {},
                "execution_meta": {
                    "agent_role": node_name,
                    "execution_mode": "llm" if is_llm else "deterministic",
                    "model_name": None,
                    "fallback_used": False,
                    "schema_valid": False,
                    "retry_count": 0,
                    "error": str(exc),
                },
                "started_at": started_at,
                "finished_at": finished_at,
            }

            if on_node_complete:
                on_node_complete(trace_item)

            trace.append(trace_item)
            raise

    total_duration_ms = int(
        (datetime.now(timezone.utc) - workflow_started_at).total_seconds() * 1000
    )
    match_result = state.get("match_result", {})
    score_items = match_result.get("score_items", [])
    high_risk = [s for s in score_items if s.get("score", 0) < 50]

    if on_event:
        on_event(
            _make_event(
                "workflow_completed",
                task_id,
                "workflow",
                final_score=match_result.get("final_score", 0),
                total_duration_ms=total_duration_ms,
                high_risk_count=len(high_risk),
                watch_count=0,
            )
        )

    return state, trace
