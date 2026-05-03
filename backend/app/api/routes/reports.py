from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.reports import ReportRead
from app.services.analysis_service import get_report_by_task

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/{task_id}", response_model=ReportRead)
def get_report_endpoint(task_id: int, db: Session = Depends(get_db)):
    report = get_report_by_task(db, task_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return report
