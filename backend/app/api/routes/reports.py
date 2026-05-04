from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.db.models import AnalysisReport, JobDescription, ResumeVersion
from app.db.session import get_db
from app.schemas.reports import ReportHistoryResponse, ReportRead
from app.services.analysis_service import get_report_by_task
from app.services.export_service import generate_html_report, generate_markdown_report
from app.services.report_history_service import get_report_history

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/history", response_model=ReportHistoryResponse)
def get_report_history_endpoint(
    db: Session = Depends(get_db),
    job_id: int | None = Query(default=None),
    resume_id: int | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
):
    return get_report_history(db, job_id=job_id, resume_id=resume_id, limit=limit)


@router.get("/{task_id}", response_model=ReportRead)
def get_report_endpoint(task_id: int, db: Session = Depends(get_db)):
    report = get_report_by_task(db, task_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    report_dict = {
        "id": report.id,
        "task_id": report.task_id,
        "final_score": report.final_score,
        "score_breakdown": report.score_breakdown or {},
        "score_items": report.evidence or [],
        "strengths": report.strengths or [],
        "gaps": report.gaps or [],
        "resume_suggestions": report.resume_suggestions or [],
        "interview_questions": report.interview_questions or [],
        "learning_plan": report.learning_plan or [],
        "next_best_action": report.next_best_action or {},
        "evidence": report.evidence or [],
        "scoring_version": report.scoring_version,
        "created_at": report.created_at,
    }
    return report_dict


@router.get("/{task_id}/export")
def export_report_endpoint(
    task_id: int,
    format: str = Query(default="markdown", pattern="^(markdown|pdf)$"),
    db: Session = Depends(get_db),
):
    report = get_report_by_task(db, task_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")

    db_report = db.query(AnalysisReport).filter(AnalysisReport.task_id == task_id).first()
    if db_report is None:
        raise HTTPException(status_code=404, detail="Report not found")

    task = db_report.task
    job = task.job if task else None
    resume = task.resume if task else None

    if job is None or resume is None:
        raise HTTPException(status_code=404, detail="Job or resume not found")

    if format == "markdown":
        content = generate_markdown_report(db_report, job, resume)
        return Response(
            content=content.encode("utf-8"),
            media_type="text/markdown; charset=utf-8",
            headers={"Content-Disposition": f"attachment; filename=report-{task_id}.md"},
        )

    if format == "pdf":
        html_content = generate_html_report(db_report, job, resume)
        return Response(
            content=html_content.encode("utf-8"),
            media_type="text/html; charset=utf-8",
            headers={"Content-Disposition": f"inline; filename=report-{task_id}.html"},
        )

    raise HTTPException(status_code=400, detail="Unsupported format")
