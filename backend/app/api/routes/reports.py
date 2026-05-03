from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.reports import ReportHistoryResponse, ReportRead
from app.services.analysis_service import get_report_by_task
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
    return report
