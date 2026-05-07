from fastapi import APIRouter, Depends, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.resumes import ResumeCreate, ResumeDiffResponse, ResumeRead, ResumeUploadResponse
from app.services.file_parser import parse_upload
from app.services.resume_diff_service import compare_resumes
from app.services.resume_service import create_resume, get_resume, list_resumes

router = APIRouter(prefix="/api/resumes", tags=["resumes"])


@router.post("", response_model=ResumeRead, status_code=status.HTTP_201_CREATED)
def create_resume_endpoint(payload: ResumeCreate, db: Session = Depends(get_db)):
    return create_resume(db, payload)


@router.post("/upload", response_model=ResumeUploadResponse, status_code=status.HTTP_201_CREATED)
def upload_resume_endpoint(
    file: UploadFile,
    candidate_name: str = Form(""),
    version_label: str = Form("uploaded"),
    db: Session = Depends(get_db),
):
    content = file.file.read()
    raw_text = parse_upload(file.filename or "upload", content)
    candidate_name = candidate_name or file.filename or "上传简历"

    create_payload = ResumeCreate(
        candidate_name=candidate_name,
        version_label=version_label,
        raw_text=raw_text,
    )
    resume = create_resume(db, create_payload)

    return ResumeUploadResponse(
        id=resume.id,
        candidate_name=resume.candidate_name,
        version_label=resume.version_label,
        raw_text=resume.raw_text,
        parsed_from=file.filename or "unknown",
        profile=resume.profile,
        created_at=resume.created_at,
    )


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
