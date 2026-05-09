from __future__ import annotations

from pydantic import BaseModel, Field


class PreviewRequest(BaseModel):
    content: str = Field(min_length=10, max_length=50000)


class JdPreviewSkill(BaseModel):
    name: str
    level: str = "mentioned"
    category: str = "technical"


class JdPreviewResponse(BaseModel):
    title: str = ""
    category: str = ""
    skills: list[JdPreviewSkill] = Field(default_factory=list)
    requirements: list[str] = Field(default_factory=list)
    domain_keywords: list[str] = Field(default_factory=list)


class ResumePreviewProject(BaseModel):
    name: str = ""
    role: str = ""
    highlights: list[str] = Field(default_factory=list)


class ResumePreviewEducation(BaseModel):
    school: str = ""
    major: str = ""
    degree: str = ""


class ResumePreviewResponse(BaseModel):
    name: str = ""
    skills: list[str] = Field(default_factory=list)
    projects: list[ResumePreviewProject] = Field(default_factory=list)
    education: list[ResumePreviewEducation] = Field(default_factory=list)
    experience_years: int = 0
