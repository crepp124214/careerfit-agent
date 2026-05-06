import asyncio
import json

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.agents.graph import LLM_NODES, NODE_LABELS, NODE_SEQUENCE
from app.db.session import get_db
from app.schemas.analysis import AnalysisCreate, AnalysisTaskRead
from app.services.analysis_service import (
    create_analysis,
    get_analysis_task,
    list_agent_runs,
)
from app.api.routes.analysis_cache import analysis_event_cache
from app.services.event_bus import event_bus

router = APIRouter(prefix="/api/analysis", tags=["analysis"])

TOTAL_NODES = len(NODE_SEQUENCE)


def _build_node_index() -> dict[str, int]:
    return {name: idx + 1 for idx, (name, _) in enumerate(NODE_SEQUENCE)}


NODE_INDEX_MAP = _build_node_index()


def _replay_events_from_runs(task_id: int, runs: list):
    # 检查缓存
    cached_events = analysis_event_cache.get(task_id, runs)
    if cached_events is not None:
        return cached_events
    
    events: list[dict] = []
    for r in runs:
        node_name = r.node_name
        node_label = NODE_LABELS.get(node_name, node_name)
        node_index = NODE_INDEX_MAP.get(node_name, 0)
        meta = r.execution_meta or {}
        duration_ms = 0
        if r.started_at and r.finished_at:
            duration_ms = int((r.finished_at - r.started_at).total_seconds() * 1000)
        is_llm = node_name in LLM_NODES

        events.append({
            "type": "node_started",
            "task_id": task_id,
            "node_name": node_name,
            "node_label": node_label,
            "node_index": node_index,
            "total_nodes": TOTAL_NODES,
            "execution_mode": "llm" if is_llm else "deterministic",
        })

        if is_llm:
            events.append({
                "type": "llm_connecting",
                "task_id": task_id,
                "node_name": node_name,
                "node_label": node_label,
                "node_index": node_index,
                "total_nodes": TOTAL_NODES,
            })

            if meta.get("fallback_used"):
                events.append({
                    "type": "llm_failed",
                    "task_id": task_id,
                    "node_name": node_name,
                    "node_label": node_label,
                    "node_index": node_index,
                    "total_nodes": TOTAL_NODES,
                    "model_name": meta.get("model_name"),
                    "error": "LLM 不可用，回退到规则引擎",
                    "fallback_used": True,
                    "connection_duration_ms": duration_ms,
                })
            else:
                events.append({
                    "type": "llm_connected",
                    "task_id": task_id,
                    "node_name": node_name,
                    "node_label": node_label,
                    "node_index": node_index,
                    "total_nodes": TOTAL_NODES,
                    "model_name": meta.get("model_name"),
                    "connection_duration_ms": duration_ms,
                })

        events.append({
            "type": "node_completed",
            "task_id": task_id,
            "node_name": node_name,
            "node_label": node_label,
            "node_index": node_index,
            "total_nodes": TOTAL_NODES,
            "status": r.status,
            "duration_ms": duration_ms,
            "execution_mode": meta.get("execution_mode", "deterministic"),
            "summary": meta.get("summary", ""),
        })

    # 将结果存入缓存
    analysis_event_cache.set(task_id, runs, events)
    
    return events


@router.post("", response_model=AnalysisTaskRead, status_code=status.HTTP_201_CREATED)
def create_analysis_endpoint(payload: AnalysisCreate, db: Session = Depends(get_db)):
    try:
        return create_analysis(db, payload)
    except ValueError as exc:
        if str(exc) == "job_or_resume_not_found":
            raise HTTPException(status_code=404, detail="Job or resume not found") from exc
        raise


@router.get("/{task_id}", response_model=AnalysisTaskRead)
def get_analysis_status_endpoint(task_id: int, db: Session = Depends(get_db)):
    task = get_analysis_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Analysis task not found")
    return task


@router.get("/{task_id}/progress")
def get_analysis_progress(task_id: int, db: Session = Depends(get_db)):
    task = get_analysis_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Analysis task not found")

    runs = list_agent_runs(db, task_id)
    completed_nodes = []
    for r in runs:
        duration_ms = 0
        if r.started_at and r.finished_at:
            duration_ms = int((r.finished_at - r.started_at).total_seconds() * 1000)
        completed_nodes.append({
            "node_name": r.node_name,
            "status": r.status,
            "duration_ms": duration_ms,
            "execution_meta": r.execution_meta or {},
        })

    return {
        "task_id": task_id,
        "status": task.status,
        "completed_nodes": completed_nodes,
        "total_nodes": TOTAL_NODES,
    }


@router.get("/{task_id}/stream")
async def stream_analysis_progress(task_id: int, db: Session = Depends(get_db)):
    task = get_analysis_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Analysis task not found")

    if task.status in ("success", "failed"):
        runs = list_agent_runs(db, task_id)
        replay_events = _replay_events_from_runs(task_id, runs)

        async def completed_generator():
            for event in replay_events:
                event_type = event.get("type", "message")
                event_data = json.dumps(event, ensure_ascii=False)
                yield f"event: {event_type}\ndata: {event_data}\n\n"
                await asyncio.sleep(0.01)

            final_data = json.dumps({
                "type": "workflow_completed",
                "task_id": task_id,
                "final_score": 0,
                "total_duration_ms": 0,
            })
            yield f"event: workflow_completed\ndata: {final_data}\n\n"

        return StreamingResponse(
            completed_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    queue = event_bus.subscribe(task_id)
    existing_runs = list_agent_runs(db, task_id)
    replay_events = _replay_events_from_runs(task_id, existing_runs)

    async def event_generator():
        try:
            for event in replay_events:
                event_type = event.get("type", "message")
                event_data = json.dumps(event, ensure_ascii=False)
                yield f"event: {event_type}\ndata: {event_data}\n\n"

            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=30)
                except asyncio.TimeoutError:
                    yield ": heartbeat\n\n"
                    continue

                if event.get("type") == "stale_cleanup":
                    break

                event_type = event.get("type", "message")
                event_data = json.dumps(event, ensure_ascii=False)
                yield f"event: {event_type}\ndata: {event_data}\n\n"

                if event_type == "workflow_completed":
                    break

        finally:
            event_bus.unsubscribe(task_id, queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
