from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.db.models import AnalysisReport, AnalysisTask, JobDescription, ResumeVersion
from app.schemas.reports import ReportHistoryItem, ReportHistoryResponse


def get_report_history(
    db: Session,
    job_id: int | None = None,
    resume_id: int | None = None,
    limit: int = 20,
) -> ReportHistoryResponse:
    clamped_limit = max(1, min(limit, 100))

    query = (
        db.query(AnalysisReport)
        .join(AnalysisTask)
        .join(JobDescription)
        .join(ResumeVersion)
        .order_by(desc(AnalysisReport.created_at))
    )

    if job_id is not None:
        query = query.filter(AnalysisTask.job_id == job_id)

    if resume_id is not None:
        query = query.filter(AnalysisTask.resume_id == resume_id)

    reports = query.limit(clamped_limit).all()

    items = []
    for report in reports:
        task = report.task
        job = task.job
        resume = task.resume

        gap_count = len(report.gaps) if report.gaps else 0

        high_risk_count = 0
        if report.resume_suggestions:
            for suggestion in report.resume_suggestions:
                if isinstance(suggestion, dict) and suggestion.get("risk_level") == "high":
                    high_risk_count += 1

        items.append(
            ReportHistoryItem(
                task_id=task.id,
                report_id=report.id,
                job_id=job.id,
                job_title=job.title,
                resume_id=resume.id,
                resume_label=resume.version_label,
                final_score=report.final_score,
                score_breakdown=report.score_breakdown,
                gap_count=gap_count,
                high_risk_suggestion_count=high_risk_count,
                created_at=report.created_at,
            )
        )

    return ReportHistoryResponse(schema_version="1", items=items)
