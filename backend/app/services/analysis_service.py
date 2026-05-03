from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.agents.graph import run_workflow
from app.db.models import AgentRun, AnalysisReport, AnalysisStatus, AnalysisTask
from app.schemas.analysis import AnalysisCreate
from app.services.job_service import get_job
from app.services.resume_service import get_resume


def create_analysis(db: Session, payload: AnalysisCreate) -> AnalysisTask:
    job = get_job(db, payload.job_id)
    resume = get_resume(db, payload.resume_id)
    if job is None or resume is None:
        raise ValueError("job_or_resume_not_found")

    task = AnalysisTask(job_id=job.id, resume_id=resume.id, status=AnalysisStatus.running)
    db.add(task)
    db.commit()
    db.refresh(task)

    try:
        final_state, trace = run_workflow({"raw_jd": job.raw_text, "raw_resume": resume.raw_text})
        match_result = final_state["match_result"]
        report = AnalysisReport(
            task_id=task.id,
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
        for item in trace:
            db.add(AgentRun(task_id=task.id, **item))
        task.status = AnalysisStatus.success
        task.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(task)
        return task
    except Exception as exc:
        task.status = AnalysisStatus.failed
        task.error_message = str(exc)
        task.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(task)
        return task


def get_report_by_task(db: Session, task_id: int) -> AnalysisReport | None:
    return db.query(AnalysisReport).filter(AnalysisReport.task_id == task_id).one_or_none()


def list_agent_runs(db: Session, task_id: int) -> list[AgentRun]:
    return list(db.query(AgentRun).filter(AgentRun.task_id == task_id).order_by(AgentRun.id).all())
