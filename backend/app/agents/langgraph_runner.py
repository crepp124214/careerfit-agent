from __future__ import annotations

import logging
import os
from collections.abc import Callable
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph

from app.agents import nodes
from app.agents.graph import LLM_NODES, NODE_LABELS, NODE_SEQUENCE, redact_state, _make_event
from app.agents.state import CareerFitState
from app.agents.workflow_mode import WorkflowMode, MODE_CONFIG


logger = logging.getLogger(__name__)


class LangGraphRunner:
    def __init__(
        self,
        *,
        task_id: int = 0,
        mode: WorkflowMode = WorkflowMode.FULL_ANALYSIS,
        on_event: Callable[[dict[str, Any]], None] | None = None,
        on_node_complete: Callable[[dict[str, Any]], None] | None = None,
    ):
        self.task_id = task_id
        self.mode = mode
        self.on_event = on_event
        self.on_node_complete = on_node_complete
        self.trace: list[dict[str, Any]] = []
        self._started_at_map: dict[str, datetime] = {}

        self._graph: StateGraph | None = None
        self._compiled: Any = None

    def _make_wrapped_node(self, node_name: str) -> Callable[[CareerFitState], dict[str, Any]]:
        node_func = dict(NODE_SEQUENCE)[node_name]
        is_llm = node_name in LLM_NODES
        total = len(NODE_SEQUENCE)
        node_index = [n for n, _ in NODE_SEQUENCE].index(node_name) + 1

        def wrapped(state: CareerFitState) -> dict[str, Any]:
            if self.on_event:
                self.on_event(
                    _make_event(
                        "node_started",
                        self.task_id,
                        node_name,
                        node_index=node_index,
                        total_nodes=total,
                        execution_mode="llm" if is_llm else "deterministic",
                    )
                )

            if is_llm and self.on_event:
                self.on_event(
                    _make_event(
                        "llm_connecting",
                        self.task_id,
                        node_name,
                        node_index=node_index,
                        total_nodes=total,
                    )
                )

            started_at = datetime.now(timezone.utc)
            self._started_at_map[node_name] = started_at
            input_snapshot = redact_state(state)
            llm_connection_started_at: datetime | None = datetime.now(timezone.utc) if is_llm else None

            try:
                output = node_func(state)
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

                self._emit_llm_events(node_name, node_index, total, is_llm, execution_meta, llm_connection_started_at)

                duration_ms = int((finished_at - started_at).total_seconds() * 1000)
                trace_item = {
                    "node_name": node_name,
                    "status": "success",
                    "input_snapshot": input_snapshot,
                    "output_snapshot": redact_state(output),
                    "execution_meta": deepcopy(execution_meta),
                    "started_at": started_at,
                    "finished_at": finished_at,
                }

                if self.on_event:
                    self.on_event(
                        _make_event(
                            "node_completed",
                            self.task_id,
                            node_name,
                            node_index=node_index,
                            total_nodes=total,
                            status="success",
                            duration_ms=duration_ms,
                            execution_mode=execution_meta.get("execution_mode", "deterministic"),
                            summary=summary,
                        )
                    )

                if self.on_node_complete:
                    self.on_node_complete(trace_item)

                self.trace.append(trace_item)
                return output

            except Exception as exc:
                finished_at = datetime.now(timezone.utc)
                duration_ms = int((finished_at - started_at).total_seconds() * 1000)

                self._emit_llm_error(node_name, node_index, total, is_llm, exc, llm_connection_started_at)

                if self.on_event:
                    self.on_event(
                        _make_event(
                            "node_failed",
                            self.task_id,
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

                if self.on_node_complete:
                    self.on_node_complete(trace_item)

                self.trace.append(trace_item)
                raise

        return wrapped

    def _emit_llm_events(
        self,
        node_name: str,
        node_index: int,
        total: int,
        is_llm: bool,
        execution_meta: dict,
        llm_connection_started_at: datetime | None,
    ) -> None:
        if not is_llm or not self.on_event:
            return
        model_name = execution_meta.get("model_name")
        fallback_used = execution_meta.get("fallback_used", False)
        connection_duration_ms = None
        if llm_connection_started_at:
            connection_duration_ms = int(
                (datetime.now(timezone.utc) - llm_connection_started_at).total_seconds() * 1000
            )
        if fallback_used:
            error_label = execution_meta.get("llm_error_label", "LLM 不可用")
            self.on_event(
                _make_event(
                    "llm_failed",
                    self.task_id,
                    node_name,
                    node_index=node_index,
                    total_nodes=total,
                    model_name=model_name,
                    error=f"{error_label}，回退到规则引擎",
                    fallback_used=True,
                    connection_duration_ms=connection_duration_ms,
                )
            )
        else:
            self.on_event(
                _make_event(
                    "llm_connected",
                    self.task_id,
                    node_name,
                    node_index=node_index,
                    total_nodes=total,
                    model_name=model_name,
                    connection_duration_ms=connection_duration_ms,
                )
            )

    def _emit_llm_error(
        self,
        node_name: str,
        node_index: int,
        total: int,
        is_llm: bool,
        exc: Exception,
        llm_connection_started_at: datetime | None,
    ) -> None:
        if not is_llm or not self.on_event:
            return
        connection_duration_ms = None
        if llm_connection_started_at:
            connection_duration_ms = int(
                (datetime.now(timezone.utc) - llm_connection_started_at).total_seconds() * 1000
            )
        self.on_event(
            _make_event(
                "llm_failed",
                self.task_id,
                node_name,
                node_index=node_index,
                total_nodes=total,
                error=str(exc),
                fallback_used=False,
                connection_duration_ms=connection_duration_ms,
            )
        )

    def _gap_router(self, state: CareerFitState) -> list[str]:
        gaps = state.get("gaps", [])
        if gaps:
            return ["resume_optimizer", "interview_coach", "learning_planner"]
        return ["next_best_action"]

    def _parse_router(self, state: CareerFitState) -> list[str]:
        return ["jd_parser", "resume_parser"]

    def build_graph(self) -> Any:
        builder = StateGraph(CareerFitState)

        if self.mode == WorkflowMode.FULL_ANALYSIS:
            self._build_full_analysis_graph(builder)
        elif self.mode == WorkflowMode.LITE_ANALYSIS:
            self._build_lite_analysis_graph(builder)
        elif self.mode == WorkflowMode.INTERVIEW_ONLY:
            self._build_interview_only_graph(builder)
        elif self.mode == WorkflowMode.INTERVIEW_WITH_PREP:
            self._build_interview_with_prep_graph(builder)
        elif self.mode == WorkflowMode.PREP_ONLY:
            self._build_prep_only_graph(builder)
        else:
            logger.warning(f"[LangGraphRunner] Unknown mode: {self.mode}, falling back to FULL_ANALYSIS")
            self._build_full_analysis_graph(builder)

        checkpointer = MemorySaver()
        self._compiled = builder.compile(checkpointer=checkpointer)
        return self._compiled

    def _build_full_analysis_graph(self, builder: StateGraph) -> None:
        node_names = [n for n, _ in NODE_SEQUENCE]
        for node_name in node_names:
            builder.add_node(node_name, self._make_wrapped_node(node_name))

        builder.set_entry_point("start_parse")

        def start_parse(state: CareerFitState) -> dict:
            return {}

        builder.add_node("start_parse", start_parse)
        builder.add_conditional_edges(
            "start_parse",
            self._parse_router,
        )

        builder.add_edge("jd_parser", "rag_query_planner")
        builder.add_edge("resume_parser", "rag_query_planner")
        builder.add_edge("rag_query_planner", "rag_retriever")
        builder.add_edge("rag_retriever", "match_scorer")
        builder.add_edge("match_scorer", "gap_analyzer")

        builder.add_conditional_edges(
            "gap_analyzer",
            self._gap_router,
        )

        builder.add_edge("resume_optimizer", "next_best_action")
        builder.add_edge("interview_coach", "next_best_action")
        builder.add_edge("learning_planner", "next_best_action")

        builder.set_finish_point("next_best_action")

    def _build_lite_analysis_graph(self, builder: StateGraph) -> None:
        nodes = MODE_CONFIG[WorkflowMode.LITE_ANALYSIS]["nodes"]

        for node_name in nodes:
            if node_name == "start_parse":
                def start_parse(state: CareerFitState) -> dict:
                    return {}
                builder.add_node(node_name, start_parse)
            else:
                builder.add_node(node_name, self._make_wrapped_node(node_name))

        builder.set_entry_point("start_parse")
        builder.add_conditional_edges("start_parse", self._parse_router)
        builder.add_edge("jd_parser", "rag_query_planner")
        builder.add_edge("resume_parser", "rag_query_planner")
        builder.add_edge("rag_query_planner", "rag_retriever")
        builder.add_edge("rag_retriever", "match_scorer")
        builder.add_edge("match_scorer", "gap_analyzer")
        builder.add_edge("gap_analyzer", "next_best_action")
        builder.set_finish_point("next_best_action")

    def _build_interview_only_graph(self, builder: StateGraph) -> None:
        builder.add_node("interview_coach", self._make_wrapped_node("interview_coach"))
        builder.set_entry_point("interview_coach")
        builder.set_finish_point("interview_coach")

    def _build_interview_with_prep_graph(self, builder: StateGraph) -> None:
        builder.add_node("interview_coach", self._make_wrapped_node("interview_coach"))
        builder.add_node("learning_planner", self._make_wrapped_node("learning_planner"))
        builder.set_entry_point("interview_coach")
        builder.add_edge("interview_coach", "learning_planner")
        builder.set_finish_point("learning_planner")

    def _build_prep_only_graph(self, builder: StateGraph) -> None:
        builder.add_node("learning_planner", self._make_wrapped_node("learning_planner"))
        builder.set_entry_point("learning_planner")
        builder.set_finish_point("learning_planner")

    def _emit_workflow_completed(self, state: CareerFitState, total_duration_ms: int) -> None:
        if not self.on_event:
            return
        match_result = state.get("match_result", {})
        score_items = match_result.get("score_items", [])
        high_risk = [s for s in score_items if s.get("score", 0) < 50]

        self.on_event(
            _make_event(
                "workflow_completed",
                self.task_id,
                "workflow",
                final_score=match_result.get("final_score", 0),
                total_duration_ms=total_duration_ms,
                high_risk_count=len(high_risk),
                watch_count=0,
            )
        )

    def run(self, initial_state: CareerFitState) -> tuple[CareerFitState, list[dict]]:
        workflow_started_at = datetime.now(timezone.utc)

        if self._compiled is None:
            self.build_graph()

        config = {"configurable": {"thread_id": str(self.task_id or "default")}}

        result_state = self._compiled.invoke(initial_state, config)

        total_duration_ms = int(
            (datetime.now(timezone.utc) - workflow_started_at).total_seconds() * 1000
        )
        self._emit_workflow_completed(result_state, total_duration_ms)

        return result_state, self.trace


def run_workflow_langgraph(
    initial_state: CareerFitState,
    *,
    task_id: int = 0,
    mode: str = "full_analysis",
    on_event: Callable[[dict[str, Any]], None] | None = None,
    on_node_complete: Callable[[dict[str, Any]], None] | None = None,
) -> tuple[CareerFitState, list[dict]]:
    workflow_mode = WorkflowMode(mode)
    runner = LangGraphRunner(
        task_id=task_id,
        mode=workflow_mode,
        on_event=on_event,
        on_node_complete=on_node_complete,
    )
    return runner.run(initial_state)
