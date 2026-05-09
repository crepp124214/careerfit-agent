import logging

from fastapi import APIRouter

from app.schemas.preview import (
    JdPreviewResponse,
    JdPreviewSkill,
    PreviewRequest,
    ResumePreviewEducation,
    ResumePreviewProject,
    ResumePreviewResponse,
)
from app.services.job_service import parse_job_profile
from app.services.resume_service import parse_resume_profile

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

router = APIRouter(prefix="/api", tags=["preview"])


@router.post("/jobs/parse-preview", response_model=JdPreviewResponse)
def jd_parse_preview(req: PreviewRequest) -> JdPreviewResponse:
    profile = parse_job_profile(req.content)
    skills = [
        JdPreviewSkill(
            name=d["name"],
            level=d.get("required_level", "mentioned"),
            category=d.get("category", "technical"),
        )
        for d in profile.get("skill_dimensions", [])
    ]
    return JdPreviewResponse(
        title=_guess_jd_title(req.content),
        category=profile.get("job_family", ""),
        skills=skills,
        requirements=profile.get("basic_requirements", []),
        domain_keywords=profile.get("domain_keywords", []),
    )


@router.post("/resumes/parse-preview", response_model=ResumePreviewResponse)
def resume_parse_preview(req: PreviewRequest) -> ResumePreviewResponse:
    profile = parse_resume_profile(req.content)
    skills = profile.get("skills", [])
    projects_raw = profile.get("projects", [])
    projects = [
        ResumePreviewProject(name=p) if isinstance(p, str) else ResumePreviewProject(
            name=p.get("name", ""),
            role=p.get("role", ""),
            highlights=p.get("highlights", []),
        )
        for p in projects_raw
    ]
    education = [
        ResumePreviewEducation(
            school=e.get("school", ""),
            major=e.get("major", ""),
            degree=e.get("degree", ""),
        )
        for e in profile.get("education", [])
    ]
    return ResumePreviewResponse(
        name=profile.get("candidate_name", ""),
        skills=skills,
        projects=projects,
        education=education,
        experience_years=profile.get("experience_years", 0),
    )


def _guess_jd_title(content: str) -> str:
    for line in content.split("\n"):
        line = line.strip()
        if len(line) > 4 and len(line) < 60:
            return line
    return ""
