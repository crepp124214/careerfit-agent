from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SkillDimension(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    canonical_key: str
    category: str
    weight: float = Field(ge=0, le=1)
    required_level: Literal["mentioned", "basic_usage", "project_practice", "deep_experience"]
    jd_evidence: list[str] = Field(min_length=1)
    aliases: list[str] = Field(default_factory=list)

    @field_validator("name", "canonical_key", "category")
    @classmethod
    def non_empty_text(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("字段不能为空")
        return stripped


class JDParseOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    job_family: str
    dimensions: list[SkillDimension] = Field(min_length=1)
    evidence_summary: str


class ResumeEvidenceItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    skill_key: str
    evidence: list[str] = Field(default_factory=list)
    expression_level: Literal["not_mentioned", "mentioned", "basic_usage", "project_practice", "deep_experience"]


class ResumeParseOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    skills: list[ResumeEvidenceItem]
    project_summary: str
    evidence_summary: str


class RagQueryItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    skill_key: str
    query: str
    job_family: str
    doc_types: list[str] = Field(default_factory=list)


class RagQueryPlanOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    queries: list[RagQueryItem] = Field(min_length=1)


class GapItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    skill_key: str
    gap_type: Literal["missing_skill", "weak_evidence", "expression_gap", "knowledge_insufficient"]
    reason: str
    priority: Literal["high", "medium", "low"]


class GapAnalysisOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    gaps: list[GapItem]
    strengths: list[dict]


class ResumeSuggestionOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    suggestions: list[dict]


class InterviewQuestionOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    questions: list[dict]


class LearningPlanOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tasks: list[dict]


class NextBestActionOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    description: str
    target_skill: str | None = None


class IntegrityCriticOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    risk_level: Literal["low", "medium", "high"]
    risk_codes: list[str] = Field(default_factory=list)
    reason: str
