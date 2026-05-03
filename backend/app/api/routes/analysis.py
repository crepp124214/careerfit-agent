from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.analysis import AnalysisCreate, AnalysisTaskRead
from app.services.analysis_service import create_analysis

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.post("", response_model=AnalysisTaskRead, status_code=status.HTTP_201_CREATED)
def create_analysis_endpoint(payload: AnalysisCreate, db: Session = Depends(get_db)):
    try:
        return create_analysis(db, payload)
    except ValueError as exc:
        if str(exc) == "job_or_resume_not_found":
            raise HTTPException(status_code=404, detail="Job or resume not found") from exc
        raise
