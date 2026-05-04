import re

from sqlalchemy.orm import Session

from app.db.models import ResumeVersion
from app.schemas.resumes import ResumeCreate
from app.services.job_service import SKILL_CATALOG, _find_evidence


def parse_resume_profile(raw_text: str) -> dict:
    evidence = {}
    skills = []
    for key, item in SKILL_CATALOG.items():
        matched = []
        for alias in item["aliases"]:
            matched.extend(_find_evidence(raw_text, alias))
        matched = list(dict.fromkeys(matched))
        if matched:
            evidence[key] = matched
            skills.append(item["name"])

    projects = [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?。！？\n])\s*", raw_text)
        if any(term in sentence for term in ["项目", "构建", "完成", "支持", "分析"])
    ]

    return {
        "schema_version": "resume-profile-v2",
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
