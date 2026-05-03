from sqlalchemy.orm import Session

from app.db.models import ResumeVersion
from app.schemas.resumes import ResumeCreate
from app.services.job_service import KNOWN_SKILLS, _find_evidence


def parse_resume_profile(raw_text: str) -> dict:
    skills = [skill for skill in KNOWN_SKILLS if _find_evidence(raw_text, skill)]
    evidence = {skill: _find_evidence(raw_text, skill) for skill in skills}
    projects = [sentence.strip() for sentence in raw_text.split(".") if "built" in sentence.lower()]
    return {
        "schema_version": "resume-profile-v1",
        "skills": skills,
        "projects": projects,
        "domain_keywords": [],
        "evidence": evidence,
    }


def create_resume(db: Session, payload: ResumeCreate) -> ResumeVersion:
    resume = ResumeVersion(
        candidate_name=payload.candidate_name.strip(),
        version_label=payload.version_label.strip(),
        raw_text=payload.raw_text,
        profile=parse_resume_profile(payload.raw_text),
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


def list_resumes(db: Session) -> list[ResumeVersion]:
    return list(db.query(ResumeVersion).order_by(ResumeVersion.created_at.desc()).all())


def get_resume(db: Session, resume_id: int) -> ResumeVersion | None:
    return db.get(ResumeVersion, resume_id)
