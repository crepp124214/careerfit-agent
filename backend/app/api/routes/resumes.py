from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.resumes import ResumeCreate, ResumeDiffResponse, ResumeRead
from app.services.resume_diff_service import compare_resumes
from app.services.resume_service import create_resume, get_resume, list_resumes

router = APIRouter(prefix="/api/resumes", tags=["resumes"])


@router.post("", response_model=ResumeRead, status_code=status.HTTP_201_CREATED)
def create_resume_endpoint(payload: ResumeCreate, db: Session = Depends(get_db)):
    return create_resume(db, payload)


@router.get("", response_model=list[ResumeRead])
def list_resumes_endpoint(db: Session = Depends(get_db)):
    return list_resumes(db)


@router.get("/compare", response_model=ResumeDiffResponse)
def compare_resumes_endpoint(
    from_id: int = Query(...),
    to_id: int = Query(...),
    db: Session = Depends(get_db),
):
    if from_id == to_id:
        raise HTTPException(status_code=400, detail="Cannot compare the same resume version")

    result = compare_resumes(db, from_id, to_id)
    if result is None:
        raise HTTPException(status_code=404, detail="One or both resume versions not found")
    return result


@router.get("/{resume_id}", response_model=ResumeRead)
def get_resume_endpoint(resume_id: int, db: Session = Depends(get_db)):
    resume = get_resume(db, resume_id)
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume
