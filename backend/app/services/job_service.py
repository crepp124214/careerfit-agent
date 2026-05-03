import re

from sqlalchemy.orm import Session

from app.db.models import JobDescription
from app.schemas.jobs import JobCreate


KNOWN_SKILLS = [
    "FastAPI",
    "SQLAlchemy",
    "PostgreSQL",
    "Python",
    "Vue",
    "TypeScript",
    "Docker",
    "pytest",
    "API testing",
    "LangGraph",
]


def _skill_pattern(skill: str) -> re.Pattern[str]:
    return re.compile(rf"(?<![A-Za-z0-9]){re.escape(skill)}(?![A-Za-z0-9])", re.IGNORECASE)


def _find_evidence(raw_text: str, skill: str) -> list[str]:
    evidence = []
    for sentence in re.split(r"(?<=[.!?。！？])\s+", raw_text.strip()):
        if _skill_pattern(skill).search(sentence):
            evidence.append(sentence.strip())
    return evidence


def parse_job_profile(raw_text: str) -> dict:
    required_skills = [skill for skill in KNOWN_SKILLS if _find_evidence(raw_text, skill)]
    evidence = {skill: _find_evidence(raw_text, skill) for skill in required_skills}
    return {
        "schema_version": "job-profile-v1",
        "required_skills": required_skills,
        "preferred_skills": [],
        "domain_keywords": [],
        "basic_requirements": [],
        "evidence": evidence,
    }


def create_job(db: Session, payload: JobCreate) -> JobDescription:
    job = JobDescription(
        title=payload.title.strip(),
        raw_text=payload.raw_text,
        profile=parse_job_profile(payload.raw_text),
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def list_jobs(db: Session) -> list[JobDescription]:
    return list(db.query(JobDescription).order_by(JobDescription.created_at.desc()).all())


def get_job(db: Session, job_id: int) -> JobDescription | None:
    return db.get(JobDescription, job_id)
