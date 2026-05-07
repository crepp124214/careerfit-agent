from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.jobs import JobCompareRequest, JobCompareResponse, JobCompareItem, JobCompareDimension, JobCreate, JobRead
from app.services.job_service import compare_jobs, create_job, get_job, list_jobs

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("", response_model=JobRead, status_code=status.HTTP_201_CREATED)
def create_job_endpoint(payload: JobCreate, db: Session = Depends(get_db)):
    return create_job(db, payload)


@router.get("", response_model=list[JobRead])
def list_jobs_endpoint(db: Session = Depends(get_db)):
    return list_jobs(db)


@router.get("/{job_id}", response_model=JobRead)
def get_job_endpoint(job_id: int, db: Session = Depends(get_db)):
    job = get_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/compare", response_model=JobCompareResponse)
def compare_jobs_endpoint(payload: JobCompareRequest, db: Session = Depends(get_db)):
    try:
        items = compare_jobs(db, payload.job_ids)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    compare_items = [
        JobCompareItem(
            job_id=item["job_id"],
            job_title=item["job_title"],
            dimensions=[JobCompareDimension(**d) for d in item["dimensions"]],
        )
        for item in items
    ]
    return JobCompareResponse(items=compare_items)
