"""Analysis Service - 分析任务服务

包含分析任务创建、执行（同步/异步）、事件发布等功能。
"""
from __future__ import annotations

import logging
import os
import threading
import time
from datetime import datetime, timezone
from typing import Callable

from sqlalchemy.orm import Session

from app.agents.graph import run_workflow
from app.core.constants import AnalysisConfig, RAGConfig
from app.core.security import redact_sensitive_data, sanitize_for_log
from app.core.thread_pool import analysis_thread_pool
from app.db.models import AgentRun, AnalysisReport, AnalysisStatus, AnalysisTask
from app.rag.retrieval import retrieve_by_skills_batch, retrieve_by_skill
from app.schemas.analysis import AnalysisCreate
from app.services.analysis_cache_service import analysis_cache
from app.services.event_bus import event_bus
from app.services.job_service import get_job, parse_job_profile
from app.services.resume_service import get_resume

logger = logging.getLogger(__name__)


def _build_rag_results(db: Session, required_skills: list[str]) -> dict:
    """构建 RAG 检索结果，使用批量查询优化性能"""
    import time
    start_time = time.time()

    # 使用批量检索避免 N+1 查询问题
    try:
        batch_results = retrieve_by_skills_batch(
            db, required_skills, top_k=RAGConfig.DEFAULT_TOP_K
        )
    except Exception as exc:
        logger.warning(f"RAG 批量检索失败，使用降级方案: {exc}")
        # 降级：返回空结果，不阻塞主流程
        return {skill: {"documents": [], "available": False, "reason": "RAG检索失败"} for skill in required_skills}

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

    elapsed = time.time() - start_time
    logger.debug(f"RAG 检索完成，耗时: {elapsed:.2f}s，技能数: {len(required_skills)}")
    return rag_results


def _update_task_status(db: Session, task_id: int, status: str, error: str | None = None) -> None:
    """更新任务状态
    
    Args:
        db: 数据库会话
        task_id: 任务ID
        status: 新状态
        error: 错误信息（可选）
    """
    try:
        task = db.query(AnalysisTask).filter(AnalysisTask.id == task_id).first()
        if task:
            task.status = status
            if error:
                task.error_message = error
            task.updated_at = datetime.now(timezone.utc)
            db.commit()
    except Exception as exc:
        logger.error(f"[Task {task_id}] 更新任务状态失败: {exc}", exc_info=True)
        db.rollback()


def _safe_publish_event(task_id: int, event: dict) -> None:
    """安全发布事件，兼容多线程环境
    
    在后台线程中，event_bus.publish 可能因为 asyncio 环境不同而失败。
    这里捕获异常并记录日志，确保分析流程不会因事件发布失败而中断。
    """
    try:
        event_bus.publish(task_id, event)
    except Exception as exc:
        # 在后台线程中，asyncio 事件循环可能不存在或不同
        # 此时事件发布失败不应影响分析流程
        logger.debug(f"[Task {task_id}] 事件发布失败（可忽略）: {exc}")


def _execute_analysis_core(
    task_id: int,
    jd_raw_text: str,
    resume_raw_text: str,
    rag_results: dict,
    db: Session,
    on_event: Callable[[dict], None] | None = None,
    mode: str = "full_analysis",
) -> None:
    """执行分析核心逻辑（同步）"""
    logger.info(f"[Task {task_id}] 开始执行分析核心逻辑 (mode={mode})")
    
    # 解析JD
    jd_profile = parse_job_profile(jd_raw_text)
    required_skills = jd_profile.get("required_skills") or []

    # 构建初始状态
    initial_state = {
        "raw_jd": jd_raw_text,
        "raw_resume": resume_raw_text,
        "rag_results": rag_results,
        "required_skills": required_skills,
        "jd_profile": jd_profile,
        "task_id": task_id,
    }

    logger.info(f"[Task {task_id}] 初始状态构建完成，所需技能: {len(required_skills)} 个")
    
    # 运行工作流
    workflow_started_at = datetime.now(timezone.utc)
    state, trace = run_workflow(initial_state, task_id=task_id, mode=mode, on_event=on_event)
    workflow_duration = (datetime.now(timezone.utc) - workflow_started_at).total_seconds()

    # 创建分析报告
    total_duration = (datetime.now(timezone.utc) - workflow_started_at).total_seconds()
    logger.info(f"[Task {task_id}] 工作流完成，耗时: {workflow_duration:.2f}s")

    # 保存 Agent 运行记录
    for entry in trace:
        agent_run = AgentRun(
            task_id=task_id,
            node_name=entry["node_name"],
            status=entry.get("status", "success"),
            input_snapshot=entry.get("input_snapshot"),
            output_snapshot=entry.get("output_snapshot"),
            execution_meta=entry.get("execution_meta"),
            started_at=entry.get("started_at"),
            finished_at=entry.get("finished_at"),
        )
        db.add(agent_run)
    db.flush()

    # 写入报告
    match_result = state.get("match_result", {})
    score_items = match_result.get("score_items", [])
    evidence = [
        {
            "skill": item.get("skill", item.get("skill_key")),
            "score": item.get("score", 0),
            "level": item.get("level"),
            "jd_evidence": item.get("jd_evidence", []),
            "resume_evidence": item.get("resume_evidence", []),
            "knowledge_evidence": item.get("knowledge_evidence", []),
        }
        for item in score_items
    ]
    report = AnalysisReport(
        task_id=task_id,
        final_score=match_result.get("final_score", 0),
        score_breakdown=match_result.get("score_breakdown", {}),
        strengths=state.get("strengths", []),
        gaps=state.get("gaps", []),
        resume_suggestions=state.get("resume_suggestions", []),
        interview_questions=state.get("interview_questions", []),
        learning_plan=state.get("learning_plan", []),
        next_best_action=state.get("next_best_action", {}),
        evidence=evidence,
        scoring_version=match_result.get("scoring_version", "v1"),
    )
    db.add(report)
    db.flush()
    logger.info(f"[Task {task_id}] 分析报告已保存")

    # 更新任务状态
    _update_task_status(db, task_id, AnalysisStatus.success)
    
    # 发布工作流完成事件
    if on_event:
        on_event({
            "type": "workflow_completed",
            "task_id": task_id,
            "final_score": match_result.get("final_score", 0),
            "total_duration_ms": int(total_duration * 1000),
        })
    
    total_duration = (datetime.now(timezone.utc) - workflow_started_at).total_seconds()
    logger.info(f"[Task {task_id}] 分析完成，总耗时: {total_duration:.2f}s")


def _run_analysis_sync(
    task_id: int,
    jd_raw_text: str,
    resume_raw_text: str,
    rag_results: dict,
    db: Session,
    mode: str = "full_analysis",
) -> None:
    """同步执行分析（测试环境使用）"""
    try:
        _execute_analysis_core(
            task_id=task_id,
            jd_raw_text=jd_raw_text,
            resume_raw_text=resume_raw_text,
            rag_results=rag_results,
            db=db,
            on_event=None,
            mode=mode,
        )
    except Exception as exc:
        logger.error(f"[Task {task_id}] 同步分析失败: {exc}", exc_info=True)
        db.rollback()
        _update_task_status(db, task_id, AnalysisStatus.failed, str(exc))
        raise


def _cache_analysis_result(db: Session, task_id: int, job_id: int, resume_id: int) -> None:
    try:
        report = db.query(AnalysisReport).filter(AnalysisReport.task_id == task_id).first()
        if report is None:
            return
        agent_runs = db.query(AgentRun).filter(AgentRun.task_id == task_id).all()
        cache_data = {
            "report": {
                "final_score": report.final_score,
                "score_breakdown": report.score_breakdown,
                "strengths": report.strengths,
                "gaps": report.gaps,
                "resume_suggestions": report.resume_suggestions,
                "interview_questions": report.interview_questions,
                "learning_plan": report.learning_plan,
                "next_best_action": report.next_best_action,
                "evidence": report.evidence,
                "scoring_version": report.scoring_version,
            },
            "agent_runs": [
                {
                    "node_name": r.node_name,
                    "status": r.status,
                    "input_snapshot": r.input_snapshot,
                    "output_snapshot": r.output_snapshot,
                    "execution_meta": r.execution_meta,
                }
                for r in agent_runs
            ],
        }
        analysis_cache.set(job_id, resume_id, cache_data)
        logger.info(f"[Cache] 分析结果已缓存: job_id={job_id}, resume_id={resume_id}")
    except Exception as exc:
        logger.warning(f"[Cache] 缓存分析结果失败: {exc}")


def _run_analysis_background(
    task_id: int,
    job_id: int,
    resume_id: int,
    jd_raw_text: str,
    resume_raw_text: str,
    rag_results: dict,
) -> None:
    """后台异步执行分析（生产环境使用）

    注意：RAG 检索在此方法中执行，可能耗时较长但不会阻塞主线程。
    """
    import time as _time
    
    total_start_time = _time.time()
    
    from app.db.session import SessionLocal

    logger.info(f"[Task {task_id}] ========== 后台分析任务开始 ==========")
    
    # 使用上下文管理器确保数据库会话正确关闭
    db = SessionLocal()
    try:
        step1_time = _time.time()
        logger.info(f"[Task {task_id}] [Step 1/5] 数据库会话创建完成 ({(step1_time-total_start_time):.2f}s)")
        
        # 更新任务为 running 状态
        _update_task_status(db, task_id, AnalysisStatus.running)
        
        step2_time = _time.time()
        logger.info(f"[Task {task_id}] [Step 2/5] 任务状态更新完成 ({(step2_time-step1_time):.2f}s)")
        
        # 在后台线程中执行耗时的 RAG 检索（不影响主线程响应）
        if not rag_results:
            logger.info(f"[Task {task_id}] [Step 3/5] 开始后台 RAG 检索...")
            try:
                step3a_time = _time.time()
                
                jd_profile = parse_job_profile(jd_raw_text)
                required_skills = jd_profile.get("required_skills") or []
                logger.info(f"[Task {task_id}]   [3a] JD 解析完成，所需技能: {len(required_skills)} 个 ({(_time.time()-step3a_time):.2f}s)")
                
                step3b_time = _time.time()
                rag_results = _build_rag_results(db, required_skills)
                available_count = sum(1 for r in rag_results.values() if r.get('available'))
                logger.info(f"[Task {task_id}]   [3b] RAG 检索完成，有效结果: {available_count}/{len(rag_results)} 个 ({(_time.time()-step3b_time):.2f}s)")
                
            except Exception as exc:
                logger.error(f"[Task {task_id}] [Step 3/5] RAG 检索失败: {exc}", exc_info=True)
                rag_results = {}
            
            step3_end_time = _time.time()
            logger.info(f"[Task {task_id}] [Step 3/5] RAG 检索总耗时: {(step3_end_time-step3a_time):.2f}s")
        else:
            logger.info(f"[Task {task_id}] [Step 3/5] 跳过RAG检索（已有数据）")
        
        step4_time = _time.time()
        logger.info(f"[Task {task_id}] [Step 4/5] 准备执行工作流...")
        
        # 创建事件发布函数 - 使用安全发布机制
        def on_event(event: dict) -> None:
            _safe_publish_event(task_id, event)

        _execute_analysis_core(
            task_id=task_id,
            jd_raw_text=jd_raw_text,
            resume_raw_text=resume_raw_text,
            rag_results=rag_results,
            db=db,
            on_event=on_event,
        )
        
        step5_time = _time.time()
        logger.info(f"[Task {task_id}] [Step 5/5] 工作流执行完成 ({(step5_time-step4_time):.2f}s)")
        logger.info(f"[Task {task_id}] ========== 后台分析任务完成 (总耗时: {(step5_time-total_start_time):.2f}s) ==========")
        
        _cache_analysis_result(db, task_id, job_id, resume_id)

    except Exception as exc:
        error_time = _time.time()
        total_duration = error_time - total_start_time
        logger.error(f"[Task {task_id}] ========== 后台分析任务失败 (耗时: {total_duration:.2f}s) ==========", exc_info=True)
        _update_task_status(db, task_id, AnalysisStatus.failed, str(exc))
    finally:
        db.close()
        logger.debug(f"[Task {task_id}] 数据库会话已关闭")


def create_analysis(db: Session, payload: AnalysisCreate) -> AnalysisTask:
    job = get_job(db, payload.job_id)
    resume = get_resume(db, payload.resume_id)
    if job is None or resume is None:
        raise ValueError("job_or_resume_not_found")

    cached = analysis_cache.get(job.id, resume.id)
    if cached is not None:
        logger.info(f"[Cache] 分析缓存命中: job_id={job.id}, resume_id={resume.id}")
        task = AnalysisTask(job_id=job.id, resume_id=resume.id, status=AnalysisStatus.success)
        db.add(task)
        db.commit()
        db.refresh(task)

        report_data = cached.get("report")
        if report_data:
            report = AnalysisReport(
                task_id=task.id,
                final_score=report_data.get("final_score", 0),
                score_breakdown=report_data.get("score_breakdown", {}),
                strengths=report_data.get("strengths", []),
                gaps=report_data.get("gaps", []),
                resume_suggestions=report_data.get("resume_suggestions", []),
                interview_questions=report_data.get("interview_questions", []),
                learning_plan=report_data.get("learning_plan", []),
                next_best_action=report_data.get("next_best_action", {}),
                evidence=report_data.get("evidence", []),
                scoring_version=report_data.get("scoring_version", "v1"),
            )
            db.add(report)
            db.commit()
            db.refresh(report)

        for run_data in cached.get("agent_runs", []):
            run = AgentRun(
                task_id=task.id,
                node_name=run_data.get("node_name", ""),
                status=run_data.get("status", "success"),
                input_snapshot=run_data.get("input_snapshot", {}),
                output_snapshot=run_data.get("output_snapshot", {}),
                execution_meta=run_data.get("execution_meta", {}),
            )
            db.add(run)
        db.commit()

        return task

    task = AnalysisTask(job_id=job.id, resume_id=resume.id, status=AnalysisStatus.running)
    db.add(task)
    db.commit()
    db.refresh(task)

    logger.info(f"[Task {task.id}] 任务创建成功，准备提交到后台...")

    sync_mode = os.environ.get("CAREERFIT_ANALYSIS_SYNC") == "1"

    if sync_mode:
        logger.info(f"[Task {task.id}] 同步模式执行...")
        try:
            jd_profile = parse_job_profile(job.raw_text)
            required_skills = jd_profile.get("required_skills") or []
            rag_results = _build_rag_results(db, required_skills)
            _run_analysis_sync(task.id, job.raw_text, resume_raw_text=resume.raw_text, rag_results=rag_results, db=db, mode=payload.mode)
            _cache_analysis_result(db, task.id, job.id, resume.id)
        except Exception as exc:
            logger.error(f"[Task {task.id}] 同步分析失败: {exc}")
            _update_task_status(db, task.id, AnalysisStatus.failed, str(exc))
    else:
        logger.info(f"[Task {task.id}] 提交到后台线程池...")
        analysis_thread_pool.submit(
            task.id,
            _run_analysis_background,
            task.id, job.id, resume.id, job.raw_text, resume.raw_text, {},
        )
        logger.info(f"[Task {task.id}] 已提交到后台线程池")

    return task


def get_report_by_task(db: Session, task_id: int) -> AnalysisReport | None:
    return db.query(AnalysisReport).filter(AnalysisReport.task_id == task_id).one_or_none()


def get_analysis_task(db: Session, task_id: int) -> AnalysisTask | None:
    return db.query(AnalysisTask).filter(AnalysisTask.id == task_id).one_or_none()


def list_agent_runs(db: Session, task_id: int) -> list[AgentRun]:
    return list(db.query(AgentRun).filter(AgentRun.task_id == task_id).order_by(AgentRun.id).all())
