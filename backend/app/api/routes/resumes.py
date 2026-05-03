from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.resumes import ResumeCreate, ResumeRead
from app.services.resume_service import create_resume, get_resume, list_resumes

router = APIRouter(prefix="/api/resumes", tags=["resumes"])


@router.post("", response_model=ResumeRead, status_code=status.HTTP_201_CREATED)
def create_resume_endpoint(payload: ResumeCreate, db: Session = Depends(get_db)):
    return create_resume(db, payload)


@router.get("", response_model=list[ResumeRead])
def list_resumes_endpoint(db: Session = Depends(get_db)):
    return list_resumes(db)


@router.get("/{resume_id}", response_model=ResumeRead)
def get_resume_endpoint(resume_id: int, db: Session = Depends(get_db)):
    resume = get_resume(db, resume_id)
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume
