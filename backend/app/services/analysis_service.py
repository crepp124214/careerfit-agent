import logging
import os
import threading
import time
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.agents.graph import run_workflow
from app.db.models import AgentRun, AnalysisReport, AnalysisStatus, AnalysisTask
from app.rag.retrieval import retrieve_by_skills_batch, retrieve_by_skill
from app.schemas.analysis import AnalysisCreate
from app.services.event_bus import event_bus
from app.services.job_service import get_job, parse_job_profile
from app.services.resume_service import get_resume

logger = logging.getLogger(__name__)


def _build_rag_results(db: Session, required_skills: list[str]) -> dict:
    """构建 RAG 检索结果，使用批量查询优化性能"""
    # 使用批量检索避免 N+1 查询问题
    batch_results = retrieve_by_skills_batch(db, required_skills, top_k=3)
    
    rag_results = {}
    for skill, documents in batch_results.items():
        if documents:
            rag_results[skill] = {
                "documents": documents,
                "available": True,
            }
        else:
            rag_results[skill] = {
                "documents": [],
                "available": False,
                "reason": "知识库证据不足",
            }
    return rag_results


def _execute_analysis_core(
    task_id: int,
    jd_raw_text: str,
    resume_raw_text: str,
    rag_results: dict,
    db: Session,
    *,
    on_event=None,
) -> None:
    start_time = time.time()
    try:
        logger.info(f"[Task {task_id}] 开始执行分析核心逻辑")
        jd_profile = parse_job_profile(jd_raw_text)

        initial_state = {
            "raw_jd": jd_raw_text,
            "raw_resume": resume_raw_text,
            "jd_profile": jd_profile,
            "rag_results": rag_results,
        }

        def on_node_complete(trace_item: dict) -> None:
            try:
                db.add(AgentRun(task_id=task_id, **trace_item))
                db.commit()
            except Exception:
                db.rollback()

        logger.debug(f"[Task {task_id}] 启动工作流")
        workflow_start = time.time()
        final_state, trace = run_workflow(
            initial_state,
            task_id=task_id,
            on_event=on_event,
            on_node_complete=on_node_complete,
        )
        workflow_duration = time.time() - workflow_start
        logger.info(f"[Task {task_id}] 工作流完成，耗时: {workflow_duration:.2f}s")

        match_result = final_state["match_result"]
        report = AnalysisReport(
            task_id=task_id,
            final_score=match_result["final_score"],
            score_breakdown=match_result["score_breakdown"],
            strengths=final_state.get("strengths", []),
            gaps=final_state.get("gaps", []),
            resume_suggestions=final_state.get("resume_suggestions", []),
            interview_questions=final_state.get("interview_questions", []),
            learning_plan=final_state.get("learning_plan", []),
            next_best_action=final_state.get("next_best_action", {}),
            evidence=match_result["score_items"],
            scoring_version=match_result["scoring_version"],
        )
        db.add(report)

        task = db.query(AnalysisTask).filter(AnalysisTask.id == task_id).one_or_none()
        if task:
            task.status = AnalysisStatus.success
            task.updated_at = datetime.now(timezone.utc)
        db.commit()
        
        total_duration = time.time() - start_time
        logger.info(f"[Task {task_id}] 分析完成，总耗时: {total_duration:.2f}s")

    except Exception as exc:
        total_duration = time.time() - start_time
        logger.error(f"[Task {task_id}] 分析失败，耗时: {total_duration:.2f}s，错误: {exc}")
        try:
            task = db.query(AnalysisTask).filter(AnalysisTask.id == task_id).one_or_none()
            if task:
                task.status = AnalysisStatus.failed
                task.error_message = str(exc)
                task.updated_at = datetime.now(timezone.utc)
                db.commit()
        except Exception:
            db.rollback()
        raise


def _run_analysis_sync(
    task_id: int,
    jd_raw_text: str,
    *,
    resume_raw_text: str,
    rag_results: dict,
    db: Session,
) -> None:
    _execute_analysis_core(
        task_id=task_id,
        jd_raw_text=jd_raw_text,
        resume_raw_text=resume_raw_text,
        rag_results=rag_results,
        db=db,
        on_event=None,
    )


def _run_analysis_background(
    task_id: int,
    job_id: int,
    resume_id: int,
    jd_raw_text: str,
    resume_raw_text: str,
    rag_results: dict,
) -> None:
    from app.db.session import SessionLocal

    time.sleep(0.5)

    # 使用上下文管理器确保数据库会话正确关闭
    db = SessionLocal()
    try:
        logger.info(f"[Task {task_id}] 开始后台分析任务")
        
        def on_event(event: dict) -> None:
            event_bus.publish(task_id, event)

        _execute_analysis_core(
            task_id=task_id,
            jd_raw_text=jd_raw_text,
            resume_raw_text=resume_raw_text,
            rag_results=rag_results,
            db=db,
            on_event=on_event,
        )
        logger.info(f"[Task {task_id}] 后台分析任务完成")
    except Exception as exc:
        logger.error(f"[Task {task_id}] 后台分析任务失败: {exc}", exc_info=True)
    finally:
        db.close()
        logger.debug(f"[Task {task_id}] 数据库会话已关闭")


def create_analysis(db: Session, payload: AnalysisCreate) -> AnalysisTask:
    job = get_job(db, payload.job_id)
    resume = get_resume(db, payload.resume_id)
    if job is None or resume is None:
        raise ValueError("job_or_resume_not_found")

    task = AnalysisTask(job_id=job.id, resume_id=resume.id, status=AnalysisStatus.running)
    db.add(task)
    db.commit()
    db.refresh(task)

    jd_profile = parse_job_profile(job.raw_text)
    required_skills = jd_profile.get("required_skills") or []
    rag_results = _build_rag_results(db, required_skills)

    sync_mode = os.environ.get("CAREERFIT_ANALYSIS_SYNC") == "1"

    if sync_mode:
        _run_analysis_sync(task.id, job.raw_text, resume_raw_text=resume.raw_text, rag_results=rag_results, db=db)
    else:
        thread = threading.Thread(
            target=_run_analysis_background,
            args=(task.id, job.id, resume.id, job.raw_text, resume.raw_text, rag_results),
            daemon=True,
        )
        thread.start()

    return task


def get_report_by_task(db: Session, task_id: int) -> AnalysisReport | None:
    return db.query(AnalysisReport).filter(AnalysisReport.task_id == task_id).one_or_none()


def get_analysis_task(db: Session, task_id: int) -> AnalysisTask | None:
    return db.query(AnalysisTask).filter(AnalysisTask.id == task_id).one_or_none()


def list_agent_runs(db: Session, task_id: int) -> list[AgentRun]:
    return list(db.query(AgentRun).filter(AgentRun.task_id == task_id).order_by(AgentRun.id).all())
